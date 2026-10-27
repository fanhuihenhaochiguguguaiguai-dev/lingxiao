import bpy,bmesh,math,numpy as np
from pathlib import Path
import os
from collections import defaultdict
from mathutils import Vector
R=Path('/workspace/sites/lingyuan-character-lab'); ref=R/'reference/makehuman';bpy.ops.wm.open_mainfile(filepath=os.environ.get('LINGYUAN_SOURCE_BLEND',str(R/'dist/Lingyuan_working.blend')))
if bpy.data.objects.get('Lingyuan head - MakeHuman CC0 base'): raise SystemExit('Head has already been applied; select a pre-refinement source via LINGYUAN_SOURCE_BLEND.')
rig=bpy.data.objects['Lingyuan_Rig']
# Remove old head and flat facial pieces from each exported model, preserving hair.
for lod in range(3):
 o=bpy.data.objects[f'Lingyuan_LOD{lod}'];me=o.data;p=list(range(len(me.vertices)))
 def rt(i):
  while p[i]!=i:p[i]=p[p[i]];i=p[i]
  return i
 for e in me.edges:
  a,b=e.vertices;p[rt(b)]=rt(a)
 cs=defaultdict(list)
 for v in me.vertices:cs[rt(v.index)].append(v)
 remove=set()
 for vs in cs.values():
  xyz=np.array([v.co[:] for v in vs]);lo=xyz.min(0);hi=xyz.max(0);n=len(vs)
  head=n>300 and lo[2]<1.66 and hi[2]>1.85 and lo[0]>-.12 and hi[0]<.12
  ears=lo[2]>1.69 and hi[2]<1.77 and lo[0]>-.11 and hi[0]<.11 and (hi[0]<-.07 or lo[0]>.07)
  facial=lo[2]>1.68 and hi[2]<1.82 and lo[0]>-.07 and hi[0]<.07 and hi[1]<-.07
  if head or ears or facial:remove.update(v.index for v in vs)
 bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(me);bm.free();me.update();print('REMOVE',lod,len(remove))
# Parse MakeHuman asset including only human body (not helper surfaces).
vertices=[];faces=[];group=''
for line in (ref/'base.obj').open():
 if line.startswith('v '):vertices.append([float(x) for x in line.split()[1:4]])
 elif line.startswith('g '):group=line.split()[1]
 elif line.startswith('f ') and group=='body':faces.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
verts=np.array(vertices)
for fname in ['asian-male-young.target','universal-male-young-averagemuscle-averageweight.target']:
 for line in (ref/fname).open():
  if line.startswith('#') or not line.strip():continue
  l=line.split()
  if len(l)==4:verts[int(l[0])]+=np.array([float(x) for x in l[1:]])
# Keep head and a small neck section, omit all helper joint data.
faces=[f for f in faces if min(verts[i,1] for i in f)>5.0]
used=sorted(set(i for f in faces for i in f));remap={i:k for k,i in enumerate(used)}
# User's reference specifies slightly slender proportions; this is a working fit.
coords=[]
for i in used:
 x,y,z=verts[i]; blend=max(0,min(1,(6.3-y)/1.3)); xx=x*.104; xx=xx*(1-blend)+max(-.047,min(.047,xx))*blend; yy=-(z-.48)*.104; yy=yy*(1-blend)+max(-.05,min(.065,yy))*blend; coords.append((xx,yy,1.926+(y-8.49)*.104))
mesh=bpy.data.meshes.new('Anatomical face topology');mesh.from_pydata(coords,[],[[remap[i] for i in f] for f in faces]);mesh.update();ob=bpy.data.objects.new('Lingyuan head - MakeHuman CC0 base',mesh);bpy.context.scene.collection.objects.link(ob)
skin=bpy.data.materials.new('Skin PBR study');skin.use_nodes=True;p=skin.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.58,.37,.30,1);p.inputs['Roughness'].default_value=.47;p.inputs['Subsurface Weight'].default_value=.08;skin.diffuse_color=(.58,.37,.30,1);ob.data.materials.append(skin)
for p in mesh.polygons:p.use_smooth=True
ob.parent=rig;g=ob.vertex_groups.new(name='head');g.add(list(range(len(mesh.vertices))),1,'REPLACE');arm=ob.modifiers.new('head rig','ARMATURE');arm.object=rig;sub=ob.modifiers.new('Smooth face surface','SUBSURF');sub.levels=2;sub.render_levels=2
# Subtle lip coloring follows the real face topology rather than a projected image.
lips=bpy.data.materials.new('Natural lip tint');lips.diffuse_color=(.36,.12,.12,1);lips.use_nodes=True;lips.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.36,.12,.12,1);lips.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.5;mesh.materials.append(lips)
for poly in mesh.polygons:
 c=poly.center
 # Polygon centers are in local anatomical coordinates.
 if abs(c.x)<.020 and 1.690<c.z<1.703 and c.y<-.065:poly.material_index=1
# Eyebrows follow the face by ray casting, each one is an actual weighted mesh.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();evaluated=ob.evaluated_get(deps);bv=BVHTree.FromObject(evaluated,deps)
browmat=bpy.data.materials.new('Dark eyebrows');browmat.diffuse_color=(.025,.017,.015,1);browmat.use_nodes=True;browmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.025,.017,.015,1)
for side in [-1,1]:
 vv=[];ff=[]
 for i in range(17):
  t=i/16;x=side*(.013+.037*t);z=1.793+.004*math.sin(math.pi*t)-.002*t
  for k in [-1,1]:
   zz=z+k*.0025*math.sin(math.pi*t)**.6;hit,normal,ind,dist=bv.ray_cast(Vector((x,-1,zz)),Vector((0,1,0)))
   vv.append((x,hit.y-.0012 if hit else -.081,zz))
 for i in range(16):ff.append((2*i,2*i+1,2*i+3,2*i+2))
 me=bpy.data.meshes.new('Eyebrow surface');me.from_pydata(vv,[],ff);me.update();b=bpy.data.objects.new('Eyebrow',me);bpy.context.scene.collection.objects.link(b);b.data.materials.append(browmat);b.parent=rig;g=b.vertex_groups.new(name='head');g.add(list(range(len(vv))),1,'REPLACE');m=b.modifiers.new('head rig','ARMATURE');m.object=rig

# Eye sockets derived from MakeHuman's embedded eye joint centers after morphing.
white=bpy.data.materials.new('Eye porcelain');white.diffuse_color=(.75,.74,.70,1);white.use_nodes=True;white.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.75,.74,.70,1)
iris=bpy.data.materials.new('Iris blue-gray');iris.diffuse_color=(.07,.12,.14,1);iris.use_nodes=True;iris.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.07,.12,.14,1)
pupil=bpy.data.materials.new('Pupil');pupil.diffuse_color=(.008,.01,.012,1);pupil.use_nodes=True;pupil.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.008,.01,.012,1)
def sphere(n,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 o.parent=rig;g=o.vertex_groups.new(name='head');g.add(list(range(len(o.data.vertices))),1,'REPLACE');mo=o.modifiers.new('head rig','ARMATURE');mo.object=rig
for s in [-1,1]:
 x=s*.0306;z=1.7732;y=-.0731
 sphere('Eye', (x,y,z),(.0125,.0125,.0125),white);sphere('Iris',(x,y-.0125,z),(.0055,.002,.0055),iris);sphere('Pupil',(x,y-.0143,z),(.0025,.001,.0025),pupil)
# Tone down source hair atlas region without changing unrelated outfit colors.
im=bpy.data.images.get('poxiao_basecolor')
if im:
 data=np.array(im.pixels[:],dtype=np.float32).reshape((im.size[1],im.size[0],4));p=data[1024:1280,1024:1280,:3];light=p.mean(2);p[:,:,0]=light*.12;p[:,:,1]=light*.14;p[:,:,2]=light*.18;im.pixels.foreach_set(data.ravel());im.pack()
bpy.ops.wm.save_as_mainfile(filepath='/tmp/Lingyuan_face_test.blend')
# Real face close-up image for comparative review, not fake image.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-1.8,1.76));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.40;scene.camera=cam;aim(cam,(0,0,1.76))
for loc,power,size in [((1,-2,3),160,2),((-1,-2,2),80,2),((0,1,2),160,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.75))
scene.render.filepath='/tmp/ling-face-preview.png';bpy.ops.render.render(write_still=True)
