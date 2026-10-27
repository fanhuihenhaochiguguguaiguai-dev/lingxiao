"""Real Blender renders of the current work-in-progress model, not reference art."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]).resolve();root.mkdir(parents=True,exist_ok=True);scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam
for loc,power,size in [((2,-3,4),450,3),((-3,-2,2.5),300,3),((0,3,3),500,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1))
for name,target,scale in [
 ('face',(0,0,1.76),.42),('hair',(0,0,1.86),.40),('shoulder',(.25,0,1.46),.48),('robe',(0,0,1.16),.85),('waist',(0,0,1.05),.5),('hand',(.43,0,.97),.30),('boots',(0,0,.24),.70),('weapon',(.43,0,1.33),1.7)]:
 cam.location=(target[0],-3,target[2]);cam.data.ortho_scale=scale;aim(cam,target);scene.render.filepath=str(root/(name+'.png'));bpy.ops.render.render(write_still=True)
