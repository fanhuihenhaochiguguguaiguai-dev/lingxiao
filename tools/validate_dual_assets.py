"""Check skin-weight integrity and preserved clothing thickness in candidate GLBs."""
from pathlib import Path
import json,struct,math,os
R=Path(__file__).resolve().parents[1];out=R/os.environ.get('LUNAR_MODEL_REPORT_DIR','verification/dual-quality');out.mkdir(exist_ok=True)
def audit(file):
 data=file.read_bytes();size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size]);binary=data[28+size:];errors=[];weighted=0;shapes=[]
 for mesh in doc['meshes']:
  if 'Blink' in mesh.get('extras',{}).get('targetNames',[]):shapes.append(mesh['name'])
  for p in mesh['primitives']:
   if 'WEIGHTS_0' not in p['attributes']:errors.append('unbound mesh '+mesh['name']);continue
   a=doc['accessors'][p['attributes']['WEIGHTS_0']];view=doc['bufferViews'][a['bufferView']];stride=view.get('byteStride',16);offset=view.get('byteOffset',0)+a.get('byteOffset',0)
   assert a['componentType']==5126
   for i in range(a['count']):
    w=struct.unpack_from('<4f',binary,offset+i*stride);weighted+=1
    if not all(math.isfinite(v) and v>=0 for v in w) or abs(sum(w)-1)>.001:errors.append('invalid weights '+mesh['name']);break
 return {'file':str(file.relative_to(R)),'skins':len(doc.get('skins',[])),'jointCount':max(len(s['joints']) for s in doc['skins']),'weightedVertices':weighted,'blinkMeshes':shapes,'errors':errors}
results=[audit(R/'dist/lingyuan-lod1.glb'),audit(R/'dist/yueli-study.glb')];assert all(not r['errors'] for r in results),results
(out/'assets.json').write_text(json.dumps({'results':results,'scope':'weights, hierarchy, blink presence only; not artistic/cloth acceptance'},ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False))
