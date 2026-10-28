from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=R/'verification/dual-quality';out.mkdir(exist_ok=True)
for char,before,after,height in [('yueli',R/'characters/qingli/Qingli_static_study.blend',Path('/tmp/dual-details/yueli.blend'),1.585),('lingyuan',R/'dist/Lingyuan_working.blend',Path('/tmp/dual-details/lingyuan.blend'),1.76)]:
 for version,path in [('before',before),('after',after)]:
  bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(0)
  for o in list(scene.objects):
   if o.type in ('CAMERA','LIGHT'):bpy.data.objects.remove(o,do_unlink=True)
   elif o.name.startswith('Lingyuan_LOD') and o.name!='Lingyuan_LOD0':o.hide_render=True
  scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.world.color=(.08,.08,.08)
  bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.36;scene.camera=cam
  for loc,power,size in [((2,-3,4),380,4),((-2,-1,2.4),180,3),((0,3,3),260,3)]:
   bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
  for view,loc in [('front',(0,-3,height)),('angle',(2,-3,height))]:
   cam.location=loc;cam.rotation_euler=(Vector((0,-.025,height))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/f'{char}-{version}-{view}.png');bpy.ops.render.render(write_still=True)
