"""Publishable small core plus one verified audio pack per generation."""
import argparse,hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
version=json.loads((root/'manifest.json').read_text())['version']
asset_version='1.0.1'
parser=argparse.ArgumentParser();parser.add_argument('--core-only',action='store_true');args=parser.parse_args()
def digest(path):
    hash=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):hash.update(block)
    return hash.hexdigest()
def checksum(path):path.with_suffix('.sha256').write_text(digest(path)+'  '+path.name+'\n')
outputs=[root.parent/f'ToolBattleMusic-assets-gen{g}-v{asset_version}.zip' for g in (1,2,3)] if args.core_only else []
for generation in (() if args.core_only else (1,2,3)):
    folder=root/'audio' if generation==1 else root/'audio'/f'gen{generation}'
    files=sorted(folder.glob('*.flac'))
    assert len(files)==41
    catalog={'assets/'+p.relative_to(root).as_posix():{'size':p.stat().st_size,'sha256':digest(p)} for p in files}
    name=f'ToolBattleMusic-assets-gen{generation}-v{asset_version}.zip'
    pack=root.parent/name
    with zipfile.ZipFile(pack,'w',zipfile.ZIP_STORED,allowZip64=False) as archive:
        archive.writestr('asset-pack.json',json.dumps({'id':f'toolmusic_gen{generation}',
          'version':asset_version,'files':catalog},separators=(',',':')))
        for path in files:archive.write(path,'assets/'+path.relative_to(root).as_posix())
    (root/'compat'/f'asset_catalog_gen{generation}.lua').write_text('return {\n'+''.join(
        f' [{json.dumps(k)}]={{size={v["size"]},sha256="{v["sha256"]}"}},\n' for k,v in catalog.items())+'}\n')
    relative=folder.relative_to(root).as_posix()
    (root/'compat'/f'asset_config_gen{generation}.lua').write_text(f'''return {{
 packId="toolmusic_gen{generation}",version="{asset_version}",repo="Bentley734/ToolBattleMusic",
 cacheNamespace="tool_audio_gen{generation}",screenId="toolbattlemusic:assets",
 assetName="{name}",assetSize={pack.stat().st_size},
 assetURL="https://github.com/Bentley734/ToolBattleMusic/releases/download/v{version}/{name}",
 indexOnly=true,verifyFiles=true,allowedPrefix="assets/{relative}/",
 legacyRoots={{"assets/{relative}"}},legacyExpectedFiles=41,
}}
''')
    checksum(pack);outputs.append(pack)
    print(f'PASS: {name}: {pack.stat().st_size:,} bytes; 41 pinned SHA256 files',flush=True)
core=root.parent/f'ToolBattleMusic-v{version}.zip'
paths=[p for p in sorted(root.rglob('*')) if p.is_file() and p.suffix not in ('.flac','.ogg','.mid')
  and not any(part in ('.git','__pycache__') for part in p.parts)]
with zipfile.ZipFile(core,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in paths:archive.write(path,'ToolBattleMusic/'+path.relative_to(root).as_posix())
checksum(core);outputs.insert(0,core)
print(f'PASS: core {core.name}: {core.stat().st_size:,} bytes',flush=True)
(root.parent/'ToolBattleMusic-publication-assets.json').write_text(json.dumps([
  {'name':p.name,'path':str(p),'size':p.stat().st_size,'sha256':digest(p)} for p in outputs],indent=2)+'\n')
