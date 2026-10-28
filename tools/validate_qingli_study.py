"""Inspect saved Blender study and independently reimport the exported GLB."""
import bpy,bmesh,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/qingli';out.mkdir(parents=True,exist_ok=True)
def stats():
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];verts=faces=0;nonmanifold=degenerate=0;details=[]
 for o in meshes:
  m=o.data;verts+=len(m.vertices);faces+=len(m.polygons);assert all(math.isfinite(x) for v in m.vertices for x in v.co),o.name
  b=bmesh.new();b.from_mesh(m);b.normal_update();nonmanifold+=sum(not e.is_manifold for e in b.edges);degenerate+=sum(f.calc_area()<1e-12 for f in b.faces);b.free();details.append({'name':o.name,'vertices':len(m.vertices),'faces':len(m.polygons),'uv_layers':len(m.uv_layers)})
 textures=[]
 for material in bpy.data.materials:
  if not material.use_nodes:continue
  for node in material.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.image:
    textures.append({'material':material.name,'image':node.image.name,'size':list(node.image.size),'linked':any(link.from_node==node for link in material.node_tree.links)})
 return {'meshes':len(meshes),'vertices':verts,'faces':faces,'nonmanifold_edges':nonmanifold,'degenerate_faces':degenerate,'rigs':len([o for o in bpy.context.scene.objects if o.type=='ARMATURE']),'actions':len(bpy.data.actions),'materials':len(bpy.data.materials),'textures':textures,'objects':details}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'characters/qingli/Qingli_static_study.blend'));blend=stats();assert blend['meshes']>10 and blend['vertices']>5000
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'characters/qingli/Qingli_static_study.glb'));glb=stats();assert glb['meshes']>10 and glb['vertices']>5000
report={'status':'PASS_LOAD_ONLY_NOT_ART_ACCEPTANCE','blend':blend,'glb':glb,'scope':'static editable study; no validated rig, animation, material bake or face controls'};(out/'model-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'status':report['status'],'blend_meshes':blend['meshes'],'blend_vertices':blend['vertices'],'blend_nonmanifold':blend['nonmanifold_edges'],'blend_degenerate':blend['degenerate_faces'],'glb_meshes':glb['meshes'],'glb_vertices':glb['vertices'],'glb_rigs':glb['rigs']}))
