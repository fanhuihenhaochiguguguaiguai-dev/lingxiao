"""Continue the unaccepted head candidate, preserving its UV, rig and morphs.
Landmark-supported anatomical corrections and an independently authored curve groom.
This is an editable art candidate, not a claim of likeness acceptance/hand sculpture.
"""
from pathlib import Path
import bpy,bmesh,math,json,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];OUT=Path('/tmp/lingyuan35');OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.environ.get('LING35_SOURCE',str(R/'characters/lingyuan/Lingyuan_head_candidate.blend')))
bpy.context.preferences.filepaths.save_version=0
head=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];rig=bpy.data.objects['Lingyuan_Rig'];mesh=head.data
assert not head.get('refinement35'),'Refusing cumulative application'
def bell(d,r):return math.exp(-(d/r)**2)
# Small support regions, not a global head/eye scale. All existing morph targets
# follow the same spatial correction so blink and jaw targets retain their deltas.
def anatomy(p):
 q=p.copy()
 if p.y>-.025:return q
 frontal=max(0,min(1,(-p.y-.025)/.045))
 for side in [-1,1]:
  x=p.x-side*.0306
  orbit=bell(x,.020)*bell(p.z-1.775,.018)*frontal
  q.x+=side*.0008*orbit
  q.z+=.0015*bell(p.z-1.779,.005)*bell(x,.014)*frontal
  q.z-=.0006*bell(p.z-1.769,.0035)*bell(x,.013)*frontal
  # Defined superior orbital plane, without shrinking the eyeball.
  q.y-=.0013*bell(p.z-1.787,.007)*bell(x,.019)*frontal
  # Distinguish zygomatic plane and hollow from the full lower cheeks.
  q.y+=.0016*bell(p.z-1.720,.020)*bell(p.x-side*.046,.018)*frontal
  q.x-=side*.0011*bell(p.z-1.727,.018)*bell(p.x-side*.067,.015)*frontal
 # Bridge continues to the radix; preserve alae rather than a single nasal cone.
 q.y-=.0016*bell(p.x,.0085)*bell(p.z-1.754,.020)*frontal
 q.y+=.0008*bell(p.x,.012)*bell(p.z-1.726,.005)*frontal
 # Reduce the round protruding lower vermilion and restore a restrained lip line.
 q.y+=.0018*bell(p.x,.019)*bell(p.z-1.695,.006)*frontal
 q.z+=.0006*bell(p.x,.019)*bell(p.z-1.694,.005)*frontal
 q.x*=1+.045*bell(p.x,.022)*bell(p.z-1.665,.015)*frontal
 q.y-=.0010*bell(p.x,.022)*bell(p.z-1.666,.012)*frontal
 return q
old=[v.co.copy() for v in mesh.vertices]
for key in mesh.shape_keys.key_blocks:
 for v in key.data:v.co=anatomy(v.co)
for v,p in zip(mesh.vertices,old):v.co=anatomy(p)
mesh.update()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob==head:continue
 if ob.name.startswith(('lingyuan upper lash','Eye microgeometry')):
  def attach(p):
   w=ob.matrix_world@p;q=anatomy(w);q.y-=.0014;return ob.matrix_world.inverted()@q
  if ob.data.shape_keys:
   for key in ob.data.shape_keys.key_blocks:
    for v in key.data:v.co=attach(v.co)
  for v in ob.data.vertices:v.co=attach(v.co)
 elif ob.name in ('Eye','Eye.001'):
  # Orbital depth, not eye size. Gaze control still operates on the existing nodes.
  ob.location.x+=math.copysign(.0008,ob.location.x);ob.location.y-=.0014
brow=bpy.data.objects['Eyebrow fibers']
for v in brow.data.vertices:
 t=max(0,min(1,(abs(v.co.x)-.014)/.036));v.co.z-=.0010*(1-t);v.co.y=anatomy(v.co).y

def bezier(p,t):return p[0]*(1-t)**3+3*p[1]*t*(1-t)**2+3*p[2]*t*t*(1-t)+p[3]*t**3
# Flow paths individually placed from the confirmed male portrait. Side locks sweep
# behind the temples; old long hair and its multi-bone weights remain untouched.
paths=[
 ([(-.006,-.010,1.891),(-.021,-.074,1.902),(-.056,-.102,1.828),(-.073,-.083,1.758)],.012),
 ([(-.014,-.004,1.893),(-.046,-.047,1.901),(-.078,-.087,1.846),(-.092,-.047,1.773)],.014),
 ([(-.022,.005,1.891),(-.063,-.025,1.897),(-.091,-.062,1.840),(-.096,-.013,1.784)],.015),
 ([(-.030,.020,1.887),(-.073,.004,1.895),(-.096,-.026,1.840),(-.091,.025,1.789)],.013),
 ([(-.034,.040,1.880),(-.082,.027,1.890),(-.100,.010,1.826),(-.087,.059,1.774)],.012),
 ([(.003,-.007,1.891),(.025,-.052,1.905),(.046,-.101,1.852),(.019,-.108,1.797)],.011),
 ([(.012,.000,1.892),(.054,-.034,1.904),(.077,-.091,1.858),(.067,-.094,1.788)],.014),
 ([(.023,.013,1.889),(.075,-.010,1.898),(.100,-.050,1.833),(.100,-.036,1.748)],.015),
 ([(.027,.035,1.885),(.078,.020,1.893),(.099,-.004,1.824),(.095,.018,1.778)],.014),
 ([(.030,.053,1.878),(.079,.041,1.885),(.096,.036,1.808),(.088,.065,1.758)],.012),
]
groom=[]
# Failed groom is retained as an explicitly rejected experiment, never default.
if os.environ.get('LING35_GROOM')=='experimental':
 bpy.context.view_layer.update();scalp_tree=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get());scalp_center=Vector((0,.015,1.78))
 for lod,n,sections,sides in [(0,20,12,6),(1,13,9,6),(2,8,6,5)]:
  hair=bpy.data.objects[f'Hair_Lod{lod}'];before=len(hair.data.vertices)
  # Six groups of n locks: two forehead fans and four old curtain side fans.
  count=6*n*(sections+1)*sides
  bm=bmesh.new();bm.from_mesh(hair.data);bm.verts.ensure_lookup_table();assert count<len(bm.verts)
  bmesh.ops.delete(bm,geom=list(bm.verts)[:count],context='VERTS');bm.to_mesh(hair.data);bm.free()
  v=[];faces=[];mi=[];uv=[];steps=[28,20,12][lod];cross=[10,8,6][lod]
  def lock(points,width,mat,fine=False):
   ps=list(map(Vector,points));start=len(v)
   for i in range(steps+1):
    t=i/steps;p=bezier(ps,t);d=(bezier(ps,min(1,t+.002))-bezier(ps,max(0,t-.002))).normalized()
    outward=Vector((p.x,p.y-.016,(p.z-1.78)*.8)).normalized();a=d.cross(outward).normalized();b=a.cross(d).normalized()
    w=width*(.36+.64*math.sin(math.pi*t)**.65)*(1-.998*t*t*t)
    for j in range(cross):
     angle=j/cross*math.tau;q=p+a*math.cos(angle)*w+b*math.sin(angle)*w*(.44 if fine else .24)
     v.append(tuple(q));uv.append((j/cross,t))
   for i in range(steps):
    for j in range(cross):a=start+i*cross+j;b=start+i*cross+(j+1)%cross;faces.append((a,a+cross,b+cross,b));mi.append(mat)
   faces.append(tuple(start+j for j in reversed(range(cross))));mi.append(mat)
   faces.append(tuple(start+steps*cross+j for j in range(cross)));mi.append(mat)
  for k,(points,width) in enumerate(paths):
   ps=list(map(Vector,points))
   # A designed mass is composed of offset, overlapping curved sub-locks. Endpoints
   # stagger inside the mass, avoiding a broad flat blade ending on the forehead.
   for j in range(5 if lod==0 else 4 if lod==1 else 3):
    u=(j/(4 if lod==0 else 3 if lod==1 else 2)-.5)
    detail=[]
    for q,p in enumerate(ps):
     tangent=(ps[min(3,q+1)]-ps[max(0,q-1)]).normalized();outward=Vector((p.x,p.y-.016,(p.z-1.78)*.8)).normalized();axis=tangent.cross(outward).normalized()
     delta=axis*u*width*1.6
     if q==3:delta.z+=.004*math.sin(j*2.31+k);delta.y+=.001*math.sin(j+k)
     detail.append(tuple(p+delta))
    lock(detail,width*.24*(1+.12*math.sin(k+j)),(k+j)%3)
  # Project the scalp shell to the actual inherited head, avoiding ellipsoid/skin
  # intersection and a stepped exposed-skin boundary. One apex, no collapsed quads.
  start=len(v);around=[48,36,24][lod];rings=12
  v.append((0,.015,1.895));uv.append((.5,0))
  for i in range(1,rings+1):
   for j in range(around):
    phi=j/around*math.tau;front=(1+math.cos(phi))*.5;theta=(i/rings)*(1.00*front+1.78*(1-front))
    direction=Vector((math.sin(theta)*math.sin(phi),-math.sin(theta)*math.cos(phi),math.cos(theta)))
    hit,normal,_,_=scalp_tree.ray_cast(scalp_center,direction,.25)
    p=hit+normal*.0028 if hit is not None else scalp_center+direction*.105
    v.append(tuple(p));uv.append((j/around,i/rings))
  for j in range(around):faces.append((start,start+1+j,start+1+(j+1)%around));mi.append(0)
  for i in range(rings-1):
   for j in range(around):a=start+1+i*around+j;b=start+1+i*around+(j+1)%around;faces.append((a,a+around,b+around,b));mi.append(0)
  me=bpy.data.meshes.new('Reference swept hairline and layered locks');me.from_pydata(v,[],faces);me.update()
  for m in hair.data.materials:me.materials.append(m)
  for p,m in zip(me.polygons,mi):p.use_smooth=True;p.material_index=m
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  layer=me.uv_layers.new(name='FlowUV')
  for p in me.polygons:
   for loop in p.loop_indices:layer.data[loop].uv=uv[me.loops[loop].vertex_index]
  ob=bpy.data.objects.new('Hairline flow join',me);bpy.context.collection.objects.link(ob);ob.vertex_groups.new(name='head').add(list(range(len(v))),1,'REPLACE')
  bpy.ops.object.select_all(action='DESELECT');hair.hide_set(False);ob.select_set(True);hair.select_set(True);bpy.context.view_layer.objects.active=hair;bpy.ops.object.join()
  hair.hide_set(lod!=0);hair.hide_render=lod!=0;hair['groom35']='curated parting, scalp hairline and swept temple locks; rear weights preserved'
  groom.append({'lod':lod,'beforeVertices':before,'afterVertices':len(hair.data.vertices),'rearVerticesPreserved':before-count,'majorFrontAndTempleLocks':len(paths)})
 for mat in hair.data.materials:
  p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.52;p.inputs['Specular IOR Level'].default_value=.30;anis=p.inputs.get('Anisotropic IOR Level') or p.inputs.get('Anisotropic');
  if anis:anis.default_value=.45
head['refinement35']='anatomical regions and non-uniform front/temple groom; unaccepted art candidate'
# Old baked surface no longer exactly matches the updated cage. Rebuild and bake
# from this cage in a separate step, rather than retaining a misleading normal map.
high=bpy.data.objects.get('Lingyuan head · offline Multires source')
if high:bpy.data.objects.remove(high,do_unlink=True)
for mat in head.data.materials:
 nt=mat.node_tree;p=nt.nodes.get('Principled BSDF')
 for socket in ['Normal']:
  for link in list(p.inputs[socket].links):nt.links.remove(link)
 p.inputs['Subsurface Weight'].default_value=.075;p.inputs['Roughness'].default_value=.46
head['artAccepted']=False
bpy.context.scene.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'candidate.blend'),compress=True)
(OUT/'structure.json').write_text(json.dumps({'baseVertices':len(mesh.vertices),'shapeKeys':[k.name for k in mesh.shape_keys.key_blocks],'maxCorrectionMeters':max((v.co-p).length for v,p in zip(mesh.vertices,old)),'groom':groom,'groomPromoted':False,'originalHairPreserved':not bool(groom),'artAccepted':False},indent=2))
print('STRUCTURE35_READY',flush=True)
