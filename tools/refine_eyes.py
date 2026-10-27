"""Add real skinned iris rims, catchlights and fine upper lid geometry to candidate."""
import bpy,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/tmp/Lingyuan_facial_candidate.blend');rig=bpy.data.objects['Lingyuan_Rig']
if bpy.data.objects.get('Eye microgeometry'):raise RuntimeError('Eye details already present')
def material(name,col,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
mats=[material('Iris edge',(.009,.024,.035),.26),material('Eye reflections',(.85,.92,1),.12),material('Lid edge',(.045,.021,.019),.48)]
v=[];f=[];slots=[]
def face(ids,slot):f.append(ids);slots.append(slot)
for side in [-1,1]:
 cx=side*.0306;z=1.7732;y=-.0879;n=32;start=len(v)
 for radius in [.00525,.00615]:
  for j in range(n):a=math.tau*j/n;v.append((cx+radius*math.cos(a),y,z+radius*math.sin(a)))
 for j in range(n):face((start+j,start+(j+1)%n,start+n+(j+1)%n,start+n+j),0)
 # Small real raised catchlight at the cornea surface.
 cx2=cx-.0018;zz=z+.0023;start=len(v)
 v.extend([(cx2-.00065,y-.0006,zz),(cx2,y-.0007,zz+.00065),(cx2+.00065,y-.0006,zz),(cx2,y-.0007,zz-.00065)])
 face((start,start+1,start+2,start+3),1)
 # Delicate upper lid edge; variation respects the almond-shaped eye opening.
 start=len(v);n=20
 for j in range(n+1):
  t=-1+2*j/n;w=math.sqrt(max(0,1-t*t));x=cx+t*.012;zz=z+.0048*w+side*t*.0008;yy=-.0824-.0045*w
  for k in [-1,1]:v.append((x,yy,zz+k*.00025*w))
 for j in range(n):face((start+2*j,start+2*j+1,start+2*j+3,start+2*j+2),2)
me=bpy.data.meshes.new('Iris and eyelid geometry');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('Eye microgeometry',me);bpy.context.scene.collection.objects.link(o)
for m in mats:me.materials.append(m)
for poly,slot in zip(me.polygons,slots):poly.material_index=slot;poly.use_smooth=True
vg=o.vertex_groups.new(name='head');vg.add(list(range(len(v))),1,'REPLACE');o.parent=rig;mod=o.modifiers.new('Head skin','ARMATURE');mod.object=rig
bpy.ops.wm.save_as_mainfile(filepath='/tmp/Lingyuan_facial_eyes_candidate.blend')
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-1.8,1.76));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.29;scene.camera=cam;aim(cam,(0,0,1.76))
for loc,power,size in [((1,-2,3),100,2),((-1,-2,2),45,2),((0,1,2),110,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.75))
scene.render.filepath='/tmp/ling-eyes-front.png';bpy.ops.render.render(write_still=True)
