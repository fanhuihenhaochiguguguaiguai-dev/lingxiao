"""Lingyuan working study. Reuses reconstructed PoXiao rig as a starting point.
Run in Blender; never writes to the original game project.
"""
import bpy, math, os, sys, json, random
from mathutils import Vector
from math import pi, sin, cos
from pathlib import Path
R=Path(__file__).resolve().parents[1]; random.seed(16)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=os.environ.get('LINGYUAN_LEGACY_SOURCE',str(R/'reference/legacy-source/poxiao.glb')))
rig=bpy.data.objects['PoXiao_Rig']; rig.name='Lingyuan_Rig'
for o in list(bpy.data.objects):
 if o.type=='MESH': o.name=o.name.replace('PoXiao','Lingyuan')
for a in list(bpy.data.actions):
 if any(s in a.name for s in ['skill_', 'attack_', 'cast_', 'death_', 'revive_', 'recall_', 'controlled_', 'hit_', 'run_']): bpy.data.actions.remove(a)
 else:a.name=a.name.replace('PoXiao__','').replace('_PoXiao_Rig','')
if rig.animation_data:
 rig.animation_data.action=None
 for track in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(track)
for a in bpy.data.actions:
 track=rig.animation_data.nla_tracks.new();track.name=a.name;track.strips.new(a.name,0,a)

def mat(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
ivory=mat('云白丝绸',(0.82,.85,.88),0,.43); navy=mat('深蓝丝绸',(.018,.04,.115),0,.46); ink=mat('墨黑衣甲',(.016,.020,.031),.12,.4);gold=mat('暖金雕饰',(.55,.32,.095),.83,.28); jade=mat('蓝玉',(.017,.19,.36),.45,.22); hair=mat('墨色发束',(.018,.015,.02),.05,.34)
# Real weighted geometry; the source reference images are never projected on the model.
def weighted(name,vertices,faces,material,bone,thickness=0):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.data.materials.append(material)
 for p in mesh.polygons:p.use_smooth=True
 g=o.vertex_groups.new(name=bone);g.add(list(range(len(vertices))),1,'REPLACE');o.parent=rig;mod=o.modifiers.new('Skin','ARMATURE');mod.object=rig
 if thickness:
  mod=o.modifiers.new('Cloth thickness','SOLIDIFY');mod.thickness=thickness
 o['study']='reference-guided work in progress';return o

def panel(name,center,span,z0,z1,depth,material,bone,phase=0):
 verts=[];faces=[]; nx,nz=16,24
 for j in range(nz+1):
  t=j/nz; width=span*(.35+.65*t); z=z0+(z1-z0)*t
  for i in range(nx+1):
   u=i/nx-.5;x=center+width*u;y=depth + .010*sin(u*8*pi+phase)*(0.4+t)+ .025*sin(t*pi); verts.append((x,y,z+.013*sin(u*7*pi)*t))
 for j in range(nz):
  for i in range(nx): a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
 return weighted(name,verts,faces,material,bone,.002)

def strand(name,points,radii,material,bone,sides=7):
 pts=[Vector(p) for p in points];v=[];f=[]
 for k,p in enumerate(pts):
  d=(pts[min(k+1,len(pts)-1)]-pts[max(0,k-1)]).normalized();ref=Vector((0,1,0)) if abs(d.y)<.9 else Vector((1,0,0));a=d.cross(ref).normalized();b=d.cross(a).normalized()
  for j in range(sides):v.append(p+radii[k]*(a*cos(2*pi*j/sides)+b*sin(2*pi*j/sides)))
 for k in range(len(pts)-1):
  for j in range(sides):a=k*sides+j;f.append((a,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,a+sides))
 return weighted(name,v,f,material,bone)
# Layered skirts, open front and under panels; approximate interpreted shape.
for i,(x,w,y,ma) in enumerate([(-.25,.30,-.12,ivory),(.25,.30,-.12,ivory),(-.12,.19,-.15,navy),(.12,.19,-.15,navy),(0,.22,-.17,ivory),(-.36,.19,.10,navy),(.36,.19,.10,navy),(0,.55,.13,ivory)]):
 panel('Robe panel %02d'%i,x,w,1.06,.23,y,ma,'pelvis',i)
# Long hanging side ribbons taper to rounded point and have real thickness.
for side in [-1,1]:
 for j in range(3):
  x=side*(.22+j*.035);points=[(x,.06,1.38),(x+side*.10,.09,1.10),(x+side*(.16+.025*j),.13,.68),(x+side*(.13+.04*j),.16,.32)]
  strand('Silk streamer',points,[.012,.023,.020,.001],ivory if j==0 else navy,'cape01.'+('L' if side<0 else 'R'),8)
 # Wide sleeve drapes from shoulder to wrist.
 panel('Outer sleeve',side*.34,.23,1.40,.94,-.08,ivory,'upper_arm.'+('L' if side<0 else 'R'),side)
 # Fine stylised filigree around shoulder, intended for later sculpt pass.
 for n in range(5):
  pts=[]
  for k in range(24):
   t=k/23;pts.append((side*(.18+.16*t),-.122-.01*sin(t*pi),1.48+.022*sin(t*2*pi+n*.75)-.018*n))
  strand('Shoulder filigree',pts,[.0018]*len(pts),gold,'upper_arm.'+('L' if side<0 else 'R'),5)
# Frontal dark robe/lapel bands and gold stitched edges.
panel('Black inner coat',0,.24,1.46,1.07,-.119,ink,'chest')
for side in [-1,1]:
 strand('Crossed collar',[(side*.052,-.14,1.52),(-side*.025,-.149,1.39),(-side*.11,-.15,1.20),(-side*.13,-.14,1.08)],[.008,.009,.009,.007],gold,'chest',6)
# Back hair has volume, individual tapered locks and head binding.
for i in range(28):
 x=(i-13.5)*.0049;endx=x*1.5+.018*sin(i*1.6);y=.065+.012*(i%4)
 pts=[(x*.45,y,1.87),(x,y+.025,1.73),(x*1.2,y+.065,1.53),(endx,y+.09,1.26+.06*sin(i))]
 strand('Long hair %02d'%i,pts,[.005,.009,.008,.0005],hair,'head',6)
# hair jewel and small crown rays
for side in [-1,1]:
 for j in range(3):
  strand('Hair ornament',[(side*.025,.035,1.88),(side*(.04+.01*j),.04,1.94),(side*(.07+.013*j),.04,1.96+.009*j)],[.003,.0025,.0005],gold,'head',6)
for i in range(10):
 x=-.11+i*.024
 strand('Waist pendant chain',[(x,-.155,1.07),(x+.01*sin(i),-.17,.91),(x+.015*sin(i),-.16,.83)],[.0015,.0015,.001],gold,'pelvis',5)
# Center buckle and blue jewel are actual meshes.
def jewel(name,location,scale,material,bone):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=location);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=rig;mod=o.modifiers.new('Skin','ARMATURE');mod.object=rig;return o
jewel('Blue waist jade',(0,-.18,1.075),(.022,.012,.032),jade,'pelvis')
# Show only finest baseline inside master; LOD exports independently.
for n in ['Lingyuan_LOD1','Lingyuan_LOD2']: bpy.data.objects[n].hide_set(True);bpy.data.objects[n].hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.color=(.16,.16,.16)
# Save clean editable master before adding rendering-only lights and camera.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'dist/Lingyuan_working.blend'))
# Export all current actual geometry for each explicit LOD; add-on parts are kept in each.
for lod in range(3):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and (not o.name.startswith('Lingyuan_LOD') or o.name==f'Lingyuan_LOD{lod}'):
   o.hide_set(False);o.select_set(True)
 rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.gltf(filepath=str(R/f'dist/lingyuan-lod{lod}.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS')
 for j in range(3):bpy.data.objects[f'Lingyuan_LOD{j}'].hide_set(j!=0)
# Actual rendered inspection images. Camera looks toward model, front is -Y.
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-4.7,1.1));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.5;scene.camera=cam;aim(cam,(0,0,1.0))
for loc,power,size in [((2,-3,4),450,3),((-3,-2,2.5),300,3),((0,3,3),500,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,1))
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
for name,loc in [('front',(0,-4.7,1.1)),('side',(4.7,0,1.1)),('back',(0,4.7,1.1))]:
 cam.location=loc;aim(cam,(0,0,1.0));scene.render.filepath=str(R/f'verification/{name}.png');bpy.ops.render.render(write_still=True)
print('BUILD COMPLETE')
