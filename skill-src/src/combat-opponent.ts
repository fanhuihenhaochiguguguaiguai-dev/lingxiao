import * as THREE from 'three/webgpu';
import {CharacterAssets,characters,type CharacterId} from './characters';
import {CharacterMotion} from './character-motion';
import {CombatActions} from './combat-actions';
import {SpearActions} from './spear-actions';
import {CombatState,basicProfiles} from './combat-state';
import {BasicAttacks} from './basic-attacks';
import {SkillInstances} from './skill-instances';
import {findSpearTip} from './spear-anchor';
import {constrainPosition} from './studio-world';
import type {CastKind} from './instance-audio';
type ActorEntry={actor:THREE.Group;motion:CharacterMotion;actions:CombatActions;spear:SpearActions;weapon?:THREE.Bone;tip:THREE.Vector3|null};
/** One bounded local opponent. Uses the same assets, movement/IK, attacks and VFX. */
export class CombatOpponent {
 readonly root=new THREE.Group();enabled=true;private entry:ActorEntry|null=null;private cache=new Map<CharacterId,ActorEntry>();private ticket=0;
 private velocity=new THREE.Vector3();private heading=Math.PI;private castAge=0;private castSkill=0;private nextSkill=2.5;private skillCursor=1;private latestId=0;private basicCount=0;private skillCount=0;character:CharacterId='yueli';
 constructor(scene:THREE.Scene,private assets:CharacterAssets,private combat:CombatState,private basics:BasicAttacks,private instances:SkillInstances){this.root.name='独立骨骼对手';this.root.visible=false;scene.add(this.root)}
 async load(character:CharacterId){const ticket=++this.ticket;let entry=this.cache.get(character);
  if(!entry){const asset=await this.assets.instantiate(character);if(ticket!==this.ticket)return false;const actor=asset.scene as THREE.Group;actor.rotation.y=Math.PI/2;this.root.add(actor);entry={actor,motion:new CharacterMotion(actor,characters[character].motion),actions:new CombatActions(actor),spear:new SpearActions(actor,this.root),tip:null};let weapon:THREE.Bone|undefined;actor.traverse(o=>{if((o as THREE.Bone).isBone&&o.name.replace(/\./g,'')==='weaponR')weapon=o as THREE.Bone});entry.weapon=weapon;entry.tip=weapon?findSpearTip(actor,weapon):null;this.cache.set(character,entry)}
  if(ticket!==this.ticket)return false;if(this.entry)this.entry.actor.removeFromParent();this.entry=entry;this.root.add(entry.actor);this.character=character;this.root.visible=true;this.reset();return true;
 }
 hide(){this.ticket++;this.root.visible=false;this.velocity.set(0,0,0);this.basics.cancelPose('opponent')}
 handWorld(combo:number){if(!this.entry)return null;let hand:THREE.Object3D|undefined;const key=combo%2===0?'handR':'handL';this.entry.actor.traverse(o=>{if((o as THREE.Bone).isBone&&o.name.replace(/\./g,'')===key)hand=o});return hand?hand.getWorldPosition(new THREE.Vector3()):null}
 reset(){this.velocity.set(0,0,0);this.heading=Math.PI;this.root.position.set(5.2,0,0);this.root.rotation.y=this.heading;this.castSkill=this.castAge=0;this.nextSkill=2.5;this.skillCursor=1;this.basicCount=this.skillCount=0;if(this.entry){this.entry.actor.position.set(0,0,0);this.entry.actor.rotation.y=Math.PI/2;this.entry.motion.reset(true);this.entry.actions.reset()}this.sync()}
 sync(){if(!this.entry)return;const p=this.entry.actor.getWorldPosition(new THREE.Vector3());Object.assign(this.combat.unit('opponent').position,{x:p.x,y:p.y+.85,z:p.z});if(this.character==='lingyuan'&&this.castSkill===1&&this.entry.weapon&&this.entry.tip)this.instances.setAnchor(this.latestId,this.entry.weapon.localToWorld(this.entry.tip.clone()))}
 private endCast(){if(!this.entry||!this.castSkill)return;const position=this.entry.actor.getWorldPosition(new THREE.Vector3());this.root.position.set(position.x,0,position.z);this.entry.actions.captureTransition();this.entry.actor.position.set(0,0,0);this.entry.actor.rotation.y=Math.PI/2;this.castSkill=0}
 cast(skill:number){if(!Number.isInteger(skill)||skill<1||skill>3)return false;if(!this.entry||!this.root.visible||!this.combat.canAct('opponent'))return false;const body=this.entry.actor.getWorldPosition(new THREE.Vector3()),target=this.combat.unit('player').position,yaw=Math.atan2(-(target.z-body.z),target.x-body.x),origin=new THREE.Vector3(body.x,0,body.z),kind=`${this.character}-${skill}` as CastKind;
  if(this.character==='lingyuan'&&skill===1)origin.add(new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw)));
  this.basics.cancelPose('opponent');this.latestId=this.instances.spawn(kind,origin,yaw,'opponent').id;this.root.position.copy(origin);this.heading=this.root.rotation.y=yaw;this.entry.actor.position.set(this.character==='lingyuan'&&skill===1?-1:0,0,0);this.castAge=0;this.castSkill=skill;this.skillCount++;return true;
 }
 update(dt:number){if(!this.entry||!this.root.visible)return;const u=this.combat.unit('opponent'),p=this.combat.unit('player'),entry=this.entry;this.castAge+=dt;
  const gesture=this.character==='lingyuan'?(this.castSkill===1?3.3:this.castSkill===2?2:6.5):(this.castSkill===3?2.6:1.8);if(this.castAge>=gesture)this.endCast();
  const dx=p.position.x-u.position.x,dz=p.position.z-u.position.z,distance=Math.hypot(dx,dz),yaw=Math.atan2(-dz,dx),active=this.combat.canAct('opponent'),moving=this.enabled&&active;
  if(!active)this.endCast();
  const desired=new THREE.Vector3(),preferred=this.character==='lingyuan'?2:4;
  if(moving&&distance>.01){const travel=distance>preferred+.35?1:this.character==='yueli'&&distance<preferred-.85?-1:0;desired.set(dx/distance,0,dz/distance).multiplyScalar(travel*(distance>6?2.3:1.65)*u.slow*(this.castSkill?.65:1))}
  this.velocity.lerp(desired,1-Math.exp(-dt*8));if(!active)this.velocity.set(0,0,0);this.root.position.addScaledVector(this.velocity,dt);constrainPosition(this.root.position,this.velocity);
  const turn=Math.atan2(Math.sin(yaw-this.heading),Math.cos(yaw-this.heading));this.heading+=turn*(1-Math.exp(-dt*9));if(!this.castSkill&&!this.basics.poses.has('opponent'))this.root.rotation.y=this.heading;
  if(moving&&dt>0&&!this.castSkill){
   if(this.combat.clock>=this.nextSkill&&distance<(this.character==='lingyuan'?3.4:6.4)){const skill=this.skillCursor;this.skillCursor=skill%3+1;this.cast(skill);this.nextSkill=this.combat.clock+(skill===3?12:skill===2?8:6)}
   else if(distance<basicProfiles[this.character].range+.25&&this.basics.request('opponent',yaw)){this.basicCount++;this.root.rotation.y=yaw}
  }
  if(!this.castSkill){entry.actor.position.set(0,0,0);entry.actor.rotation.y=Math.PI/2}
  const speed=this.velocity.length(),casting=!!this.castSkill;entry.motion.update(dt,speed,speed>1.8,0,0,casting,this.castSkill,this.castAge,turn,0);
  if(casting&&this.character==='lingyuan')entry.spear.apply(this.castSkill,this.castAge,speed);
  const basic=this.basics.poses.get('opponent');if(basic)entry.actions.basic({...basic,age:basic.age+dt});entry.actions.transition(dt);entry.actions.feedback(u);entry.actor.updateWorldMatrix(true,true);this.sync();
 }
 snapshot(){return {character:this.character,visible:this.root.visible,ai:this.enabled,speed:this.velocity.length(),position:[...Object.values(this.combat.unit('opponent').position)],castSkill:this.castSkill,castAge:this.castAge,basicCount:this.basicCount,skillCount:this.skillCount,cachedActors:this.cache.size,bones:this.entry?this.boneIds():[]}}
 private boneIds(){const ids:string[]=[];this.entry!.actor.traverse(o=>{if((o as THREE.Bone).isBone)ids.push(o.uuid)});return ids}
}
