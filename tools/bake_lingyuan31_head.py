"""Real high-to-low tangent normal/AO bake on the reference head candidate.
Offline Multires source stays editable and is excluded from GLB export.
"""
from pathlib import Path
import bpy,math,json,os,numpy as np
from mathutils import Vector
from io_scene_gltf2.blender.com.material_helpers import create_settings_group
R=Path(__file__).resolve().parents[1];work=Path(os.environ.get('LINGYUAN_HEAD_WORK','/tmp/lingyuan31-head'));out=work/'bakes';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(work/'candidate.blend'));bpy.context.preferences.filepaths.save_version=0
low=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];rig=bpy.data.objects['Lingyuan_Rig'];scene=bpy.context.scene
scene.frame_set(0);visibility={o.name:(o.hide_render,o.hide_get()) for o in scene.objects}
for o in scene.objects:o.hide_render=True
low.hide_set(False);low.hide_render=False
arm=next(m for m in low.modifiers if m.type=='ARMATURE');sub=next(m for m in low.modifiers if m.type=='SUBSURF');arm.show_viewport=False;arm.show_render=False
sub.levels=2;sub.show_viewport=True;sub.show_render=True;bpy.context.view_layer.update()
mesh=bpy.data.meshes.new_from_object(low.evaluated_get(bpy.context.evaluated_depsgraph_get()));high=bpy.data.objects.new('Lingyuan head · offline Multires source',mesh);bpy.context.collection.objects.link(high);high.matrix_world=low.matrix_world.copy();high['offline_only']=True
# Anatomical sculpt layers on the dense surface: superior tarsal fold, lower rim,
# alar crease and cupid bow. No random pore displacement or sharpen filter.
def bell(d,r):return math.exp(-(d/r)**2)
modified=0
for v in mesh.vertices:
 p=v.co
 if p.y>-.04 or not 1.675<p.z<1.810:continue
 detail=0.0
 for side in [-1,1]:
  u=(p.x-side*.0306)/.014
  if abs(u)<1.08:
   lid=1.7732+.0048*math.sqrt(max(0,1-u*u))+side*u*.0017
   mask=bell(u,.92)
   detail+=mask*(.00032*bell(p.z-lid-.0012,.0009)-.00026*bell(p.z-lid-.0032,.0010))
  alar=((p.x-side*.0105)/.006)**2+((p.z-1.726)/.006)**2
  detail-=.00018*bell(alar-1,.28)
 upper=1.7015+.0015*bell(abs(p.x)-.005,.004)-.0008*bell(p.x,.0028)
 detail+=.00020*bell(p.z-upper,.0008)*bell(p.x,.019)
 if abs(detail)>1e-6:p.y-=detail;modified+=1
mesh.update();bpy.ops.object.select_all(action='DESELECT');high.select_set(True);bpy.context.view_layer.objects.active=high
multi=high.modifiers.new('Editable high sculpt surface','MULTIRES');bpy.ops.object.multires_subdivide(modifier=multi.name,mode='CATMULL_CLARK');multi.levels=1;multi.sculpt_levels=1;multi.render_levels=1
high['sculpt_layer']='Deterministic anatomical fold candidate; hand-sculpt/likeness not accepted'
sub.show_viewport=False;sub.show_render=False
# Independent target materials prevent a face normal map affecting unrelated meshes.
for i,m in enumerate(list(low.data.materials)):low.data.materials[i]=m.copy();low.data.materials[i].name='Lingyuan31 face '+str(i)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.bake.use_selected_to_active=True;scene.render.bake.use_clear=True;scene.render.bake.cage_extrusion=.008;scene.render.bake.max_ray_distance=.025;scene.render.bake.margin=12
normal=bpy.data.images.new('Lingyuan31 tangent normal',width=2048,height=2048,alpha=False);normal.colorspace_settings.name='Non-Color';normal.generated_color=(.5,.5,1,1)
ao=bpy.data.images.new('Lingyuan31 self AO',width=1024,height=1024,alpha=False);ao.colorspace_settings.name='Non-Color';ao.generated_color=(1,1,1,1)
targets=[]
for m in low.data.materials:
 node=m.node_tree.nodes.new('ShaderNodeTexImage');m.node_tree.nodes.active=node;targets.append(node)
low.select_set(True);high.select_set(True);bpy.context.view_layer.objects.active=low;high.hide_render=False
for kind,image,path in [('NORMAL',normal,out/'lingyuan-head-normal.png'),('AO',ao,out/'lingyuan-head-ao.png')]:
 for node in targets:node.image=image
 bpy.ops.object.bake(type=kind)
 if kind=='AO':
  pixels=np.array(image.pixels[:],dtype=np.float32).reshape(-1,4);pixels[:,:3]=.60+.40*pixels[:,:3];image.pixels.foreach_set(pixels.ravel())
 image.filepath_raw=str(path);image.file_format='PNG';image.save();image.pack()
gltf_group=bpy.data.node_groups.get('glTF Material Output') or create_settings_group('glTF Material Output')
for m,node in zip(low.data.materials,targets):
 nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');node.image=normal;nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.6;nt.links.new(node.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 ao_node=nt.nodes.new('ShaderNodeTexImage');ao_node.image=ao;settings=nt.nodes.new('ShaderNodeGroup');settings.node_tree=gltf_group;nt.links.new(ao_node.outputs['Color'],settings.inputs['Occlusion'])
# Restore the production scene. Offline source never appears in the export.
for name,(render,hidden) in visibility.items():
 o=bpy.data.objects.get(name)
 if o:o.hide_render=render;o.hide_set(hidden)
arm.show_viewport=True;arm.show_render=True;sub.show_viewport=True;sub.show_render=True;high.hide_render=True;high.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(work/'head-master.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
 if o.type!='MESH':continue
 allowed=not o.get('offline_only') and (not o.name.startswith(('Lingyuan_LOD','Hair_Lod')) or o.name.endswith('1'))
 o.hide_set(not allowed);o.hide_render=not allowed;o.select_set(allowed)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(work/'lingyuan-head-sample.glb'),export_format='GLB',use_selection=True,use_visible=True,use_renderable=True,export_apply=False,export_animations=True,export_animation_mode='NLA_TRACKS')
(work/'bake-report.json').write_text(json.dumps({'sourceCageVertices':len(low.data.vertices),'highBaseVertices':len(mesh.vertices),'offlineMultiresLevels':multi.total_levels,'anatomicalDetailVertices':modified,'normalSize':[2048,2048],'aoSize':[1024,1024],'randomNoiseUsed':False,'runtimeSubdivisionExported':False,'artAccepted':False},indent=2));print('HEAD_HIGH_TO_LOW_BAKE_READY',flush=True)
