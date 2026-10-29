"""Scoped asset gate: updated candidate, shared solids, unchanged approved resources."""
from pathlib import Path
import json,struct,subprocess,hashlib,math
R=Path(__file__).resolve().parents[1];out=R/'verification/v35';base='3528f0a'
def glb(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]
def vec(d,buf,index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];num={'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5123:'H',5121:'B'}[a['componentType']];size=struct.calcsize('<'+fmt*num);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
 rows=[struct.unpack_from('<'+fmt*num,buf,start+i*stride) for i in range(a['count'])]
 if a.get('normalized'):
  divisor=65535 if fmt=='H' else 255;rows=[tuple(x/divisor for x in row) for row in rows]
 return rows
kept={}
paths=['dist/lingyuan-lod0.glb','dist/lingyuan-lod1.glb','dist/lingyuan-lod2.glb','dist/yueli-study.glb','skill-src/src/dragon.ts','skill-src/src/slash-dragon.ts','skill-src/src/star-vortex.ts','skill-src/src/ice-dragon.ts','skill-src/src/dragon-frames.ts','skill-src/src/skill-instances.ts','skill-src/src/instance-audio.ts','skill-src/src/skill-registry.ts','skill-src/src/character-motion.ts']
for path in paths:
 data=(R/path).read_bytes();assert data==subprocess.check_output(['git','show',base+':'+path],cwd=R),path;kept[path]=hashlib.sha256(data).hexdigest()
d,bin=glb(R/'dist/quality/lingyuan31-head.glb');nodes=d['nodes'];active=set()
def visit(i):
 if i in active:return
 active.add(i)
 for child in nodes[i].get('children',[]):visit(child)
for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i)
assert len(d['skins'][0]['joints'])==60
assert [nodes[i]['name'] for i in active if nodes[i].get('name','').startswith('Hair_Lod')]==['Hair_Lod1']
assert not any(n.get('extras',{}).get('offline_only') for n in nodes)
head=next(m for m in d['meshes'] if m['name']=='Anatomical face topology');assert {'Blink','Chin narrower','Chin tapered','Cheeks refined'}<=set(head['extras']['targetNames'])
mat=d['materials'][head['primitives'][0]['material']];assert mat.get('normalTexture') and mat.get('occlusionTexture')
weighted=0
for i in active:
 if 'mesh' not in nodes[i]:continue
 for p in d['meshes'][nodes[i]['mesh']]['primitives']:
  a=p['attributes'];normals=vec(d,bin,a['NORMAL']);assert all(abs(math.sqrt(sum(x*x for x in n))-1)<.003 for n in normals)
  assert 'WEIGHTS_0' in a
  weights=vec(d,bin,a['WEIGHTS_0']);assert all(abs(sum(w)-1)<.01 for w in weights);weighted+=len(weights)
before=json.loads((out/'web/before.json').read_text())['cases'];after=json.loads((out/'web/after.json').read_text())['cases'];comparison={}
for case,row in before.items():
 for view,s in row.items():
  t=after[case][view];assert s['cameraPosition']==t['cameraPosition'] and s['cameraTarget']==t['cameraTarget'];assert s['drawCalls']==t['drawCalls']
 comparison[case]={'drawCalls':[row['angle']['drawCalls'],after[case]['angle']['drawCalls']],'triangles':[row['angle']['triangles'],after[case]['angle']['triangles']]}
# Blender/glTF coordinate round trip for the real source solids.
if (R/'dist/quality/effect-surfaces.glb').exists():
 e,eb=glb(R/'dist/quality/effect-surfaces.glb');parts=json.loads(Path('/tmp/surface35-after.json').read_text());rt=[]
 for source in parts:
  mesh=next(m for m in e['meshes'] if m['name']==source['role']);coords=[];triangles=0
  for p in mesh['primitives']:coords+=vec(e,eb,p['attributes']['POSITION']);triangles+=e['accessors'][p['indices']]['count']//3
  expected=[source['positions'][i:i+3] for i in range(0,len(source['positions']),3)];sig=lambda rows:{tuple(round(x,6) for x in p) for p in rows};assert sig(coords)==sig(expected),source['role'];assert triangles==len(source['indices'])//3;rt.append({'part':source['role'],'triangles':triangles,'coordinatesRoundTrip':True})
else:rt=[]
(out/'assets.json').write_text(json.dumps({'baseline':base,'unchanged':kept,'candidate':{'bones':60,'shapeKeys':head['extras']['targetNames'],'weightedVertices':weighted,'onlyHairLOD':1,'offlineHighExcluded':True,'artAccepted':False},'surfaceCoordinateRoundTrip':rt,'fixedWebComparison':comparison,'phoneTested':False},indent=2))
print('PASS_SCOPED_V35_ASSETS')
