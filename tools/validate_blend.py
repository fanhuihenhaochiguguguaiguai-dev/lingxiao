"""Blender checks on the refined rig and visible hair deformation."""
import bpy,json,math
from collections import defaultdict
rig=bpy.data.objects['Lingyuan_Rig'];assert len(rig.data.bones)==58
for n in range(3):
 hair=bpy.data.objects[f'Hair_Lod{n}'];assert any(m.type=='ARMATURE' and m.object==rig for m in hair.modifiers)
 missing=[g for g in ['head','hair01.L','hair02.L','hair01.R','hair02.R'] if hair.vertex_groups.get(g) is None];assert not missing
 for vertex in hair.data.vertices:
  assert abs(sum(g.weight for g in vertex.groups)-1)<1e-4
 o=bpy.data.objects[f'Lingyuan_LOD{n}'];verts=o.data.vertices;p=list(range(len(verts)))
 def root(i):
  while p[i]!=i:p[i]=p[p[i]];i=p[i]
  return i
 for e in o.data.edges:a,b=e.vertices;p[root(b)]=root(a)
 comps=defaultdict(list)
 for v in verts:comps[root(v.index)].append(v)
 for vs in comps.values():
  if len(vs)<=60:continue
  xs=[v.co.x for v in vs];ys=[v.co.y for v in vs];zs=[v.co.z for v in vs]
  is_old=1.47<min(zs)<1.50 and 1.64<max(zs)<1.66 and min(xs)>-.055 and max(xs)<.055 and min(ys)>-.055 and max(ys)<.07
  assert not is_old,f'Old overlapping neck remains in LOD{n}'
assert not any(o.name.startswith('Long hair ') for o in bpy.data.objects)
act=bpy.data.actions.get('walk');assert act
for track in rig.animation_data.nla_tracks:track.mute=True
rig.animation_data.action=act
hair=bpy.data.objects['Hair_Lod0'];group=hair.vertex_groups['hair02.L'];idx=next(v.index for v in hair.data.vertices if any(g.group==group.index and g.weight>.8 for g in v.groups))
coords=[]
for frame in (0,9):
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();obj=hair.evaluated_get(dg);mesh=obj.to_mesh();coords.append(tuple(mesh.vertices[idx].co));obj.to_mesh_clear()
delta=math.dist(*coords);assert delta>1e-5,f'Hair mesh did not deform during walk: {delta}'
print('VALIDATION_JSON '+json.dumps({'result':'PASS','bones':58,'old_overlap_neck_removed':True,'lods':3,'hair_vertex_motion_m':delta,'tested_action':'walk'}))
