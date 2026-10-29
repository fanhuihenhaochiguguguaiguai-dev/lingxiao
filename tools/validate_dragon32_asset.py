"""Check runtime-template to Blender to glTF axis/geometry round trip."""
from pathlib import Path
import json,struct,math,hashlib
R=Path(__file__).resolve().parents[1];path=R/'dist/quality/dragon-slash32.glb';raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);binary=raw[28+size:]
def read(index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3}[a['type']];typ={5126:'f',5123:'H',5125:'I'}[a['componentType']];step=struct.calcsize('<'+typ*n);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',step)
 return [struct.unpack_from('<'+typ*n,binary,start+i*stride) for i in range(a['count'])]
templates=json.loads(Path('/tmp/dragon32-master.json').read_text());rows=[]
for source in templates:
 mesh=next(m for m in d['meshes'] if m['name']==source['name']);triangles=sum(d['accessors'][p['indices']]['count']//3 for p in mesh['primitives']);assert triangles==len(source['indices'])//3
 original=[source['positions'][i:i+3] for i in range(0,len(source['positions']),3)];actual=[]
 for p in mesh['primitives']:
  positions=read(p['attributes']['POSITION']);normals=read(p['attributes']['NORMAL']);actual.extend(positions);assert all(math.isfinite(x) for row in positions for x in row);assert all(abs(math.sqrt(sum(x*x for x in row))-1)<.002 for row in normals)
 # Quantized coordinate multisets tolerate exporter welding and float roundoff,
 # while detecting accidentally shipping Z-up data into a Y-up webpage.
 signature=lambda points:{tuple(round(v,5) for v in p) for p in points}
 assert signature(actual)==signature(original),(source['name'],'axis/geometry mismatch')
 rows.append({'mesh':source['name'],'triangles':triangles,'runtimeCoordinatesRoundTrip':True})
assert len(d['meshes'])==len(templates) and not d.get('animations') and not d.get('skins')
report={'status':'PASS_STATIC_ASSET_ROUND_TRIP','sha256':hashlib.sha256(raw).hexdigest(),'parts':rows,'animations':'rest asset; curve animation is implemented in slash-dragon.ts, not a skeletal clip','artAccepted':False,'realPhoneTested':False}
(R/'verification/dragon32/asset.json').write_text(json.dumps(report,indent=2));print('PASS_DRAGON_STATIC_GLTF_AND_AXES',flush=True)
