import * as THREE from 'three/webgpu';
import { DragonEffect } from './dragon';
import { BindStar } from './bind-star';
import { StarVortex } from './star-vortex';
import { MoonFrost } from './moon-frost';
import { Moonfall } from './moonfall';
import { MoonTide } from './moon-tide';
import { InstanceAudio, type CastKind } from './instance-audio';
import { skillRegistry, type SkillEffect } from './skill-registry';
import { PracticeTargets } from './studio-world';
import {DamageAreaView} from './damage-area-view';
import {skillVolumes} from './skill-volumes';
import {sweepVolume,hurtDistance,type DamageVolume} from './damage-volumes';
import {CombatState,type DamageToken} from './combat-state';
type Effect=SkillEffect;
export interface SkillInstance {id:number;kind:CastKind;age:number;duration:number;root:THREE.Group;effect:Effect;position:THREE.Vector3;yaw:number;variant:number;events:Set<string>;hitTimes:Map<number,number>;previousPoint:THREE.Vector3|null;anchor:THREE.Vector3|null;createdAt:number;createdWallTimeMs:number;owner:string;damageToken:DamageToken|null;combatHits:Map<string,{life:number;age:number;tick:number}>;volumes:DamageVolume[];previousTargets:Map<string,THREE.Vector3>}
export const skillDuration=(kind:CastKind)=>skillRegistry[kind].duration;
const smooth=(a:number,b:number,t:number)=>THREE.MathUtils.smoothstep(t,a,b);
export class SkillInstances {
 readonly active:SkillInstance[]=[];readonly history:{id:number;kind:CastKind;position:number[];yaw:number;variant:number;createdAt:number;createdWallTimeMs:number;endedAt:number|null}[]=[];
 private readonly pool=new Map<CastKind,{root:THREE.Group;effect:Effect}[]>();private sequence=0;private quality:'high'|'ultra'='high';private counters=new Map<CastKind,number>();
 private areas:DamageAreaView;paused=false;clock=0;created=0;allocations=0;reused=0;recycled=0;disposed=0;
 constructor(private scene:THREE.Scene,readonly targets:PracticeTargets,readonly audio:InstanceAudio,readonly combat?:CombatState){this.areas=new DamageAreaView(scene)}
 private construct(kind:CastKind){this.allocations++;const root=new THREE.Group(),effect=skillRegistry[kind].create(root);effect.setQuality(this.quality);return {root,effect}}
 spawn(kind:CastKind,position:THREE.Vector3,yaw:number,owner="player"){
  if(this.combat&&(!this.combat.units.has(owner)||!this.combat.canAct(owner)))throw new Error('Inactive or unknown skill owner: '+owner);
  const cached=this.pool.get(kind)?.pop(),entry=cached||this.construct(kind),id=++this.sequence,count=this.counters.get(kind)||0;this.counters.set(kind,count+1);
  if(cached)this.reused++;entry.root.name=`${kind} #${id}`;entry.root.position.copy(position);entry.root.rotation.set(0,yaw,0);entry.root.visible=true;this.scene.add(entry.root);
  const instance:SkillInstance={...entry,id,kind,age:0,duration:skillDuration(kind),position:position.clone(),yaw,variant:count%3,events:new Set(),hitTimes:new Map(),previousPoint:null,anchor:null,createdAt:this.clock,createdWallTimeMs:performance.now(),owner,damageToken:this.combat?.token(`skill:${id}`,owner,kind,skillRegistry[kind].damage)||null,combatHits:new Map(),volumes:[],previousTargets:new Map()};
  this.active.push(instance);this.created++;this.history.push({id,kind,position:position.toArray(),yaw,variant:instance.variant,createdAt:instance.createdAt,createdWallTimeMs:instance.createdWallTimeMs,endedAt:null});if(this.history.length>512)this.history.shift();this.updateEffect(instance);instance.volumes=skillVolumes(kind,instance.effect);this.rememberTargets(instance);this.emit(instance,skillRegistry[kind].audioStyle?'cast':'legacy:0');return instance;
 }
 private emit(i:SkillInstance,phase:string,position=i.position){if(i.events.has(phase))return;i.events.add(phase);this.audio.fire(i.id,i.kind,phase,i.variant,i.age,position);window.dispatchEvent(new CustomEvent('lingyuan:instance-cue',{detail:{instanceId:i.id,kind:i.kind,phase,age:i.age}}))}
 private updateEffect(i:SkillInstance){skillRegistry[i.kind].update(i.effect,i.age,i.id);const fx=i.effect;if(fx instanceof DragonEffect&&i.anchor){fx.group.position.copy(i.anchor).sub(fx.head.position).multiplyScalar(1-smooth(1.3,1.95,i.age))}}
 setAnchor(id:number,world:THREE.Vector3){const i=this.active.find(i=>i.id===id);if(i)i.anchor=i.root.worldToLocal(world.clone())}
 update(dt:number,force=false){if(this.paused&&!force)return;this.clock+=dt;const counts=new Map<CastKind,number>();for(const i of this.active)counts.set(i.kind,(counts.get(i.kind)||0)+1);for(const i of this.active)skillRegistry[i.kind].concurrency?.(i.effect,counts.get(i.kind)!);for(let n=this.active.length-1;n>=0;n--){const i=this.active[n];if(this.combat&&i.damageToken&&!this.combat.valid(i.damageToken)){this.retire(n,true);continue}i.age+=dt;this.updateEffect(i);
   for(const [at,phase] of skillRegistry[i.kind].cues)if(i.age>=at)this.emit(i,phase);
   this.collide(i,Math.max(0,i.age-dt),dt);
   if(i.age>=i.duration)this.retire(n);
  }
  this.refreshAreas();
 }
 private refreshAreas(){this.areas.update(this.active.map(i=>({...i,valid:!this.combat||!!i.damageToken&&this.combat.valid(i.damageToken)})))}
 private retire(index:number,cancelled=false){const [i]=this.active.splice(index,1);if(cancelled)this.audio.stopInstance(i.id);const record=this.history.find(r=>r.id===i.id);if(record)record.endedAt=this.clock;i.root.visible=false;i.root.removeFromParent();let list=this.pool.get(i.kind);if(!list){list=[];this.pool.set(i.kind,list)}if(list.length<2){list.push({root:i.root,effect:i.effect});this.recycled++}else{this.destroy(i);this.disposed++}}
 cancelOwner(owner:string){for(let n=this.active.length-1;n>=0;n--)if(this.active[n].owner===owner)this.retire(n,true);this.refreshAreas()}
 private rememberTargets(i:SkillInstance){
  if(this.combat)for(const u of this.combat.units.values())i.previousTargets.set(u.id,new THREE.Vector3(u.position.x,u.position.y,u.position.z));
  else this.targets.centers.forEach((p,n)=>i.previousTargets.set('target-'+n,p.clone()));
 }
 private collide(i:SkillInstance,previousAge:number,dt:number){
  const def=skillRegistry[i.kind],volumes=skillVolumes(i.kind,i.effect),old=new Map(i.volumes.map(v=>[v.id,v]));
  const targets=this.combat?this.combat.enemies(i.owner).map(u=>({id:u.id,life:u.life,position:new THREE.Vector3(u.position.x,u.position.y,u.position.z),radius:u.radius,halfHeight:u.halfHeight})):this.targets.centers.map((p,n)=>({id:'target-'+n,life:0,position:p,radius:.45,halfHeight:.2}));
  if(dt>0&&(!this.combat||i.damageToken&&this.combat.valid(i.damageToken)))for(const target of targets){
   const last=i.combatHits.get(target.id);if(last?.life===target.life&&(!def.hit.repeat||i.age-last.age<def.hit.repeat-1e-7))continue;
   const previous=i.previousTargets.get(target.id)||target.position;let contact:number|null=null,region='';
   for(const v of volumes){const t=sweepVolume(old.get(v.id)||v,v,previous,target.position,target.radius,previousAge,i.age,target.halfHeight);if(t!==null&&(contact===null||t<contact)){contact=t;region=v.id}}
   if(contact===null)continue;
   if(last?.life===target.life&&def.hit.repeat&&contact-last.age<def.hit.repeat-1e-7)continue;
   const tick=last?.life===target.life?last.tick+1:0;
   const event=this.combat&&i.damageToken?this.combat.damage(i.damageToken,target.id,tick,def.hit.slow||1):null;
   if(this.combat&&!event)continue;
   if(event)Object.assign(event,{region,contactAge:contact});
   i.combatHits.set(target.id,{life:target.life,age:contact,tick});
   if(target.id.startsWith('target-')){const index=Number(target.id.slice(7));i.hitTimes.set(index,i.age);this.targets.applyInstanceHit(i.id,def.character,def.slot,index,i.age,tick,def.hit.slow||1);if(def.audioStyle||def.hitAudio)this.emit(i,`hit:${index}:${tick}`,target.position)}
   else if(def.audioStyle||def.hitAudio)this.emit(i,`hit:combat-${target.id}:${tick}`,target.position);
  }
  i.volumes=volumes;this.rememberTargets(i);
 }
 /** The AI queries the same active geometry for distance-based avoidance. */
 danger(owner:string,point:THREE.Vector3,radius=.36){let distance=Infinity,away=new THREE.Vector3();for(const i of this.active){if(i.owner===owner||this.combat&&i.damageToken&&!this.combat.valid(i.damageToken))continue;for(const v of i.volumes){if(i.age<v.start||i.age>v.end)continue;const d=hurtDistance(v,point,.49)-radius;if(d<distance){distance=d;away.copy(point).sub(new THREE.Vector3(v.a.x,v.a.y,v.a.z));away.y=0;if(v.shape==='ring'&&Math.hypot(point.x-v.a.x,point.z-v.a.z)<(v.inner||0))away.negate();if(away.lengthSq()<1e-6)away.set(0,0,1);away.normalize()}}}return {distance,away}}
 volumes(id:number){const i=this.active.find(i=>i.id===id);return i?{id:i.id,age:i.age,kind:i.kind,volumes:i.volumes.map(v=>({...v,active:i.age>=v.start&&i.age<=v.end}))}:null}
 private destroy(i:{kind:CastKind;root:THREE.Group;effect:Effect}){const release=skillRegistry[i.kind].dispose;if(release){release(i.effect);i.root.clear();return}i.root.traverse(o=>{if((o as THREE.InstancedMesh).isInstancedMesh)(o as THREE.InstancedMesh).dispose()});const geos=new Set<THREE.BufferGeometry>(),mats=new Set<THREE.Material>();i.root.traverse(o=>{const m=o as THREE.Mesh;if(m.isMesh){geos.add(m.geometry);for(const mat of Array.isArray(m.material)?m.material:[m.material])mats.add(mat)}});for(const g of geos)g.dispose();for(const m of mats)m.dispose();i.root.clear()}
 setQuality(q:'high'|'ultra'){this.quality=q;for(const i of this.active)i.effect.setQuality(q);for(const list of this.pool.values())for(const i of list)i.effect.setQuality(q)}
 latest(){return this.active[this.active.length-1]}
 seekLatest(t:number){const i=this.latest();if(!i)return;i.age=Math.max(0,t);this.updateEffect(i);i.volumes=skillVolumes(i.kind,i.effect);this.rememberTargets(i);this.refreshAreas()}
 clear(){for(const i of this.active){this.destroy(i);this.disposed++;const r=this.history.find(r=>r.id===i.id);if(r)r.endedAt=this.clock}this.active.length=0;this.areas.update([]);this.audio.stopAll()}
 snapshot(){return {paused:this.paused,created:this.created,allocations:this.allocations,reused:this.reused,activeCount:this.active.length,pooled:[...this.pool.values()].reduce((n,v)=>n+v.length,0),recycled:this.recycled,disposed:this.disposed,clock:this.clock,active:this.active.map(i=>({id:i.id,kind:i.kind,age:i.age,position:i.position.toArray(),yaw:i.yaw,variant:i.variant,owner:i.owner,combatHits:[...i.combatHits.keys()],events:[...i.events],hitTargets:[...i.hitTimes.keys()],rootUuid:i.root.uuid,iceDragon:i.effect instanceof Moonfall?i.effect.sample().dragon:null,dragonCount:i.effect instanceof Moonfall?i.effect.sample().dragonCount:undefined})),history:this.history}}
}
