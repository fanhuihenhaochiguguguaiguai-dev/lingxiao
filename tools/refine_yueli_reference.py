"""Local reference-proportion and fitted clothing experiment on the existing bound model.
Preserves UVs, thickness, bones and all untouched meshes. Review candidate before promotion.
"""
from pathlib import Path
from collections import defaultdict
import bpy,bmesh,math,json,os
from mathutils import Vector,kdtree
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];OUT=Path('/tmp/moonfall-character');OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.environ.get('YUELI_REFERENCE_SOURCE_BLEND',str(R/'characters/qingli/Yueli_working.blend')));bpy.context.preferences.filepaths.save_version=0
if any(o.name.startswith('Yueli reference ') for o in bpy.context.scene.objects):raise RuntimeError('Reference adjustment already applied; select a pre-refinement source for this one-time migration')
body=bpy.data.objects['Qingli female base — CC0 study'];rig=bpy.data.objects['Yueli_Rig'];eyes=[bpy.data.objects['Eyeball '+s].location.copy() for s in ['l','r']]
# A coherent local deformation of orbit, nasal wedge, lips and jaw. All face keys
# use the same mapping so the saved eyelid delta remains tied to the new shape.
def g(v,c,rx,rz):return math.exp(-((v.x-c.x)/rx)**2-((v.z-c.z)/rz)**2)
def deform(p):
 q=p.copy()
 if p.z<1.43 or p.y>-.025:return q
 front=max(0,min(1,(-p.y-.025)/.065));vertical=max(0,min(1,(p.z-1.43)/.035));front*=vertical*vertical*(3-2*vertical)
 jaw=math.exp(-((p.z-1.477)/.040)**2)*front;q.x*=1-.11*jaw
 q.z+=.009*math.exp(-((p.z-1.455)/.025)**4)*front
 for e in eyes:
  w=g(p,e,.039,.039)*front;q.x+=(p.x-e.x)*.27*w;q.z+=(p.z-e.z)*.20*w
 nose=math.exp(-(p.x/.032)**2-((p.z-1.529)/.030)**2)*front;q.x-=p.x*.20*nose;q.y+=.0035*nose
 mouth=math.exp(-(p.x/.027)**4-((p.z-1.494)/.014)**4)*front;q.x-=p.x*.08*mouth;q.y-=.0010*mouth
 return q
old=[v.co.copy() for v in body.data.vertices]
for key in body.data.shape_keys.key_blocks:
 for v in key.data:v.co=deform(v.co)
for v,p in zip(body.data.vertices,old):v.co=deform(p)
body.data.update()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob==body:continue
 if ob.name.startswith(('Eyeball','Iris','Pupil','yueli upper lash','Natural eyebrow')) or 'brow' in ob.name.lower():
  inv=ob.matrix_world.inverted()
  if ob.data.shape_keys:
   mesh_original=[v.co.copy() for v in ob.data.vertices]
   for key in ob.data.shape_keys.key_blocks:
    for v in key.data:v.co=inv@deform(ob.matrix_world@v.co)
   for v,p in zip(ob.data.vertices,mesh_original):v.co=inv@deform(ob.matrix_world@p)
  else:
   for v in ob.data.vertices:v.co=inv@deform(ob.matrix_world@v.co)
# Body BVH is used to fit roots/ornaments to real surfaces rather than floating coordinates.
bpy.context.view_layer.update();bv=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
def front(x,z,offset=.006):
 hit,normal,_,_=bv.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
 return hit.y-offset if hit is not None else -.14

def material(n,c,rough,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
hair=material('Yueli silver lavender locks',(.57,.61,.73),.32);silver=material('Yueli fine hair sheen',(.72,.77,.87),.28);gold=bpy.data.materials['Warm gold metal'];ivory=bpy.data.materials['Ivory silk'];gem=bpy.data.materials['Blue gemstone']
# Replace only the unapproved rigid front strips. Back-hair volume is retained.
for ob in list(bpy.context.scene.objects):
 if ob.name.startswith(('Fringe sweep','Tapered side lock','Swept hairline','Face framing lock')):bpy.data.objects.remove(ob,do_unlink=True)
buckets=defaultdict(lambda:[[],[]])
def append_mesh(key,verts,faces):
 v,f=buckets[key];start=len(v);v.extend(verts);f.extend(tuple(start+i for i in face) for face in faces)
def bezier(points,t):
 if len(points)==4:return points[0]*(1-t)**3+points[1]*3*t*(1-t)**2+points[2]*3*t*t*(1-t)+points[3]*t**3
 return points[0].lerp(points[-1],t)
def lock(points,width,key,depth=.34):
 pts=[Vector(p) for p in points];centers=[];rows=28;sides=8;verts=[];faces=[]
 for i in range(rows+1):
  t=i/rows;p=bezier(pts,t)
  if p.z>1.44:
   hit,normal,_,_=bv.ray_cast(Vector((p.x,-1,p.z)),Vector((0,1,0)))
   if hit is not None:p.y=min(p.y,hit.y-.004)
  centers.append(p)
 for i,p in enumerate(centers):
  t=i/rows;tangent=(centers[min(i+1,rows)]-centers[max(i-1,0)]).normalized();axis=tangent.cross(Vector((0,1,0))).normalized();normal=tangent.cross(axis).normalized();w=width*(.62+.38*math.sin(math.pi*t))*(1-.985*t**5)
  for k in range(sides):a=k*2*math.pi/sides;verts.append(tuple(p+axis*math.cos(a)*w+normal*math.sin(a)*w*depth))
 for i in range(rows):
  for k in range(sides):a=i*sides+k;b=i*sides+(k+1)%sides;faces.append((a,b,b+sides,a+sides))
 append_mesh(key,verts,faces)
for side in [-1,1]:
 for k in range(7):
  root=side*(.006+k*.004);end=side*(.071+k*.005);pts=[(root,-.034,1.682-k*.0007),(side*(.020+k*.007),-.090,1.674),(side*(.061+k*.006),-.146,1.620),(end,-.115,1.583-k*.005)]
  lock(pts,.0068+k*.0003,'hair' if k%3 else 'sheen')
  # Thin swept fibers reinforce the same volume, not a new hair identity.
  offset=[(x+side*.002,y-.001,z+.001) for x,y,z in pts];lock(offset,.0008,'sheen',.8)
 for k in range(3):
  x=side*(.079+k*.010);lock([(x,.002,1.664),(x*1.15,-.085,1.57),(x*1.06,-.075,1.36),(x*1.14,-.032,1.24-k*.025)],.0074,'hair' if k else 'sheen')
# Clip the fitted shell at real seam planes. Face-center selection left sawtooth
# boundaries under the sharper web lighting, despite looking acceptable in soft light.
source=bpy.data.objects['Fitted bodice shell'];panel=bmesh.new();panel.from_mesh(source.data)
for v in panel.verts:v.co+=v.normal*.004
for point,normal in [((0,0,.89),(0,0,-1)),((0,0,1.315),(0,0,1)),((.135,0,0),(1,0,0)),((-.135,0,0),(-1,0,0)),((0,-.025,0),(0,1,0))]:
 bmesh.ops.bisect_plane(panel,geom=list(panel.verts)+list(panel.edges)+list(panel.faces),plane_co=point,plane_no=normal,clear_outer=True,dist=1e-6)
panel.normal_update();panel.verts.index_update();verts=[tuple(v.co) for v in panel.verts];n=len(verts)
verts.extend(tuple(v.co-v.normal*.0015) for v in panel.verts);faces=[tuple(v.index for v in f.verts) for f in panel.faces];faces.extend(tuple(v.index+n for v in reversed(f.verts)) for f in panel.faces)
for e in panel.edges:
 if e.is_boundary:a,b=(v.index for v in e.verts);faces.append((a,b,b+n,a+n))
append_mesh('ivory',verts,faces);panel.free()
# Real filigree is surface-fitted; repeated metal forms are batched by material.
def tube(points,r,key):
 pts=[Vector(p) for p in points];verts=[];faces=[];sides=5
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();axis=tangent.cross(Vector((0,1,0))).normalized();b=tangent.cross(axis).normalized()
  for k in range(sides):a=k*2*math.pi/sides;verts.append(tuple(p+axis*math.cos(a)*r+b*math.sin(a)*r))
 for i in range(len(pts)-1):
  for k in range(sides):a=i*sides+k;b=i*sides+(k+1)%sides;faces.append((a,b,b+sides,a+sides))
 append_mesh(key,verts,faces)
for side in [-1,1]:
 points=[]
 for i in range(36):t=i/35;z=.90+t*.40;x=side*(.045+.048*math.sin(t*math.pi*.8));points.append((x,front(x,z,.016),z))
 tube(points,.0017,'gold')
 for j in range(5):
  z=.94+j*.062;x=side*(.052+.042*math.sin(j*.48));pts=[]
  for i in range(20):a=i/19*2*math.pi;xx=x+side*.015*math.sin(a);zz=z+.023*(1-math.cos(a));pts.append((xx,front(xx,zz,.017),zz))
  tube(pts,.0010,'gold')
for z,r in [(1.18,.030),(.90,.027)]:
 for k in range(6):
  a=k*math.pi/3;pts=[]
  for i in range(24):t=i/23;d=math.sin(math.pi*t)*r;cross=math.sin(t*2*math.pi)*r*.28;x=math.sin(a)*d+math.cos(a)*cross;zz=z+math.cos(a)*d-math.sin(a)*cross;pts.append((x,front(x,zz,.020),zz))
  tube(pts,.0014,'gold')
# Replace only the unapproved spherical blossom petals with cupped, pointed surfaces.
flower_mat=material('Yueli lavender crystal petals',(.58,.66,.86),.24,.08)
for ob in list(bpy.context.scene.objects):
 if not ob.name.startswith('Hair flower ') or ' petal ' not in ob.name:continue
 vertices=[];faces=[];rows=10;cols=6;oldmesh=ob.data
 for i in range(rows+1):
  t=i/rows
  for j in range(cols+1):
   u=j/cols*2-1;vertices.append((u*.007*math.sin(math.pi*t)**.7,-.0015-.003*math.sin(math.pi*t)+.001*u*u,.027*t-.013))
 for i in range(rows):
  for j in range(cols):a=i*(cols+1)+j;faces.append((a,a+1,a+cols+2,a+cols+1))
 me=bpy.data.meshes.new('Pointed blossom petal');me.from_pydata(vertices,[],faces);me.update();ob.data=me;me.materials.append(flower_mat)
 for poly in me.polygons:poly.use_smooth=True
 for vg in list(ob.vertex_groups):ob.vertex_groups.remove(vg)
 vg=ob.vertex_groups.new(name='head');vg.add(list(range(len(vertices))),1,'REPLACE')
 for sign in [-1,1]:
  pts=[]
  for i in range(21):
   t=i/20;local=Vector((sign*.007*math.sin(math.pi*t)**.7,-.0018-.003*math.sin(math.pi*t)+.001,.027*t-.013));pts.append(tuple(ob.matrix_world@local))
  tube(pts,.00032,'headgold')

# Build head and torso batches with weights inherited from the fitted geometry.
kdt=kdtree.KDTree(len(source.data.vertices))
for v in source.data.vertices:kdt.insert(source.matrix_world@v.co,v.index)
kdt.balance()
for key,(verts,faces) in buckets.items():
 me=bpy.data.meshes.new('Yueli reference '+key);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('Yueli reference '+key,me);bpy.context.collection.objects.link(ob);me.materials.append({'hair':hair,'sheen':silver,'ivory':ivory,'gold':gold,'headgold':gold}[key])
 for p in me.polygons:p.use_smooth=True
 groups={}
 def weight(index,n,w):
  if w<=0:return
  if n not in groups:groups[n]=ob.vertex_groups.new(name=n)
  groups[n].add([index],w,'REPLACE')
 for v in me.vertices:
  if key=='headgold':weight(v.index,'head',1)
  elif key in ['hair','sheen']:
   w=max(0,min(1,(1.47-v.co.z)/.22));side='L' if v.co.x>0 else 'R';weight(v.index,'head',1-w);weight(v.index,'hair01.'+side,w)
  else:
   nearest=source.data.vertices[kdt.find(v.co)[1]]
   for g in nearest.groups:weight(v.index,source.vertex_groups[g.group].name,g.weight)
 mod=ob.modifiers.new('Preserved skin','ARMATURE');mod.object=rig;ob.parent=rig
 if key=='ivory':mod=ob.modifiers.new('Overlay thickness','SOLIDIFY');mod.thickness=.002;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
# Material distinction supplements, rather than substitutes for, geometry.
for name in ['Eye sclera','Blue irises','Eye dark pupil candidate']:
 m=bpy.data.materials.get(name)
 if m:
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.17 if 'pupil' in name else .23;p.inputs['Coat Weight'].default_value=.45;p.inputs['Coat Roughness'].default_value=.08
skin=bpy.data.materials['Skin study'].node_tree.nodes['Principled BSDF'];skin.inputs['Subsurface Weight'].default_value=.11;skin.inputs['Roughness'].default_value=.43
bpy.context.scene.frame_set(0);body.data.shape_keys.key_blocks['Blink'].value=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Yueli_working.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in ['MESH','ARMATURE']:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.ops.export_scene.gltf(filepath=str(OUT/'yueli-study.glb'),export_format='GLB',use_selection=True,export_apply=False,export_animations=True,export_animation_mode='NLA_TRACKS')
changed=[(v.co-old[v.index]).length for v in body.data.vertices];(OUT/'geometry.json').write_text(json.dumps({'faceVerticesMoved':sum(d>1e-6 for d in changed),'maximumDisplacement':max(changed),'bonesPreserved':len(rig.data.bones),'newBatches':list(buckets),'source':'characters/qingli/Yueli_working.blend'},indent=2));print('REFERENCE_CANDIDATE_READY',OUT,flush=True)
