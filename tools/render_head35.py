"""Fixed-condition actual low-cage Blender renders; unchanged cameras and lighting."""
from pathlib import Path
import bpy,os,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=R/'verification/v35/head';out.mkdir(parents=True,exist_ok=True)
versions=[('before','/tmp/lingyuan35-before.blend'),('after',str(R/'characters/lingyuan/Lingyuan_head_candidate.blend'))]
for label,path in versions:
 if os.environ.get('HEAD35_ONLY') and label!=os.environ['HEAD35_ONLY']:continue
 bpy.ops.wm.open_mainfile(filepath=path);scene=bpy.context.scene;scene.frame_set(0)
 for ob in list(scene.objects):
  if ob.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
  elif ob.get('offline_only'):ob.hide_render=True
  elif ob.name.startswith(('Hair_Lod','Lingyuan_LOD')):ob.hide_render=not ob.name.endswith('1')
 for m in bpy.data.objects['Lingyuan head - MakeHuman CC0 base'].modifiers:
  if m.type=='SUBSURF':m.show_render=False
 scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.08,.08,.08)
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.36;scene.camera=cam;target=Vector((0,-.025,1.765))
 for loc,power,size in [((2,-3,4),300,4),((-2,-1,2.4),130,3),((0,3,3),200,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 for view,loc in [('front',(0,-3,1.765)),('angle',(2,-3,1.765)),('side',(3,0,1.765)),('back',(0,3,1.765))]:
  if os.environ.get('HEAD35_VIEW') and view!=os.environ['HEAD35_VIEW']:continue
  cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/f'{label}-{view}.png');bpy.ops.render.render(write_still=True)
 print('HEAD35_RENDERED',label,flush=True)
