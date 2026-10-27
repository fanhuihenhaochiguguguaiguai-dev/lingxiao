"""Local candidate experiment. Reads the current master, never overwrites it.
Run: blender -b dist/Lingyuan_working.blend -t 4 --python tools/candidate_face_hair.py
"""
import bpy,math
from pathlib import Path
from mathutils import Vector
out=Path('/tmp/lingyuan-local-refine');out.mkdir(exist_ok=True)
scene=bpy.context.scene;old_camera=scene.camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.36;scene.camera=cam;created=[cam]
for loc,power,size in [((1,-2,3),100,2),((-1,-2,2),45,2),((0,1,2),110,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.76));created.append(l)
def render(stage):
 for name,loc in [('front',(0,-1.8,1.76)),('three-quarter',(-1.3,-1.3,1.76)),('side',(-1.8,0,1.76))]:
  cam.location=loc;aim(cam,(0,0,1.76));scene.render.filepath=str(out/(stage+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
render('before')
head=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];assert head.data.shape_keys and len(head.data.shape_keys.key_blocks)==4
# Thicken and raise the outer portions of the existing weighted eyebrow fibers.
brow=bpy.data.objects['Eyebrow fibers']
for v in brow.data.vertices:
 x=v.co.x;t=max(0,min(1,(abs(x)-.014)/.036));center=1.793+.004*math.sin(math.pi*t)-.002*t
 v.co.z=center+(v.co.z-center)*1.65+.002*(t-.4)
# Bend existing, weighted front locks; no replacement hair mesh, no change to bones/UVs.
for lod,n,sections,sides in [(0,20,12,6),(1,13,9,6),(2,8,6,5)]:
 hair=bpy.data.objects[f'Hair_Lod{lod}'];stride=(sections+1)*sides;assert len(hair.data.vertices)>=2*n*stride
 for half in range(2):
  side=-1 if half==0 else 1
  for lock in range(n):
   u=lock/max(1,n-1);start=(half*n+lock)*stride
   for j in range(sections+1):
    t=j/sections;offset=math.sin(math.pi*t);dx=side*.006*offset*(.4+.6*u);dy=-.003*offset;dz=-.006*u*math.sin(t*math.pi/2)
    for k in range(sides):
     v=hair.data.vertices[start+j*sides+k];v.co.x+=dx;v.co.y+=dy;v.co.z+=dz
 hair.data.update()
head.data.update();brow.data.update();bpy.context.view_layer.update();render('candidate')
# Remove only inspection objects before saving the candidate, leaving the original scene's camera unchanged.
scene.camera=old_camera
for obj in created:bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'candidate.blend'))
print('CANDIDATE_READY',flush=True)
