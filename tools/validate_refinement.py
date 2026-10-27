"""Validate LOD exports, skin weights, and preserved animation channels."""
import json,math,struct,sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else 'dist').resolve();rows=[]
for lod in range(3):
 path=root/f'lingyuan-lod{lod}.glb';raw=path.read_bytes();magic,version,size=struct.unpack_from('<4sII',raw,0)
 assert magic==b'glTF' and version==2 and size==len(raw),f'{path}: invalid GLB header'
 length,chunk=struct.unpack_from('<II',raw,12);assert chunk==0x4e4f534a
 doc=json.loads(raw[20:20+length]);pos=20+length;blen,kind=struct.unpack_from('<II',raw,pos);assert kind==0x004e4942;bin=raw[pos+8:pos+8+blen]
 def accessor(ix):
  a=doc['accessors'][ix];v=doc['bufferViews'][a['bufferView']];num={'SCALAR':1,'VEC4':4}[a['type']];kind={5126:'f',5123:'H',5121:'B'}[a['componentType']];step=struct.calcsize('<'+kind*num);stride=v.get('byteStride',step);off=v.get('byteOffset',0)+a.get('byteOffset',0)
  values=[struct.unpack_from('<'+kind*num,bin,off+i*stride) for i in range(a['count'])]
  if a.get('normalized') and kind in ('H','B'):
   div=65535 if kind=='H' else 255;values=[tuple(x/div for x in row) for row in values]
  return values
 nodes=doc['nodes'];head=next((n for n in nodes if 'MakeHuman CC0 base' in n.get('name','')),None);assert head and 'mesh' in head and 'skin' in head;headmesh=doc['meshes'][head['mesh']];assert len(headmesh.get('weights',[]))==3 and all(len(p.get('targets',[]))==3 for p in headmesh['primitives']),f'LOD {lod}: missing editable face targets';eyes=next((n for n in nodes if n.get('name')=='Eye microgeometry'),None);assert eyes and 'mesh' in eyes and 'skin' in eyes,f'LOD {lod}: missing eye detail geometry';hairs=[n for n in nodes if n.get('name','').startswith('Hair_Lod')];assert len(hairs)==1 and hairs[0]['name']==f'Hair_Lod{lod}',f'LOD {lod}: wrong hair node'
 hair=hairs[0];assert 'skin' in hair and 'mesh' in hair;primitives=doc['meshes'][hair['mesh']]['primitives'];num_vertices=0
 for p in primitives:
  a=p['attributes'];assert all(x in a for x in ['POSITION','NORMAL','JOINTS_0','WEIGHTS_0']);weights=accessor(a['WEIGHTS_0']);num_vertices+=len(weights)
  assert weights and all(all(math.isfinite(x) and x>=0 for x in row) and abs(sum(row)-1)<.01 for row in weights),f'LOD {lod}: invalid hair weights'
 joints=[nodes[i].get('name','') for i in doc['skins'][hair['skin']]['joints']];assert all(x in joints for x in ['head','hair01.L','hair02.L','hair01.R','hair02.R'])
 clips={a['name'] for a in doc.get('animations',[])};assert {'idle','walk','turn_left','turn_right'}<=clips
 tris=sum(doc['accessors'][p['indices']]['count']//3 for mesh in doc['meshes'] for p in mesh['primitives'] if 'indices' in p)
 rows.append({'lod':lod,'triangles':tris,'hair_vertices':num_vertices,'hair_primitives':len(primitives),'animation_names':sorted(clips),'validated':'PASS'})
assert rows[0]['triangles']>rows[1]['triangles']>rows[2]['triangles'],'LOD triangle order is not descending'

if '--stats-out' in sys.argv:
 dest=Path(sys.argv[sys.argv.index('--stats-out')+1]);tmp=dest.with_suffix(dest.suffix+'.tmp');tmp.write_text(json.dumps({'version':1,'lods':rows},ensure_ascii=False,indent=2)+'\n');tmp.replace(dest)
print(json.dumps(rows,ensure_ascii=False,indent=2))
