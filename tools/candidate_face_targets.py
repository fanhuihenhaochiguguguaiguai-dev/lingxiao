"""CC0 MakeHuman target experiment; candidate only, never overwrites master."""
import bpy,math,os
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
R=Path(__file__).resolve().parents[1];ref=R/'reference/makehuman';targets=Path(os.environ.get('LING_FACE_TARGETS',str(ref)));out=Path('/tmp/ling-target-refine');out.mkdir(exist_ok=True)
head=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];mesh=head.data;assert mesh.shape_keys and len(mesh.shape_keys.key_blocks)==4
verts=[];faces=[];group=''
for line in (ref/'base.obj').open():
 if line.startswith('v '):verts.append([float(x) for x in line.split()[1:4]])
 elif line.startswith('g '):group=line.split()[1]
 elif line.startswith('f ') and group=='body':faces.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
for name in ['asian-male-young.target','universal-male-young-averagemuscle-averageweight.target']:
 for line in (ref/name).open():
  parts=line.split()
  if len(parts)==4 and not line.startswith('#'):
   i=int(parts[0]);verts[i]=[verts[i][j]+float(parts[j+1]) for j in range(3)]
faces=[f for f in faces if min(verts[i][1] for i in f)>5.0];used=sorted(set(i for f in faces for i in f));mapping={v:i for i,v in enumerate(used)};assert len(used)==len(mesh.vertices)
def transform(x,y,z):
 b=max(0,min(1,(6.3-y)/1.3));xx=x*.104;xx=xx*(1-b)+max(-.047,min(.047,xx))*b;yy=-(z-.48)*.104;yy=yy*(1-b)+max(-.05,min(.065,yy))*b;return Vector((xx,yy,1.926+(y-8.49)*.104))
changes=defaultdict(lambda:Vector((0,0,0)))
for name,weight in [('nose-width1-decr.target',.65),('nose-width2-decr.target',.55),('nose-flaring-decr.target',.45),('mouth-lowerlip-volume-decr.target',.35),('mouth-scale-vert-decr.target',.25)]:
 for line in (targets/name).open():
  p=line.split()
  if len(p)==4 and not line.startswith('#'):
   index=int(p[0])
   if index in mapping:changes[index]+=Vector(tuple(float(x)*weight for x in p[1:]))
for original,delta in changes.items():
 i=mapping[original];base=Vector(verts[original]);offset=transform(*(base+delta))-transform(*base)
 for key in mesh.shape_keys.key_blocks:key.data[i].co+=offset
mesh.update();bpy.context.view_layer.update();print('TARGET_VERTICES',len(changes),flush=True)
# Save the model before adding any temporary lights or cameras.
bpy.ops.wm.save_as_mainfile(filepath=str(out/'candidate.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.36;scene.camera=cam
for loc,power,size in [((1,-2,3),100,2),((-1,-2,2),45,2),((0,1,2),110,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.76))
for name,loc in [('front',(0,-1.8,1.76)),('three-quarter',(-1.3,-1.3,1.76)),('side',(-1.8,0,1.76))]:
 cam.location=loc;aim(cam,(0,0,1.76));scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('CANDIDATE_READY',flush=True)
