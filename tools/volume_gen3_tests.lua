local volume=100;local source;local nativeGain=.6;local A={_bgmVolume=.6,_bgmSource={setVolume=function(self,v)self.volume=v end}}
function A.resolveSong(id)return id end
function A.songs()return{MUS_VS_WILD=1,MUS_ROUTE101=2}end
function A.songInfo()return{}end
function A.playSong()return true end
function A.applyGain()A._bgmSource.volume=nativeGain end
function A.update()A.applyGain()end
function A.applyEngineOptions(o)A._bgmVolume=(o.musicVol or 7)/7 end
function A.pauseBgm()A._bgmPaused=true end
function A.resumeBgm()A._bgmPaused=false end
local mod={generation=3,options={get=function()return volume end},log={error=function()error('audio failed')end}}
local active=true;local choice='test'
local env=setmetatable({require=function(n)
 if n=='src.core.game3.audio'then return A end
 if n=='src.core.game3.scripting.trainers'then return{}end
 if n=='src.core.game3.battle'then return{isActive=function()return true end}end
end,love={audio={newSource=function()
 local s={};for _,k in ipairs({'stop','pause'})do s[k]=function(self)self.playing=false end end
 function s:play()self.playing=true end
 function s:isPlaying()return self.playing end
 function s:setVolume(v)self.volume=v end
 function s:setLooping()end
 source=s;return s
end}}},{__index=_G})
local function module(p)local f=assert(io.open(p));local s=f:read('*a');f:close();return assert(load(s,'@'..p,'t',env))()end
local control=module('volume.lua')(mod)
module('emerald.lua')(mod,function()return choice end,function()end,function()return active end,{source=function()return'test.flac'end},function()return'route'end,control.gain)
local function near(a,b)assert(math.abs(a-b)<1e-8,tostring(a)..' ~= '..tostring(b))end
A.playSong(1);local playing=source;near(source.volume,1);near(A._bgmSource.volume,0)
A.applyEngineOptions({musicVol=0});near(source.volume,1);assert(source==playing)
volume=35;control.refresh();near(source.volume,.35);assert(source==playing)
A._duck=.5;A._seDuck=.8;A._helpActive=true;A.update();near(source.volume,.0875)
A._fadeOut={t=.5,dur=1};A.update();near(source.volume,.04375)
volume=0;control.refresh();near(source.volume,0);near(A._bgmSource.volume,0)
volume=100;A._duck=1;A._seDuck=1;A._helpActive=false;A._fadeOut=nil
A._fanfareActive=true;A.update();assert(not source.playing)
A._fanfareActive=false;A.update();assert(source.playing)
A.pauseBgm();assert(not source.playing);A.resumeBgm();assert(source.playing)
A._audioMode='external_only';control.refresh();near(source.volume,0)
A._audioMode='both';choice=nil;A.playSong(2);near(A._bgmSource.volume,nativeGain)
print('PASS Gen 3 independent mute/live volume, native fallback, ducking, fade, fanfare, pause and audio mode')
-- OPTIONS writes only this mod's gain and reports the key for a live update.
local game={save={options={musicVol=0}},mods={},writeOptions=function(self)self.writes=(self.writes or 0)+1 end}
local pages={};local changed
mod.id='toolbattlemusic';mod.options.get=function(_,key)return game.save.options.modOptions and game.save.options.modOptions[mod.id]and game.save.options.modOptions[mod.id][key]or(key=='volume'and 100)end
mod.ui={};local schema=assert(loadfile('options.lua'))()
local baseRequire=env.require;env.require=function(n)
 if n=='src.core.GameVersion'then return{get=function()return'emerald'end}end
 if n=='src.ui.game3.rse.option_menu'then return{_st={pages=pages}}end
 return baseRequire(n)
end
local decorate=module('settings.lua')(mod,schema,function(key)changed=key end,{packs={},enabled=function()return true end})
local rows=decorate({},game);rows[1].activate(game)
assert(pages[1].rows[1].label=='TOOL VOLUME')
pages[1].rows[1].step(game,-1)
assert(game.save.options.modOptions[mod.id].volume==95 and game.save.options.musicVol==0 and game.writes==1 and changed=='volume')
assert(pages[1].rows[1].value()=='95%')
print('PASS volume option persistence and game-slider isolation')
