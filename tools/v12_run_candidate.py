"""Create an editable run-cycle candidate for visual evaluation, never overwrite the master."""
import bpy, math
from mathutils import Euler, Vector
from pathlib import Path
out=Path('/tmp/ling-v12-candidate');out.mkdir(exist_ok=True)
rig=bpy.data.objects['Lingyuan_Rig'];assert bpy.data.actions.get('run') is None
anim=rig.animation_data;old_action=anim.action;old_mutes=[t.mute for t in anim.nla_tracks]
for t in anim.nla_tracks:t.mute=True
act=bpy.data.actions.new('run');anim.action=act
names=['pelvis','spine','chest','thigh.L','shin.L','foot.L','thigh.R','shin.R','foot.R','upper_arm.L','forearm.L','upper_arm.R','forearm.R']
for f in range(0,21):
 phase=2*math.pi*f/20;s=math.sin(phase);c=math.cos(phase)
 def rotate(n,x=0,y=0,z=0):
  b=rig.pose.bones[n];b.rotation_mode='QUATERNION';b.rotation_quaternion=Euler((x,y,z),'XYZ').to_quaternion();b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=n)
 rotate('pelvis',0,.055*s,.025*c);b=rig.pose.bones['pelvis'];b.location=(0,.020+.025*math.cos(2*phase),0);b.keyframe_insert(data_path='location',frame=f,group='pelvis')
 rotate('spine',.10,0,-.045*s);rotate('chest',.14,.08*s,-.035*c)
 for side,sgn in [('L',1),('R',-1)]:
  z=s*sgn;knee=max(0,z);rotate('thigh.'+side,-.67*z,0,.035*sgn);rotate('shin.'+side,.12+.95*knee,0,0);rotate('foot.'+side,-.12-.30*knee+.14*z,0,0)
  rotate('upper_arm.'+side,.36*z,0,.05*sgn);rotate('forearm.'+side,-.22-.10*knee,0,.03*sgn)
for curve in act.fcurves:
 for point in curve.keyframe_points:point.interpolation='BEZIER'
anim.action=None
for t,m in zip(anim.nla_tracks,old_mutes):t.mute=m
track=anim.nla_tracks.new();track.name='run';track.strips.new('run',0,act)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'run_candidate.blend'))
# Fixed orthographic view captures the existing walk and new run at matching phases.
for t in anim.nla_tracks:t.mute=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.resolution_x=480;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.10,.10,.10)
bpy.ops.object.camera_add(location=(3,-.2,1.18));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.35;cam.rotation_euler=(Vector((0,0,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
for location,power,size in [((2,-3,4),500,4),((-2,-1,2),260,3)]:
 bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object;light.data.energy=power;light.data.size=size;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
for mode in ('walk','run'):
 anim.action=bpy.data.actions[mode]
 for frac in (.25,.75):
  scene.frame_set(round((24 if mode=='walk' else 20)*frac));scene.render.filepath=str(out/f'{mode}-{frac}.png');bpy.ops.render.render(write_still=True)
