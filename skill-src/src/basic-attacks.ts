import * as THREE from 'three/webgpu';
import {CombatState,basicProfiles,type DamageToken} from './combat-state';
import {InstanceAudio} from './instance-audio';
import {frostFeather} from './crystal-geometry';
export interface BasicPose {age:number;combo:number;yaw:number;token:DamageToken;released:boolean}
interface Strike {pose:BasicPose;age:number;origin:THREE.Vector3;previous:THREE.Vector3;point:THREE.Vector3;direction:THREE.Vector3;root:THREE.Group;hits:Set<string>}
const blade=new THREE.ConeGeometry(.07,.7,6),arc=new THREE.TorusGeometry(.28,.009,4,24,Math.PI*1.2),feather=frostFeather();
/** Independent releases, shared immutable geometry, bounded per-character pool. */
export class BasicAttacks {
 readonly poses=new Map<string,BasicPose>();readonly strikes:Strike[]=[];readonly events:{id:string;source:string;phase:string;time:number}[]=[];
 private sequence=0;private next=new Map<string,number>();private combos=new Map<string,{index:number;at:number}>();private pool:THREE.Group[]=[];created=0;reused=0;
 origin:(source:string,combo:number)=>THREE.Vector3|null=()=>null;
 constructor(private scene:THREE.Scene,readonly combat:CombatState,private audio:InstanceAudio,private onHit:(target:string,attack:number,character:string,age:number)=>void){}
 request(source:string,yaw:number){
  if(!this.combat.canAct(source)||this.combat.clock+1e-8<(this.next.get(source)||0))return false;
  const character=this.combat.unit(source).character as 'lingyuan'|'yueli',profile=basicProfiles[character],combo=this.combos.get(source),index=combo&&this.combat.clock-combo.at<1.5?(combo.index+1)%3:0;
  const token=this.combat.token(`basic:${++this.sequence}`,source,character+'-basic',profile.damage)!;this.poses.set(source,{age:0,combo:index,yaw,token,released:false});this.next.set(source,this.combat.clock+profile.interval);this.combos.set(source,{index,at:this.combat.clock});this.record(token,'windup');return true;
 }
 private record(t:DamageToken,phase:string){this.events.push({id:t.id,source:t.source,phase,time:this.combat.clock});if(this.events.length>256)this.events.shift()}
 cancelPose(source:string){const p=this.poses.get(source);if(p&&!p.released)this.record(p.token,'cancelled-before-release');this.poses.delete(source)}
 replaceSource(source:string){this.cancelPose(source);this.next.delete(source);this.combos.delete(source);for(let i=this.strikes.length-1;i>=0;i--)if(this.strikes[i].pose.token.source===source)this.release(i)}
 private createRoot(character:'lingyuan'|'yueli'){
  const root=new THREE.Group();root.userData.character=character;root.name='独立普攻轨迹';
  const material=new THREE.MeshStandardMaterial({color:character==='lingyuan'?0xa8d9f6:0xc3d7ff,emissive:character==='lingyuan'?0x155d9f:0x477ba6,emissiveIntensity:.6,metalness:.4,roughness:.25,transparent:true,opacity:.86});
  const mesh=new THREE.Mesh(character==='lingyuan'?blade:feather,material);mesh.rotation.z=character==='lingyuan'?-Math.PI/2:0;if(character==='yueli')mesh.scale.setScalar(.7);root.add(mesh);
  const rim=new THREE.Mesh(arc,new THREE.MeshBasicMaterial({color:character==='lingyuan'?0xd9bd7c:0xb9dcff,transparent:true,opacity:.55,depthWrite:false}));rim.rotation.x=Math.PI/2;root.add(rim);this.created++;return root;
 }
 update(dt:number){
  for(const [source,p] of this.poses){if(!this.combat.valid(p.token)){this.poses.delete(source);continue}const profile=basicProfiles[p.token.character];p.age+=dt;
   if(!p.released&&p.age>=profile.windup){p.released=true;const u=this.combat.unit(source),origin=p.token.character==='yueli'?this.origin(source,p.combo)||new THREE.Vector3(u.position.x,u.position.y+.24,u.position.z):new THREE.Vector3(u.position.x,u.position.y,u.position.z),direction=new THREE.Vector3(Math.cos(p.yaw),0,-Math.sin(p.yaw));
    if(p.token.character==='yueli'){const target=this.combat.enemies(source).filter(t=>{const d=new THREE.Vector3(t.position.x-origin.x,0,t.position.z-origin.z).normalize();return d.dot(direction)>.75}).sort((a,b)=>Math.hypot(a.position.x-origin.x,a.position.z-origin.z)-Math.hypot(b.position.x-origin.x,b.position.z-origin.z))[0];if(target)direction.set(target.position.x-origin.x,target.position.y-origin.y,target.position.z-origin.z).normalize()}
    const index=this.pool.findIndex(g=>g.userData.character===p.token.character),root=index<0?this.createRoot(p.token.character):this.pool.splice(index,1)[0];if(index>=0)this.reused++;root.visible=true;this.scene.add(root);const point=origin.clone().addScaledVector(direction,.45);root.position.copy(point);root.rotation.y=p.yaw;
    if(p.token.character==='yueli')point.copy(origin);this.strikes.push({pose:{...p},age:0,origin,previous:point.clone(),point,direction,root,hits:new Set()});this.audio.fireBasic(-Number(p.token.id.split(':')[1]),p.token.character,'release',p.combo,p.age,point);this.record(p.token,'release');
   }
   if(p.age>=profile.interval)this.poses.delete(source);
  }
  for(let i=this.strikes.length-1;i>=0;i--){const s=this.strikes[i],p=s.pose,profile=basicProfiles[p.token.character];s.age+=dt;const duration=p.token.character==='lingyuan'?profile.active+.12:profile.range/profile.speed+.14;
   if(!this.combat.valid(p.token)||s.age>duration){this.release(i);continue}
   s.previous.copy(s.point);const travel=p.token.character==='lingyuan'?.45+(profile.range-.45)*Math.min(1,s.age/profile.active):s.age*profile.speed;s.point.copy(s.origin).addScaledVector(s.direction,travel);s.root.position.copy(s.point);if(p.token.character==='yueli')s.root.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),s.direction);
   for(const child of s.root.children){const m=child as THREE.Mesh;(m.material as THREE.MeshStandardMaterial).opacity=.85*Math.min(1,(duration-s.age)/.12)}
   if(p.token.character==='lingyuan'&&s.age>profile.active)continue;
   const segment=s.point.clone().sub(s.previous),length=segment.lengthSq();
   for(const target of this.combat.enemies(p.token.source)){
    if(s.hits.has(target.id))continue;const center=new THREE.Vector3(target.position.x,target.position.y,target.position.z),u=length?THREE.MathUtils.clamp(center.clone().sub(s.previous).dot(segment)/length,0,1):0,nearest=s.previous.clone().addScaledVector(segment,u);
    if(nearest.distanceTo(center)>target.radius+(p.token.character==='lingyuan'?.23:.12))continue;
    const event=this.combat.damage(p.token,target.id);if(!event)continue;s.hits.add(target.id);this.onHit(target.id,-Number(p.token.id.split(':')[1]),p.token.character,p.age+s.age);this.audio.fireBasic(-Number(p.token.id.split(':')[1]),p.token.character,'hit',p.combo,p.age+s.age,center);this.record(p.token,'hit:'+target.id);
    if(p.token.character==='yueli'){this.release(i);break}
   }
  }
 }
 private release(index:number){const [s]=this.strikes.splice(index,1);s.root.visible=false;s.root.removeFromParent();if(this.pool.filter(g=>g.userData.character===s.pose.token.character).length<4)this.pool.push(s.root);else{s.root.traverse(o=>{if((o as THREE.Mesh).isMesh)((o as THREE.Mesh).material as THREE.Material).dispose()});s.root.clear()}}
 reset(){while(this.strikes.length)this.release(this.strikes.length-1);this.poses.clear();this.next.clear();this.combos.clear();this.events.length=0}
 snapshot(){return {poses:[...this.poses].map(([owner,p])=>({owner,age:p.age,combo:p.combo,yaw:p.yaw,released:p.released,id:p.token.id})),active:this.strikes.length,pooled:this.pool.length,created:this.created,reused:this.reused,events:[...this.events]}}
}
