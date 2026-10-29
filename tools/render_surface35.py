"""Real source geometry in Blender for before/after form review, not concept art."""
from pathlib import Path
import bpy,json,math,os
from mathutils import Vector
R=Path(__file__).resolve().parents[1];OUT=R/'verification/v35/surfaces';OUT.mkdir(parents=True,exist_ok=True)
for label in ['before','after']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;scene=bpy.context.scene
 source={p['role']:p for p in json.loads(Path('/tmp/surface35-'+label+'.json').read_text())};meshes={}
 ice=bpy.data.materials.new('Ice form review');ice.use_nodes=True;p=ice.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.24,.46,.68,1);p.inputs['Metallic'].default_value=.25;p.inputs['Roughness'].default_value=.23
 for role,data in source.items():
  v=data['positions'];ix=data['indices'];me=bpy.data.meshes.new(role);me.from_pydata([(v[i],-v[i+2],v[i+1]) for i in range(0,len(v),3)],[],[ix[i:i+3] for i in range(0,len(ix),3)]);me.materials.append(ice);me.update();meshes[role]=me
  for poly in me.polygons:poly.use_smooth='Crystal' not in role
 root=bpy.data.objects.new('Source parts',None);bpy.context.collection.objects.link(root)
 def part(role,location=(0,0,0),angle=0,scale=1):
  o=bpy.data.objects.new(role,meshes[role]);bpy.context.collection.objects.link(o);o.parent=root;o.location=location;o.rotation_euler.z=angle;o.scale=(scale,scale,scale);return o
 scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.render.resolution_x=720;scene.render.resolution_y=520;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Surface studio');scene.world.color=(.07,.08,.1)
 target=Vector((0,0,.35));bpy.ops.object.camera_add(location=(1.5,-2,1.4));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.4;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
 for pos,power,size in [((1,-3,4),250,3),((-2,1,2),150,2)]:
  bpy.ops.object.light_add(type='AREA',location=pos);ob=bpy.context.object;ob.data.energy=power;ob.data.size=size;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
 for case in ['petals','crystals']:
  if os.environ.get('SURFACE35_CASE') and case!=os.environ['SURFACE35_CASE']:continue
  target=Vector((0,0,.62 if case=='crystals' else .35));cam.data.ortho_scale=2.6 if case=='crystals' else 2.4;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
  for ob in list(root.children):bpy.data.objects.remove(ob,do_unlink=True)
  if case=='petals':
   for i in range(12):
    a=i*math.tau/12;part('frostPetal',(.22*math.cos(a),.22*math.sin(a),.12),a+math.pi/2,1 if i%2==0 else .78)
   part('feather',(.72,0,.55),.4,.9)
  else:
   part('lunarCrystal',(-.40,0,0));part('lunarCrystal',(-.1,-.08,0),.3,.58);part('starCrystal',(.42,0,0))
  scene.render.filepath=str(OUT/f'{label}-{case}.png');bpy.ops.render.render(write_still=True)
 # Compact editable geometry library. Mathematically same meshes as the browser.
 if label=='after':
  for ob in list(root.children):bpy.data.objects.remove(ob,do_unlink=True)
  for i,role in enumerate(meshes):part(role,((i-2)*1.2,0,0))
  folder=R/'characters/effect-surfaces';folder.mkdir(parents=True,exist_ok=True)
  bpy.ops.wm.save_as_mainfile(filepath=str(folder/'Effect_surfaces.blend'),compress=True)
  bpy.ops.object.select_all(action='DESELECT')
  for ob in root.children:ob.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(R/'dist/quality/effect-surfaces.glb'),export_format='GLB',use_selection=True,export_animations=False)
 print('SURFACE35_BLENDER',label,flush=True)
