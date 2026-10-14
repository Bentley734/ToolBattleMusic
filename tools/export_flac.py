import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'.tools/toolmusic-deps'))
import numpy as np
import soundfile as sf
from render import master_loudness
for style in ('classic','gen2','gen3'):
    folder=root/'audio' if style=='classic' else root/'audio'/style
    report_path=root/('audio-report.json' if style=='classic' else f'audio-report-{style}.json')
    records=json.loads(report_path.read_text())
    for path in folder.glob('*.ogg'):
        with sf.SoundFile(path) as stream:
            rate,channels=stream.samplerate,stream.channels
            blocks=[]
            while True:
                block=stream.read(4096,dtype='float32')
                if not len(block):break
                blocks.append(block)
        samples,gain,before,after=master_loudness(np.concatenate(blocks))
        target=path.with_suffix('.flac')
        with sf.SoundFile(target,'w',samplerate=rate,channels=channels,format='FLAC',subtype='PCM_16') as stream:
            for offset in range(0,len(samples),4096):stream.write(samples[offset:offset+4096])
        assert np.max(np.abs(samples))<=1 and after>=.165
        records[path.stem].update(rms_after=round(after,6),format='FLAC',
            decoded_peak=round(float(np.max(np.abs(samples))),6),
            ogg_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        print(style,path.stem,round(after,4),flush=True)
    report_path.write_text(json.dumps(records,indent=2)+'\n')
# Switch the shipped code, tests and renderer to lossless assets.
for path in root.rglob('*'):
    if path.suffix not in ('.py','.lua','.md') or path.name=='export_flac.py':continue
    source=path.read_text(encoding='utf-8')
    source=source.replace('.ogg','.flac').replace("format='OGG',subtype='VORBIS'","format='FLAC',subtype='PCM_16'")
    source=source.replace('OGG','FLAC')
    path.write_text(source,encoding='utf-8')
