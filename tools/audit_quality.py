"""Read real GLB structural metadata; this does not replace visual review."""
from pathlib import Path
import json,math,struct
root=Path(__file__).resolve().parents[1];rows=[]
for lod in range(3):
 path=root/'dist'/f'lingyuan-lod{lod}.glb';raw=path.read_bytes();magic,version,size=struct.unpack_from('<4sII',raw)
 assert magic==b'glTF' and version==2 and size==len(raw)
 length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a;doc=json.loads(raw[20:20+length]);textures=doc.get('textures',[]);mats=[]
 for m in doc.get('materials',[]):
  p=m.get('pbrMetallicRoughness',{});row={'name':m.get('name',''),'metallic':p.get('metallicFactor',1),'roughness':p.get('roughnessFactor',1),'base_color_texture': 'baseColorTexture' in p,'metal_roughness_texture':'metallicRoughnessTexture' in p,'normal_texture':'normalTexture' in m}
  assert all(math.isfinite(row[k]) and 0<=row[k]<=1 for k in ('metallic','roughness'))
  for ref in [p.get('baseColorTexture'),p.get('metallicRoughnessTexture'),m.get('normalTexture')]:
   if ref: assert 0<=ref['index']<len(textures)
  mats.append(row)
 assert doc.get('skins') and doc.get('animations')
 rows.append({'lod':lod,'meshes':len(doc.get('meshes',[])),'skins':len(doc['skins']),'animations':[a.get('name','') for a in doc['animations']],'materials':mats,'texture_count':len(textures)})
out={'status':'PASS_STRUCTURAL_METADATA_ONLY','lods':rows,'note':'Valid references do not prove texture appearance, deformation quality or artistic acceptance.'}
(root/'verification/quality/glb-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':out['status'],'lods':len(rows),'lod1_materials':len(rows[1]['materials']),'lod1_normal_maps':sum(x['normal_texture'] for x in rows[1]['materials'])},ensure_ascii=False))
