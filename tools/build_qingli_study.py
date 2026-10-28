"""Build a clearly labelled, editable *static study* from a CC0 female mesh and selected reference.
Not a scan, production asset, retopology, rig, or art-approved character.
"""
from pathlib import Path
from collections import defaultdict
from mathutils import Vector, Matrix
import bpy,math,random,sys,os
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'reference/makehuman';OUT=Path('/tmp/qingli-study');OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;random.seed(32)
vs=[];uvs=[];faces=[];face_uvs=[];groups=defaultdict(set);grp=''
for line in (SRC/'base.obj').read_text().splitlines():
 if line.startswith('v '):vs.append(Vector(map(float,line.split()[1:4])))
 elif line.startswith('vt '):uvs.append(tuple(map(float,line.split()[1:3])))
 elif line.startswith('g '):grp=line[2:]
 elif line.startswith('f '):
  parts=[s.split('/') for s in line.split()[1:]];f=[int(p[0])-1 for p in parts];groups[grp].update(f)
  if grp=='body':
   faces.append(f);face_uvs.append([int(p[1])-1 for p in parts])
for f in ['asian-female-young.target','universal-female-young-averagemuscle-averageweight.target']:
 for line in (SRC/f).read_text().splitlines():
  if line and not line.startswith('#'):
   i,*xyz=line.split();vs[int(i)]+=Vector(map(float,xyz))
# The working study uses CC0 base-compatible facial deltas. Set the flag to 0
# to regenerate the prior baseline for fixed-view comparison.
if os.environ.get('QINGLI_FACE_EXPERIMENT','1')=='1':
 for f,weight in [('l-eye-scale-incr.target',.55),('r-eye-scale-incr.target',.55),
                  ('l-eye-height1-incr.target',.35),('r-eye-height1-incr.target',.35),
                  ('head-oval.target',.25),('chin_chin-width-decr.target',.25),
                  ('nose-width1-decr.target',.35),('nose-width2-decr.target',.30),
                  ('mouth-lowerlip-volume-decr.target',.20)]:
  for line in (SRC/f).read_text().splitlines():
   if line and not line.startswith('#'):
    i,*xyz=line.split();vs[int(i)]+=weight*Vector(map(float,xyz))
bodyids=sorted(groups['body']);ground=min(vs[i].y for i in bodyids);sc=1.68/(max(vs[i].y for i in bodyids)-ground)
def conv(v):return Vector((v.x*sc,-v.z*sc,(v.y-ground)*sc))
coords=[conv(v) for v in vs];joints={g:conv(sum((vs[i] for i in ids),Vector())/len(ids)) for g,ids in groups.items() if g.startswith('joint-')}
# Adapt the freely licensed base into a relaxed standing silhouette.
for side in ['l','r']:
 sh=joints['joint-'+side+'-shoulder'];sign=1 if side=='l' else -1;rot=Matrix.Rotation(sign*.62,3,'Y')
 for i in bodyids:
  v=coords[i]
  if v.x*sign>.14 and v.z>.80:
   w=max(0,min(1,(v.x*sign-.14)/.075));coords[i]=v.lerp(sh+rot@(v-sh),w)

def mat(name,color,rough=.5,metal=0,alpha=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,alpha);n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=metal
 if 'Subsurface Weight' in n.inputs and name=='Skin study':n.inputs['Subsurface Weight'].default_value=.08
 if alpha<1:n.inputs['Alpha'].default_value=alpha;m.surface_render_method='DITHERED' if hasattr(m,'surface_render_method') else None
 return m
skin=mat('Skin study',(.72,.48,.43),.48);hair=mat('Silver blue hair',(.55,.63,.74),.37);hair_light=mat('Silver hair highlights',(.77,.82,.89),.32);silk=mat('Ivory silk',(.83,.88,.96),.42);silk2=mat('Periwinkle silk',(.43,.55,.74),.48);dark=mat('Deep blue lining',(.08,.14,.27),.54);gold=mat('Warm gold metal',(.66,.43,.16),.28,.8);gem=mat('Blue gemstone',(.04,.20,.49),.18,.34);eye_white=mat('Eye sclera',(.77,.78,.79),.28);iris=mat('Blue irises',(.07,.25,.48),.25);lip=mat('Lips study',(.50,.20,.20),.55)

def mesh(name,vertices,polygons,material):
 m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],polygons);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(material)
 for f in m.polygons:f.use_smooth=True
 uv=m.uv_layers.new(name='StudyUV')
 for f in m.polygons:
  for li in f.loop_indices:
   co=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(.5+math.atan2(co.x,-co.y)/(2*math.pi),co.z/1.8)
 return o
remap={v:i for i,v in enumerate(bodyids)};body=mesh('Qingli female base — CC0 study',[coords[i] for i in bodyids],[[remap[i] for i in f] for f in faces],skin)
body['status']='STATIC STUDY — generic CC0 base; likeness, topology, skinning and expressions are not validated'
if os.environ.get('QINGLI_SKIN_EXPERIMENT','1')=='1':
 # Original per-corner CC0 UVs avoid the cylindrical study map's seams and
 # distortion. This is a generic skin texture, not a likeness of the design.
 uv=body.data.uv_layers.active
 for polygon,indices in zip(body.data.polygons,face_uvs):
  for loop_index,uv_index in zip(polygon.loop_indices,indices):uv.data[loop_index].uv=uvs[uv_index]
 texture=skin.node_tree.nodes.new('ShaderNodeTexImage')
 texture.image=bpy.data.images.load(str(SRC/'young_asian_female_diffuse.png'),check_existing=True)
 texture.image.pack()
 skin.node_tree.links.new(texture.outputs['Color'],skin.node_tree.nodes['Principled BSDF'].inputs['Base Color'])

def sphere(name,loc,scale,material,segments=24,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return o

def line(name,points,radius,material):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=radius;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
# Genuine eyeball/iris meshes rather than face image projections.
for side in ['l','r']:
 e=joints['joint-'+side+'-eye'];sphere('Eyeball '+side,e,(.014,.014,.012),eye_white);sphere('Iris '+side,e+Vector((0,-.012,0)),(.006,.0025,.006),iris,20,12)
# Extract a fitted garment shell from the torso surface and offset it outward.
# The original body remains intact beneath it; this is an editable first fitting.
selected=[]
for poly in body.data.polygons:
 center=sum((body.data.vertices[i].co for i in poly.vertices),Vector())/len(poly.vertices)
 if .85<center.z<1.33 and abs(center.x)<.145:selected.append(list(poly.vertices))
used=sorted({v for face in selected for v in face});lookup={old:i for i,old in enumerate(used)}
clothverts=[body.data.vertices[i].co+body.data.vertices[i].normal*.012 for i in used]
bodice=mesh('Fitted bodice shell',clothverts,[[lookup[i] for i in f] for f in selected],silk2);solid=bodice.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.003
# Independent skirt panels form a slit front and a layered back drape.
def skirt(name,a0,a1,material,extension=0):
 rows=20;cols=10;v=[];f=[]
 for i in range(rows+1):
  u=i/rows;z=.88-u*(.81+extension);rx=.17+u*(.30+extension*.25);ry=.17+u*(.16+extension*.20)
  for j in range(cols+1):
   q=j/cols;a=a0+(a1-a0)*q;fold=.012*math.sin(q*math.pi*4+i*.25)*u;v.append(((rx+fold)*math.sin(a),-.02-(ry+fold)*math.cos(a),z+.018*math.sin(q*math.pi*3)*u))
 for i in range(rows):
  for j in range(cols):a=i*(cols+1)+j;f.append((a,a+cols+1,a+cols+2,a+1))
 o=mesh(name,v,f,material);mod=o.modifiers.new('Cloth thickness','SOLIDIFY');mod.thickness=.003
 # The hem is real geometry and does not stand in for embroidery.
 line(name+' hem',[v[rows*(cols+1)+j] for j in range(cols+1)],.002,gold)
for k in range(12):
 a0=.34+k*((2*math.pi-.68)/12);a1=.34+(k+.94)*((2*math.pi-.68)/12);skirt(f'Skirt panel {k+1:02}',a0,a1,[silk,silk2,silk,dark][k%4],.025 if k in (3,4,7,8) else 0)
skirt('Front short layered apron',-.36,.36,silk2,-.38)
# Detached shoulder drapes and narrow ribbons.
for s in (-1,1):
 for j in range(3):
  x=s*(.17+j*.022);pts=[(x,-.005,1.32),(x+s*.07,.015,1.17),(x+s*.15,.045,.91),(x+s*(.17+j*.025),.09,.66)]
  line(f'Shoulder ribbon {s} {j}',pts,.007 if j==0 else .004,[silk,silk2,gold][j])
# Silver hair cap plus tapered volume locks, as geometry.
sphere('Hair cap',(0,.018,1.625),(.092,.089,.095),hair,32,20)
def lock(name,points,width,material):
 sides=8;v=[];f=[]
 for i,p in enumerate(points):
  t=i/(len(points)-1);r=width*(1-.88*t)
  for j in range(sides):
   a=2*math.pi*j/sides;v.append((p[0]+r*math.cos(a),p[1]+r*.45*math.sin(a),p[2]))
 for i in range(len(points)-1):
  for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;f.append((a,b,b+sides,a+sides))
 return mesh(name,v,f,material)
for i in range(17):
 x=(i-8)*.0105;y=.042+.008*(i%4);length=.75+(.05*(i%5));points=[]
 for j in range(17):
  t=j/16;points.append((x*(1+.95*t)+.012*math.sin(t*6+i),y+.05*t+.009*math.sin(t*4+i),1.68-length*t))
 lock(f'Back silver hair {i:02}',points,.013,hair_light if i%4==0 else hair)
for side in (-1,1):
 for i in range(3):
  x=side*(.040+i*.018);points=[(x,-.075,1.70),(x*1.5,-.11,1.61),(x*1.55,-.12,1.51),(x*1.6,-.09,1.38),(x*1.8,-.065,1.27)]
  lock(f'Face framing lock {side} {i}',points,.011,hair_light if i==0 else hair)
# Swept top locks establish a hairline volume, not individual strands.
for side in (-1,1):
 for i in range(4):
  x=side*(.012+i*.014);pts=[(x,-.005,1.724),(side*(.025+i*.012),-.055,1.708),(side*(.055+i*.012),-.087,1.68),(side*(.083+i*.01),-.09,1.60),(side*(.09+i*.01),-.085,1.51)]
  lock(f'Swept hairline {side} {i}',pts,.010,hair_light if i%3==0 else hair)
# Floral/gem focal motifs use separate solid components and are intentionally incomplete studies.
def flower(center,scale,name):
 x,y,z=center
 for i in range(6):
  a=i*2*math.pi/6;o=sphere(f'{name} petal {i}',(x+math.sin(a)*scale*.55,y,z+math.cos(a)*scale*.55),(scale*.28,scale*.12,scale*.62),silk,16,8);o.rotation_euler[1]=a
 sphere(name+' blue core',(x,y-.005,z),(scale*.28,scale*.18,scale*.28),gem,16,8)
for side in (-1,1):
 flower((side*.074,-.045,1.69),.024,f'Hair flower {side}');line(f'Crown arc {side}',[(side*.025,-.025,1.70),(side*.075,-.005,1.75),(side*.105,.015,1.73)],.003,gold)
 e=joints['joint-'+('l' if side==1 else 'r')+'-eye'];line(f'Earring {side}',[(side*.092,-.02,1.56),(side*.098,-.025,1.48)],.0017,gold);sphere(f'Earring gem {side}',(side*.098,-.025,1.47),(.008,.005,.012),gem,16,8)
flower((0,-.185,1.15),.025,'Bodice flower');sphere('Waist blue gem',(0,-.165,.86),(.022,.009,.033),gem,20,10)
for s in (-1,1):line(f'Waist trim {s}',[(0,-.165,.87),(s*.05,-.15,.90),(s*.10,-.10,.88)],.003,gold)
# Incremental geometry study. Kept separate so the reference baseline and the
# changes can be inspected and reverted independently.
exec(compile((ROOT/'tools/refine_qingli_study.py').read_text(), 'refine_qingli_study.py', 'exec'))
if os.environ.get('QINGLI_HAIR_CC0_EXPERIMENT','1')=='1':
 exec(compile((ROOT/'tools/candidate_qingli_cc0_hair.py').read_text(), 'candidate_qingli_cc0_hair.py', 'exec'))
# Make all curves into exportable, editable geometry.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='CURVE':o.select_set(True)
if bpy.context.selected_objects:
 bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o['quality_status']='WORK IN PROGRESS; NOT ART APPROVED; NO RIG'
# No external files in the editable study.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Qingli_static_study.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'Qingli_static_study.glb'),export_format='GLB',export_animations=False)
# All images below are actual renders of the same geometry under fixed light.
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Study world');scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=False;scene.render.resolution_x=560;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.world.color=(.08,.08,.08)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.0;scene.camera=cam
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((2,-3,4),380,4),((-2,-1,2.4),180,3),((0,3,3),260,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;aim(o,(0,0,1))
for name,loc in [('front',(0,-4,1.02)),('side',(4,0,1.02)),('back',(0,4,1.02)),('angle',(3,-3,1.18))]:
 cam.location=loc;aim(cam,(0,0,.9));scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=(0,-3,1.6);cam.data.ortho_scale=.32;aim(cam,(0,-.04,1.57));scene.render.resolution_x=700;scene.render.resolution_y=700;scene.render.filepath=str(OUT/'face.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-4,1.02);cam.data.ortho_scale=2.0;aim(cam,(0,0,.9));scene.render.resolution_x=560;scene.render.resolution_y=800;scene.render.filepath='//qingli-render.png';bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Qingli_static_study.blend'));print('STATIC_STUDY_FINISHED',OUT)
