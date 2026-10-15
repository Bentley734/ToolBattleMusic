local factory=assert(loadfile('settings.lua'))()
local schema=assert(loadfile('options.lua'))()
for _,gen in ipairs({1,2,3})do
 local data={volume=95,regular='random'};local pages={};local pushed;local registered;local opens=0;local changes=0
 local game={save={options={modOptions={toolbattlemusic=data}}},mods={},writeOptions=function()end,stack={push=function(_,m)pushed=m end},input={wasPressed=function()return false end}}
 local mod={id='toolbattlemusic',generation=gen,options={get=function(_,k)return data[k]end},ui={ListMenu={new=function(g,t,items,opts)return{title=t,items=items,opts=opts,rows=7,update=function()end,close=function(self)self.closed=true end}end}},content={screens={register=function(_,id,v)registered=v end}}}
 mod.ui.push=function()pushed=registered.new(game)end
 package.loaded['src.core.GameVersion']={get=function()return'emerald'end}
 package.loaded['src.ui.game3.rse.option_menu']={_st={pages=pages}}
 local assets={packs={{id='a',downloadLabel='GET A',manager={statusLabel=function()return'READY'end,open=function()opens=opens+1 end}},{id='b',downloadLabel='GET B',manager={statusLabel=function()return'READY'end,open=function()opens=opens+1 end}}},enabled=function()return true end}
 local out=factory(mod,schema,function()changes=changes+1 end,assets)({},game);out[1].activate(game)
 if gen==3 then
  local rows=pages[1].rows;assert(#rows==#schema+1 and rows[#rows].label=='DOWNLOAD ASSETS')
  rows[1].activate(game);assert(#pages==2 and pages[2].index==20 and data.volume==95)
  pages[2].rows[4].activate();assert(data.volume==15 and #pages==1 and changes==1)
  rows[1].step(game,-1);assert(data.volume==10)
  rows[#rows].activate(game);assert(#pages[2].rows==2);pages[2].rows[1].activate(game);assert(opens==1)
 else
  local main=pushed;assert(#main.items==#schema+2 and main.items[#main.items-1].downloads)
  main.opts.onChoose(main.items[1],main);local choices=pushed;assert(choices.index==20 and choices.scroll==13 and data.volume==95)
  choices.opts.onChoose(choices.items[4],choices);assert(data.volume==15 and choices.closed and changes==1)
  game.input.wasPressed=function(_,key)return key=='right'end;main.index=1;main:update(0);assert(data.volume==20)
  main.opts.onChoose(main.items[#main.items-1],main);assert(#pushed.items==3 and pushed.items[1].right=='READY');pushed.opts.onChoose(pushed.items[1],pushed);assert(opens==1)
 end
 print('PASS menu grouping, picker selection/persistence and cycling generation '..gen)
end
