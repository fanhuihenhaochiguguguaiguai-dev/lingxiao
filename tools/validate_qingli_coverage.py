"""Check static garment fitting on the saved study and its reimported GLB.

This checks selected sampled distances and symmetry only. It does not certify
appearance, all-surface clearance, skinning, movement, or collision behaviour.
"""
from pathlib import Path
import bpy,json
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[1]
def inspect(label):
    bpy.context.view_layer.update()
    body=bpy.data.objects.get('Qingli female base — CC0 study')
    if body is None:
        raise RuntimeError(label+': body object missing')
    verts=[body.matrix_world @ v.co for v in body.data.vertices]
    polygons=[list(p.vertices) for p in body.data.polygons]
    tree=BVHTree.FromPolygons(verts,polygons,all_triangles=False)
    result={}
    for name in ('Fitted sleeve -1','Fitted sleeve 1','Upper inner collar','Foot covering -1','Foot covering 1'):
        ob=bpy.data.objects.get(name)
        if not ob or ob.type!='MESH':raise RuntimeError(label+': missing '+name)
        step=max(1,len(ob.data.vertices)//250)
        distances=[]
        for index in range(0,len(ob.data.vertices),step):
            v=ob.data.vertices[index]
            position=ob.matrix_world @ v.co
            hit=tree.find_nearest(position)
            if hit[0] is None:raise RuntimeError(label+': no surface near '+name)
            distances.append(hit[3])
        if max(distances)>.03:raise RuntimeError(f'{label}: {name} too far from body ({max(distances):.4f}m)')
        result[name]={'vertices':len(ob.data.vertices),'sample_count':len(distances),'max_distance_m':round(max(distances),6)}
    return result

bpy.ops.wm.open_mainfile(filepath=str(root/'characters/qingli/Qingli_static_study.blend'))
blend=inspect('blend')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'characters/qingli/Qingli_static_study.glb'))
glb=inspect('glb')
for name in blend:
    if glb[name]['vertices'] < 2*blend[name]['vertices']:
        raise RuntimeError('GLB is missing expected solidified coverage geometry: '+name)
result={'scope':'sampled static proximity only; not art, full intersection or animation acceptance','blend':blend,'glb':glb}
(root/'verification/qingli/coverage-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('COVERAGE_CHECK',json.dumps(result,ensure_ascii=False))
