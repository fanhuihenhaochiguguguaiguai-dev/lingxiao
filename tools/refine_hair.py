"""Reference-driven hair/neck pass. Candidate is saved separately for review."""
import bpy,bmesh,math,random,sys,os
from mathutils import Vector
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1];mode=os.environ.get('LING_PASS','representative')
bpy.ops.wm.open_mainfile(filepath=os.environ.get('LING_SOURCE_BLEND',str(R/'dist/Lingyuan_working.blend')));rig=bpy.data.objects['Lingyuan_Rig'];random.seed(707)
if bpy.data.objects.get('Hair_Lod0'):raise SystemExit('Already refined: do not apply twice')
# Representative pass touches LOD0 only; subsequent LODs change only after review.
lods=[0] if mode=='representative' else [0,1,2]
for lod in lods:
 o=bpy.data.objects[f'Lingyuan_LOD{lod}'];me=o.data;p=list(range(len(me.vertices)))
 def root(i):
  while p[i]!=i:p[i]=p[p[i]];i=p[i]
  return i
 for e in me.edges:
  a,b=e.vertices;p[root(b)]=root(a)
 components=defaultdict(list)
 for v in me.vertices:components[root(v.index)].append(v)
 remove=set();parts={'fringe':0,'old_neck':0}
 for vs in components.values():
  lo=Vector((min(v.co.x for v in vs),min(v.co.y for v in vs),min(v.co.z for v in vs)));hi=Vector((max(v.co.x for v in vs),max(v.co.y for v in vs),max(v.co.z for v in vs)))
  # Old segmented fringe: independent pieces on forehead, not skin or scalp.
  fringe=(len(vs)>=20 and lo.z>1.75 and hi.z>1.875 and lo.y<-.095 and hi.y<.015 and lo.x>-.13 and hi.x<.13)
  neck=(len(vs)>60 and 1.47<lo.z<1.50 and 1.64<hi.z<1.66 and lo.x>-.055 and hi.x<.055 and lo.y>-.055 and hi.y<.07)
  if fringe or neck:
   remove.update(v.index for v in vs);parts['fringe' if fringe else 'old_neck']+=1
 if parts['fringe']<5 or parts['old_neck']!=1:raise RuntimeError(f'Unexpected component layout LOD {lod}: {parts}; stopped before editing')
 bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(me);bm.free();me.update();print('CLEAN',lod,parts,len(remove),flush=True)
# old rigid long strands removed from candidate, not the source master.
old=[o for o in bpy.data.objects if o.name.startswith('Long hair ')]
if len(old)!=28:raise RuntimeError('Unexpected long-hair baseline; refusing to replace')
for o in old:bpy.data.objects.remove(o,do_unlink=True)
materials=[]
for name,col in [('hair deep',(.015,.011,.015)),('hair dark brown',(.024,.017,.017)),('hair blue-black',(.014,.020,.027))]:
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.38;p.inputs['Metallic'].default_value=.03;materials.append(m)

def bezier(p0,p1,p2,p3,t):return p0*(1-t)**3+p1*(3*(1-t)**2*t)+p2*(3*(1-t)*t*t)+p3*t**3

def create_hair(lod,front_n,back_n):
 random.seed(707);v=[];f=[];w=[];mi=[];sections=12 if lod==0 else 9 if lod==1 else 6;sides=6 if lod<2 else 5
 def lock(pts,width,mat,side,back=False):
  p0,p1,p2,p3=map(Vector,pts);start=len(v)
  for j in range(sections+1):
   t=j/sections;p=bezier(p0,p1,p2,p3,t);d=(bezier(p0,p1,p2,p3,min(1,t+.01))-bezier(p0,p1,p2,p3,max(0,t-.01))).normalized();a=d.cross(Vector((0,1,0))).normalized()
   if a.length<.1:a=Vector((1,0,0))
   b=d.cross(a).normalized();shape=max(.03,math.sin(math.pi*min(.97,.10+.87*t))**.48)*(1-.68*t)
   if back:
    h=max(0,1-t*3);second=max(0,min(1,(t-.22)*2.6));third=max(0,min(1,(t-.55)*2.2));weights={'head':h,'hair01.'+side:(1-h)*(1-third),'hair02.'+side:(1-h)*third}
   else:weights={'head':1.}
   for k in range(sides):
    a0=2*math.pi*k/sides;v.append(tuple(p+width*shape*(a*math.cos(a0)+b*.32*math.sin(a0))));w.append(weights)
  for j in range(sections):
   for k in range(sides):f.append((start+j*sides+k,start+j*sides+(k+1)%sides,start+(j+1)*sides+(k+1)%sides,start+(j+1)*sides+k));mi.append(mat)
 # Center-parted, irregular overlapping locks. Outside tips sit beside the eyes.
 for s,side in [(-1,'L'),(1,'R')]:
  for i in range(front_n):
   u=i/max(1,front_n-1);rnd=random.uniform(-.004,.004);startx=s*(.003+u*.035);endx=s*(.025+u*.064+rnd);endz=1.842-.045*u-random.random()*.008
   if u>.75:endz-=.025*(u-.75)/.25
   lock([(startx,-.018-u*.016,1.897+random.uniform(-.004,.002)),(s*(.008+u*.024),-.065,1.89),(endx*.75,-.103-.002*u,1.858),(endx,-.098+.018*u,endz)],.0038+random.random()*.0022,i%3,side)
 # Side locks bridge the front parting and the rear hair, covering exposed scalp.
 for s,side in [(-1,'L'),(1,'R')]:
  for i in range(front_n*2):
   u=i/max(1,front_n*2-1); yy=-.095+.21*u;zz=1.73+.05*u
   lock([(s*.035,yy*.35,1.897),(s*.083,yy*.55,1.89),(s*.105,yy,1.81),(s*(.10+.006*u),yy+.012,zz)],.0055+random.random()*.002,i%3,side)
 # Layered swept locks behind both shoulders; tapered 3D profiles and weighted segments.
 for i in range(back_n):
  s=-1 if i%2==0 else 1;side='L' if s<0 else 'R';u=(i//2)/max(1,(back_n//2)-1);x=s*(.015+.065*u);bend=s*(.012+.022*math.sin(i*1.73));endz=1.17+.18*random.random();depth=.09+.075*u
  lock([(x*.45,.06,1.89),(x,.15,1.77),(x*1.18+bend,.18+depth*.45,1.48),(x*1.40+bend,.21+depth*.55,endz)],.0035+random.random()*.0035,i%3,side,True)
 me=bpy.data.meshes.new(f'Layered hair geometry LOD{lod}');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(f'Hair_Lod{lod}',me);bpy.context.scene.collection.objects.link(o)
 for material in materials:me.materials.append(material)
 for poly,index in zip(me.polygons,mi):poly.material_index=index;poly.use_smooth=True
 groups={n:o.vertex_groups.new(name=n) for n in ['head','hair01.L','hair02.L','hair01.R','hair02.R']}
 for i,weights in enumerate(w):
  for n,weight in weights.items():
   if weight>1e-6:groups[n].add([i],weight,'REPLACE')
 o.parent=rig;mod=o.modifiers.new('Hair skin','ARMATURE');mod.object=rig;o['hair_refinement']='tapered layered mesh bound to hair rig';o['lod']=lod
 o.hide_set(lod!=0);o.hide_render=(lod!=0)
 print('HAIR',lod,len(v),len(f),flush=True)
for lod in lods:create_hair(lod,*[(20,64),(13,36),(8,18)][lod])

# Replace the previous solid eyebrow strips with fine, curved surface strokes.
from mathutils.bvhtree import BVHTree
head=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();bv=BVHTree.FromObject(head.evaluated_get(deps),deps)
old_brows=[o for o in bpy.data.objects if o.name=='Eyebrow' or o.name.startswith('Eyebrow.') ]
if len(old_brows)!=2:raise RuntimeError('Unexpected brow baseline; stopped')
for o in old_brows:bpy.data.objects.remove(o,do_unlink=True)
vv=[];ff=[];random.seed(1091)
for side in [-1,1]:
 for i in range(64):
  t=(i+.4)/64;x0=side*(.014+.036*t);z0=1.793+.004*math.sin(math.pi*t)-.002*t;length=(.0025+.0038*math.sin(math.pi*t)**.7)*random.uniform(.7,1.1)
  for j in range(4):
   q=j/3;x=x0+side*(q*.0011);z=z0+(q-.45)*length;hit,normal,_,_=bv.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
   y=hit.y-.0008 if hit else -.081;wid=.00033*math.sin(math.pi*(.05+.9*q))
   vv.extend([(x-wid,y,z),(x+wid,y,z)])
  base=len(vv)-8
  for j in range(3):ff.append((base+2*j,base+2*j+1,base+2*j+3,base+2*j+2))
me=bpy.data.meshes.new('Fine eyebrow strands');me.from_pydata(vv,[],ff);me.update();o=bpy.data.objects.new('Eyebrow fibers',me);bpy.context.scene.collection.objects.link(o);me.materials.append(materials[0]);o.parent=rig;group=o.vertex_groups.new(name='head');group.add(list(range(len(vv))),1,'REPLACE');mod=o.modifiers.new('Brow skin','ARMATURE');mod.object=rig
# Candidate persisted separately; original master remains untouched until reviewed.
bpy.ops.wm.save_as_mainfile(filepath='/tmp/Lingyuan_hair_candidate.blend')
# Consistent inspection lighting and camera for real render comparison.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-1.8,1.76));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.4;scene.camera=cam
for loc,power,size in [((1,-2,3),100,2),((-1,-2,2),45,2),((0,1,2),110,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.75))
for name,loc in [('front',(0,-1.8,1.76)),('side',(-1.8,0,1.76))]:
 cam.location=loc;aim(cam,(0,0,1.76));scene.render.filepath=f'/tmp/ling-hair-{name}.png';bpy.ops.render.render(write_still=True)
