import bpy,numpy as np
from pathlib import Path
R=Path('/workspace/sites/lingyuan-character-lab');ref=R/'reference/makehuman'
ob=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];v=[];uv=[];faces=[];g=''
for l in (ref/'base.obj').open():
 if l.startswith('v '):v.append([float(x) for x in l.split()[1:4]])
 elif l.startswith('vt '):uv.append([float(x) for x in l.split()[1:3]])
 elif l.startswith('g '):g=l.split()[1]
 elif l.startswith('f ') and g=='body':
  row=[x.split('/') for x in l.split()[1:]];faces.append(([int(x[0])-1 for x in row],[int(x[1])-1 for x in row]))
v=np.array(v)
for fname in ['asian-male-young.target','universal-male-young-averagemuscle-averageweight.target']:
 for l in (ref/fname).open():
  p=l.split()
  if len(p)==4 and not l.startswith('#'):v[int(p[0])]+=np.array([float(x) for x in p[1:]])
faces=[x for x in faces if min(v[i,1] for i in x[0])>5.0]
if len(faces)!=len(ob.data.polygons):raise RuntimeError('UV source topology does not match head')
lay=ob.data.uv_layers.new(name='MakeHumanUV')
for poly,face in zip(ob.data.polygons,faces):
 for idx,ui in zip(poly.loop_indices,face[1]):lay.data[idx].uv=uv[ui]
 poly.material_index=0
m=bpy.data.materials['Skin PBR study'];nodes=m.node_tree.nodes;im=bpy.data.images.load(str(ref/'young_male_diffuse.png'),check_existing=True);im.pack();tex=nodes.new('ShaderNodeTexImage');tex.image=im;tex.label='MakeHuman young Asian male CC0';m.node_tree.links.new(tex.outputs['Color'],nodes['Principled BSDF'].inputs['Base Color'])
bpy.ops.wm.save_as_mainfile(filepath='/tmp/Lingyuan_face_textured.blend')
from mathutils import Vector
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-1.8,1.76));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.40;scene.camera=cam;aim(cam,(0,0,1.76))
for loc,power,size in [((1,-2,3),160,2),((-1,-2,2),80,2),((0,1,2),160,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.75))
scene.render.filepath='/tmp/ling-face-textured.png';bpy.ops.render.render(write_still=True)
