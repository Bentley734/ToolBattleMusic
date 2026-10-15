-- Replacement soundtrack gain is independent of the native music slider.
return function(mod)
 local M={}
 function M.gain()
  return math.max(0,math.min(100,tonumber(mod.options:get('volume'))or 100))/100
 end
 function M.refresh()
  if mod.generation==3 then
   local A=require('src.core.game3.audio');if A.applyGain then A.applyGain()end
  else
   local Music=require('src.core.Music');if Music.setVolumeLevel then Music.setVolumeLevel()end
  end
 end
 function M.install(active)
  if mod.generation==3 then return end
  local Music=require('src.core.Music')
  local tracked=setmetatable({},{__mode='k'})
  local inPlay,custom=false,false
  local function isTool(id)return type(id)=='string'and id:sub(1,11)=='Music_Tool_'end
  local function gain()
   if Music.audioMode and Music.audioMode()=='external_only'then return 0 end
   local level=Music.fadeLevel and Music.fadeLevel()
   return .7*M.gain()*(level and math.max(0,math.min(7,level))/7 or 1)
  end
  mod.hooks:wrap('music.select',function(nextFn,id,ctx)
   local selected=nextFn(id,ctx);if inPlay then custom=isTool(selected)end
   return selected
  end,-10000)
  mod.hooks:wrap('music.volume',function(nextFn,v,ctx)
   if active()and(inPlay and custom or not inPlay and ctx and isTool(ctx.song))then v=gain()end
   return nextFn(v,ctx)
  end)
  local play=Music.play
  Music.play=function(data,...)
   if not active()then return play(data,...)end
   local original=love.audio.newSource
   local previousPlay,previousCustom=inPlay,custom;inPlay,custom=true,false
   love.audio.newSource=function(file,...)
    local source=original(file,...)
    local song
    -- Asset preparation can replace a filename with cached FileData during
    -- music.select, so resolve the current definition after that callback.
    for id,def in pairs(data and data.audio and data.audio.songs or{})do
     if isTool(id)and(file==def.file or file==def.loopFile)then song=id;break end
    end
    custom=song~=nil
    if song then tracked[source]=song end
    return source
   end
   local out={pcall(play,data,...)}
   love.audio.newSource=original;inPlay,custom=previousPlay,previousCustom
   if not out[1]then error(out[2],0)end
   return (unpack or table.unpack)(out,2)
  end
  -- Native GB fades write source gains directly, bypassing music.volume.
  -- Retain their timing/level while replacing only the user-volume factor.
  local update=Music.update
  Music.update=function(...)
   local out={update(...)}
   local level=Music.fadeLevel and Music.fadeLevel()
   if active()and level and isTool(Music.current())then
    for source,id in pairs(tracked)do if id==Music.current()then source:setVolume(gain())end end
   end
   return (unpack or table.unpack)(out)
  end
 end
 return M
end
