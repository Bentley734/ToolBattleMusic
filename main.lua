-- Tool MIDI battle soundtrack. Random choices remain stable through repeated cues.
local league = { OPP_LORELEI=true, OPP_BRUNO=true, OPP_AGATHA=true,
  OPP_LANCE=true, OPP_RIVAL3=true }
return function(mod)
  local assets=assert(load(assert(mod:read('assets.lua')),'@ToolMusic/assets.lua'))()(mod)
  local songs=assert(load(assert(mod:read('songs.lua')),'@ToolBattleMusic/songs.lua'))()
  local schema=assert(load(assert(mod:read('options.lua')),'@ToolBattleMusic/options.lua'))()
  local ids = {}
  for _,song in ipairs(songs) do
    local id = 'Music_Tool_' .. song[2]
    ids[song[2]] = id
    if mod.generation~=3 then
      mod.content.music:register(id, {file=mod.assets:path((mod.generation==2 and 'audio/gen2/' or 'audio/')..song[2]..'.flac')})
    end
  end
  mod.options:define(schema)
  local choose,reset,currentMap=assert(load(assert(mod:read('playlist.lua'))))()(mod,songs,assets)
  local function changed()
    reset()
    if mod.generation==3 then
      local Audio=require('src.core.game3.audio')
      local id=Audio.currentMapMusic()
      if id and id~=0 then Audio.playSong(id)end
    elseif assets.game and currentMap() then
      require('src.core.Music').restoreMap(assets.game.data,'map')
    end
  end
  local decorate=assert(load(assert(mod:read('settings.lua')),'@ToolBattleMusic/settings.lua'))()(mod,schema,changed,assets)
  local marker=function(next,game,rows) return decorate(next(game,rows),game) end
  mod.hooks:wrap('ui.options.rows',marker)
  local function active()
    local Runtime=require('src.mods.Runtime')
    for _,entry in ipairs(Runtime.hooks and Runtime.hooks.chains['ui.options.rows'] or {}) do
      if entry.owner==mod.id and entry.callback==marker then return true end
    end
    return false
  end
  mod.events:on('battle.ended',reset)
  mod.events:on('mod.options_changed',function(ctx)if ctx.mod==mod.id then reset()end end)
  if mod.generation==3 then
    local Rows=require('src.ui.game3.option_rows')
    local build=Rows.build
    Rows.build=function(ctx,...)
      local out=build(ctx,...)
      return active() and decorate(out,ctx and ctx.game) or out
    end
    assert(load(assert(mod:read('emerald.lua')),'@ToolBattleMusic/emerald.lua'))()(mod,choose,reset,active,assets,currentMap)
    return
  end
  mod.hooks:wrap('music.select',function(next,chosen,ctx)
    if not ctx or (ctx.reason~='battle' and ctx.reason~='map' and ctx.reason~='bike' and ctx.reason~='surf') then
      return next(chosen,ctx)
    end
    local category = ctx.reason~='battle' and 'locations' or league[ctx.trainerId] and 'league'
      or (ctx.kind == 'gym' and 'gym' or 'regular')
    local key=category=='locations' and ('locations:'..tostring(ctx.mapId or currentMap()))
      or category..':'..tostring(ctx.trainerId)..':'..tostring(chosen)
    local selected=choose(category,key,ctx.mapId or currentMap())
    if selected and not assets:available(selected) then selected=nil end
    if selected and assets.game and not assets:prepare(assets.game.data,selected) then selected=nil end
    return next(selected and ids[selected] or chosen,ctx)
  end)
  if mod.generation==2 then
    assert(load(assert(mod:read('gen2.lua')),'@ToolBattleMusic/gen2.lua'))()(mod,choose,active,assets)
  end
end
