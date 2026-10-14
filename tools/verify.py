"""Validate manifests, battle routing, randomized cue stability, and every audio file."""
import hashlib, json, os, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(root.parent/'.tools/toolmusic-deps'),str(root.parent/'.tools/python')]
from lupa.lua53 import LuaRuntime
import soundfile as sf
import numpy as np
catalog=json.loads((root/'catalog.json').read_text())
song_count=len(catalog)
assert song_count==len({r['slug'] for r in catalog})==len({r['title'].casefold() for r in catalog})
digests=[hashlib.sha256((root/'midi'/f"{r['slug']}.mid").read_bytes()).hexdigest() for r in catalog]
assert len(set(digests))==song_count,'Duplicate MIDI payloads'
lua=LuaRuntime(unpack_returned_tuples=True)
lua.globals().song_count=song_count
os.chdir(root.parent/'gen1recomp-0.3.54')
lua.globals().manifest_json=(root/'manifest.json').read_text()
lua.globals().entry=(root/'main.lua').read_text()
lua.globals().mod_sources=lua.table_from({p.relative_to(root).as_posix():p.read_text() for p in root.rglob('*.lua')})
lua.execute('''
package.path='./?.lua;'..package.path
local Manifest=require('src.mods.Manifest')
local json=require('src.link.Json')
local raw=json.decode(manifest_json)
Manifest.validate(raw,'ToolBattleMusic')
local Schemas=require('src.mods.Schemas')
local hook, ended
local options={regular='sober',gym='aenima',league='eulogy'}
local registered={}
local mod={id='toolbattlemusic',generation=1,read=function(_,p)return mod_sources[p]end,
  info=function()return {type='file',size=1}end,
  assets={path=function(_,p)return 'mods/ToolBattleMusic/'..p end},
  content={screens={register=function()end},music={register=function(_,id,def)
    local ok,err=Schemas.check(Schemas.REGISTRIES.music,'music',id,def,'register')
    assert(ok,err);registered[id]=def
  end}},options={define=function(_,rows)
    assert(#rows==3)
    for _,r in ipairs(rows)do assert(#r.choices==song_count+2) end
  end,get=function(_,key)return options[key]end},
  hooks={wrap=function(_,name,f)if name=='music.select' then hook=f end end},
  events={on=function(_,name,f)if name=='battle.ended' then ended=f end end}}
assert(load(entry))()(mod)
local count=0;for _ in pairs(registered)do count=count+1 end;assert(count==song_count)
local function cue(kind,id,reason)
  return hook(function(s)return s end,'Vanilla',{kind=kind,trainerId=id,reason=reason or 'battle'})
end
assert(cue('wild')=='Music_Tool_sober')
assert(cue('trainer','OPP_GIOVANNI')=='Music_Tool_sober')
assert(cue('gym','OPP_GIOVANNI')=='Music_Tool_aenima')
assert(cue('gym','OPP_BROCK')=='Music_Tool_aenima')
for _,id in ipairs({'OPP_LORELEI','OPP_BRUNO','OPP_AGATHA','OPP_LANCE','OPP_RIVAL3'})do
  assert(cue('gym',id)=='Music_Tool_eulogy')
end
assert(cue(nil,nil,'map')=='Vanilla')
assert(cue(nil,nil,'victory')=='Vanilla')
options.gym='original';assert(cue('gym','OPP_BROCK')=='Vanilla')
options.regular='random'
local previous,seen=nil,{}
for i=1,2000 do
  ended()
  local song=cue('wild');assert(registered[song]);assert(song~=previous)
  assert(cue('wild')==song,'repeated transition/entry cue changed song')
  seen[song]=true;previous=song
end
count=0;for _ in pairs(seen)do count=count+1 end;assert(count==song_count)
print('PASS: manifest, music schema, category routing, Original, map/victory passthrough, random stability and all song choices')
''')
report=json.loads((root/'audio-report.json').read_text())
assert set(report)=={r['slug'] for r in catalog}
for slug,data in report.items():
    peak=0
    power,count=0.0,0
    with sf.SoundFile(root/'audio'/f'{slug}.flac') as audio:
        assert audio.samplerate==22050 and audio.channels==1
        assert abs(audio.frames/audio.samplerate-data['seconds'])<.01
        while True:
            block=audio.read(4096,dtype='float32')
            if not len(block): break
            assert np.isfinite(block).all()
            peak=max(peak,float(np.max(np.abs(block))))
            power+=float(np.sum(block.astype(np.float64)**2));count+=block.size
    assert 0.05<peak<=1.0,(slug,peak)
    if 'rms_after' in data:
        assert np.sqrt(power/count)>=.165,(slug,'quiet mastered track')
    assert hashlib.sha256((root/'audio'/f'{slug}.flac').read_bytes()).hexdigest()==data['ogg_sha256']
print(f'PASS: {song_count} full-length Gen 1 FLAC files decode, meet loudness and peak targets, and contain no duplicate MIDI payloads')
lua=LuaRuntime(unpack_returned_tuples=True)
files={'mods/ToolBattleMusic/'+p.relative_to(root).as_posix():p.read_text()
       for p in root.rglob('*') if p.suffix in ('.lua','.json')}
for song in catalog:
    for prefix in ('audio/','audio/gen2/','audio/gen3/'):
        files['mods/ToolBattleMusic/'+prefix+song['slug']+'.flac']='fixture audio'
lua.globals().files=lua.table_from(files)
lua.execute("package.path='./?.lua;'..package.path")
lua.execute((root/'tools/menu-tests.lua').read_text())
lua.execute((root/'tools/gen2-tests.lua').read_text())
menu_test=(root/'tools/menu-tests.lua').read_text()
manifest=json.loads((root/'manifest.json').read_text())
for game in manifest['games']:
    vm=LuaRuntime(unpack_returned_tuples=True)
    vm.globals().files=vm.table_from(files)
    vm.execute("package.path='./?.lua;'..package.path")
    if game in ('ruby','sapphire','emerald','firered','leafgreen'):
        test=menu_test.replace("'emerald'",repr(game)).replace(
            "package.loaded['src.ui.game3.rse.option_menu']=menu",
            "package.loaded['src.ui.game3.rse.option_menu']=menu;package.loaded['src.ui.game3.option_menu']=menu")
    elif game in ('gold','silver','crystal'):
        test=menu_test.split('local loader=Loader.new')[0].replace("'emerald'",repr(game))
        test+=(root/'tools/gen2-tests.lua').read_text().replace("version='crystal'",f"version='{game}'")
    else:
        test=menu_test.split('local loader=Loader.new')[0].replace("'emerald'",repr(game))
        test+=f"""
local loader=Loader.new({{fs=fs,generation=1,version='{game}'}})
local data={{pokemon={{}},audio={{songs={{}}}}}}
assert(loader:load(data))
assert(loader.mods.toolbattlemusic.state=='loaded')
assert(data.audio.songs.Music_Tool_sober.file=='mods/ToolBattleMusic/audio/sober.flac')
assert(#loader.optionSchemas.toolbattlemusic==3)
local rows=loader.hooks:call('ui.options.rows',function(_,r)return r end,{{}}, {{}})
assert(rows[1].label=='TOOL MUSIC')
local manager=setmetatable({{game={{mods=loader,save={{options={{}}}}}},status=loader:status(),
screen='list',tab=1,cursor=1,scroll=1}},require('src.mods.ManagerState'))
manager:snapCursor();assert(manager.cursor==2)
"""
    vm.execute(test)
    print(f'PASS: unified mod automatically loads the correct system in {game}')
for style in ('gen2','gen3'):
    variant_report=json.loads((root/f'audio-report-{style}.json').read_text())
    assert set(variant_report)==set(report)
    for slug,record in variant_report.items():
        with sf.SoundFile(root/'audio'/style/f'{slug}.flac') as audio:
            assert audio.samplerate==record['sample_rate'] and audio.channels==record['channels']
            assert abs(audio.frames/audio.samplerate-record['seconds'])<.01
            peak=0
            power,count=0.0,0
            while True:
                block=audio.read(4096,dtype='float32')
                if not len(block):break
                assert np.isfinite(block).all()
                peak=max(peak,float(np.max(np.abs(block))))
                power+=float(np.sum(block.astype(np.float64)**2));count+=block.size
            assert .05<peak<=1.0,(style,slug,peak)
            if 'rms_after' in record:
                assert np.sqrt(power/count)>=.165,(style,slug,'quiet mastered track')
                if record['loudness_gain_db']>0:assert peak<=1.0,(style,slug,'encoded peak clipping')
        assert hashlib.sha256((root/'audio'/style/f'{slug}.flac').read_bytes()).hexdigest()==record['ogg_sha256']
        assert record['ogg_sha256']!=report[slug]['ogg_sha256']
    print(f'PASS: {style} soundtrack has {song_count} distinct full-length decoded renders')
