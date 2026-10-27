"""Editable MakeHuman facial target experiment; compare renders before promoting.
Inputs are CC0 base and targets. Does not overwrite the master; output is /tmp.
"""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
R=Path(__file__).resolve().parents[1];src=R/'reference/makehuman';bpy.ops.wm.open_mainfile(filepath=str(R/'dist/Lingyuan_working.blend'));head=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];mesh=head.data
if mesh.shape_keys:raise RuntimeError('Existing shape keys detected; refusing to overwrite')
verts=[];faces=[];g=''
for l in (src/'base.obj').open():
 if l.startswith('v '):verts.append([float(x) for x in l.split()[1:4]])
 elif l.startswith('g '):g=l.split()[1]
 elif l.startswith('f ') and g=='body':faces.append([int(x.split('/')[0])-1 for x in l.split()[1:]])
for fn in ['asian-male-young.target','universal-male-young-averagemuscle-averageweight.target']:
 for l in (src/fn).open():
  p=l.split()
  if len(p)==4 and not l.startswith('#'):
   ix=int(p[0]);verts[ix]=[verts[ix][j]+float(p[j+1]) for j in range(3)]
faces=[f for f in faces if min(verts[i][1] for i in f)>5.0];used=sorted(set(i for f in faces for i in f));mapping={original:i for i,original in enumerate(used)}
assert len(used)==len(mesh.vertices),'Base mesh topology changed; stopping to avoid wrong vertex edits'
def transform(x,y,z):
 blend=max(0,min(1,(6.3-y)/1.3));xx=x*.104;xx=xx*(1-blend)+max(-.047,min(.047,xx))*blend;yy=-(z-.48)*.104;yy=yy*(1-blend)+max(-.05,min(.065,yy))*blend;return Vector((xx,yy,1.926+(y-8.49)*.104))
head.shape_key_add(name='Basis')
for name,files,weight in [
 ('Chin narrower',['chin_chin-width-decr.target'],.48),
 ('Chin tapered',['chin_chin-triangle.target'],.38),
 ('Cheeks refined',['cheek_l-cheek-volume-decr.target','cheek_r-cheek-volume-decr.target'],.24)]:
 key=head.shape_key_add(name=name);key.value=weight;changes=defaultdict(lambda:Vector((0,0,0)))
 for fn in files:
  for l in (src/fn).open():
   p=l.split()
   if len(p)==4 and not l.startswith('#'):
    ix=int(p[0])
    if ix in mapping:changes[ix]+=Vector(tuple(float(v) for v in p[1:]))
 for original,delta in changes.items():
  i=mapping[original];base=Vector(verts[original]);key.data[i].co=mesh.vertices[i].co+transform(*(base+delta))-transform(*base)
 print('FACIAL_TARGET',name,len(changes),'weight',weight,flush=True)
head['facial_adjustment']='Editable CC0 chin and cheek targets; visual likeness not yet approved.'
bpy.ops.wm.save_as_mainfile(filepath='/tmp/Lingyuan_facial_candidate.blend')
# Render actual candidate mesh at the same lighting/view as the previous stage.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-1.8,1.76));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.4;scene.camera=cam
for loc,power,size in [((1,-2,3),100,2),((-1,-2,2),45,2),((0,1,2),110,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.75))
for name,loc in [('front',(0,-1.8,1.76)),('side',(-1.8,0,1.76))]:
 cam.location=loc;aim(cam,(0,0,1.76));scene.render.filepath=f'/tmp/ling-facial-{name}.png';bpy.ops.render.render(write_still=True)
