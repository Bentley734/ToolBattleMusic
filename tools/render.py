"""Reproducible full-length MIDI to chip-style FLAC renderer (no soundfont)."""
import argparse, hashlib, json, re, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
deps = ROOT.parent / '.tools' / 'toolmusic-deps'
if deps.exists(): sys.path.insert(0, str(deps))
import mido
import numpy as np
import soundfile as sf
RATE = 22050
TARGET_RMS = 0.17  # measured vanilla GBA battle themes: 0.1455–0.1706
def master_loudness(audio):
    """Raise quiet arrangements to native battle levels with a soft peak ceiling."""
    before=float(np.sqrt(np.mean(audio.astype(np.float64)**2)))
    if before>=TARGET_RMS and float(np.max(np.abs(audio)))<=.9: return audio,1.0,before,before
    def limited(gain):
        boosted=audio*gain
        magnitude=np.abs(boosted)
        limited=np.where(magnitude>.55,.55+.15*np.tanh((magnitude-.55)/.15),magnitude)
        return np.sign(boosted)*limited
    lo,hi=1.0,max(2.0,TARGET_RMS/max(before,1e-8)*2)
    initial=limited(1)
    initial_rms=float(np.sqrt(np.mean(initial.astype(np.float64)**2)))
    if initial_rms>=TARGET_RMS:return initial,1.0,before,initial_rms
    for _ in range(10):
        gain=(lo+hi)/2
        out=limited(gain)
        rms=float(np.sqrt(np.mean(out.astype(np.float64)**2)))
        if rms<TARGET_RMS:lo=gain
        else:hi=gain
    mastered=limited(hi)
    return mastered,hi,before,float(np.sqrt(np.mean(mastered.astype(np.float64)**2)))
def four_channel(notes):
    """Two pulse voices, one bass wave voice, one noise voice; steal oldest voice."""
    ends=[0.0]*4; slots=[None]*4; out=[]
    for start,end,ch,note,vel,program in sorted(notes):
        candidates=[3] if ch==9 else ([2] if 32<=program<=39 else [0,1])
        free=[slot for slot in candidates if ends[slot]<=start]
        slot=free[0] if free else min(candidates,key=lambda s:ends[s])
        if slots[slot] is not None and ends[slot]>start:
            previous=out[slots[slot]];previous[1]=start
        record=[start,max(start+.02,end),ch,note,round(vel/127*15)*127/15,program,slot]
        slots[slot]=len(out);ends[slot]=record[1];out.append(record)
    return [tuple(row) for row in out if row[1]>row[0]]

def render(path, target, style='classic'):
    rate=32000 if style=='gen3' else RATE
    midi = mido.MidiFile(path)
    active, notes, programs = {}, [], [0]*16
    now = 0
    def finish(key):
        for start, vel, program in active.pop(key, []):
            notes.append((start, now, key[0], key[1], vel, program))
    for msg in midi:
        now += msg.time
        if msg.type == 'program_change': programs[msg.channel] = msg.program
        elif msg.type == 'note_on' and msg.velocity:
            active.setdefault((msg.channel,msg.note),[]).append((now,msg.velocity,programs[msg.channel]))
        elif msg.type == 'note_off' or (msg.type == 'note_on' and not msg.velocity):
            finish((msg.channel,msg.note))
    for key in list(active): finish(key)
    assert notes, f'No notes: {path}'
    duration=max(n[1] for n in notes)+0.15
    if style=='gen2': notes=four_channel(notes)
    audio=np.zeros((int(duration*rate)+1,2),np.float32) if style=='gen3' else np.zeros(int(duration*rate)+1,np.float32)
    rng=np.random.default_rng(1117)
    for record in notes:
        start,end,ch,note,vel,program=record[:6]
        slot=record[6] if style=='gen2' else None
        length=min(end-start if style=='gen2' else max(end-start,0.04)+0.04, duration-start)
        count=int(length*rate)
        if count < 1: continue
        t=np.arange(count,dtype=np.float32)/rate
        freq=440*2**((note-69)/12)
        if ch==9:
            if note in (35,36): wave=np.sin(2*np.pi*(55*t+2*(1-np.exp(-30*t))))*np.exp(-18*t)
            else: wave=rng.uniform(-1,1,count).astype(np.float32)*np.exp(-t*(45 if note in (42,44,46) else 18))
            gain=0.18
        elif style=='gen2':
            if slot==2:
                wave=2*np.abs(2*((freq*t)%1)-1)-1
                wave=np.round((wave+1)*7.5)/7.5-1
            else:
                duty=.125 if slot==0 else .5
                wave=np.zeros(count,np.float32)
                for harmonic in range(1,min(24,int(rate/(2*freq))+1)):
                    wave+=np.sin(np.pi*harmonic*duty)*np.cos(2*np.pi*freq*harmonic*t-np.pi*harmonic*duty)/harmonic
            gain=.12 if slot==2 else .085
        elif style=='gen3':
            # GBA-style PCM timbres: bass, guitar, piano, pads, and leads.
            wave=np.zeros(count,np.float32)
            for harmonic in range(1,min(20,int(rate/(2*freq))+1)):
                decay=2 if 32<=program<=39 else (1.1 if 24<=program<=31 else 1.7)
                phase=.003*np.sin(2*np.pi*5*t) if program>=80 else 0
                wave+=np.sin(2*np.pi*freq*harmonic*(t+phase/freq))/(harmonic**decay)
            if 24<=program<=31: wave=np.tanh(wave*2)*np.exp(-.65*t)
            elif program<24: wave*=np.exp(-1.4*t)
            wave=np.round(wave*127)/127
            gain=.08
        else:
            # Band-limited harmonic oscillators: bass triangle, melodic pulse.
            wave=np.zeros(count,np.float32)
            bass=32<=program<=39
            for harmonic in range(1,min(16,int(RATE/(2*freq))+1),2):
                wave+=np.sin(2*np.pi*freq*harmonic*t)/(harmonic**2 if bass else harmonic)
            gain=0.09 if bass else 0.055
        env=np.minimum(t/0.006,1)*np.minimum((length-t)/0.035,1)
        offset=int(start*rate)
        samples=wave*env*gain*(vel/127)
        if style=='gen3':
            pan=.5 if ch==9 else .2+.6*((ch*7)%16)/15
            audio[offset:offset+count,0]+=samples*np.sqrt(1-pan)
            audio[offset:offset+count,1]+=samples*np.sqrt(pan)
        else: audio[offset:offset+count]+=samples
    peak=float(np.max(np.abs(audio)))
    assert peak>0
    audio*=0.92/peak
    # Quiet boundary avoids a click when the complete arrangement repeats.
    fade=min(int(.025*rate),len(audio)//2)
    envelope=np.linspace(0,1,fade)
    if style=='gen3':envelope=envelope[:,None]
    audio[:fade]*=envelope;audio[-fade:]*=envelope[::-1]
    audio,loudness_gain,rms_before,rms_after=master_loudness(audio)
    # Remove the MIDI's silent pickup before encoding, while retaining quiet
    # audible attacks and all later pauses in the arrangement.
    audible=np.abs(audio)>=1/32768
    if audio.ndim>1:audible=np.any(audible,axis=1)
    onset=np.flatnonzero(audible)
    leading=int(onset[0]) if len(onset) else 0
    audio=audio[leading:]
    with sf.SoundFile(target,'w',samplerate=rate,channels=2 if style=='gen3' else 1,format='FLAC',subtype='PCM_16') as stream:
        for offset in range(0,len(audio),4096): stream.write(audio[offset:offset+4096])
    return {'style':style,'sample_rate':rate,'channels':2 if style=='gen3' else 1,
            'seconds':round(len(audio)/rate,3),'leading_silence_removed_seconds':leading/rate,'notes':len(notes),'peak':round(peak,4),
            'loudness_gain_db':round(20*np.log10(loudness_gain),3),
            'rms_before':round(rms_before,6),'rms_after':round(rms_after,6),
            'midi_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'ogg_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true')
    parser.add_argument('--style',choices=['classic','gen2','gen3'],default='classic')
    args=parser.parse_args()
    for directory in ('midi','audio'): (ROOT/directory).mkdir(exist_ok=True)
    catalog=json.loads((ROOT/'catalog.json').read_text())
    report={}
    output=ROOT/'audio' if args.style=='classic' else ROOT/'audio'/args.style
    output.mkdir(parents=True,exist_ok=True)
    for song in catalog:
        title,slug=song['title'],song['slug'];path=ROOT/'midi'/f'{slug}.mid'
        url=song.get('download',song['source'])
        if args.download:
            data=urllib.request.urlopen(url,timeout=60).read()
            assert data.startswith(b'MThd'),f'Not MIDI: {url}'
            path.write_bytes(data)
        report[slug]={**song,**render(path,output/f'{slug}.flac',args.style)}
        print(title,report[slug]['seconds'],flush=True)
    name='audio-report.json' if args.style=='classic' else f'audio-report-{args.style}.json'
    (ROOT/name).write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__': main()
