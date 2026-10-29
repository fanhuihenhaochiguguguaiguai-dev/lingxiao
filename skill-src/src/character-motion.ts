import * as THREE from 'three/webgpu';
import type { MotionProfile } from './motion-profile';
const V=()=>new THREE.Vector3();
/** Shared two-bone contact solver. Targets and lengths come from each actual skeleton. */
export class CharacterMotion {
 private readonly bones=new Map<string,THREE.Bone>();
 private readonly rest=new Map<string,{q:THREE.Quaternion;p:THREE.Vector3}>();
 private readonly legs:{hip:THREE.Bone;knee:THREE.Bone;foot:THREE.Bone;ankle:THREE.Vector3;pole:THREE.Vector3;footQ:THREE.Quaternion}[]=[];
 blinkOverride:number|null=null;
 private phase=0; private clock=0; private run=0; private weight=0; private nextBlink=2.9; private blinkStart=-10;
 private springs=new Map<string,{x:number;v:number}>();
 readonly sample={castPose:'none',gait:'idle',runBlend:0,contactErrors:[] as number[],blink:0,ikLegs:0};
 constructor(private actor:THREE.Group,private profile:Readonly<MotionProfile>){
  actor.updateWorldMatrix(true,true);const aq=actor.getWorldQuaternion(new THREE.Quaternion()).invert();
  actor.traverse(o=>{if((o as THREE.Bone).isBone){const b=o as THREE.Bone;this.bones.set(b.name.replace(/\./g,''),b);this.rest.set(b.name,{q:b.quaternion.clone(),p:b.position.clone()})}});
  for(const side of ['L','R']){
   const hip=this.bones.get('thigh'+side),knee=this.bones.get('shin'+side),foot=this.bones.get('foot'+side);if(!hip||!knee||!foot)continue;
   const h=actor.worldToLocal(hip.getWorldPosition(V())),k=actor.worldToLocal(knee.getWorldPosition(V())),a=actor.worldToLocal(foot.getWorldPosition(V()));
   let pole=k.clone().sub(h.clone().lerp(a,.5));if(pole.length()<.015)pole.set(0,0,1);else pole.normalize();pole.y=0;if(pole.z<0)pole.negate();if(pole.length()<.1)pole.set(0,0,1);
   this.legs.push({hip,knee,foot,ankle:a,pole:pole.normalize(),footQ:aq.clone().multiply(foot.getWorldQuaternion(new THREE.Quaternion()))});
  }this.sample.ikLegs=this.legs.length;
 }
 reset(full=false){if(full){this.phase=this.clock=this.run=this.weight=0;this.nextBlink=2.9;this.blinkStart=-10;this.springs.clear();this.blinkOverride=null;this.sample.gait='idle';this.sample.runBlend=this.sample.blink=0;this.sample.castPose='none';this.sample.contactErrors=[]}for(const [,b] of this.bones){const r=this.rest.get(b.name)!;b.quaternion.copy(r.q);b.position.copy(r.p)}this.actor.traverse(o=>{const m=o as THREE.Mesh;if(m.morphTargetDictionary?.Blink!==undefined&&m.morphTargetInfluences)m.morphTargetInfluences[m.morphTargetDictionary.Blink]=0})}
 private turn(name:string,x:number,y=0,z=0){const b=this.bones.get(name),r=b&&this.rest.get(b.name);if(b&&r)b.quaternion.copy(r.q).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(x,y,z)))}
 private aim(b:THREE.Bone,end:THREE.Vector3,target:THREE.Vector3){const p=b.getWorldPosition(V()),from=end.clone().sub(p).normalize(),to=target.clone().sub(p).normalize(),worldQ=b.getWorldQuaternion(new THREE.Quaternion());worldQ.premultiply(new THREE.Quaternion().setFromUnitVectors(from,to));const parentQ=b.parent!.getWorldQuaternion(new THREE.Quaternion()).invert();b.quaternion.copy(parentQ.multiply(worldQ));b.updateWorldMatrix(false,true)}
 update(dt:number,speed:number,running:boolean,air:number,vertical:number,casting:boolean,skill:number,time:number,turnRate:number,landing:number){
  const d=Math.min(dt,.08);this.clock+=d;this.run=THREE.MathUtils.damp(this.run,running?1:0,8,d);this.weight=THREE.MathUtils.damp(this.weight,speed>.05?1:0,10,d);
  const profile=this.profile,stride=THREE.MathUtils.lerp(profile.walkStride,profile.runStride,this.run);
  this.phase+=speed*d/stride;const cycle=this.phase%1;this.sample.gait=air>.01?'jump':speed>.05?(this.run>.5?'run':'walk'):'idle';this.sample.runBlend=this.run;
  // Reset just the controlled channels; material/face shape controls remain independent.
  for(const [name,b] of this.bones){const r=this.rest.get(b.name)!;if(/^(pelvis|spine|chest|neck|head|thigh|shin|foot|upper_arm|forearm|hand|hair|cape|skirt)/.test(name)){b.quaternion.copy(r.q);b.position.copy(r.p)}}
  const pelvis=this.bones.get('pelvis');if(pelvis){pelvis.position.y-=profile.pelvisDrop*this.weight*(1+this.run*.6);pelvis.position.y+=Math.sin(this.clock*1.8)*profile.breath-.025*Math.sin(Math.PI*landing/.18)}
  this.turn('chest',-.025*this.run+Math.sin(this.clock*1.8)*.006,Math.sin(cycle*Math.PI*2)*.025*this.weight);
  this.turn('head',0,Math.sin(this.clock*.42)*profile.headSway);for(const side of ['L','R'])this.turn('eye'+side,Math.sin(this.clock*.37)*.025,Math.sin(this.clock*.51)*.045);
  this.actor.updateWorldMatrix(true,true);this.sample.contactErrors=[];
  this.legs.forEach((leg,i)=>{
   const phase=(cycle+i*.5)%1,stance=THREE.MathUtils.lerp(profile.stance,profile.runStance,this.run),flight=phase>=stance,u=flight?(phase-stance)/(1-stance):phase/stance;
   const reach=stride*stance*.5;const z=(flight?-reach+reach*2*u:reach-reach*2*u)*this.weight;
   const lift=(flight?Math.sin(Math.PI*u)*THREE.MathUtils.lerp(profile.walkLift,profile.runLift,this.run):0)*this.weight;
   const target=leg.ankle.clone();target.z+=z;target.y+=lift;
   if(air>.01){target.z+=i===0?.09:-.08;target.y+=.08+Math.max(0,vertical)*.018}
   const world=this.actor.localToWorld(target.clone()),hip=leg.hip.getWorldPosition(V()),knee=leg.knee.getWorldPosition(V()),foot=leg.foot.getWorldPosition(V());
   const l1=hip.distanceTo(knee),l2=knee.distanceTo(foot),distance=THREE.MathUtils.clamp(hip.distanceTo(world),Math.abs(l1-l2)+.001,l1+l2-.001),direction=world.clone().sub(hip).normalize();
   const pole=leg.pole.clone().transformDirection(this.actor.matrixWorld);pole.addScaledVector(direction,-pole.dot(direction)).normalize();
   const along=(l1*l1-l2*l2+distance*distance)/(2*distance),height=Math.sqrt(Math.max(0,l1*l1-along*along));
   const desired=hip.clone().addScaledVector(direction,along).addScaledVector(pole,height);
   this.aim(leg.hip,knee,desired);this.aim(leg.knee,leg.foot.getWorldPosition(V()),world);
   const q=this.actor.getWorldQuaternion(new THREE.Quaternion()).multiply(leg.footQ);leg.foot.quaternion.copy(leg.foot.parent!.getWorldQuaternion(new THREE.Quaternion()).invert().multiply(q));leg.foot.updateWorldMatrix(false,true);
   if(!flight&&air<.01)this.sample.contactErrors.push(leg.foot.getWorldPosition(V()).distanceTo(world));
   const side=i===0?'L':'R',swing=Math.sin((cycle+i*.5)*Math.PI*2)*THREE.MathUtils.lerp(profile.armSwing,profile.runArmSwing,this.run)*this.weight;
   if(!casting){this.turn('upper_arm'+side,swing,0,(i===0?1:-1)*.015);this.turn('forearm'+side,-.06-.20*this.run)}
  });
  // Bounded, damped secondary bones. Skirts flare away from the stride; no full cloth claim.
  for(const [name,b] of this.bones){if(!/^(hair|cape|skirt)/.test(name))continue;const r=this.rest.get(b.name)!;let s=this.springs.get(name);if(!s){s={x:0,v:0};this.springs.set(name,s)}const target=THREE.MathUtils.clamp(speed*profile.secondaryLag+Math.sin(this.clock*2.1+name.length)*.012+Math.abs(turnRate)*.009,0,.16);s.v+=(target-s.x)*65*d;s.v*=Math.exp(-12*d);s.x+=s.v*d;b.quaternion.copy(r.q).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(s.x,0,0)))}
  // Per-character deterministic irregular timing; no fixed interval blink loop.
  if(this.clock>this.nextBlink){this.blinkStart=this.clock;this.nextBlink=this.clock+2.7+1.8*(.5+.5*Math.sin(this.clock*1.718))}
  const u=(this.clock-this.blinkStart)/.18;this.sample.blink=this.blinkOverride??(u>=0&&u<1?Math.sin(u*Math.PI):0);
  this.actor.traverse(o=>{const m=o as THREE.Mesh;const dict=m.morphTargetDictionary;if(dict&&m.morphTargetInfluences&&dict.Blink!==undefined)m.morphTargetInfluences[dict.Blink]=this.sample.blink});
  this.sample.castPose='none';
  if(casting&&profile.castStyle==='lunar'){
   const ultimate=skill===3,tidal=skill===2;const pulse=THREE.MathUtils.smoothstep(time,.04,ultimate?.85:.55)*(1-THREE.MathUtils.smoothstep(time,ultimate?1.8:1.05,ultimate?2.6:1.8));this.sample.castPose=ultimate?'moonfall-invoke':tidal?'moon-tide-raise':'frost-feather-release';
   const swing=Math.sin(cycle*Math.PI*2)*THREE.MathUtils.lerp(profile.armSwing,profile.runArmSwing,this.run)*this.weight;
   this.turn('upper_armR',-swing*(1-pulse)+(ultimate?-.90:tidal?-.30:-.55)*pulse,0,-.24*pulse);this.turn('forearmR',(-.06-.20*this.run)*(1-pulse)+(ultimate?-.68:tidal?-.42:-.48)*pulse);
   this.turn('upper_armL',swing*(1-pulse)+(ultimate?-.98:tidal?-.92:-.25)*pulse,0,(tidal?.20:.28)*pulse);this.turn('forearmL',(-.06-.20*this.run)*(1-pulse)+(ultimate?-.76:tidal?-.72:-.30)*pulse);
   this.turn('handL',-.12*pulse,(tidal?.18:0)*pulse,.10*pulse);this.turn('handR',-.10*pulse,0,-.06*pulse);this.turn('chest',-.035*pulse,(ultimate?0:tidal?-.06:.10)*pulse);
  }

 }
}
