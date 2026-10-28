"""Incremental binding of the saved Yueli study; never regenerates its geometry.
Candidate is written under /tmp until deformation checks and rendering pass.
"""
from pathlib import Path
from collections import defaultdict
import bpy,math,json
from mathutils import Vector,Matrix,kdtree
R=Path(__file__).resolve().parents[1];out=Path('/tmp/yueli-binding');out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'characters/qingli/Qingli_static_study.blend'));bpy.context.preferences.filepaths.save_version=0
body=bpy.data.objects['Qingli female base — CC0 study']
vs=[];groups=defaultdict(set);group=''
for line in (R/'reference/makehuman/base.obj').read_text().splitlines():
 if line.startswith('v '):vs.append(Vector(map(float,line.split()[1:4])))
 elif line.startswith('g '):group=line[2:]
 elif line.startswith('f '):groups[group].update(int(p.split('/')[0])-1 for p in line.split()[1:])
for fn in ['asian-female-young.target','universal-female-young-averagemuscle-averageweight.target']:
 for line in (R/'reference/makehuman'/fn).read_text().splitlines():
  if line and not line.startswith('#'):
   i,*xyz=line.split();vs[int(i)]+=Vector(map(float,xyz))
ids=sorted(groups['body']);floor=min(vs[i].y for i in ids);scale=1.68/(max(vs[i].y for i in ids)-floor)
def conv(v):return Vector((v.x*scale,-v.z*scale,(v.y-floor)*scale))
j={g[6:]:conv(sum((vs[i] for i in ids),Vector())/len(ids)) for g,ids in groups.items() if g.startswith('joint-')}
for side,sgn in [('l',1),('r',-1)]:
 sh=j[side+'-shoulder'];rot=Matrix.Rotation(sgn*.62,3,'Y')
 for key in [side+'-elbow',side+'-hand']:
  if key in j:j[key]=sh+rot@(j[key]-sh)
arm=bpy.data.armatures.new('Yueli skeleton');rig=bpy.data.objects.new('Yueli_Rig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
segments={}
def bone(n,h,t,parent=None):
 b=arm.edit_bones.new(n);b.head=h;b.tail=t
 if parent:b.parent=arm.edit_bones[parent]
 segments[n]=(Vector(h),Vector(t));return b
bone('root',(0,0,0),(0,0,.12));bone('pelvis',j['pelvis'],j['spine-3'],'root');bone('spine',j['spine-3'],j['spine-2'],'pelvis');bone('chest',j['spine-2'],j['spine-1'],'spine');bone('neck',j['spine-1'],j['head'],'chest');bone('head',j['head'],(0,-.04,1.70),'neck')
for side,sgn in [('L',1),('R',-1)]:
 key=side.lower();hip=j[key+'-upper-leg'];knee=j[key+'-knee'];ankle=j[key+'-ankle'];toe=j[key+'-foot-1']
 bone('thigh.'+side,hip,knee,'pelvis');bone('shin.'+side,knee,ankle,'thigh.'+side);bone('foot.'+side,ankle,toe,'shin.'+side)
 sh=j[key+'-shoulder'];el=j[key+'-elbow'];hand=j[key+'-hand'];bone('upper_arm.'+side,sh,el,'chest');bone('forearm.'+side,el,hand,'upper_arm.'+side);bone('hand.'+side,hand,hand+Vector((0,0,-.06)),'forearm.'+side)
 bone('hair01.'+side,(sgn*.055,.05,1.55),(sgn*.075,.10,1.18),'head');bone('hair02.'+side,(sgn*.075,.10,1.18),(sgn*.10,.12,.83),'hair01.'+side)
for k in range(12):
 a=.34+(k+.5)*(2*math.pi-.68)/12
 bone('skirt%02d'%k,(.17*math.sin(a),-.02-.17*math.cos(a),.88),(.36*math.sin(a),-.02-.30*math.cos(a),.10),'pelvis')
bpy.ops.object.mode_set(mode='OBJECT')
# Weights for body and fitted clothing share the same nearest-surface map.
body_segments=[n for n in segments if not n.startswith(('root','hair','skirt'))]
def dseg(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared));return (p-a-t*v).length

def body_weights(p):
 if p.z>1.46:return [('head',1.)]
 if p.z>.84 and abs(p.x)>.16:
  side='L' if p.x>0 else 'R';names=['upper_arm.'+side,'forearm.'+side,'hand.'+side]
 elif p.z<.85:
  side='L' if p.x>0 else 'R';names=['thigh.'+side,'shin.'+side,'foot.'+side,'pelvis']
 else:names=['pelvis','spine','chest','neck']
 pairs=sorted((dseg(p,*segments[n]),n) for n in names)[:2];vals=[(n,1/(d+.025)**4) for d,n in pairs];total=sum(v for _,v in vals);return [(n,v/total) for n,v in vals]
kdt=kdtree.KDTree(len(body.data.vertices));bw=[]
for v in body.data.vertices:kdt.insert(body.matrix_world@v.co,v.index);bw.append(body_weights(body.matrix_world@v.co))
kdt.balance();count=0
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 # Commit existing thickness before skinning: exporting must retain the lining.
 bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):
  if mod.type in ('SOLIDIFY',):bpy.ops.object.modifier_apply(modifier=mod.name)
 groups_out={n:o.vertex_groups.get(n) or o.vertex_groups.new(name=n) for n in segments}
 for v in o.data.vertices:
  p=o.matrix_world@v.co;n=o.name.lower()
  if 'skirt panel ' in n or 'skirt panel ' in n.replace(' hem',''):
   k=int(o.name.split('Skirt panel ')[1].split()[0])-1;w=max(0,min(1,(.86-p.z)/.45));weights=[('pelvis',1-w),('skirt%02d'%k,w)]
  elif ('hair' in n or 'earring' in n or 'crown' in n or 'pupil' in n or 'iris' in n or 'eyeball' in n or 'eyebrow' in n):
   side='L' if p.x>0 else 'R';w=max(0,min(1,(1.51-p.z)/.35)) if 'hair' in n else 0;low=max(0,min(1,(1.16-p.z)/.3));weights=[('head',1-w),('hair01.'+side,w*(1-low)),('hair02.'+side,w*low)]
  elif o==body:weights=bw[v.index]
  else:weights=bw[kdt.find(p)[1]]
  for name,w in weights:
   if w>1e-7:groups_out[name].add([v.index],w,'REPLACE')
 mod=o.modifiers.new('Yueli skin','ARMATURE');mod.object=rig;o.parent=rig;o['quality_status']='BOUND STUDY — likeness and dynamic art acceptance pending';count+=1
# Neutral action is deliberately distinct from the shared runtime gait solver.
rig.animation_data_create();act=bpy.data.actions.new('idle');rig.animation_data.action=act
for frame in [0,24,48]:
 b=rig.pose.bones['chest'];b.rotation_mode='XYZ';b.rotation_euler.x=.006*math.sin(frame/48*2*math.pi);b.keyframe_insert(data_path='rotation_euler',frame=frame)
rig.animation_data.action=None;track=rig.animation_data.nla_tracks.new();track.name='idle';track.strips.new('idle',0,act)
bpy.context.scene.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Yueli_working.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in ('MESH','ARMATURE'):o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out/'yueli-study.glb'),export_format='GLB',use_selection=True,export_apply=False,export_animations=True,export_animation_mode='NLA_TRACKS')
print('BINDING_RESULT',json.dumps({'bones':len(arm.bones),'meshes':count,'weighted_vertices':sum(len(o.data.vertices) for o in bpy.context.scene.objects if o.type=='MESH')}),flush=True)
