from pathlib import Path
import json,struct,math,hashlib
R=Path(__file__).resolve().parents[1];raw=(R/'dist/quality/dragon-head-variants.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);binary=raw[28+size:];source=json.loads(Path('/tmp/promotion-heads.json').read_text());rows=[]
def vec3(index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12);return [struct.unpack_from('<3f',binary,start+i*stride) for i in range(a['count'])]
for part in source:
 name=part['variant']+' '+part['role'];mesh=next(m for m in d['meshes'] if m['name']==name);positions=[];triangles=0
 for primitive in mesh['primitives']:
  positions+=vec3(primitive['attributes']['POSITION']);normals=vec3(primitive['attributes']['NORMAL']);assert all(abs(math.sqrt(sum(x*x for x in p))-1)<.002 for p in normals);triangles+=d['accessors'][primitive['indices']]['count']//3
 p=part['positions'];expected=[p[i:i+3] for i in range(0,len(p),3)];signature=lambda points:{tuple(round(x,5) for x in row) for row in points};assert signature(positions)==signature(expected),name;assert triangles==len(part['indices'])//3;rows.append({'mesh':name,'triangles':triangles,'runtimeCoordinatesRoundTrip':True})
assert not d.get('skins') and not d.get('animations');assert len(d['meshes'])==len(source)
(R/'verification/promotion/heads/asset.json').write_text(json.dumps({'scope':'static editable head geometry; runtime TSL materials/animation verified in browser separately','sha256':hashlib.sha256(raw).hexdigest(),'parts':rows,'finalArtAccepted':False},indent=2));print('PASS_THREE_HEAD_ASSET_ROUND_TRIP')
