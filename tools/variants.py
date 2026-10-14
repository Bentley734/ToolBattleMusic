"""Build isolated, generation-specific private distribution folders and verified ZIPs."""
import hashlib,json,os,shutil,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
version=json.loads((root/'manifest.json').read_text())['version']
sys.path.insert(0,str(root.parent/'.tools/python'))
from lupa.lua53 import LuaRuntime
os.chdir(root.parent/'gen1recomp-0.3.54')
for generation,games in ((2,['gold','silver','crystal']),(3,['ruby','sapphire','emerald','firered','leafgreen'])):
    name=f'ToolBattleMusicGen{generation}'
    folder=root.parent/name
    folder.mkdir(exist_ok=True)
    for filename in ('main.lua','settings.lua','options.lua','README.md','RELEASE-NOTES.md'):
        shutil.copyfile(root/filename,folder/filename)
    adapter='gen2.lua' if generation==2 else 'emerald.lua'
    shutil.copyfile(root/adapter,folder/adapter)
    (folder/'tools').mkdir(exist_ok=True)
    shutil.copyfile(root/'tools/render.py',folder/'tools/render.py')
    manifest=json.loads((root/'manifest.json').read_text())
    manifest.update(id=f'toolbattlemusic_gen{generation}',name=f'Tool Battle Music Gen {generation}',games=games,
      conflicts=['toolbattlemusic'],description=f'Gen {generation} soundtrack variant: ten Tool MIDI arrangements, independent regular/gym/League settings and Random.')
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    report=root/f'audio-report-gen{generation}.json'
    shutil.copyfile(report,folder/report.name)
    for directory in ('midi',f'audio/gen{generation}'):
        (folder/directory).mkdir(parents=True,exist_ok=True)
        for file in (root/directory).iterdir():
            if file.is_file():shutil.copyfile(file,folder/directory/file.name)
    # Exercise the final variant ID/manifest through the real loader in every supported game.
    menu_test=(root/'tools/menu-tests.lua').read_text()
    for game in games:
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.globals().files=vm.table_from({'mods/'+name+'/'+p.name:p.read_text()
            for p in folder.iterdir() if p.suffix in ('.lua','.json')})
        vm.execute("package.path='./?.lua;'..package.path")
        if generation==3:
            test=menu_test.replace("'emerald'",repr(game))
            test=test.replace("package.loaded['src.ui.game3.rse.option_menu']=menu",
                "package.loaded['src.ui.game3.rse.option_menu']=menu;package.loaded['src.ui.game3.option_menu']=menu")
        else:
            prelude=menu_test.split('local loader=Loader.new')[0].replace("'emerald'",repr(game))
            test=prelude+(root/'tools/gen2-tests.lua').read_text().replace("version='crystal'",f"version='{game}'")
        vm.execute(test.replace('toolbattlemusic',manifest['id']))
        print(f'PASS: final {name} variant loads and exposes settings in {game}')
    paths=sorted(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    archive=root.parent/f'ToolBattleMusic-Gen{generation}-v{version}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zipped:
        for path in paths:zipped.write(path,name+'/'+path.relative_to(folder).as_posix())
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.testzip() is None
        for path in paths:assert zipped.read(name+'/'+path.relative_to(folder).as_posix())==path.read_bytes()
        m=json.loads(zipped.read(name+'/manifest.json'))
        assert m['games']==games and m['options_schema']=='options.lua'
        assert len([p for p in zipped.namelist() if p.endswith('.flac')])==10
    archive.with_suffix('.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
    print(f'PASS: {archive.name}, {len(paths)} files, {archive.stat().st_size:,} bytes')
