"""Fit MakeHuman's CC0 long01 mesh to this morphed CC0 body for comparison.

The long01 mapping contains three weighted body vertices and an offset per
hair vertex. The generic mesh does not reproduce the reference hairstyle.
"""
for ob in list(bpy.context.scene.objects):
    if ob.name == 'Hair cap' or ob.name.startswith('Layered back hair '):
        bpy.data.objects.remove(ob,do_unlink=True)

hair_faces=[];hair_uvs=[];hair_face_uvs=[]
for line in (SRC/'long01.obj').read_text().splitlines():
    if line.startswith('vt '):
        hair_uvs.append(tuple(map(float,line.split()[1:3])))
    elif line.startswith('f '):
        parts=[p.split('/') for p in line.split()[1:]]
        hair_faces.append([int(p[0])-1 for p in parts])
        hair_face_uvs.append([int(p[1])-1 for p in parts])
lines=(SRC/'long01.mhclo').read_text().splitlines()
start=lines.index('verts 0')
mapping=[]
for line in lines[start+1:]:
    fields=line.split()
    if len(fields)==9:
        try: mapping.append(([int(x) for x in fields[:3]],[float(x) for x in fields[3:6]],[float(x) for x in fields[6:9]]))
        except ValueError: pass
expected=sum(line.startswith('v ') for line in (SRC/'long01.obj').read_text().splitlines())
if len(mapping)!=expected:
    raise RuntimeError(f'Long hair mapping mismatch: {len(mapping)} != {expected}')
sx=abs(vs[5399].x-vs[11998].x)/1.398
sy=abs(vs[791].y-vs[881].y)/2.2048
sz=abs(vs[962].z-vs[5320].z)/1.8461
hair_vertices=[]
for indices,weights,offset in mapping:
    pos=sum((vs[index]*weight for index,weight in zip(indices,weights)),Vector())
    pos+=Vector((offset[0]*sx,offset[1]*sy,offset[2]*sz))
    hair_vertices.append(conv(pos))
hair_texture=mat('Silver hair CC0 candidate',(.65,.69,.76),.42,alpha=.99)
tex=hair_texture.node_tree.nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(str(SRC/'long01_silver_study.png'),check_existing=True)
tex.image.pack()
shader=hair_texture.node_tree.nodes.get('Principled BSDF')
hair_texture.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
hair_texture.node_tree.links.new(tex.outputs['Alpha'],shader.inputs['Alpha'])
ob=mesh('CC0 long hair base candidate',hair_vertices,hair_faces,hair_texture)
uv=ob.data.uv_layers.active
for polygon,indices in zip(ob.data.polygons,hair_face_uvs):
    for loop_index,uv_index in zip(polygon.loop_indices,indices):
        uv.data[loop_index].uv=hair_uvs[uv_index]
ob['quality_status']='GENERIC HAIR EXPERIMENT: reference likeness, roots and dynamics unverified'
