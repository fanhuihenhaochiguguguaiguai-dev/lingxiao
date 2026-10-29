"""One representative long-hair candidate; keeps existing face, clothes, UV and rig.
Static rear-surface clearance is not a runtime cloth/collision implementation.
"""
from pathlib import Path
import bpy,bmesh,math,json
from mathutils import Vector,kdtree
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];out=Path('/tmp/yueli-back-layers');out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'characters/qingli/Yueli_working.blend'));bpy.context.preferences.filepaths.save_version=0
if bpy.data.objects.get('Yueli layered back locks'):raise RuntimeError('Candidate already present; do not apply twice')
rig=bpy.data.objects['Yueli_Rig'];body=bpy.data.objects['Qingli female base — CC0 study']
# The two fitted garments inherited face-center selection from the first study,
# leaving stair-stepped boundaries. Clip actual surface geometry at seam planes.
kd=kdtree.KDTree(len(body.data.vertices))
for v in body.data.vertices:kd.insert(v.co,v.index)
kd.balance()
for name,z0,z1,width,offset,thickness in [('Fitted bodice shell',.85,1.33,.175,.012,.003),('Upper inner collar',1.275,1.385,.28,.008,.0018)]:
 ob=bpy.data.objects[name];materials=list(ob.data.materials);bm=bmesh.new();bm.from_mesh(body.data)
 for v in bm.verts:v.co+=v.normal*offset
 for point,normal in [((0,0,z0),(0,0,-1)),((0,0,z1),(0,0,1)),((width,0,0),(1,0,0)),((-width,0,0),(-1,0,0))]:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,clear_outer=True,dist=1e-6)
 me=bpy.data.meshes.new(name+' continuous seam');bm.to_mesh(me);bm.free();ob.data=me
 for mat in materials:me.materials.append(mat)
 for p in me.polygons:p.material_index=0;p.use_smooth=True
 for g in list(ob.vertex_groups):ob.vertex_groups.remove(g)
 groups={}
 for v in me.vertices:
  source=body.data.vertices[kd.find(v.co)[1]]
  for entry in source.groups:
   if entry.weight<=0:continue
   group=body.vertex_groups[entry.group].name
   if group not in groups:groups[group]=ob.vertex_groups.new(name=group)
   groups[group].add([v.index],entry.weight,'REPLACE')
 for m in list(ob.modifiers):ob.modifiers.remove(m)
 solid=ob.modifiers.new('Preserved fabric thickness','SOLIDIFY');solid.thickness=thickness;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=solid.name)
 skin=ob.modifiers.new('Preserved existing rig','ARMATURE');skin.object=rig
surface=[];faces=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not (o.name.startswith(('Skirt panel','Fitted bodice','Yueli continuous')) or o.name=='Qingli female base — CC0 study'):continue
 offset=len(surface);surface.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(offset+i for i in f.vertices) for f in o.data.polygons)
bvh=BVHTree.FromPolygons(surface,faces)
vertices=[];polygons=[];rows=[]
def strand(k,side,width,length,fine=False):
 centers=[];steps=60 if not fine else 44;sides=8 if not fine else 5;start=len(vertices)
 for i in range(steps+1):
  t=i/steps;z=1.62-length*t;x=side*(.012+k*.012+math.sin(math.pi*t)*(.045+.004*k)+.025*math.sin(t*4.8+k*.42)*t)
  y=.05+.25*t**1.35+.012*math.sin(t*5+k*.5)
  hit,_,_,_=bvh.ray_cast(Vector((x,2,z)),Vector((0,-1,0)))
  if hit is not None:y=max(y,hit.y+.022+width*.3)
  centers.append(Vector((x,y,z)))
 for i,p in enumerate(centers):
  t=i/steps;tangent=(centers[min(i+1,steps)]-centers[max(i-1,0)]).normalized();axis=Vector((1,0,0));normal=tangent.cross(axis).normalized();axis=normal.cross(tangent).normalized()
  w=width*(.6+.4*math.sin(math.pi*t))*(1-.995*t**4)
  for j in range(sides):
   a=j/sides*math.tau;vertices.append(tuple(p+axis*math.cos(a)*w+normal*math.sin(a)*w*.30));rows.append(t)
 for i in range(steps):
  for j in range(sides):a=start+i*sides+j;b=start+i*sides+(j+1)%sides;polygons.append((a,b,b+sides,a+sides))
for side in [-1,1]:
 for k in range(8):strand(k,side,.016+(k%3)*.002,1.20-(k%4)*.045)
 for k in range(8):strand(k+.28,side,.0012,1.19-(k%4)*.043,True)
mesh=bpy.data.meshes.new('Layered tapering rear hair');mesh.from_pydata(vertices,[],polygons);mesh.update();ob=bpy.data.objects.new('Yueli layered back locks',mesh);bpy.context.collection.objects.link(ob)
mat=bpy.data.materials.new('Silver lavender rear satin');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.55,.59,.72,1);bs.inputs['Roughness'].default_value=.34;bs.inputs['Anisotropic'].default_value=.55;mesh.materials.append(mat)
for p in mesh.polygons:p.use_smooth=True
groups={n:ob.vertex_groups.new(name=n) for n in ['head','hair01.L','hair01.R','hair02.L','hair02.R']}
for v,t in zip(mesh.vertices,rows):
 side='L' if v.co.x>=0 else 'R';w1=min(1,max(0,(t-.06)/.35));w2=min(1,max(0,(t-.38)/.33));weights={'head':1-w1,'hair01.'+side:w1*(1-w2),'hair02.'+side:w1*w2}
 for name,w in weights.items():
  if w>0:groups[name].add([v.index],w,'REPLACE')
mod=ob.modifiers.new('Shared existing hair bones','ARMATURE');mod.object=rig;ob.parent=rig
ob['reference']='Silver-haired board-04 / board-01 rear silhouette; static clearance only'
bpy.context.scene.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out/'Yueli_working.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in ['MESH','ARMATURE']:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.ops.export_scene.gltf(filepath=str(out/'yueli-study.glb'),export_format='GLB',use_selection=True,export_apply=False,export_animations=True,export_animation_mode='NLA_TRACKS')
(out/'geometry.json').write_text(json.dumps({'addedHairVertices':len(vertices),'locks':32,'hairDrawBatches':1,'staticSurfaceClearance':True,'newBones':0,'faceChanged':False,'clothSeamsRebuilt':2,'fabricThicknessMeters':[.003,.0018],'dynamicCollisionAccepted':False},indent=2));print('REAR_HAIR_CANDIDATE_READY',flush=True)
