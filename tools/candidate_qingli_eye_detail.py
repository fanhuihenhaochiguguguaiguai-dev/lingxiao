"""Eye material/geometry candidate, not a facial rig or approved likeness."""
iris.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.045,.14,.24,1)
iris.diffuse_color=(.045,.14,.24,1)
pupil_material=mat('Eye dark pupil candidate',(.008,.012,.022),.29)
rim_material=mat('Eye outer rim candidate',(.022,.045,.072),.42)
for side in (-1,1):
    pupil=bpy.data.objects.get(f'Pupil {side}')
    if pupil:pupil.data.materials.clear();pupil.data.materials.append(pupil_material)
    eye=bpy.data.objects['Iris '+('l' if side==1 else 'r')]
    center=eye.location;vertices=[];faces=[];segments=32
    # A slim three-dimensional rim around the existing iris; the inner edge is
    # recessed slightly into the spherical iris so it does not look like a disc.
    for radius,yoffset in ((.0061,-.0021),(.0069,-.0011)):
        for j in range(segments):
            a=2*math.pi*j/segments
            vertices.append((center.x+radius*math.cos(a),center.y+yoffset,
                             center.z+radius*math.sin(a)))
    for j in range(segments):
        n=(j+1)%segments;faces.append((j,n,segments+n,segments+j))
    ob=mesh(f'Iris rim {side}',vertices,faces,rim_material)
    ob['quality_status']='STATIC EYE STUDY: no eye deformation or gaze controls'
