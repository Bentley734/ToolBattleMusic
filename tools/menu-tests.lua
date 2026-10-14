package.preload.bit=function()
  local b={}
  b.band=function(a,c,...)local n=a&c;for _,v in ipairs({...})do n=n&v end;return n end
  b.bor=function(a,c,...)local n=a|c;for _,v in ipairs({...})do n=n|v end;return n end
  b.bxor=function(a,c,...)local n=a~c;for _,v in ipairs({...})do n=n~v end;return n end
  b.bnot=function(a)return (~a)&0xffffffff end
  b.lshift=function(a,c)return (a<<c)&0xffffffff end
  b.rshift=function(a,c)return (a&0xffffffff)>>c end
  b.rol=function(a,c)return ((a<<c)|((a&0xffffffff)>>(32-c)))&0xffffffff end
  b.tobit=function(a)return a&0xffffffff end
  return b
end
bit=require('bit')
local Loader=require('src.mods.Loader')
local Runtime=require('src.mods.Runtime')
love=require('tests.love_stub')
love.audio=love.audio or {}
local sources={}
local Audio={_bgmVolume=.6,_bgmSource={setVolume=function(self,v)self.volume=v end},
  songs=function()return {MUS_VS_WILD=1,MUS_VS_TRAINER=2,MUS_VS_GYM_LEADER=3,
    MUS_VS_ELITE_FOUR=4,MUS_VS_CHAMPION=5,MUS_VS_FRONTIER_BRAIN=6,MUS_ROUTE101=7,MUS_VICTORY_TRAINER=8}end,
  resolveSong=function(id)return id end,songInfo=function()return {}end}
function Audio.playSong(id,opts) Audio.id=id;Audio._bgmPaused=false;Audio._bgmSource.volume=.6;return true end
function Audio.applyGain() Audio._bgmSource.volume=.6 end
function Audio.pauseBgm()Audio._bgmPaused=true end
function Audio.resumeBgm()Audio._bgmPaused=false end
function Audio.playFanfare()Audio._fanfareActive=true end
function Audio.update()Audio._bgmSource.volume=.6 end
function Audio.pumpBgm()Audio._bgmSource.volume=.6 end
function Audio.applyEngineOptions(opts)Audio._bgmVolume=(opts.musicVol or 7)/7 end
function Audio.setSuspended(flag)Audio.suspended=flag end
function Audio.stopAll()Audio.id=nil end
function Audio.endSession()Audio.id=nil end
function Audio.shutdown()Audio.id=nil end
package.loaded['src.core.game3.audio']=Audio
local Trainers={get=function(id)return {class=id}end,getBattleMusicRole=function()return 'battleGymLeader',3 end}
package.loaded['src.core.game3.scripting.trainers']=Trainers
local Rows={build=function()return {{id='other',label='OTHER'}}end}
package.loaded['src.ui.game3.option_rows']=Rows
local menu={_st={pages={{title='OPTIONS'}}}}
require('src.core.GameVersion').set('emerald')
package.loaded['src.ui.game3.rse.option_menu']=menu
love.audio.newSource=function(path,kind)
  assert(kind=='stream');assert(path:match('audio/.*%.flac$'))
  local s={path=path}
  function s:play()self.playing=true end
  function s:pause()self.playing=false end
  function s:stop()self.playing=false;self.stopped=true end
  function s:isPlaying()return self.playing end
  function s:setVolume(v)self.volume=v end
  function s:setLooping(v)self.loop=v end
  sources[#sources+1]=s;return s
end
local fs={read=function(path)return files[path]end,
  write=function(path,data)files[path]=data;return true end,
  load=function(path)return files[path] and load(files[path],'@'..path)end,
  getInfo=function(path)
    if files[path] then return {type='file',size=#files[path]} end
    for key in pairs(files)do if key:sub(1,#path+1)==path..'/' then return {type='directory'} end end
  end,
  getDirectoryItems=function(path)
    local seen,out={},{}
    for key in pairs(files)do
      if key:sub(1,#path+1)==path..'/' then
        local item=key:sub(#path+2):match('^[^/]+')
        if not seen[item] then seen[item]=true;out[#out+1]=item end
      end
    end
    table.sort(out);return out
  end}
local loader=Loader.new({fs=fs,generation=3,version='emerald'})
assert(loader:load({pokemon={}}))
local m=loader.mods.toolbattlemusic
assert(m and m.state=='loaded' and loader.optionSchemas.toolbattlemusic,'Emerald mod did not load: '..table.concat(loader.errors,'; '))
assert(#loader.optionSchemas.toolbattlemusic==3)
local writes=0
local game={mods=loader,save={options={}},writeOptions=function()writes=writes+1 end,
  input={wasPressed=function()return false end},stack={push=function()end,pop=function()end}}
local out=Rows.build({game=game,options=game.save.options})
assert(#out==2 and out[2].label=='TOOL MUSIC','Missing Emerald OPTIONS row')
out[2].activate({game=game})
local page=menu._st.pages[2]
assert(page and #page.rows==4 and page.rows[4].label=='DOWNLOAD ASSETS')
assert(page.rows[1].value()=='Random')
page.rows[1].step({game=game},1)
assert(page.rows[1].value()=='46 N 2' and loader.modOptions.toolbattlemusic.regular=='46_n_2')
assert(game.save.options.modOptions.toolbattlemusic.regular=='46_n_2' and writes==1)
page.rows[1].step({game=game},-1);assert(page.rows[1].value()=='Random')
page.rows[1].step({game=game},-1);assert(page.rows[1].value()=='Original')
page.rows[1].step({game=game},-1)
local choices=loader.optionSchemas.toolbattlemusic[1].choices
assert(page.rows[1].value()==choices[#choices][1])
local Manager=require('src.mods.ManagerState')
local manager=setmetatable({game=game,status={available={m.manifest}},screen='list',tab=1,cursor=1,scroll=1},Manager)
local list=manager:modRows()
assert(#list==2 and list[1].header and not list[2].header)
manager:snapCursor();assert(manager.cursor==2,'Cursor skipped Tool mod')
assert(#manager:schemaFor(m.manifest)==3)
-- MODS sees settings even before runtime initialization / while disabled.
loader.optionSchemas.toolbattlemusic=nil
local manifest=m.manifest;manifest.path=m.path
assert(#manager:schemaFor(manifest)==3,'Static schema did not expose disabled mod options')
loader.modOptions.toolbattlemusic={regular='sober',gym='aenima',league='eulogy'}
for _,choice in ipairs(choices)do
  if choice[2]~='original' and choice[2]~='random' then
    loader.modOptions.toolbattlemusic.regular=choice[2]
    Audio.playSong(1)
    assert(sources[#sources].path:find('/'..choice[2]..'.flac',1,true),'Song choice failed: '..choice[2])
  end
end
loader.modOptions.toolbattlemusic.regular='sober'
Audio.playSong(1);assert(sources[#sources].path:match('/sober%.flac$'))
assert(sources[#sources].playing and Audio._bgmSource.volume==0)
local previous=sources[#sources];Audio.playSong(1);assert(sources[#sources]==previous)
Audio.playSong(3);assert(previous.stopped and sources[#sources].path:match('/aenima%.flac$'))
Audio.playSong(4);assert(sources[#sources].path:match('/eulogy%.flac$'))
Audio.playSong(5);assert(sources[#sources].path:match('/eulogy%.flac$'))
Trainers.getBattleMusicRole(87);Audio.playSong(3);assert(sources[#sources].path:match('/eulogy%.flac$'))
Trainers.getBattleMusicRole(84);Audio.playSong(3);assert(sources[#sources].path:match('/aenima%.flac$'))
Audio.playFanfare(9);assert(not sources[#sources].playing)
Audio._fanfareActive=false;Audio.update(.016);assert(sources[#sources].playing)
Audio.pauseBgm();assert(not sources[#sources].playing)
Audio.resumeBgm();assert(sources[#sources].playing)
Audio.applyEngineOptions({musicVol=0});assert(sources[#sources].volume==0)
Audio.setSuspended(true);assert(not sources[#sources].playing)
Audio.setSuspended(false);assert(sources[#sources].playing)
Audio.pumpBgm();assert(Audio._bgmSource.volume==0)
Audio.playSong(8);assert(sources[#sources].stopped and Audio.id==8)
Audio.playSong(7);assert(Audio.id==7 and Audio._bgmSource.volume==.6)
loader.modOptions.toolbattlemusic.regular='original'
local count=#sources;Audio.playSong(2);assert(#sources==count and Audio._bgmSource.volume==.6)
loader.modOptions.toolbattlemusic.regular='random'
Audio.playSong(1);local random=sources[#sources];Audio.playSong(1);assert(sources[#sources]==random)
Audio.stopAll();assert(random.stopped)
Audio.playSong(1);Runtime.hooks:removeOwner('toolbattlemusic');Audio.update(.016)
assert(sources[#sources].stopped and Audio._bgmSource.volume==.6)
assert(#Rows.build({game=game})==1,'Disabled mod settings row leaked')
print('PASS: real Emerald loader, selectable MODS entry, static settings schema, OPTIONS submenu, persisted choices, native audio bridge, victory/map restoration, volume, fanfares, suspension and disable cleanup')
