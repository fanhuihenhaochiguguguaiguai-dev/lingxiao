from pathlib import Path
import bpy,os
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=R/'verification/lingyuan31/head';out.mkdir(parents=True,exist_ok=True)
for version,path in [('before',R/'dist/Lingyuan_working.blend'),('candidate',Path(os.environ.get('LING31_AFTER_BLEND','/tmp/lingyuan31-head/candidate.blend')))]:
 if os.environ.get('LING31_ONLY') and os.environ['LING31_ONLY']!=version:continue
 bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(0)
 for o in list(scene.objects):
  if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
  elif o.name.startswith(('Lingyuan_LOD','Hair_Lod')):o.hide_render=not o.name.endswith('0')
 if os.environ.get('LING31_LOW')=='1':
  for m in bpy.data.objects['Lingyuan head - MakeHuman CC0 base'].modifiers:
   if m.type=='SUBSURF':m.show_render=False
 scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.08,.08,.08)
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.36;scene.camera=cam;target=Vector((0,-.025,1.765))
 for loc,power,size in [((2,-3,4),300,4),((-2,-1,2.4),130,3),((0,3,3),200,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 for view,loc in [('front',(0,-3,1.765)),('angle',(2,-3,1.765)),('side',(3,0,1.765)),('back',(0,3,1.765))]:
  cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/f'{version}-{view}.png');bpy.ops.render.render(write_still=True)
