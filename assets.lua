-- Uses the same asynchronous verified ZIP/cache installer as 1025Dex.
return function(mod)
  local generation=tonumber(mod.generation) or 1
  local config=assert(load(assert(mod:read('compat/asset_config_gen'..generation..'.lua'))))()
  local expected=assert(load(assert(mod:read('compat/asset_catalog_gen'..generation..'.lua'))))()
  config.expectedFiles=expected
  config.legacyFiles=expected
  config.embedded=true
  local function originalPath(relative)
    return relative:sub(1,7)=='assets/' and relative:sub(8) or relative
  end
  local view=setmetatable({
    read=function(_,relative)return mod:read(originalPath(relative))end,
    info=function(_,relative)return mod:info(originalPath(relative))end,
    list=function(_,relative)return mod:list(originalPath(relative))end,
  },{__index=mod})
  local manager=assert(load(assert(mod:read('compat/asset_manager.lua')),'@ToolMusic/asset_manager.lua'))()(view,config)
  local assets={manager=manager,generation=generation,game=nil}
  function assets:relative(slug)
    return (generation==1 and 'audio/' or 'audio/gen'..generation..'/')..slug..'.flac'
  end
  function assets:available(slug)
    local relative=self:relative(slug)
    local info=mod:info(relative)
    return (info and (info.size or 0)>0) or manager:exists('assets/'..relative)
  end
  local cachedSlug,cachedData,cachedRevision
  local preparedSlug,preparedData
  function assets:source(slug)
    local relative=self:relative(slug)
    local info=mod:info(relative)
    if info and (info.size or 0)>0 then return mod.assets:path(relative) end
    if not manager:exists('assets/'..relative) then return nil end
    local revision=manager:sourceRevision()
    if cachedSlug==slug and cachedRevision==revision then return cachedData end
    local bytes=manager:read('assets/'..relative)
    if not bytes or not love or not love.filesystem or not love.filesystem.newFileData then return nil end
    -- FileData also works when portable cache paths are outside PhysFS.
    local ok,file=pcall(love.filesystem.newFileData,bytes,slug..'.flac')
    if not ok then return nil end
    cachedSlug,cachedData,cachedRevision=slug,file,revision
    return file
  end
  function assets:prepare(data,slug)
    local source=self:source(slug)
    local record=data and data.audio and data.audio.songs and data.audio.songs['Music_Tool_'..slug]
    if not source or not record then return false end
    if preparedSlug and preparedSlug~=slug then
      local old=preparedData.audio.songs['Music_Tool_'..preparedSlug]
      if old then old.file=mod.assets:path(self:relative(preparedSlug)) end
    end
    record.file=source
    preparedSlug,preparedData=slug,data
    return true
  end
  mod.events:on('game.ready',function(event)
    assets.game=event and event.game
    manager.game=assets.game
  end)
  return assets
end
