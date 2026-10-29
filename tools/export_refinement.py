"""Export one LOD at a time from a candidate, preserving its matching hair."""
import bpy,sys,os
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
rig=bpy.data.objects['Lingyuan_Rig']
for n in ([int(os.environ['LING_EXPORT_LOD'])] if os.environ.get('LING_EXPORT_LOD') else range(3)):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  allowed=not o.get('offline_only') and (not o.name.startswith(('Lingyuan_LOD','Hair_Lod')) or o.name in (f'Lingyuan_LOD{n}',f'Hair_Lod{n}'))
  o.hide_set(not allowed);o.hide_render=not allowed;o.select_set(allowed)
 rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.gltf(filepath=str(out/f'lingyuan-lod{n}.glb'),export_format='GLB',use_selection=True,use_visible=True,use_renderable=True,export_animations=True,export_animation_mode='NLA_TRACKS')
 for j in range(3):
  for prefix in ('Lingyuan_LOD','Hair_Lod'):bpy.data.objects[f'{prefix}{j}'].hide_set(j!=0)
