import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/sites/lingyuan-character-lab');scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=720;scene.render.resolution_y=990;scene.render.resolution_percentage=100
scene.world.color=(.12,.12,.12)
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-4.7,1.1));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.5;scene.camera=cam;aim(cam,(0,0,1.0))
for loc,power,size in [((2,-3,4),450,3),((-3,-2,2.5),300,3),((0,3,3),500,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1))
scene.render.image_settings.file_format='PNG'
for name,loc in [('front',(0,-4.7,1.1)),('side',(4.7,0,1.1)),('back',(0,4.7,1.1))]:
 cam.location=loc;aim(cam,(0,0,1.0));scene.render.filepath=str(R/f'verification/{name}.png');bpy.ops.render.render(write_still=True)
