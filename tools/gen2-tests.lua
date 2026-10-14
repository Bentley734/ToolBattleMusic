-- Run after menu-tests.lua in a fresh VM: exercises the real Gen 2 loader and music policy.
local World={playBattleMusic=function()return 'Original' end}
function World:battleMusicContext(opts)return opts end
package.loaded['src.world.gen2.World']=World
local heard
package.loaded['src.core.Music']={play=function(_,id,loop,ctx)
  assert(loop and ctx.selected and ctx.reason=='battle');heard=id
end}
local Loader=require('src.mods.Loader')
local fs={read=function(path)return files[path]end,
  write=function(path,data)files[path]=data;return true end,
  load=function(path)return files[path] and load(files[path],'@'..path)end,
  getInfo=function(path)
    if files[path] then return {type='file',size=#files[path]}end
    for key in pairs(files)do if key:sub(1,#path+1)==path..'/'then return {type='directory'}end end
  end,
  getDirectoryItems=function(path)
    local seen,out={},{}
    for key in pairs(files)do if key:sub(1,#path+1)==path..'/'then
      local item=key:sub(#path+2):match('^[^/]+')
      if not seen[item]then seen[item]=true;out[#out+1]=item end
    end end
    table.sort(out);return out
  end}
local loader=Loader.new({fs=fs,generation=2,version='crystal'})
local data={pokemon={},audio={songs={}}}
assert(loader:load(data))
assert(loader.mods.toolbattlemusic.state=='loaded',table.concat(loader.errors,'; '))
local options={regular='sober',gym='aenima',league='eulogy'}
loader.modOptions.toolbattlemusic=options
local world=setmetatable({game={data=data}},{__index=World})
for _,class in ipairs({'WILL','KOGA','BRUNO','KAREN','CHAMPION','RED'})do
  assert(world:playBattleMusic({class=class,member=class..'1'})=='Music_Tool_eulogy')
end
for _,class in ipairs({'FALKNER','WHITNEY','BUGSY','MORTY','PRYCE','JASMINE','CHUCK','CLAIR',
 'BROCK','MISTY','LT_SURGE','ERIKA','JANINE','SABRINA','BLAINE','BLUE'})do
 assert(world:playBattleMusic({class=class,member=class..'1'})=='Music_Tool_aenima')
end
assert(world:playBattleMusic({class='GRUNTM'})=='Music_Tool_sober')
assert(world:playBattleMusic({})=='Music_Tool_sober')
assert(data.audio.songs.Music_Tool_sober.file:match('audio/gen2/sober%.flac$'))
options.gym='original';assert(world:playBattleMusic({class='BLUE'})=='Original')
options.regular='random'
local seen,previous={},nil
for i=1,2000 do
 loader.events:emit('battle.ended',{})
 local id=world:playBattleMusic({});assert(id~=previous)
 assert(world:playBattleMusic({})==id);seen[id]=true;previous=id
end
local count=0;for _ in pairs(seen)do count=count+1 end
assert(count==#loader.optionSchemas.toolbattlemusic[1].choices-2)
local Manager=require('src.mods.ManagerState')
local manifest=loader:status().available[1]
local manager=setmetatable({game={mods=loader,save={options={}}},status={available={manifest}},
  screen='list',tab=1,cursor=1,scroll=1},Manager)
manager:snapCursor();assert(manager.cursor==2)
assert(#manager:schemaFor(manifest)==3)
local rows=loader.hooks:call('ui.options.rows',function(_,r)return r end,{}, {})
assert(rows[1] and rows[1].label=='TOOL MUSIC')
print('PASS: real Gen 2 loader, all 16 gym leaders, Elite Four/Champion/Red, regular/wild, Original, stable random, GB audio path and selectable MODS/settings entry')
