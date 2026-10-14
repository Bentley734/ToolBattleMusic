return function(mod,choose,active,assets)
  local World=require('src.world.gen2.World')
  local BattleMusic=require('src.battle.gen2.BattleMusic')
  local Music=require('src.core.Music')
  local league={WILL=true,KOGA=true,BRUNO=true,KAREN=true,CHAMPION=true,RED=true}
  local original=World.playBattleMusic
  World.playBattleMusic=function(self,opts)
    if not active() then return original(self,opts) end
    local ctx=self:battleMusicContext(opts)
    local category=league[ctx.class] and 'league'
      or (BattleMusic.isGymLeader(ctx.class) and 'gym' or 'regular')
    local key=category..':'..tostring(ctx.class)..':'..tostring(ctx.member)
    local selected=choose(category,key)
    if not selected then return original(self,opts) end
    local id='Music_Tool_'..selected
    local data=self.game and self.game.data
    if not (data and data.audio and data.audio.songs and data.audio.songs[id]) then return original(self,opts) end
    if not assets:prepare(data,selected) then return original(self,opts) end
    Music.play(data,id,true,{reason='battle',selected=true})
    return id
  end
end
