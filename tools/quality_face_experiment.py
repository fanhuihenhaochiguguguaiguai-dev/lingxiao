import bpy
from mathutils import Vector
from pathlib import Path
head=bpy.data.objects['Lingyuan head - MakeHuman CC0 base'];keys=head.data.shape_keys.key_blocks
print('CURRENT',[(x.name,x.value) for x in keys],flush=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=False;scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.world.color=(.12,.12,.12)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-1.8,1.76));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.4;scene.camera=cam;aim(cam,(0,0,1.76))
for loc,power,size in [((1,-2,3),100,2),((-1,-2,2),45,2),((0,1,2),110,1)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1.75))
for stage in ['before','candidate']:
 if stage=='candidate':
  keys['Chin narrower'].value=.85;keys['Chin tapered'].value=.75;keys['Cheeks refined'].value=.55
 scene.render.filepath=f'/tmp/ling-quality-face-{stage}.png';bpy.ops.render.render(write_still=True)
