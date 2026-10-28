"""Experimental geometry additions to the editable Qingli study.

Executed inside build_qingli_study.py. This is a static art study, not a
replacement for hand-sculpted facial topology, rigging, or art approval.
"""
from mathutils import Vector

# Remove only the particularly straight face-framing blocks of the first study.
for ob in list(bpy.context.scene.objects):
    if ob.name.startswith(('Face framing lock ', 'Swept hairline ', 'Back silver hair ')):
        bpy.data.objects.remove(ob, do_unlink=True)

def smooth_line(name, pts, radius, material):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(pts)-1)
    for point, pos in zip(spline.bezier_points, pts):
        point.co = pos
        point.handle_left_type = point.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(ob)
    curve.materials.append(material)
    return ob

def hair_sweep(name, controls, width, material):
    # Swept elliptical tube with smoothly interpolated centerline and taper.
    coords = [Vector(p) for p in controls]
    sampled = []
    for i in range(len(coords)-1):
        p0 = coords[max(0, i-1)]; p1 = coords[i]
        p2 = coords[i+1]; p3 = coords[min(len(coords)-1, i+2)]
        for j in range(5):
            t = j/5
            sampled.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    sampled.append(coords[-1])
    vertices = []; faces = []; sides = 10
    for i,p in enumerate(sampled):
        t = i/(len(sampled)-1)
        tangent = (sampled[min(i+1,len(sampled)-1)]-sampled[max(0,i-1)]).normalized()
        side = tangent.cross(Vector((0,1,0))).normalized()
        if side.length < .1: side = Vector((1,0,0))
        normal = tangent.cross(side).normalized()
        radius = width * (0.15 + .85 * math.sin(math.pi * (0.12 + .85*t))**.65) * (1-.76*t)
        for j in range(sides):
            a=2*math.pi*j/sides
            vertices.append(p+radius*(math.cos(a)*side+.55*math.sin(a)*normal))
    for i in range(len(sampled)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    return mesh(name,vertices,faces,material)

# Long locks form overlapping volumetric layers behind the head. They remain a
# static approximation: the hair has no dynamics or collision constraints.
for i in range(19):
    x=(i-9)*.0085
    length=.69+.025*(i%5)
    y=.064+.006*(i%3)
    controls=[]
    for j in range(6):
        t=j/5
        controls.append((x*(1+.75*t)+.012*math.sin(5*t+i*.7)*t,
                         y+.045*t+.009*math.sin(4*t+i*.6)*t,
                         1.68-length*t))
    hair_sweep(f'Layered back hair {i:02}',controls,.013 if i%3 else .016,
               hair_light if i%4==0 else hair)

for side in (-1,1):
    # A center part, softly sweeping fringe and longer side locks around face.
    for i in range(6):
        offset=i*.0055
        points=[(side*(.004+offset),-.045,1.706),
                (side*(.018+offset),-.110,1.686-i*.003),
                (side*(.039+offset),-.142,1.655-i*.005),
                (side*(.062+offset),-.145,1.615-i*.005),
                (side*(.077+offset),-.129,1.575-i*.007)]
        hair_sweep(f'Fringe sweep {side} {i}',points,.009,hair_light if i in (1,4) else hair)
    for i in range(4):
        x=side*(.072+i*.009)
        points=[(x,-.075,1.683),(x*1.1,-.112,1.625),
                (x*1.12,-.126,1.55),(x*1.16,-.117,1.46),
                (x*1.20,-.092,1.34-i*.018)]
        hair_sweep(f'Tapered side lock {side} {i}',points,.011,hair_light if i==1 else hair)
    # Brows and lid edges are actual curved geometry. Existing base eye opening
    # is retained; no claim of facial deformation or anatomically correct eyelids.
    browmat=bpy.data.materials.get('Brow ash blue') or mat('Brow ash blue',(.29,.29,.32),.68)
    smooth_line(f'Brow {side}',[(side*.014,-.145,1.590),(side*.024,-.147,1.594),
                               (side*.036,-.144,1.594),(side*.049,-.136,1.589)],.0009,browmat)
    # Avoid moving pupils independently of their supporting eye objects.
    iris_obj=bpy.data.objects['Iris '+('l' if side==1 else 'r')]
    iris_obj.scale.x=1.16; iris_obj.scale.z=1.14
    e=iris_obj.location
    sphere(f'Pupil {side}',(e.x,e.y-.0026,e.z),(.0025,.0015,.0032),browmat,16,8)

# Necklace and independently modeled hair ornaments. The first trial's
# floating bodice trims and rigid dress panels were removed after rendering.
for side in (-1,1):
    smooth_line(f'Collar necklace {side}',[(side*.055,-.105,1.36),(side*.035,-.132,1.32),
        (0,-.143,1.30)],.0016,gold)

for side in (-1,1):
    # Hair jewelry uses separate solid petals and gems, rather than a texture.
    flower((side*.085,-.055,1.704),.017,f'Side hair blossom {side}')
    smooth_line(f'Head ornament branch {side}',[(side*.045,-.035,1.72),
        (side*.075,-.035,1.75),(side*.098,-.022,1.765)],.0018,gold)
    sphere(f'Head ornament gem {side}',(side*.079,-.044,1.747),(.005,.004,.008),gem,16,8)
