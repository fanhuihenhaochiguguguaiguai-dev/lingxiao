"""Editable mesh master from the exact runtime rest geometry; no concept images.
Run after node tools/check_slash_dragon32.mjs. Curve animation lives in TypeScript;
the exported rest GLB is an inspectable asset, not a claimed baked skeletal clip.
"""
from pathlib import Path
import bpy,json,os
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=R/'verification/dragon32/blender';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
colors={'skin':(.025,.13,.30,1),'plate':(.09,.32,.53,1),'gold':(.57,.35,.12,1),'light':(.36,.69,.80,1),'dark':(.002,.006,.018,1)};materials={}
for role,c in colors.items():
 m=bpy.data.materials.new('Slash dragon '+role);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=c;p.inputs['Roughness'].default_value=.29;p.inputs['Metallic'].default_value=.75 if role=='gold' else .35;materials[role]=m
# Three.js/glTF are Y-up; the editable Blender source is Z-up. Export converts
# back to glTF Y-up, so the final asset must round-trip to the original buffers.
for part in json.loads(Path('/tmp/dragon32-master.json').read_text()):
 p=part['positions'];indices=part['indices'];mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)],[],[indices[i:i+3] for i in range(0,len(indices),3)]);mesh.update();ob=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(ob);mesh.materials.append(materials[part['role']]);ob['runtime_source']='skill-src/src/slash-dragon.ts';ob['curve_deformed_at_runtime']=part['body']
 for face in mesh.polygons:face.use_smooth=True
root=R/'characters/lingyuan';root.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(root/'Dragon_slash_master.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(R/'dist/quality/dragon-slash32.glb'),export_format='GLB',export_animations=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=False;scene.render.resolution_x=900;scene.render.resolution_y=520;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Dragon studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.045,.07,1)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';target=Vector((-1.65,0,0))
for pos,power,size in [((1,-4,5),600,4),((-3,2,4),700,3),((1,3,1),230,2)]:
 bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.size=size;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
for label,pos,look,width in [('body',(1.8,-6,3),(-1.65,0,0),5.5),('head',(1.8,-3,1.1),(-.03,0,0),1.95)]:
 target=Vector(look);cam.location=pos;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=width;scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
print('DRAGON_MASTER_AND_REAL_RENDERS_SAVED',flush=True)
