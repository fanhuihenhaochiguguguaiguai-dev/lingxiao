"""Verify lossless scene repair and genuine baked runtime sample resources."""
from pathlib import Path
import hashlib,json,struct,subprocess,io
from PIL import Image,ImageStat
R=Path(__file__).resolve().parents[1];out=R/'verification/lingyuan31'
def glb(raw):
 n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[20+n:]
rows=[]
for lod in range(3):
 p=f'dist/lingyuan-lod{lod}.glb';before=subprocess.check_output(['git','show','650edf1:'+p],cwd=R);after=(R/p).read_bytes();a,abin=glb(before);b,bbin=glb(after);assert abin==bbin and a['skins']==b['skins'] and a['animations']==b['animations'];active=set()
 def walk(i):
  if i in active:return
  active.add(i)
  for c in b['nodes'][i].get('children',[]):walk(c)
 for i in b['scenes'][b.get('scene',0)]['nodes']:walk(i)
 names=[b['nodes'][i].get('name') for i in active if b['nodes'][i].get('name','').startswith('Hair_Lod')];assert names==[f'Hair_Lod{lod}']
 rows.append({'lod':lod,'activeHair':names,'binaryPayloadSkinsAnimationsUnchanged':True,'sha256':hashlib.sha256(after).hexdigest()})
raw=(R/'dist/quality/lingyuan31-head.glb').read_bytes();d,chunks=glb(raw);binary=chunks[8:];head=next(m for m in d['meshes'] if m['name']=='Anatomical face topology');material=d['materials'][head['primitives'][0]['material']]
assert material.get('normalTexture') and material.get('occlusionTexture')
assert 'Blink' in head.get('extras',{}).get('targetNames',[]) and len(d['skins'][0]['joints'])==60
assert not any(n.get('extras',{}).get('offline_only') for n in d['nodes'])
images={}
for kind,key,size in [('normal','normalTexture',(2048,2048)),('ao','occlusionTexture',(1024,1024))]:
 image=d['images'][d['textures'][material[key]['index']]['source']];v=d['bufferViews'][image['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];im=Image.open(io.BytesIO(data));assert im.size==size
 deviation=ImageStat.Stat(im.convert('RGB')).stddev;assert max(deviation)>2,deviation
 images[kind]={'size':im.size,'stddev':deviation,'embedded':True}
report={'canonicalRepair':rows,'sample':{'sha256':hashlib.sha256(raw).hexdigest(),'headTargetNames':head['extras']['targetNames'],'headRuntimeVertices':sum(d['accessors'][p['attributes']['POSITION']]['count'] for p in head['primitives']),'offlineSourceExported':False,'bakedImages':images},'artAccepted':False,'realPhoneTested':False}
(out/'resource-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS_SCENE_REPAIR_AND_REAL_BAKES',flush=True)
