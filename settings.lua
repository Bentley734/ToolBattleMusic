return function(mod, schema, changed, assets)
  local SCREEN=mod.id..':settings'
  local function value(row)
    local v=mod.options:get(row.key)
    for _,choice in ipairs(row.choices) do if choice[2]==v then return choice[1] end end
    return 'Original'
  end
  local function step(game,row,dir)
    local v=mod.options:get(row.key)
    local index=1
    for i,choice in ipairs(row.choices) do if choice[2]==v then index=i end end
    local selected=row.choices[((index-1+(dir<0 and -1 or 1)) % #row.choices)+1][2]
    local options=(game.save and game.save.options) or game.options
    assert(options,'Tool Music: missing options storage')
    options.modOptions=options.modOptions or {}
    options.modOptions[mod.id]=options.modOptions[mod.id] or {}
    options.modOptions[mod.id][row.key]=selected
    if game.mods then
      game.mods.modOptions=game.mods.modOptions or {}
      game.mods.modOptions[mod.id]=options.modOptions[mod.id]
    end
    if game.writeOptions then game:writeOptions() end
    changed()
    return false
  end
  local function rows(game)
    local out={}
    for _,row in ipairs(schema) do
      local setting=row
      out[#out+1]={id=SCREEN..':'..setting.key,label=setting.label,
        value=function() return value(setting) end,
        step=function(ctx,dir) return step((ctx and ctx.game) or ctx or game,setting,dir) end}
    end
    out[#out+1]={id=SCREEN..':assets',label='DOWNLOAD ASSETS',
      value=function()return assets:statusLabel()end,
      activate=function(ctx)assets.open((ctx and ctx.game) or ctx or game)end}
    return out
  end
  if mod.generation~=3 then
    mod.content.screens:register(SCREEN,{new=function(game)
      local menu
      local function refresh()
        local items={}
        for _,row in ipairs(schema) do items[#items+1]={label=row.label,right=value(row),setting=row} end
        items[#items+1]={label='DOWNLOAD ASSETS',right=assets:statusLabel(),assets=true}
        items[#items+1]={label='BACK',back=true};menu.items=items
      end
      menu=mod.ui.ListMenu.new(game,'TOOL MUSIC',{}, {wrap=true,keyRepeat=true,
        onChoose=function(item,m)
          if item.back then m:close()
          elseif item.assets then assets.open(game)
          else step(game,item.setting,1);refresh() end
        end})
      refresh()
      local update=menu.update
      menu.update=function(self,dt)
        local item=self.items[self.index]
        if item and item.setting then
          if game.input:wasPressed('left') then step(game,item.setting,-1);refresh();return end
          if game.input:wasPressed('right') then step(game,item.setting,1);refresh();return end
        end
        return update(self,dt)
      end
      return menu
    end})
  end
  return function(out,game)
    if type(out)~='table' then return out end
    for _,row in ipairs(out) do if row.id==SCREEN then return out end end
    out[#out+1]={id=SCREEN,label='TOOL MUSIC',value=function() return 'OPEN' end,
      text=function() return 'OPEN' end,activate=function(ctx)
        local g=(ctx and ctx.game) or ctx or game
        if mod.generation==3 then
          local version=require('src.core.GameVersion').get()
          local menu=require((version=='firered' or version=='leafgreen')
            and 'src.ui.game3.option_menu' or 'src.ui.game3.rse.option_menu')
          local pages=menu._pages or (menu._st and menu._st.pages)
          assert(type(pages)=='table','Tool Music: options menu is not open')
          pages[#pages+1]={title='TOOL MUSIC',rows=rows(g),index=1,scroll=0}
          menu.cursor=1
        else mod.ui.push(g,SCREEN) end
      end}
    return out
  end
end
