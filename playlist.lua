-- One saved shuffle pool shared by every battle category and field music.
return function(mod,songs,assets)
 local areaSongs=assert(load(assert(mod:read('area_songs.lua'))))()
 local mixedAreas=assert(load(assert(mod:read('mixed_area_songs.lua'))))()
 local version=require('src.core.GameVersion').get()
 local state=mod.save:get('playlist_v1') or {}
 local Json=require('src.link.Json')
 local saved=mod.cache:read('playlist-v1.json')
 if saved then local ok,value=pcall(Json.decode,saved);if ok and type(value)=='table' then state=value end end
 if type(state)~='table' then state={}end
 if type(state.played)~='table' then
  state.played={}
  if type(state.remaining)=='table' then
   local remaining={};for _,slug in ipairs(state.remaining)do remaining[slug]=true end
   for _,song in ipairs(songs)do if not song[3] and not remaining[song[2]]then state.played[song[2]]=true end end
  end
 end
 local cached={};local mapId
 local function persist()
  mod.save:set('playlist_v1',state)
  mod.cache:write('playlist-v1.json',Json.encode(state))
 end
 local function pool()
  local eligible={}
  for _,song in ipairs(songs)do if assets:available(song[2])then eligible[#eligible+1]=song[2]end end
  state.remaining={}
  for _,slug in ipairs(eligible)do if not state.played[slug]then state.remaining[#state.remaining+1]=slug end end
  if #state.remaining==0 and #eligible>0 then state.played={};state.remaining=eligible end
  for i=#state.remaining,2,-1 do local j=math.random(i);state.remaining[i],state.remaining[j]=state.remaining[j],state.remaining[i]end
  if #state.remaining>1 and state.remaining[#state.remaining]==state.last then
   state.remaining[1],state.remaining[#state.remaining]=state.remaining[#state.remaining],state.remaining[1]
  end
 end
 local function consume(slug)
  pool()
  for i=#state.remaining,1,-1 do if state.remaining[i]==slug then table.remove(state.remaining,i);break end end
  state.played[slug]=true;state.last=slug;persist()
 end
 local function currentMap()
  if mod.generation==3 then return require('src.core.game3.map').current or mapId end
  local g=assets.game;return mapId or (g and g.world and g.world.map and g.world.map.id)
 end
 local function area(id)
  local choices=mixedAreas[version] or {}
  local function result(tool,key)
   if mod.options:get('artists')=='mixed' then
    for _,slug in ipairs(choices[key] or {})do if assets:available(slug)then return slug end end
   end
   return tool
  end
  if mod.generation==3 and id then
   local slot=require('src.import.gba.map_catalog').slotKeyFor(id)
   local fixed=slot and (areaSongs[version] or {})[slot]
   if fixed then return result(fixed,slot)end
  end
  local key=tostring(id or ''):upper():gsub('^EM_',''):gsub('^FR_',''):gsub('^SEVII_',''):gsub('^RU_',''):gsub('^SA_',''):gsub('[^A-Z0-9]','')
  return result((areaSongs[version] or {})[key] or 'reflection',key)
 end
 local function choose(category,key,areaId)
  if cached[key] then return cached[key]end
  local value=mod.options:get(category);local slug
  if category~='locations' and value~='original' and value~='random' and not assets:enabled(value)then value='random'end
  if value=='random' then
   pool()
   while #state.remaining>0 do
    local candidate=table.remove(state.remaining)
    if assets:available(candidate)then slug=candidate;break end
   end
   if slug then state.played[slug]=true;state.last=slug;persist()end
  elseif category=='locations' and value=='curated' then slug=area(areaId or currentMap())
  else
   for _,song in ipairs(songs)do if song[2]==value then slug=value;break end end
  end
  if slug and assets:available(slug) then
   if value~='random' then consume(slug)end
   cached[key]=slug;return slug
  end
 end
 local function reset()cached={}end
 mod.events:on('map.entered',function(event)mapId=event.mapId;reset()end)
 return choose,reset,currentMap
end
