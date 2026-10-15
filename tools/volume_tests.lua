-- Actual native GB Music state machine: independent gain and native fades.
love=require('tests.love_stub');love.audio={}
local sources={}
love.audio.newSource=function(path)
 local s={path=path,volume=0}
 function s:setVolume(v)self.volume=v end
 function s:getVolume()return self.volume end
 function s:play()self.playing=true end
 function s:stop()self.playing=false end
 function s:pause()self.playing=false end
 function s:isPlaying()return self.playing end
 function s:setLooping()end
 function s:setFilter()end
 sources[#sources+1]=s;return s
end
local Runtime=require('src.mods.Runtime');local Hooks=require('src.mods.Hooks');local Events=require('src.mods.Events')
local hooks=Hooks.new();Runtime.install(Events.new(),hooks,{})
local Music=require('src.core.Music');local volume=100;local enabled=true
local mod={generation=tonumber(arg[1]),options={get=function()return volume end},hooks=hooks}
local control=assert(loadfile('volume.lua'))()(mod);control.install(function()return enabled end)
local data={audio={generation=mod.generation,songs={Music_Tool_test={file='tool.flac',loopFile='loop.flac'},Original={file='native.flac'}}}}
local function near(a,b)assert(math.abs(a-b)<1e-8,tostring(a)..' ~= '..tostring(b))end
Music.setVolumeLevel(0);Music.play(data,'Music_Tool_test')
near(sources[1].volume,.7);near(sources[2].volume,.7)
Music.setVolumeLevel(2);near(sources[1].volume,.7)
volume=35;control.refresh();near(sources[1].volume,.245);near(sources[2].volume,.245)
Music.setVolumeLevel(0);Music.fadeOut(1)
for i=1,3 do Music.update(data)end
local level=Music.fadeLevel();assert(level and level<7);near(sources[1].volume,.245*level/7)
volume=70;control.refresh();near(sources[1].volume,.49*level/7)
volume=0;control.refresh();near(sources[1].volume,0)
for i=1,100 do Music.update(data)end
Music.play(data,'Original');near(sources[#sources].volume,0)
Music.setVolumeLevel(4);near(sources[#sources].volume,.4)
volume=50;Music.play(data,'Music_Tool_test');near(sources[#sources].volume,.35)
Music.fadeIn(1,0);Music.update(data);local n=Music.fadeLevel();near(sources[#sources].volume,.35*n/7)
Music.setAudioMode('external_only');near(sources[#sources].volume,0)
Music.setAudioMode('both');Music.stop();Music.play(data,'Music_Tool_test');near(sources[#sources].volume,.35)
enabled=false;Music.setVolumeLevel(7);near(sources[#sources].volume,.7)
enabled=true;Music.stop();Music.setVolumeLevel(0);volume=50
local portable={cached=true}
hooks:wrap('music.select',function(nextFn,id,ctx)
 if id=='Music_Tool_test'then data.audio.songs[id].file=portable end
 return nextFn(id,ctx)
end,100)
Music.play(data,'Music_Tool_test');local body=sources[#sources-1]
assert(body.path==portable);near(body.volume,.35)
Music.fadeOut(1);for i=1,3 do Music.update(data)end
local portableLevel=Music.fadeLevel();near(body.volume,.35*portableLevel/7)
print('PASS Gen '..mod.generation..' actual Music: separate gain, game mute, live update, intro/loop, fade-out/in, native fallback and audio mode')
