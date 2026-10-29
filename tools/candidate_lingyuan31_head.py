"""Reference-led local head candidate. Review before promotion; no canonical writes.
The cage and all existing morph keys receive the same continuous anatomy mapping.
This is a procedural structure candidate, not a claim of completed hand sculpture.
"""
from pathlib import Path
import bpy,bmesh,math,json,os
from mathutils import Vector
R=Path(__file__).resolve().parents[1];OUT=Path('/tmp/lingyuan31-head');OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.environ.get('LING31_SOURCE_BLEND',str(R/'dist/Lingyuan_working.blend')));bpy.context.preferences.filepaths.save_version=0
head=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];mesh=head.data
if head.get('reference31'):raise RuntimeError('Do not apply this candidate twice')
before=[v.co.copy() for v in mesh.vertices]
def fall(x,r):return math.exp(-(x/r)**2)
def fit(p):
 q=p.copy()
 if p.z<1.635 or p.y>.055:return q
 front=max(0,min(1,(.055-p.y)/.085))
 # Mandibular plane, chin and zygomatic contour remain separate from the cranium.
 jaw=fall(p.z-1.687,.035)*front
 q.x*=1-.20*jaw
 q.z-=.0025*fall(p.z-1.654,.019)*front
 cheek=fall(p.z-1.737,.025)*fall(abs(p.x)-.057,.028)*front
 q.y+=.0015*cheek
 # A straight nasal wedge with independent alar width, tip and radix volumes.
 ala=fall(p.z-1.730,.020)*fall(p.x,.022)*front
 q.x-=p.x*.23*ala
 q.y+=.0020*fall(p.z-1.726,.010)*fall(p.x,.014)*front
 q.y-=.0024*fall(p.z-1.755,.024)*fall(p.x,.008)*front
 # Cupid bow and lower vermilion: control volume rather than flattening the face.
 mouth=fall(p.z-1.699,.013)*fall(p.x,.026)*front
 q.z+=(1.699-p.z)*.17*mouth
 q.y+=.0022*mouth
 # Outer canthus inclines subtly; eyeball diameter is unchanged.
 for side in [-1,1]:
  dx=p.x-side*.0306;orb=fall(dx,.018)*fall(p.z-1.774,.018)*front
  q.z+=side*dx*.19*orb
  hood=fall(p.x-side*.031,.020)*fall(p.z-1.789,.007)*front
  q.y-=.0016*hood
  q.z-=.0012*hood
 return q
for k in mesh.shape_keys.key_blocks:
 for v in k.data:v.co=fit(v.co)
for v,p in zip(mesh.vertices,before):v.co=fit(p)
mesh.update()
# Keep eye surrounds and the blink meshes coherent with the edited orbital rim.
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob==head:continue
 if ob.name.startswith(('lingyuan upper lash','Eye microgeometry')):
  inv=ob.matrix_world.inverted();original=[v.co.copy() for v in ob.data.vertices]
  if ob.data.shape_keys:
   for k in ob.data.shape_keys.key_blocks:
    for v in k.data:v.co=inv@fit(ob.matrix_world@v.co)
  for v,p in zip(ob.data.vertices,original):v.co=inv@fit(ob.matrix_world@p)
# Replace the raised thin eyebrow arc with a heavier, tapered brow following the rim.
brow=bpy.data.objects['Eyebrow fibers']
for v in brow.data.vertices:
 t=max(0,min(1,(abs(v.co.x)-.014)/.036));old=1.793+.004*math.sin(math.pi*t)-.002*t
 center=1.788+.012*t-.003*t*t
 v.co.z=center+(v.co.z-old)*1.35;v.co.y=fit(v.co).y-.0003
brow.data.update()
# Curated major front locks replace the old evenly spaced narrow comb. Preserve
# the existing rear/side hair and weights; all three LODs use the same groom design.
def bezier(points,t):return points[0]*(1-t)**3+points[1]*3*t*(1-t)**2+points[2]*3*t*t*(1-t)+points[3]*t**3
groom=[]
for lod,n,sections,sides in ([(1,13,9,6)] if os.environ.get('LING31_GROOM')=='1' else []):
 hair=bpy.data.objects[f'Hair_Lod{lod}'];old_count=len(hair.data.vertices);stride=(sections+1)*sides
 bm=bmesh.new();bm.from_mesh(hair.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=list(bm.verts)[:2*n*stride],context='VERTS');bm.to_mesh(hair.data);bm.free()
 vertices=[];polys=[];indices=[];steps=[24,16,10][lod];ring_sides=[8,6,5][lod]
 # x end, z end, root x, width: asymmetric swept fringe, not mirror clones.
 design=[(-.021,1.824,-.002,.010),(-.041,1.799,-.006,.012),(-.065,1.771,-.012,.012),(-.084,1.735,-.021,.010),(-.095,1.706,-.029,.007),(.036,1.817,.008,.012),(.059,1.790,.018,.014),(.079,1.753,.029,.012),(.096,1.715,.040,.008)]
 for k,(endx,endz,rootx,width) in enumerate(design):
  side=1 if endx>0 else -1;points=list(map(Vector,[(rootx,-.018,1.903),(.35*endx,-.071,1.902),(.84*endx,-.118,1.856),(endx,-.103 if abs(endx)<.075 else -.070,endz)]));start=len(vertices)
  for i in range(steps+1):
   t=i/steps;p=bezier(points,t);tangent=(bezier(points,min(1,t+.005))-bezier(points,max(0,t-.005))).normalized();axis=tangent.cross(Vector((0,1,0))).normalized();normal=tangent.cross(axis).normalized();w=width*(.4+.6*math.sin(math.pi*t)**.6)*(1-.985*t**3)
   for j in range(ring_sides):a=j/ring_sides*math.tau;vertices.append(tuple(p+axis*math.cos(a)*w+normal*math.sin(a)*w*.34))
  for i in range(steps):
   for j in range(ring_sides):a=start+i*ring_sides+j;b=start+i*ring_sides+(j+1)%ring_sides;polys.append((a,b,b+ring_sides,a+ring_sides));indices.append(k%3)
 me=bpy.data.meshes.new('Reference swept fringe');me.from_pydata(vertices,[],polys);me.update();ob=bpy.data.objects.new('Reference fringe join',me);bpy.context.collection.objects.link(ob)
 for m in hair.data.materials:me.materials.append(m)
 for p,mi in zip(me.polygons,indices):p.material_index=mi;p.use_smooth=True
 vg=ob.vertex_groups.new(name='head');vg.add(list(range(len(vertices))),1,'REPLACE')
 bpy.ops.object.select_all(action='DESELECT');hair.hide_set(False);ob.select_set(True);hair.select_set(True);bpy.context.view_layer.objects.active=hair;bpy.ops.object.join();hair.hide_set(lod!=0);hair.hide_render=lod!=0
 groom.append({'lod':lod,'oldVertices':old_count,'newVertices':len(hair.data.vertices),'newMajorLocks':len(design)})
head['reference31']='Original portrait and front/side detail; art candidate, no automatic likeness approval'
report={'source':'650edf1','references':['reference/1-1000069993.jpg','reference/detail/4-mmexport1793091788549.jpg'],'baseVertexCount':len(mesh.vertices),'existingKeys':[k.name for k in mesh.shape_keys.key_blocks],'mappedVertices':sum((v.co-p).length>1e-6 for v,p in zip(mesh.vertices,before)),'maxDisplacementMeters':max((v.co-p).length for v,p in zip(mesh.vertices,before)),'eyeDiameterChanged':False,'groom':groom,'artAccepted':False}
(OUT/'structure.json').write_text(json.dumps(report,indent=2))
bpy.context.scene.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'candidate.blend'));print('STRUCTURAL_CANDIDATE_READY',flush=True)
