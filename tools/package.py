"""Package distributable mod files and verify ZIP contents against source hashes."""
import hashlib, json, zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
version=json.loads((root/'manifest.json').read_text())['version']
out=root.parent/f'ToolBattleMusic-v{version}.zip'
paths=sorted(p for p in root.rglob('*') if p.is_file() and p.suffix!='.ogg' and '.git' not in p.parts and '__pycache__' not in p.parts)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for path in paths: archive.write(path,'ToolBattleMusic/'+path.relative_to(root).as_posix())
with zipfile.ZipFile(out) as archive:
    assert archive.testzip() is None
    for path in paths:
        assert archive.read('ToolBattleMusic/'+path.relative_to(root).as_posix())==path.read_bytes()
    catalog=json.loads(archive.read('ToolBattleMusic/catalog.json'))
    assert len(catalog)==len({song['slug'] for song in catalog})
    assert len([p for p in archive.namelist() if p.endswith('.flac')])==len(catalog)*3
    assert len([p for p in archive.namelist() if p.endswith('.mid')])==len(catalog)
hasher=hashlib.sha256()
with out.open('rb') as packaged:
    for block in iter(lambda:packaged.read(1024*1024),b''):hasher.update(block)
digest=hasher.hexdigest()
out.with_suffix('.sha256').write_text(digest+'  '+out.name+'\n')
print(f'PASS: {len(paths)} files, {out.stat().st_size:,} bytes, SHA256 {digest}')
