"""Exercise the production asset installer, UI and portable-safe audio resolver."""
import hashlib,io,json,os,sys,time,zipfile,zlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];workspace=root.parent
sys.path.insert(0,str(workspace/'.tools/python'))
from lupa.lua53 import LuaRuntime
os.chdir(workspace/'gen1recomp-0.3.54')
ui=(root/'tools/asset_manager_ui_fixture.lua').read_text()
vm=LuaRuntime(unpack_returned_tuples=True)
vm.globals().manager_source=(root/'compat/asset_manager.lua').read_text()
vm.globals().arg=vm.table_from([str(root),'',str(workspace/'gen1recomp-0.3.54')])
vm.execute(ui)
def fixture(case):
    name='assets/audio/gen3/sober.flac';data=b'fLaC verified fixture audio'
    meta={'id':'toolmusic_gen3','version':'1.0.0','files':{name:{'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}}}
    if case=='wrong_id':meta['id']='other_pack'
    if case=='wrong_version':meta['version']='9.9.9'
    if case=='unsafe':name='assets/../../escape.flac'
    catalog={name:{'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}}
    if case=='corrupt':data=data[:-1]+b'X'
    archive=io.BytesIO()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as zipped:
        zipped.writestr('asset-pack.json',json.dumps(meta))
        zipped.writestr(name,data)
    return archive.getvalue(),catalog
def install(blob,catalog,disk_full=False):
    vm=LuaRuntime(unpack_returned_tuples=True,encoding='latin-1');cache={};temporary={}
    def write(k,v):
        if disk_full and '/files/' in k:return None,'disk full'
        cache[k]=v;return True
    def newfile(name):
        f=io.BytesIO(blob)
        return vm.table_from({'open':lambda *_:True,'getSize':lambda *_:len(blob),
            'seek':lambda _,n:f.seek(int(n))>=0,'read':lambda _,n:f.read(int(n)).decode('latin-1'),'close':lambda *_:f.close()})
    def download(url,name,opts):temporary[name]=True;return vm.table_from({})
    g=vm.globals();g.source=(root/'compat/asset_manager.lua').read_bytes().decode('latin-1')
    g.json_source=(workspace/'gen1recomp-0.3.54/src/link/Json.lua').read_text()
    g.catalog=vm.table_from({k:vm.table_from(v) for k,v in catalog.items()})
    g.cacheRead=lambda k:cache.get(k);g.cacheWrite=write
    g.cacheInfo=lambda k:vm.table_from({'size':len(cache[k]),'type':'file'}) if k in cache else None
    g.cacheDelete=lambda k:cache.pop(k,None) is not None
    g.newFile=newfile;g.download=download
    g.fsInfo=lambda n:vm.table_from({'size':len(blob)}) if n in temporary else None
    g.fsRemove=lambda n:temporary.pop(n,None) is not None
    g.hashBytes=lambda _,s:hashlib.sha256(s.encode('latin-1')).hexdigest()
    g.inflate=lambda _,__,s:zlib.decompress(s.encode('latin-1'),-15).decode('latin-1')
    g.clock=time.monotonic
    g.blob_size=len(blob)
    vm.execute('''
local Json=assert(load(json_source))()
local fs={newFile=function(n)return newFile(n)end,getInfo=function(n)return fsInfo(n)end,remove=function(n)return fsRemove(n)end}
local modules={['src.link.Json']=Json,['src.core.SaveData']={persistenceFs=function()return fs end},
 ['src.net.Fetch']={download=function(u,n,o)return download(u,n,o)end,poll=function()return {status='ok'}end,release=function()end,cancel=function()end}}
local mod={generation=3,path='fixture',content={screens={register=function()end}},info=function()return nil end,list=function()return {}end,
 cache={read=function(_,k)return cacheRead(k)end,write=function(_,k,v)return cacheWrite(k,v)end,
 info=function(_,k)return cacheInfo(k)end,delete=function(_,k)return cacheDelete(k)end}}
local config={packId='toolmusic_gen3',version='1.0.0',cacheNamespace='tool_audio_gen3',embedded=true,
 assetURL='https://github.com/Bentley734/ToolBattleMusic/releases/download/v1.4.0/fixture.zip',assetSize=blob_size,
 indexOnly=true,verifyFiles=true,allowedPrefix='assets/audio/gen3/',legacyExpectedFiles=1,expectedFiles=catalog}
local env=setmetatable({require=function(n)return assert(modules[n],n)end,
 love={timer={getTime=function()return clock()end},data={hash=function(a,s)return hashBytes(a,s)end,
 encode=function(_,__,s)return s end,decompress=function(a,b,s)return inflate(a,b,s)end}}},{__index=_G})
manager=assert(load(source,'Tool Music asset installer','t',env))()(mod,config)
manager:start()
''')
    for _ in range(1000):
        vm.execute('manager:update()')
        if vm.globals().manager.state in ('done','error'):break
    return vm,cache,temporary
for case in ('good','wrong_id','wrong_version','unsafe','corrupt','disk_full'):
    blob,catalog=fixture(case)
    vm,cache,temp=install(blob,catalog,case=='disk_full')
    manager=vm.globals().manager
    if case=='good':
        assert manager.state=='done',manager.error
        assert cache['tool_audio_gen3/complete.txt']=='zip:1.0.0' and not temp
        assert manager.exists(manager,'assets/audio/gen3/sober.flac')
    else:
        assert manager.state=='error',(case,manager.state)
        assert 'tool_audio_gen3/complete.txt' not in cache
    print('PASS: production installer',case,flush=True)
# Resolver: a downloaded FileData stream works without any mounted cache path.
vm=LuaRuntime(unpack_returned_tuples=True)
vm.globals().asset_source=(root/'assets.lua').read_text()
vm.execute('''
local current={};local revision=1
local manager={exists=function(_,p)return current[p]~=nil end,read=function(_,p)return current[p]end,
 sourceRevision=function()return revision end}
local sources={['compat/asset_config_gen3.lua']='return {}',['compat/asset_catalog_gen3.lua']='return {}',
 ['compat/asset_manager.lua']='return function() return test_manager end'}
local events={};local managerFactory=sources['compat/asset_manager.lua']
sources['compat/asset_manager.lua']=nil
local mod={generation=3,info=function()return nil end,list=function()return {}end,
 read=function(_,p)
   if p=='compat/asset_manager.lua' then return 'return function() return shared_manager end' end
   return sources[p]
 end,assets={path=function(_,p)return p end},events={on=function(_,n,f)events[n]=f end}}
local env=setmetatable({shared_manager=manager,love={filesystem={newFileData=function(bytes,name)return {bytes=bytes,name=name}end}},
 load=function(s,n) return load(s,n,'t',setmetatable({shared_manager=manager},{__index=_G})) end},{__index=_G})
local assets=assert(load(asset_source,'resolver','t',env))()(mod)
assert(not assets:available('sober') and not assets:source('sober'))
current['assets/audio/gen3/sober.flac']='audio1'
current['assets/audio/gen3/eulogy.flac']='audio2'
local one=assets:source('sober');assert(one.bytes=='audio1' and assets:source('sober')==one)
local data={audio={songs={Music_Tool_sober={},Music_Tool_eulogy={}}}}
assert(assets:prepare(data,'sober'));assert(data.audio.songs.Music_Tool_sober.file==one)
assert(assets:prepare(data,'eulogy'));assert(type(data.audio.songs.Music_Tool_sober.file)=='string')
current['assets/audio/gen3/sober.flac']=nil;revision=2
assert(not assets:source('sober'))
events['game.ready']({game={data=data}});assert(assets.game.data==data)
print('PASS: missing audio, downloaded FileData, portable cache, cache revision and bounded retained audio')
''')
