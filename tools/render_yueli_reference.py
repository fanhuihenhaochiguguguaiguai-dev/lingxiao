from pathlib import Path
import bpy,subprocess,tempfile,os
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=Path(os.environ.get('YUELI_RENDER_OUT',str(R/'verification/moonfall/character')));out.mkdir(parents=True,exist_ok=True)
baseline=Path(tempfile.gettempdir())/'yueli-reference-baseline.blend'
baseline.write_bytes(subprocess.check_output(['git','show',os.environ.get('YUELI_BASELINE_COMMIT','c4bee71638f92cabbbff55cf5bda10e4fee597db')+':characters/qingli/Yueli_working.blend'],cwd=R))
for version,path in [('before',baseline),('candidate',Path(os.environ.get('YUELI_CANDIDATE_BLEND',str(R/'characters/qingli/Yueli_working.blend'))))]:
 if os.environ.get('YUELI_RENDER_ONLY') and version!=os.environ['YUELI_RENDER_ONLY']:continue
 bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(0)
 for o in list(scene.objects):
  if o.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
 scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.world.color=(.08,.08,.08)
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam
 for loc,power,size in [((2,-3,4),380,4),((-2,-1,2.4),180,3),((0,3,3),260,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
 for name,loc,target,scale in [('face',(0,-3,1.575),(0,-.035,1.575),.33),('angle',(2,-3,1.575),(0,-.035,1.575),.33),('side',(3,0,1.575),(0,-.035,1.575),.33),('full',(0,-4,1.05),(0,0,.9),1.95),('back',(0,4,1.05),(0,0,.9),1.95)]:
  if os.environ.get('YUELI_RENDER_VIEW') and name!=os.environ['YUELI_RENDER_VIEW']:continue
  cam.location=loc;cam.data.ortho_scale=scale;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/f'{version}-{name}.png');bpy.ops.render.render(write_still=True)
 if version=='candidate':
  bpy.data.objects['Qingli female base — CC0 study'].data.shape_keys.key_blocks['Blink'].value=1;cam.location=(0,-3,1.575);cam.data.ortho_scale=.33;cam.rotation_euler=(Vector((0,-.035,1.575))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/'candidate-blink.png');bpy.ops.render.render(write_still=True)
