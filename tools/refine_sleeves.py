"""Non-destructive candidate: open the robe above the wrist to expose the hands."""
import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/sites/lingyuan-character-lab/dist/Lingyuan_working.blend')
for name in ['Outer sleeve','Outer sleeve.001']:
 o=bpy.data.objects.get(name)
 if not o:raise RuntimeError('Expected sleeve not found: '+name)
 zs=[v.co.z for v in o.data.vertices];lo=min(zs);hi=max(zs)
 if abs(lo-.94)>.02 or abs(hi-1.4)>.01:raise RuntimeError('Sleeve differs from expected baseline: '+name)
 for v in o.data.vertices:v.co.y+=.14
 o.data.update();o['refinement']='moved white outer sleeve behind forearm to expose hands while retaining length'
# The provided hand reference shows exposed fingers. Reuse the existing skin atlas
# for palm/finger surfaces while leaving the forearm and weapon materials intact.
for lod in range(3):
 body=bpy.data.objects[f'Lingyuan_LOD{lod}'];skin_groups={g.index for g in body.vertex_groups if g.name.startswith(('hand.','finger'))};uv=body.data.uv_layers.active
 if not uv:raise RuntimeError('Missing UV map on LOD '+str(lod))
 changed=0
 for poly in body.data.polygons:
  vertices=[body.data.vertices[i] for i in poly.vertices]
  if all(sum(g.weight for g in vertex.groups if g.group in skin_groups)>.6 and vertex.co.z<1.01 for vertex in vertices):
   for li in poly.loop_indices:
    vert=body.data.vertices[body.data.loops[li].vertex_index];uv.data[li].uv=(.055+vert.co.y*.35,.555+(vert.co.z-.96)*.2)
   changed+=1
 if changed<30:raise RuntimeError('Unexpected hand topology on LOD '+str(lod))
 print('HAND_UV',lod,changed,flush=True)
bpy.ops.wm.save_as_mainfile(filepath='/tmp/Lingyuan_sleeve_candidate.blend')
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam
for loc,power,size in [((2,-3,4),450,3),((-3,-2,2.5),300,3),((0,3,3),500,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1))
for name,target,scale in [('hand',(.43,0,.99),.36),('sleeve',(.34,0,1.23),.6)]:
 cam.location=(target[0],-3,target[2]);cam.data.ortho_scale=scale;aim(cam,target);scene.render.filepath='/tmp/ling-sleeve-'+name+'.png';bpy.ops.render.render(write_still=True)
