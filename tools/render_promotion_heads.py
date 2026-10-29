"""Editable distinct head meshes. Blender material approximation for shape review;
the browser remains authoritative for TSL ice/energy appearance and animation.
"""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=R/'verification/promotion/heads';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;groups={};mats={}
for name,offset in [('binding',-2.4),('sovereign',0),('lunar',2.4)]:
 root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root);root.location.x=offset;groups[name]=root
 colors={'shell':(.025,.13,.30,1),'light':(.28,.57,.73,1),'gold':(.57,.35,.12,1),'dark':(.002,.008,.02,1),'eye':(.65,.9,1,1)}
 if name=='lunar':colors.update(shell=(.13,.30,.55,1),gold=(.32,.65,.88,1),light=(.55,.80,.95,1))
 for role,color in colors.items():
  m=bpy.data.materials.new(name+' '+role);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Metallic'].default_value=.65 if role=='gold' else .3;p.inputs['Roughness'].default_value=.27;mats[name,role]=m
for part in json.loads(Path('/tmp/promotion-heads.json').read_text()):
 p=part['positions'];ix=part['indices'];me=bpy.data.meshes.new(part['variant']+' '+part['role']);me.from_pydata([(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)],[],[ix[i:i+3] for i in range(0,len(ix),3)]);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);ob.parent=groups[part['variant']];me.materials.append(mats[part['variant'],part['role']]);ob['runtime_geometry_source']='dragon-head.ts / lunar-dragon-head.ts'
 for poly in me.polygons:poly.use_smooth=True
folder=R/'characters/dragon-heads';folder.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'Dragon_heads.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(R/'dist/quality/dragon-head-variants.glb'),export_format='GLB',export_animations=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=False;scene.render.resolution_x=720;scene.render.resolution_y=520;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Head studio');scene.world.color=(.06,.07,.10)
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=2.5
for pos,power,size in [((1,-4,4),400,4),((-2,3,3),500,3)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
for name,root in groups.items():
 for other,parent in groups.items():
  for ob in parent.children:ob.hide_render=other!=name
 root.location.x=0
 camera.location=(2,-3,1.1);camera.rotation_euler=(Vector((-.1,0,.20))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);root.location.x={'binding':-2.4,'sovereign':0,'lunar':2.4}[name]
print('DISTINCT_DRAGON_HEADS_SAVED',flush=True)
