"""Remove codec overshoots from encoded files and record measured final levels."""
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/'.tools/toolmusic-deps'))
import numpy as np
import soundfile as sf
for style in ('classic','gen2','gen3'):
    directory=root/'audio' if style=='classic' else root/'audio'/style
    report_path=root/('audio-report.json' if style=='classic' else f'audio-report-{style}.json')
    report=json.loads(report_path.read_text())
    for path in directory.glob('*.flac'):
        with sf.SoundFile(path) as stream:
            rate,channels=stream.samplerate,stream.channels
            blocks=[]
            while True:
                block=stream.read(4096,dtype='float32')
                if not len(block):break
                blocks.append(block)
        data=np.concatenate(blocks)
        peak=float(np.max(np.abs(data)))
        for attempt in range(3):
            if peak<=1:break
            data*=.98/peak
            with sf.SoundFile(path,'w',samplerate=rate,channels=channels,format='FLAC',subtype='PCM_16') as stream:
                for offset in range(0,len(data),4096):stream.write(data[offset:offset+4096])
            with sf.SoundFile(path) as stream:
                data=np.concatenate(list(stream.blocks(blocksize=4096,dtype='float32')))
            peak=float(np.max(np.abs(data)))
            print('Adjusted codec peak:',style,path.stem,peak,flush=True)
        rms=float(np.sqrt(np.mean(data.astype(np.float64)**2)))
        assert peak<=1 and rms>=.165,(style,path.stem,peak,rms)
        report[path.stem].update(decoded_peak=round(peak,6),rms_after=round(rms,6),
            ogg_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    report_path.write_text(json.dumps(report,indent=2)+'\n')
print('PASS: all decoded tracks meet vanilla-reference loudness and remain within full scale')
