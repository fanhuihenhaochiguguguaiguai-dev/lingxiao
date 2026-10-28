import * as THREE from 'three/webgpu';
import { DragonEffect } from './dragon';
import { BindStar } from './bind-star';
import { StarVortex } from './star-vortex';
import { MoonFrost } from './moon-frost';
import { MoonTide } from './moon-tide';
import { InstanceAudio, type CastKind } from './instance-audio';
import { tracks } from './skill-audio';
import { PracticeTargets } from './studio-world';
type Effect=DragonEffect|BindStar|StarVortex|MoonFrost|MoonTide;
export interface SkillInstance {id:number;kind:CastKind;age:number;duration:number;root:THREE.Group;effect:Effect;position:THREE.Vector3;yaw:number;variant:number;events:Set<string>;hitTimes:Map<number,number>;previousPoint:THREE.Vector3|null;anchor:THREE.Vector3|null;createdAt:number}
export const skillDuration=(kind:CastKind)=>kind==='yueli-2'?8.6:kind.endsWith('-1')?4.4:kind.endsWith('-2')?6.4:7.4;
const layers={dragon:true,circle:true,crystals:true,beams:true,chains:true,particles:true};
const timings:[number,string][]=[[0,'cast'],[.42,'moon'],[.95,'crystal'],[1.45,'burst'],[1.9,'field'],[5.1,'field:tail'],[7,'dissolve']];
const featherTimings:[number,string][]=[[0,'cast'],[.32,'moon'],[.66,'crystal'],[2.12,'burst'],[2.6,'field'],[3.6,'dissolve']];
const smooth=(a:number,b:number,t:number)=>THREE.MathUtils.smoothstep(t,a,b);
export class SkillInstances {
 readonly active:SkillInstance[]=[];readonly history:{id:number;kind:CastKind;position:number[];yaw:number;variant:number;createdAt:number;endedAt:number|null}[]=[];
 private readonly pool=new Map<CastKind,{root:THREE.Group;effect:Effect}[]>();private sequence=0;private quality:'high'|'ultra'='high';private counters=new Map<CastKind,number>();
 paused=false;clock=0;created=0;allocations=0;reused=0;recycled=0;disposed=0;
 constructor(private scene:THREE.Scene,readonly targets:PracticeTargets,readonly audio:InstanceAudio){}
 private construct(kind:CastKind){this.allocations++;const root=new THREE.Group();let effect:Effect;if(kind==='lingyuan-1')effect=new DragonEffect(root);else if(kind==='lingyuan-2')effect=new BindStar(root);else if(kind==='lingyuan-3')effect=new StarVortex(root);else if(kind==='yueli-1')effect=new MoonFrost(root);else effect=new MoonTide(root);effect.setQuality(this.quality);return {root,effect}}
 spawn(kind:CastKind,position:THREE.Vector3,yaw:number){
  const cached=this.pool.get(kind)?.pop(),entry=cached||this.construct(kind),id=++this.sequence,count=this.counters.get(kind)||0;this.counters.set(kind,count+1);
  if(cached)this.reused++;entry.root.name=`${kind} #${id}`;entry.root.position.copy(position);entry.root.rotation.set(0,yaw,0);entry.root.visible=true;this.scene.add(entry.root);
  const instance:SkillInstance={...entry,id,kind,age:0,duration:skillDuration(kind),position:position.clone(),yaw,variant:count%3,events:new Set(),hitTimes:new Map(),previousPoint:null,anchor:null,createdAt:performance.now()};
  this.active.push(instance);this.created++;this.history.push({id,kind,position:position.toArray(),yaw,variant:instance.variant,createdAt:instance.createdAt,endedAt:null});if(this.history.length>512)this.history.shift();this.updateEffect(instance);this.emit(instance,kind.startsWith('yueli')?'cast':'legacy:0');return instance;
 }
 private emit(i:SkillInstance,phase:string,position=i.position){if(i.events.has(phase))return;i.events.add(phase);this.audio.fire(i.id,i.kind,phase,i.variant,i.age,position);window.dispatchEvent(new CustomEvent('lingyuan:instance-cue',{detail:{instanceId:i.id,kind:i.kind,phase,age:i.age}}))}
 private updateEffect(i:SkillInstance){const fx=i.effect;if(fx instanceof BindStar)fx.update(i.age,true,layers);else if(fx instanceof MoonTide)fx.update(i.age,true,i.id);else fx.update(i.age,true);if(fx instanceof DragonEffect&&i.anchor){fx.group.position.copy(i.anchor).sub(fx.head.position).multiplyScalar(1-smooth(1.3,1.95,i.age))}}
 setAnchor(id:number,world:THREE.Vector3){const i=this.active.find(i=>i.id===id);if(i)i.anchor=i.root.worldToLocal(world.clone())}
 update(dt:number,force=false){if(this.paused&&!force)return;this.clock+=dt;const tideCount=this.active.filter(i=>i.kind==='yueli-2').length;for(const i of this.active)if(i.effect instanceof MoonTide)i.effect.setConcurrency(tideCount);for(let n=this.active.length-1;n>=0;n--){const i=this.active[n];i.age+=dt;this.updateEffect(i);
   const cues=i.kind.startsWith('yueli')?(i.kind==='yueli-2'?timings:featherTimings):tracks[Number(i.kind.slice(-1))].map((c,n)=>[c.t,`legacy:${n}`] as [number,string]);for(const [at,phase] of cues)if(i.age>=at)this.emit(i,phase);
   this.collide(i);
   if(i.age>=i.duration){this.active.splice(n,1);const record=this.history.find(r=>r.id===i.id);if(record)record.endedAt=this.clock;i.root.visible=false;i.root.removeFromParent();let list=this.pool.get(i.kind);if(!list){list=[];this.pool.set(i.kind,list)}if(list.length<2){list.push({root:i.root,effect:i.effect});this.recycled++}else{this.destroy(i);this.disposed++}}
  }
 }
 private collide(i:SkillInstance){
  const lunar=i.kind.startsWith('yueli'),skill=Number(i.kind.slice(-1));let point=new THREE.Vector3(),radius:number,continuous=false;
  if(i.kind==='yueli-2'){if(i.age<1.45||i.age>7)return;point.set(2.4,.6,0);radius=(i.effect as MoonTide).sample(i.age).radius;continuous=true}
  else if(i.kind==='yueli-1'){if(i.age<.85||i.age>2.8)return;point.set((i.effect as MoonFrost).sample().crescentX,.6,0);radius=.5}
  else{if(i.age<1||i.age>3)return;point.set(skill===1?1.5:0,1,0);radius=skill===3?4.4:skill===2?3:1}
  i.root.localToWorld(point);const previous=i.previousPoint||point,segment=point.clone().sub(previous),length=segment.lengthSq();
  this.targets.centers.forEach((target,index)=>{const last=i.hitTimes.get(index);if(last!==undefined&&(!continuous||i.age-last<1))return;const u=length&&!continuous?THREE.MathUtils.clamp(target.clone().sub(previous).dot(segment)/length,0,1):1,nearest=previous.clone().addScaledVector(segment,u);const dist=continuous?Math.hypot(point.x-target.x,point.z-target.z):nearest.distanceTo(target);if(dist>radius+.45)return;const tick=last===undefined?0:Math.floor((i.age-1.45));i.hitTimes.set(index,i.age);this.targets.applyInstanceHit(i.id,lunar?'yueli':'lingyuan',skill,index,i.age,tick,continuous?.55:1);if(lunar)this.emit(i,`hit:${index}:${tick}`,target)});i.previousPoint=point;
 }
 private destroy(i:{root:THREE.Group;effect:Effect}){if(i.effect instanceof MoonTide){i.effect.dispose();i.root.clear();return}i.root.traverse(o=>{if((o as THREE.InstancedMesh).isInstancedMesh)(o as THREE.InstancedMesh).dispose()});const geos=new Set<THREE.BufferGeometry>(),mats=new Set<THREE.Material>();i.root.traverse(o=>{const m=o as THREE.Mesh;if(m.isMesh){geos.add(m.geometry);for(const mat of Array.isArray(m.material)?m.material:[m.material])mats.add(mat)}});for(const g of geos)g.dispose();for(const m of mats)m.dispose();i.root.clear()}
 setQuality(q:'high'|'ultra'){this.quality=q;for(const i of this.active)i.effect.setQuality(q);for(const list of this.pool.values())for(const i of list)i.effect.setQuality(q)}
 latest(){return this.active[this.active.length-1]}
 seekLatest(t:number){const i=this.latest();if(!i)return;i.age=Math.max(0,t);this.updateEffect(i)}
 clear(){for(const i of this.active)this.destroy(i);this.active.length=0;this.audio.stopAll()}
 snapshot(){return {created:this.created,allocations:this.allocations,reused:this.reused,activeCount:this.active.length,pooled:[...this.pool.values()].reduce((n,v)=>n+v.length,0),recycled:this.recycled,disposed:this.disposed,clock:this.clock,active:this.active.map(i=>({id:i.id,kind:i.kind,age:i.age,position:i.position.toArray(),yaw:i.yaw,variant:i.variant,events:[...i.events],hitTargets:[...i.hitTimes.keys()],rootUuid:i.root.uuid})),history:this.history}}
}
