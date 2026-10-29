import * as THREE from 'three/webgpu';
import {basicProfiles,type CombatUnit} from './combat-state';
import type {BasicPose} from './basic-attacks';
const smooth=THREE.MathUtils.smoothstep;
/** Upper-body attacks layer over the existing leg/IK controller. */
export class CombatActions {
 private bones=new Map<string,THREE.Bone>();private rest=new Map<string,THREE.Quaternion>();
 private from=new Map<string,THREE.Quaternion>();private remaining=0;private blendDuration=.18;
 constructor(private actor:THREE.Group){actor.traverse(o=>{if((o as THREE.Bone).isBone){const b=o as THREE.Bone;this.bones.set(b.name.replace(/\./g,''),b);this.rest.set(b.name,b.quaternion.clone())}})}
 private blend(name:string,x:number,y:number,z:number,weight:number){const b=this.bones.get(name),r=b&&this.rest.get(b.name);if(!b||!r)return;const to=r.clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(x,y,z)));b.quaternion.slerp(to,weight)}
 captureTransition(){this.from.clear();for(const [name,b] of this.bones)if(/^(chest|spine|neck|head|upper_arm|forearm|hand|weapon)/.test(name))this.from.set(name,b.quaternion.clone());this.remaining=this.blendDuration}
 reset(){this.from.clear();this.remaining=0}
 transition(dt:number){if(this.remaining<=0)return;this.remaining=Math.max(0,this.remaining-dt);const alpha=1-this.remaining/this.blendDuration;for(const [name,q] of this.from){const b=this.bones.get(name)!;b.quaternion.slerpQuaternions(q,b.quaternion.clone(),alpha)}if(!this.remaining)this.from.clear()}
 basic(p:BasicPose){const profile=basicProfiles[p.token.character],a=p.age,load=smooth(a,0,profile.windup),strike=smooth(a,profile.windup,profile.windup+.1),weight=load*(1-smooth(a,profile.windup+profile.active,profile.interval));
  if(p.token.character==='lingyuan'){
   const sweep=p.combo===1;this.blend('chest',-.04*load+.10*strike,sweep?.26-.55*strike:-.12+.20*strike,0,weight);this.blend('upper_armR',-.58*load-.38*strike,0,sweep?-.22+.65*strike:-.14,weight);this.blend('forearmR',-.78*load+.62*strike,0,0,weight);this.blend('handR',-.1,.1*strike,0,weight);this.blend('upper_armL',-.30,0,.25,weight);this.blend('forearmL',-.55+.2*strike,0,0,weight);
  }else{
   const side=p.combo%2===0?'R':'L',other=side==='R'?'L':'R',sign=side==='R'?-1:1;this.blend('chest',-.025,-sign*.12*load+sign*.16*strike,0,weight);this.blend('upper_arm'+side,-.65*load-.24*strike,0,sign*.20,weight);this.blend('forearm'+side,-.75*load+.46*strike,0,0,weight);this.blend('hand'+side,-.16,.12*sign,.12*sign,weight);this.blend('upper_arm'+other,-.16,0,-sign*.16,weight);
  }
 }
 feedback(unit:CombatUnit){const chest=this.bones.get('chest');if(chest&&unit.hitFlash>0)chest.quaternion.multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(.16*unit.hitFlash/.22,0,.045*Math.sin(unit.hitFlash*35))));if(unit.alive)return;
  const fall=smooth(unit.deadFor,0,.8);this.blend('chest',.65,0,0,fall);for(const side of ['L','R']){this.blend('thigh'+side,-.65,0,0,fall);this.blend('shin'+side,1.25,0,0,fall);this.blend('upper_arm'+side,.1,0,side==='L'?.12:-.12,fall)}this.actor.position.y-=.25*fall;
 }
}
