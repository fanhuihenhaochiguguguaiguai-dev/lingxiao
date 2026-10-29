from pathlib import Path
import bpy,subprocess,os
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=R/'verification/governance/art';out.mkdir(parents=True,exist_ok=True)
before=Path('/tmp/yueli-governance-before.blend');before.write_bytes(subprocess.check_output(['git','show','a6f9570c6abf3fe8724c606709b39de6f460a697:characters/qingli/Yueli_working.blend'],cwd=R))
for version,path in [('before',before),('candidate',Path('/tmp/yueli-back-layers/Yueli_working.blend'))]:
 if os.environ.get('GOVERNANCE_RENDER_ONLY') and os.environ['GOVERNANCE_RENDER_ONLY']!=version:continue
 bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(0)
 for o in list(scene.objects):
  if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
 scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.08,.08,.08)
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=1.95;scene.camera=cam
 for loc,power,size in [((2,-3,4),380,4),((-2,-1,2.4),180,3),((0,3,3),260,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
 for name,loc in [('front',(0,-4,1.0)),('side',(4,0,1.0)),('back',(0,4,1.0)),('angle',(3,-3,1.0))]:
  cam.location=loc;cam.rotation_euler=(Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/f'{version}-{name}.png');bpy.ops.render.render(write_still=True)
