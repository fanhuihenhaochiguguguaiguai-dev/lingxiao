"""Static fitted coverage study; no rig, deformation or art approval.

Reuse the actual body surface as the shape constraint. This avoids the previous
free-floating sleeve ribbons, but silhouette and dynamic collision still require
separate review.
"""
def fitted_shell(name,predicate,material,offset):
    selected=[]
    for polygon in body.data.polygons:
        center=sum((body.data.vertices[i].co for i in polygon.vertices),Vector())/len(polygon.vertices)
        if predicate(center):selected.append(list(polygon.vertices))
    used=sorted({index for face in selected for index in face})
    if len(used)<20:
        raise RuntimeError(name+' surface selection unexpectedly empty')
    remap={old:i for i,old in enumerate(used)}
    verts=[body.data.vertices[index].co+body.data.vertices[index].normal*offset for index in used]
    ob=mesh(name,verts,[[remap[i] for i in face] for face in selected],material)
    solid=ob.modifiers.new('Real fabric thickness','SOLIDIFY');solid.thickness=.0018
    ob['quality_status']='CANDIDATE: static coverage only; seams and deformation need review'
    return ob

for ob in list(bpy.context.scene.objects):
    if ob.name.startswith('Shoulder ribbon '):bpy.data.objects.remove(ob,do_unlink=True)

# Each sleeve is offset from the actual arm rather than constructed along a
# guessed world-space line. Hands and fingertips remain uncovered.
for side in (-1,1):
    fitted_shell(f'Fitted sleeve {side}',
                 lambda c,s=side: .985<c.z<1.31 and c.x*s>.16,
                 silk,.006)

# Closed modesty layer between the existing bodice and the base of the neck.
fitted_shell('Upper inner collar',lambda c:1.275<c.z<1.385 and abs(c.x)<.24,
             silk,.008)

# Replace visibly bare feet with actual fabric shells; shoe shape is unfinished.
for side in (-1,1):
    fitted_shell(f'Foot covering {side}',lambda c,s=side:c.z<.105 and c.x*s>.008,
                 silk,.004)
