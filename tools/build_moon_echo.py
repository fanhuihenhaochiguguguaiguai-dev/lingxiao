"""Bake a lightweight 3D moon echo from the saved character; no image projection."""
from pathlib import Path
import bpy,json,hashlib,os
R=Path(__file__).resolve().parents[1];src=R/'characters/qingli/Yueli_working.blend';out=R/'dist/skill/assets';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.scene.frame_set(0)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name='Yueli moon echo geometry';o.parent=None
for vg in list(o.vertex_groups):o.vertex_groups.remove(vg)
o.data.materials.clear();material=bpy.data.materials.new('Moon echo');material.diffuse_color=(.4,.5,.8,1);o.data.materials.append(material)
for p in o.data.polygons:p.material_index=0
mod=o.modifiers.new('Silhouette LOD','DECIMATE');mod.ratio=.13;bpy.ops.object.modifier_apply(modifier=mod.name)
for p in o.data.polygons:p.use_smooth=True
bpy.ops.export_scene.gltf(filepath=str(out/'yueli-moon-echo.glb'),export_format='GLB',use_selection=True,export_animations=False,export_skins=False)
report=R/os.environ.get('LUNAR_ECHO_REPORT_DIR','verification/moon-tide');report.mkdir(exist_ok=True,parents=True)
(report/'echo-source.json').write_text(json.dumps({'source':'characters/qingli/Yueli_working.blend','sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'status':'real 3D silhouette derivative; source character art remains unapproved'},indent=2))
