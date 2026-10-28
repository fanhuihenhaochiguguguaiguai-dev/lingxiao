"""Render identical face views of a loaded Qingli blend, without modifying it.

Usage: blender -b path/to/file.blend -t 4 --python tools/render_qingli_face_validation.py -- /tmp/output-dir
"""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:]
if len(args)!=1:
    raise SystemExit('Pass an output directory after --')
out=Path(args[0]);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
cam=scene.camera
if not cam or not any(o.type=='LIGHT' for o in scene.objects):
    raise SystemExit('Study camera or fixed study lights are absent')
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=False
scene.render.resolution_x=560
scene.render.resolution_y=560
scene.render.resolution_percentage=100
cam.data.type='ORTHO';cam.data.ortho_scale=.32
target=Vector((0,-.04,1.57))
for name,pos in [('front',(0,-3,1.57)),('angle',(2.12,-2.12,1.57)),('side',(3,0,1.57))]:
    cam.location=pos
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
print('FACE_VIEWS_COMPLETE',out)
