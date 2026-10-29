import * as THREE from 'three/webgpu';
import {constrainPosition,MOVE_RADIUS} from './studio-world';
const ease=(a:number,b:number,t:number)=>{const x=THREE.MathUtils.clamp((t-a)/(b-a),0,1);return x*x*(3-2*x)};
/** Existing Lingyuan skill choreography, reused for either independently posed actor. */
export class SpearActions {
 private bones=new Map<string,THREE.Bone>();private rest=new Map<string,THREE.Quaternion>();private speed=0;private skill=1;
 readonly sample={boneSample:0};
 constructor(private actor:THREE.Group,private stage:THREE.Group){actor.traverse(o=>{if((o as THREE.Bone).isBone){const b=o as THREE.Bone,key=b.name.replace(/\./g,'');this.bones.set(key,b);this.rest.set(key,b.quaternion.clone())}})}
 apply(skill:number,time:number,speed:number){this.skill=skill;this.speed=speed;if(skill===1)this.pose(time);else if(skill===2)this.poseBind(time);else this.poseUltimate(time)}
private rotateBone(name:string,x:number,y:number,z:number){const key=name.replace(/\./g,'');const b=this.bones.get(key),q=this.rest.get(key);if(!b||!q)return;const delta=new THREE.Quaternion().setFromEuler(new THREE.Euler(x,y,z));b.quaternion.copy(q).multiply(delta);}
// Keep the walk clip on the lower body when translating during a cast.
private resetCastingBones(){for(const [name,b] of this.bones){if(this.speed>.08&&this.skill!==3&&/^(thigh|shin|foot|toe)/i.test(name))continue;const q=this.rest.get(name);if(q)b.quaternion.copy(q)}}
private pose(t:number){
 const wind=ease(.05,.72,t)*(1-ease(1.05,1.55,t));const dash=ease(.82,1.22,t)*(1-ease(1.7,2.0,t));const sweep=Math.sin(Math.PI*ease(1.65,3.15,t));const end=ease(3.25,4.3,t);
 this.resetCastingBones();
 this.rotateBone('chest',-.04*wind+.13*dash, -.12*wind+.35*sweep, .05*sweep);
 this.rotateBone('pelvis',0,.22*sweep,0);
 this.rotateBone('upper_arm.R',-.34*wind-.66*dash-.48*sweep,0,-.18*wind+.16*sweep);
 this.rotateBone('forearm.R',-.45*wind-.58*dash-.65*sweep,0,.12*sweep);
 this.rotateBone('hand.R',-.12*wind,-.12*sweep,.18*sweep);
 this.rotateBone('weapon.R',0,.15*sweep,.12*sweep);
 this.rotateBone('upper_arm.L',.12*wind+.20*dash,0,.18*sweep);
 if(this.speed<=.08){this.rotateBone('thigh.L',.12*dash-.18*sweep,0,0);this.rotateBone('thigh.R',-.18*dash+.18*sweep,0,0)}
 for(const side of ['L','R']){this.rotateBone('hair01.'+side,.08*Math.sin(t*8)*(wind+dash+sweep),0,0);this.rotateBone('hair02.'+side,.13*Math.sin(t*8-.8)*(wind+dash+sweep),0,0);this.rotateBone('cape01.'+side,.08*Math.sin(t*7-.5)*(wind+dash+sweep),0,0);}
 this.actor.position.x=-1+2.25*ease(.95,1.72,t);this.actor.position.y=0;this.actor.rotation.y=Math.PI/2+(.50*sweep)*(1-end);this.stage.updateWorldMatrix(true,false);const position=this.stage.localToWorld(this.actor.position.clone()),radius=Math.hypot(position.x,position.z);if(radius>MOVE_RADIUS){constrainPosition(position);this.actor.position.copy(this.stage.worldToLocal(position))}
 const bone=this.bones.get('forearmR');this.sample.boneSample=bone?.quaternion.x??0;
}
private poseBind(t:number){
 const raise=ease(.05,.85,t)*(1-ease(5.45,6.3,t)),hold=ease(.8,2.1,t)*(1-ease(5.4,6.3,t));
 this.resetCastingBones();
 this.rotateBone('chest',-.06*raise,.12*hold,0);this.rotateBone('upper_arm.R',-.72*raise,0,-.28*raise);this.rotateBone('forearm.R',-.72*raise,0,.14*raise);this.rotateBone('hand.R',-.15*raise,0,.15*raise);this.rotateBone('weapon.R',0,0,-.16*raise);
 this.rotateBone('upper_arm.L',-.25*raise,0,.42*raise);this.rotateBone('forearm.L',-.2*raise,0,-.2*raise);
 for(const side of ['L','R']){this.rotateBone('hair01.'+side,.07*Math.sin(t*4)*hold,0,0);this.rotateBone('hair02.'+side,.12*Math.sin(t*4-.7)*hold,0,0);this.rotateBone('cape01.'+side,.10*Math.sin(t*4-.4)*hold,0,0)}
 this.actor.position.set(0,0,0);this.actor.rotation.y=Math.PI/2;this.sample.boneSample=this.bones.get('forearmR')?.quaternion.x??0;
}
private poseUltimate(t:number){
 const charge=ease(.05,.9,t)*(1-ease(6.2,7.3,t));const lift=ease(.85,1.8,t)*(1-ease(5.25,6.45,t));const impact=Math.sin(Math.PI*ease(4.4,5.3,t));
 this.resetCastingBones();
 this.rotateBone('pelvis',-.06*lift,0,.05*impact);this.rotateBone('chest',-.12*charge+.12*impact,.10*lift,.05*impact);
 this.rotateBone('upper_arm.R',-1.0*charge-.25*impact,0,-.28*charge);this.rotateBone('forearm.R',-.85*charge-.2*impact,0,.12*charge);this.rotateBone('hand.R',-.15*charge,0,.12*charge);this.rotateBone('weapon.R',0,0,-.18*charge);
 this.rotateBone('upper_arm.L',-.35*charge,0,.48*charge);this.rotateBone('forearm.L',-.22*charge,0,-.2*charge);
 this.rotateBone('thigh.L',-.20*lift,0,0);this.rotateBone('thigh.R',.25*lift,0,0);this.rotateBone('shin.L',.20*lift,0,0);this.rotateBone('shin.R',-.20*lift,0,0);
 for(const side of ['L','R']){this.rotateBone('hair01.'+side,.08*Math.sin(t*4)*charge,0,0);this.rotateBone('hair02.'+side,.14*Math.sin(t*4-.7)*charge,0,0);this.rotateBone('cape01.'+side,.11*Math.sin(t*4-.4)*charge,0,0)}
 this.actor.position.set(0,.65*lift,0);this.actor.rotation.y=Math.PI/2+.12*impact;this.sample.boneSample=this.bones.get('forearmR')?.quaternion.x??0;
}

}
