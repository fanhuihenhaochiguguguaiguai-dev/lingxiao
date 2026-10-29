import * as THREE from 'three/webgpu';
import {CombatState,basicProfiles,type DamageToken} from './combat-state';
import {InstanceAudio} from './instance-audio';
import {sweepVolume,type DamageVolume} from './damage-volumes';
import {frostFeather} from './crystal-geometry';
export interface BasicPose {age:number;combo:number;yaw:number;token:DamageToken;released:boolean}
interface Strike {pose:BasicPose;age:number;origin:THREE.Vector3;previous:THREE.Vector3;point:THREE.Vector3;direction:THREE.Vector3;root:THREE.Group;hits:Set<string>;weapon:{a:THREE.Vector3;b:THREE.Vector3}|null;targets:Map<string,THREE.Vector3>}
const blade=new THREE.ConeGeometry(.07,.7,6),arc=new THREE.TorusGeometry(.28,.009,4,24,Math.PI*1.2),feather=frostFeather();
/** Independent releases, shared immutable geometry, bounded per-character pool. */
export class BasicAttacks {
 readonly poses=new Map<string,BasicPose>();readonly strikes:Strike[]=[];readonly events:{id:string;source:string;phase:string;time:number}[]=[];
 private sequence=0;private next=new Map<string,number>();private combos=new Map<string,{index:number;at:number}>();private pool:THREE.Group[]=[];created=0;reused=0;
 weapon:(source:string)=>{grip:THREE.Vector3;tip:THREE.Vector3}|null=()=>null;
 origin:(source:string,combo:number)=>THREE.Vector3|null=()=>null;
 constructor(private scene:THREE.Scene,readonly combat:CombatState,private audio:InstanceAudio,private onHit:(target:string,attack:number,character:string,age:number)=>void){}
 request(source:string,yaw:number){
  if(!this.combat.canAct(source)||this.combat.clock+1e-8<(this.next.get(source)||0))return false;
  const character=this.combat.unit(source).character as 'lingyuan'|'yueli',profile=basicProfiles[character],combo=this.combos.get(source),index=combo&&this.combat.clock-combo.at<1.5?(combo.index+1)%3:0;
  const token=this.combat.token(`basic:${++this.sequence}`,source,character+'-basic',profile.damage)!;this.poses.set(source,{age:0,combo:index,yaw,token,released:false});this.next.set(source,this.combat.clock+profile.interval);this.combos.set(source,{index,at:this.combat.clock});this.record(token,'windup');return true;
 }
 cooldown(source:string){return Math.max(0,(this.next.get(source)||0)-this.combat.clock)}
 private record(t:DamageToken,phase:string){this.events.push({id:t.id,source:t.source,phase,time:this.combat.clock});if(this.events.length>256)this.events.shift()}
 cancelPose(source:string){const p=this.poses.get(source);if(p&&!p.released)this.record(p.token,'cancelled-before-release');this.poses.delete(source)}
 replaceSource(source:string){const pose=this.poses.get(source);if(pose)this.audio.stopInstance(-Number(pose.token.id.split(':')[1]));this.cancelPose(source);this.next.delete(source);this.combos.delete(source);for(let i=this.strikes.length-1;i>=0;i--)if(this.strikes[i].pose.token.source===source){this.audio.stopInstance(-Number(this.strikes[i].pose.token.id.split(':')[1]));this.release(i)}}
 private createRoot(character:'lingyuan'|'yueli'){
  const root=new THREE.Group();root.userData.character=character;root.name='独立普攻轨迹';
  const material=new THREE.MeshStandardMaterial({color:character==='lingyuan'?0xa8d9f6:0xc3d7ff,emissive:character==='lingyuan'?0x155d9f:0x477ba6,emissiveIntensity:.6,metalness:.4,roughness:.25,transparent:true,opacity:.86});
  const mesh=new THREE.Mesh(character==='lingyuan'?blade:feather,material);mesh.rotation.z=character==='lingyuan'?-Math.PI/2:0;if(character==='yueli')mesh.scale.setScalar(.7);root.add(mesh);
  const rim=new THREE.Mesh(arc,new THREE.MeshBasicMaterial({color:character==='lingyuan'?0xd9bd7c:0xb9dcff,transparent:true,opacity:.55,depthWrite:false}));rim.rotation.x=Math.PI/2;root.add(rim);this.created++;return root;
 }
 update(dt:number){
  for(const [source,p] of this.poses){if(!this.combat.valid(p.token)){this.audio.stopInstance(-Number(p.token.id.split(':')[1]));this.poses.delete(source);continue}const profile=basicProfiles[p.token.character];p.age+=dt;
   if(!p.released&&p.age>=profile.windup){p.released=true;const u=this.combat.unit(source),origin=p.token.character==='yueli'?this.origin(source,p.combo)||new THREE.Vector3(u.position.x,u.position.y+.24,u.position.z):new THREE.Vector3(u.position.x,u.position.y,u.position.z),direction=new THREE.Vector3(Math.cos(p.yaw),0,-Math.sin(p.yaw));
    if(p.token.character==='yueli'){const target=this.combat.enemies(source).filter(t=>{const d=new THREE.Vector3(t.position.x-origin.x,0,t.position.z-origin.z).normalize();return d.dot(direction)>.75}).sort((a,b)=>Math.hypot(a.position.x-origin.x,a.position.z-origin.z)-Math.hypot(b.position.x-origin.x,b.position.z-origin.z))[0];if(target)direction.set(target.position.x-origin.x,target.position.y-origin.y,target.position.z-origin.z).normalize()}
    const index=this.pool.findIndex(g=>g.userData.character===p.token.character),root=index<0?this.createRoot(p.token.character):this.pool.splice(index,1)[0];if(index>=0)this.reused++;root.visible=true;this.scene.add(root);const point=origin.clone().addScaledVector(direction,.45);root.position.copy(point);root.rotation.y=p.yaw;
    if(p.token.character==='yueli')point.copy(origin);const weapon=p.token.character==='lingyuan'?this.weapon(source):null;if(weapon)point.copy(weapon.tip);this.strikes.push({pose:{...p},age:-Math.max(0,dt-(p.age-profile.windup)),origin,previous:point.clone(),point,direction,root,hits:new Set(),weapon:weapon?{a:weapon.grip,b:weapon.tip}:null,targets:new Map(this.combat.enemies(source).map(t=>[t.id,new THREE.Vector3(t.position.x,t.position.y,t.position.z)]))});this.audio.fireBasic(-Number(p.token.id.split(':')[1]),p.token.character,'release',p.combo,p.age,point);this.record(p.token,'release');
   }
   if(p.age>=profile.interval)this.poses.delete(source);
  }
  for(let i=this.strikes.length-1;i>=0;i--){const s=this.strikes[i],p=s.pose,profile=basicProfiles[p.token.character],previousAge=Math.max(0,s.age);s.age+=dt;const duration=p.token.character==='lingyuan'?profile.active+.12:profile.range/profile.speed+.14;
   if(!this.combat.valid(p.token)||s.age>duration){if(!this.combat.valid(p.token))this.audio.stopInstance(-Number(p.token.id.split(':')[1]));this.release(i);continue}
   const weapon=p.token.character==='lingyuan'?this.weapon(p.token.source):null;s.previous.copy(s.point);const travel=p.token.character==='lingyuan'?.45+(profile.range-.45)*Math.min(1,s.age/profile.active):Math.min(profile.range,s.age*profile.speed);s.point.copy(s.origin).addScaledVector(s.direction,travel);if(weapon)s.point.copy(weapon.tip);s.root.position.copy(s.point);if(weapon)s.root.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),weapon.tip.clone().sub(weapon.grip).normalize());if(p.token.character==='yueli')s.root.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0),s.direction);
   for(const child of s.root.children){const m=child as THREE.Mesh;(m.material as THREE.MeshStandardMaterial).opacity=.85*Math.min(1,(duration-s.age)/.12)}
   if(p.token.character==='lingyuan'&&previousAge>profile.active||p.token.character==='yueli'&&previousAge>profile.range/profile.speed)continue;
   for(const target of this.combat.enemies(p.token.source)){
    if(s.hits.has(target.id))continue;const center=new THREE.Vector3(target.position.x,target.position.y,target.position.z);
    const start=s.targets.get(target.id)||center,oldWeapon=s.weapon;const current:DamageVolume={id:'basic',shape:'capsule',a:weapon?weapon.grip:s.point,b:weapon?weapon.tip:s.point,radius:weapon?.085:p.token.character==='lingyuan'?.23:.12,start:0,end:p.token.character==='lingyuan'?profile.active:profile.range/profile.speed};const previous:DamageVolume={...current,a:oldWeapon?.a||s.previous,b:oldWeapon?.b||s.previous};const contact=sweepVolume(previous,current,start,center,target.radius,previousAge,s.age,target.halfHeight);if(contact===null)continue;
    const event=this.combat.damage(p.token,target.id);if(!event)continue;Object.assign(event,{region:weapon?'weapon-sweep':'ice-feather',contactAge:profile.windup+contact});s.hits.add(target.id);this.onHit(target.id,-Number(p.token.id.split(':')[1]),p.token.character,p.age+s.age);this.audio.fireBasic(-Number(p.token.id.split(':')[1]),p.token.character,'hit',p.combo,p.age+s.age,center);this.record(p.token,'hit:'+target.id);
    if(p.token.character==='yueli'){this.release(i);break}
   }
   if(weapon)s.weapon={a:weapon.grip.clone(),b:weapon.tip.clone()};for(const target of this.combat.enemies(p.token.source))s.targets.set(target.id,new THREE.Vector3(target.position.x,target.position.y,target.position.z));
  }
 }
 private release(index:number){const [s]=this.strikes.splice(index,1);s.root.visible=false;s.root.removeFromParent();if(this.pool.filter(g=>g.userData.character===s.pose.token.character).length<4)this.pool.push(s.root);else{s.root.traverse(o=>{if((o as THREE.Mesh).isMesh)((o as THREE.Mesh).material as THREE.Material).dispose()});s.root.clear()}}
 reset(){while(this.strikes.length)this.release(this.strikes.length-1);this.poses.clear();this.next.clear();this.combos.clear();this.events.length=0}
 snapshot(){return {poses:[...this.poses].map(([owner,p])=>({owner,age:p.age,combo:p.combo,yaw:p.yaw,released:p.released,id:p.token.id})),active:this.strikes.length,strikes:this.strikes.map(s=>({id:s.pose.token.id,age:s.age,point:s.point.toArray(),weapon:s.weapon?{a:s.weapon.a.toArray(),b:s.weapon.b.toArray()}:null})),pooled:this.pool.length,created:this.created,reused:this.reused,events:[...this.events]}}
}
