"""Local geometry detail experiment on existing faces and Yueli front locks.
No replacement body or reference-image projection. Candidate outputs in /tmp.
"""
from pathlib import Path
import bpy,math,json,os
from mathutils import Vector
R=Path(__file__).resolve().parents[1];OUT=Path('/tmp/dual-details');OUT.mkdir(exist_ok=True)
def process(kind,path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.preferences.filepaths.save_version=0
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');head=next(o for o in bpy.context.scene.objects if o.type=='MESH' and ('female base' in o.name or 'head - MakeHuman' in o.name))
 eyes=[o for o in bpy.context.scene.objects if o.name in (['Eyeball l','Eyeball r'] if kind=='yueli' else ['Eye','Eye.001'])]
 centers=[o.location.copy() for o in eyes]
 if head.data.shape_keys and 'Blink' in head.data.shape_keys.key_blocks:raise RuntimeError('Source already has Blink; use a pre-refinement source, do not duplicate the migration')
 if not head.data.shape_keys:head.shape_key_add(name='Basis')
 key=head.shape_key_add(name='Blink');changed=0
 for v in head.data.vertices:
  p=v.co
  for e in centers:
   dx=abs(p.x-e.x);dz=abs(p.z-e.z)
   if dx<.019 and dz<.025 and p.y<e.y+.005:
    # Localized lid closure, fade into the orbital rim instead of moving the face.
    w=max(0,1-(dx/.019)**4)*max(0,1-(dz/.025)**2)
    key.data[v.index].co.z-= (p.z-e.z)*w;changed+=1
 # Independent gaze pivots, adapted to each existing eye center.
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 eye_names=[]
 for i,e in enumerate(centers):
  name='eye.'+('L' if i==0 else 'R');eye_names.append(name);bone=rig.data.edit_bones.new(name);bone.head=e;bone.tail=e+Vector((0,-.025,0));bone.parent=rig.data.edit_bones['head']
 bpy.ops.object.mode_set(mode='OBJECT')
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or not ob.name.lower().startswith(('eye','iris','pupil')) or 'brow' in ob.name.lower():continue
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;i=min(range(len(centers)),key=lambda i:(p-centers[i]).length)
   for vg in ob.vertex_groups:vg.remove([v.index])
   group=ob.vertex_groups.get(eye_names[i]) or ob.vertex_groups.new(name=eye_names[i]);group.add([v.index],1,'REPLACE')
 # Lacrimal rims and upper lashes are independent true geometry, head-skinned.
 material=bpy.data.materials.new(kind+' lash');material.diffuse_color=(.045,.035,.055,1);material.use_nodes=True;material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=material.diffuse_color
 for e in centers:
  points=[]
  for i in range(25):
   u=i/24;points.append((e.x+(u*2-1)*.012,e.y-.0115,e.z+.0058*math.sin(math.pi*u)))
  c=bpy.data.curves.new('Upper lash line','CURVE');c.dimensions='3D';c.bevel_depth=.00045;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(points)-1)
  for p,co in zip(sp.points,points):p.co=(*co,1)
  ob=bpy.data.objects.new(kind+' upper lash',c);bpy.context.collection.objects.link(ob);ob.data.materials.append(material);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');vg=ob.vertex_groups.new(name='head');vg.add(list(range(len(ob.data.vertices))),1,'REPLACE');ob.parent=rig;mod=ob.modifiers.new('Head skin','ARMATURE');mod.object=rig
  # The lash follows the same vertical closure as the skin.
  ob.shape_key_add(name='Basis');k=ob.shape_key_add(name='Blink')
  for v in ob.data.vertices:k.data[v.index].co.z=e.z+(v.co.z-e.z)*.04
 if kind=='yueli':
  # Continuous inner skirt closes gaps between the retained independent outer panels.
  vertices=[];faces=[];rows=22;cols=72
  for i in range(rows+1):
   t=i/rows;radius=.175+.20*t;z=.865-.72*t
   for q in range(cols):
    a=q/cols*2*math.pi;fold=.006*math.sin(a*18)*t;vertices.append(((radius+fold)*math.sin(a),-.02-(radius*.86+fold)*math.cos(a),z))
  for i in range(rows):
   for q in range(cols):a=i*cols+q;b=i*cols+(q+1)%cols;faces.append((a,b,b+cols,a+cols))
  me=bpy.data.meshes.new('Continuous inner skirt');me.from_pydata(vertices,[],faces);me.update();ob=bpy.data.objects.new('Yueli continuous inner skirt',me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials['Ivory silk'])
  for poly in me.polygons:poly.use_smooth=True
  vg={n:ob.vertex_groups.new(name=n) for n in ['pelvis']+['skirt%02d'%k for k in range(12)]}
  for v in me.vertices:
   t=max(0,min(1,(.855-v.co.z)/.35));a=math.atan2(v.co.x,-v.co.y-.02)%(2*math.pi);k=max(0,min(11,round((a-.34)/(2*math.pi-.68)*12-.5)));vg['pelvis'].add([v.index],1-t,'REPLACE');vg['skirt%02d'%k].add([v.index],t,'REPLACE')
  mod=ob.modifiers.new('Lining thickness','SOLIDIFY');mod.thickness=.003;mod=ob.modifiers.new('Skin','ARMATURE');mod.object=rig;ob.parent=rig
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH' or not ob.name.startswith('Swept hairline'):continue
   side=int(ob.name.split()[-2]);idx=int(ob.name.split()[-1]);nr=len(ob.data.vertices)//8
   centers=[]
   for i in range(nr):
    t=i/(nr-1);x=side*(.008+idx*.011+(.082-idx*.007)*math.sin(t*math.pi*.5));y=-.025-.071*math.sin(t*math.pi*.5);z=1.711-.12*t*t-.002*idx
    centers.append(Vector((x,y,z)))
   for i,c in enumerate(centers):
    tangent=(centers[min(i+1,nr-1)]-centers[max(i-1,0)]).normalized();a=tangent.cross(Vector((0,1,0))).normalized();b=tangent.cross(a).normalized();t=i/(nr-1);width=.009*(.65+math.sin(math.pi*t)*.35)*(1-.92*t**4)
    for k in range(8):ob.data.vertices[i*8+k].co=c+a*width*math.cos(k*math.pi/4)+b*width*.5*math.sin(k*math.pi/4)
   mod=ob.modifiers.new('Flow surface','SUBSURF');mod.levels=2;mod.render_levels=2
 # Explicitly apply non-face geometry modifiers before exporting skin/shape keys.
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):
   if mod.type=='SOLIDIFY' or mod.name=='Flow surface':bpy.ops.object.modifier_apply(modifier=mod.name)
 # Write editable model and actual exports with original cloth geometry preserved.
 key.value=0;bpy.context.scene.frame_set(0)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(kind+'.blend')))
 for lod in ([0,1,2] if kind=='lingyuan' else [0]):
  bpy.ops.object.select_all(action='DESELECT')
  for o in bpy.context.scene.objects:
   if o.type in ('MESH','ARMATURE') and (not o.name.startswith('Lingyuan_LOD') or o.name==f'Lingyuan_LOD{lod}'):
    o.hide_set(False);o.select_set(True)
  bpy.context.view_layer.objects.active=rig
  bpy.ops.export_scene.gltf(filepath=str(OUT/(f'lingyuan-lod{lod}.glb' if kind=='lingyuan' else 'yueli-study.glb')),export_format='GLB',use_selection=True,export_apply=False,export_animations=True,export_animation_mode='NLA_TRACKS')
 print('DETAIL_RESULT',kind,changed,flush=True)
process('yueli',Path('/tmp/yueli-binding/Yueli_working.blend'))
process('lingyuan',Path(os.environ.get('LINGYUAN_DETAIL_SOURCE',str(R/'dist/Lingyuan_working.blend'))))
