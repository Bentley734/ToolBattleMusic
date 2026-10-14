from pathlib import Path
import json,hashlib,zipfile
root=Path(__file__).resolve().parents[1]
version=json.loads((root/'manifest.json').read_text())['version']
songs=json.loads((root/'expansion-catalog.json').read_text(encoding='utf8'))
labels={'tool_extra':'TOOL EXTRAS','pink_floyd':'PINK FLOYD','puscifer':'PUSCIFER','a_perfect_circle':'A PERFECT CIRCLE','rage':'RAGE AGAINST MACHINE','rush':'RUSH'}
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def checksum(p):p.with_suffix('.sha256').write_text(digest(p)+'  '+p.name+'\n')
outputs=[]
for band in labels:
 chosen=[s for s in songs if s['artist']==band]
 for g in (1,2,3):
  directory='audio' if g==1 else f'audio/gen{g}'
  files=[root/directory/(s['slug']+'.flac') for s in chosen]
  pinned={'assets/'+p.relative_to(root).as_posix():{'size':p.stat().st_size,'sha256':digest(p)} for p in files}
  name=f'ToolBattleMusic-{band}-gen{g}-v1.0.0.zip';pack=root.parent/name
  with zipfile.ZipFile(pack,'w',zipfile.ZIP_STORED,allowZip64=False) as z:
   z.writestr('asset-pack.json',json.dumps({'id':f'toolmusic_{band}_gen{g}','version':'1.0.0','files':pinned},separators=(',',':')))
   for p in files:z.write(p,'assets/'+p.relative_to(root).as_posix())
  (root/'compat'/f'asset_catalog_{band}_gen{g}.lua').write_text('return {\n'+''.join(' ['+json.dumps(k)+']={size='+str(v['size'])+',sha256="'+v['sha256']+'"},\n' for k,v in pinned.items())+'}\n')
  (root/'compat'/f'asset_config_{band}_gen{g}.lua').write_text(f'''return {{
 packId="toolmusic_{band}_gen{g}",version="1.0.0",repo="Bentley734/ToolBattleMusic",
 cacheNamespace="tool_audio_{band}_gen{g}",screenId="toolbattlemusic:assets:{band}",label="{labels[band]}",
 assetName="{name}",assetSize={pack.stat().st_size},
 assetURL="https://github.com/Bentley734/ToolBattleMusic/releases/download/v{version}/{name}",
 indexOnly=true,verifyFiles=true,allowedPrefix="assets/{directory}/",
 legacyRoots={{"assets/{directory}"}},legacyExpectedFiles={len(chosen)},
}}
''')
  checksum(pack);outputs.extend([pack,pack.with_suffix('.sha256')]);print('Built',name,pack.stat().st_size,flush=True)
core=root.parent/f'ToolBattleMusic-v{version}.zip'
with zipfile.ZipFile(core,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(root.rglob('*')):
  if p.is_file() and p.suffix not in ('.mid','.ogg','.flac') and not any(v in ('.git','__pycache__') for v in p.parts):z.write(p,'ToolBattleMusic/'+p.relative_to(root).as_posix())
checksum(core);outputs=[core,core.with_suffix('.sha256')]+outputs
(root.parent/'.work/toolmusic-expansion/publication-assets.json').write_text(json.dumps([{'name':p.name,'path':str(p),'size':p.stat().st_size,'sha256':digest(p)} for p in outputs],indent=2))
print('Built core and',len(outputs),'release assets; tests skipped',flush=True)
