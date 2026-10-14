"""Measure native battle audio and master custom streams to a consistent loudness."""
import argparse,hashlib,json,os,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(root.parent/'.tools/toolmusic-deps'),str(root.parent/'.tools/python')]
import numpy as np
import soundfile as sf
from render import master_loudness,TARGET_RMS
from lupa.lua53 import LuaRuntime
os.chdir(root.parent/'gen1recomp-0.3.54')
vm=LuaRuntime(unpack_returned_tuples=True,encoding='latin1')
bit=(root/'tools/menu-tests.lua').read_text().split("local Loader=require")[0]
vm.execute("package.path='./?.lua;'..package.path\n"+bit)
cache_root=root.parent/'.tools/audio-real-cache/firered'
def read_cache(relative):
    path=cache_root/relative
    return path.read_bytes() if path.exists() else None
vm.globals().read_cache=read_cache
vm.execute('''
local Player=require('src.core.game3.m4a_player')
local cache={read=function(_,path)return read_cache(path)end}
local pack=assert(Player.loadPack(cache))
function native(id)
 return Player.bakeSong(pack,cache,id,{maxSec=12,master=1})
end
''')
parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
report={}
for song in (296,297,298,299):
    result=vm.globals().native(song)
    left,right=result[:2]
    audio=np.column_stack((list(left.values()),list(right.values())))
    rms=float(np.sqrt(np.mean(np.clip(audio,-1,1)**2)))
    report[str(song)]={'rms':rms,'peak':float(np.max(np.abs(audio)))}
    print(song,report[str(song)],flush=True)
for style in ('classic','gen2','gen3'):
    directory=root/'audio' if style=='classic' else root/'audio'/style
    report_path=root/('audio-report.json' if style=='classic' else f'audio-report-{style}.json')
    records=json.loads(report_path.read_text())
    for path in sorted(directory.glob('*.flac')):
        blocks=[]
        with sf.SoundFile(path) as stream:
            rate,channels=stream.samplerate,stream.channels
            while True:
                block=stream.read(4096,dtype='float32')
                if not len(block):break
                blocks.append(block)
        audio=np.concatenate(blocks)
        mastered,gain,before,after=master_loudness(audio)
        print(style,path.stem,'RMS',round(before,4),'->',round(after,4),flush=True)
        if args.apply:
            if gain>1 or not np.array_equal(mastered,audio):
                with sf.SoundFile(path,'w',samplerate=rate,channels=channels,format='FLAC',subtype='PCM_16') as stream:
                    for offset in range(0,len(mastered),4096):stream.write(mastered[offset:offset+4096])
            record=records[path.stem]
            record.update(loudness_gain_db=round(float(20*np.log10(gain)),3),
                rms_before=round(before,6),rms_after=round(after,6),
                ogg_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    if args.apply:report_path.write_text(json.dumps(records,indent=2)+'\n')
(root/'native-loudness-reference.json').write_text(json.dumps(report,indent=2)+'\n')
