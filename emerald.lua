-- Emerald has its own M4A audio bus; GB music.select never reaches it.
return function(mod,choose,reset,active,assets)
  local Audio=require('src.core.game3.audio')
  local source, selected, cue, suspended
  local roleCategory
  -- FR/LG shares one song between gym leaders and Elite Four members.
  local Trainers=require('src.core.game3.scripting.trainers')
  local getRole=Trainers.getBattleMusicRole
  if getRole then Trainers.getBattleMusicRole=function(id)
    local role,fallback=getRole(id)
    if active() then
      local class=tonumber((Trainers.get(id) or {}).class)
      roleCategory=class==87 and 'league' or (class==90 and 'league' or (class==84 and 'gym' or 'regular'))
    end
    return role,fallback
  end end
  local function stop()
    if source then source:stop() end
    source,selected,cue=nil,nil,nil
    if Audio.applyGain then Audio.applyGain() end
  end
  local function category(id)
    local resolved=Audio.resolveSong(id)
    for name,value in pairs(Audio.songs()) do
      if value==resolved and name:match('^MUS_VS_') then
        if name=='MUS_VS_GYM_LEADER' then return roleCategory or 'gym' end
        if name=='MUS_VS_ELITE_FOUR' or name=='MUS_VS_CHAMPION' then return 'league' end
        return 'regular'
      end
    end
  end
  local function sync()
    if not source then return end
    if not active() then stop();reset();return end
    -- The engine still owns song identity, fades and victory/map restoration.
    -- Silence only its BGM source while our streamed soundtrack owns that bus.
    if Audio._bgmSource then Audio._bgmSource:setVolume(0) end
    local volume=(Audio._bgmVolume or 1)*math.min(Audio._duck or 1,Audio._seDuck or 1)
      *(Audio._helpActive and .5 or 1)
    local fade=Audio._fadeOut
    if fade then volume=volume*(1-math.min(1,(fade.t or 0)/math.max(fade.dur or .01,.01))) end
    source:setVolume(volume)
    if suspended or Audio._bgmPaused or Audio._fanfareActive then
      source:pause()
    elseif not source:isPlaying() then source:play() end
  end
  local play=Audio.playSong
  Audio.playSong=function(id,opts)
    if not active() then stop();return play(id,opts) end
    local group=category(id)
    -- Fanfare playback pauses the custom track instead of ending the battle cue.
    if (opts and opts.fanfare) or (Audio.songInfo(Audio.resolveSong(id)) or {}).kind=='fanfare' then
      local result=play(id,opts);sync();return result
    end
    if not group then roleCategory=nil;stop();reset();return play(id,opts) end
    local key=group..':'..tostring(Audio.resolveSong(id))
    local song=choose(group,key)
    local asset=song and assets:source(song)
    local result=play(id,opts)
    if not song or not asset then stop();return result end
    if not source or selected~=song or cue~=key or (opts and opts.restart) then
      stop()
      local ok,newSource=pcall(love.audio.newSource,asset,'stream')
      if not ok then mod.log:error('Tool Music audio failed: %s',tostring(newSource));return result end
      source,selected,cue=newSource,song,key
      source:setLooping(true)
    end
    sync()
    return result
  end
  for _,name in ipairs({'update','pumpBgm','applyEngineOptions','applyGain','pauseBgm','resumeBgm','playFanfare','setHelpActive'}) do
    local original=Audio[name]
    if original then Audio[name]=function(...)
      local result=original(...);sync();return result
    end end
  end
  for _,name in ipairs({'stopAll','endSession','shutdown'}) do
    local original=Audio[name]
    if original then Audio[name]=function(...) stop();reset();return original(...) end end
  end
  local suspend=Audio.setSuspended
  if suspend then Audio.setSuspended=function(flag) suspended=flag;local result=suspend(flag);sync();return result end end
end
