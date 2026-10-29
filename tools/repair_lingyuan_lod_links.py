"""Unlink unintended hair LOD nodes from each runtime scene.
Keep the binary payload, every skin, morph, animation and material unchanged.
Future clean exports use export_refinement.py visibility filtering.
"""
from pathlib import Path
import json,struct,hashlib
R=Path(__file__).resolve().parents[1];rows=[]
for lod in range(3):
 path=R/f'dist/lingyuan-lod{lod}.glb';before=path.read_bytes();length=struct.unpack_from('<I',before,12)[0];doc=json.loads(before[20:20+length]);binary_chunks=before[20+length:]
 nodes=doc['nodes'];target=f'Hair_Lod{lod}';bad={i for i,n in enumerate(nodes) if n.get('name','').startswith('Hair_Lod') and n['name']!=target}
 assert any(n.get('name')==target for n in nodes)
 removed=[]
 for owners,key in [(nodes,'children'),(doc['scenes'],'nodes')]:
  for owner in owners:
   if key not in owner:continue
   removed.extend(i for i in owner[key] if i in bad);owner[key]=[i for i in owner[key] if i not in bad]
 # No animation channel may secretly reattach a removed hair scene node.
 assert not any(c['target'].get('node') in bad for a in doc.get('animations',[]) for c in a['channels'])
 encoded=json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
 after=struct.pack('<4sII',b'glTF',2,20+len(encoded)+len(binary_chunks))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+binary_chunks
 assert after[20+len(encoded):]==binary_chunks
 tmp=path.with_suffix('.glb.tmp');tmp.write_bytes(after);tmp.replace(path)
 rows.append({'lod':lod,'removedSceneLinks':[nodes[i]['name'] for i in removed],'matchingHair':target,'binaryDataIdentical':True,'beforeSha256':hashlib.sha256(before).hexdigest(),'afterSha256':hashlib.sha256(after).hexdigest(),'unusedDefinitionsRetained':True})
out=R/'verification/lingyuan31';out.mkdir(exist_ok=True)
if any(row['removedSceneLinks'] for row in rows):(out/'lod-repair.json').write_text(json.dumps(rows,indent=2))
print('PASS_LOD_SCENE_LINK_REPAIR',flush=True)
