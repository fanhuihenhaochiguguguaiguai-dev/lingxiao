import * as THREE from 'three/webgpu';
const V=THREE.Vector3,UP=new V(0,1,0),SIDE=new V(0,0,1);
export type DragonFrame={p:THREE.Vector3;forward:THREE.Vector3;up:THREE.Vector3;side:THREE.Vector3};
/** Convention: u=0 is the head, u=1 is the tail. Artist-authored paths stay external. */
export class DragonFrames {
 readonly frames:DragonFrame[];
 private readonly rotation=new THREE.Quaternion();
 constructor(readonly segments:number,private readonly bank:'upright'|'transport'='upright',private readonly directionSpan=1){this.frames=Array.from({length:segments+1},()=>({p:new V(),forward:new V(1,0,0),up:UP.clone(),side:SIDE.clone()}))}
 update(sample:(u:number)=>THREE.Vector3){
  const n=this.segments;for(let i=0;i<=n;i++)this.frames[i].p.copy(sample(i/n));
  for(let i=0;i<=n;i++){
   const f=this.frames[i];f.forward.copy(this.frames[Math.max(0,i-this.directionSpan)].p).sub(this.frames[Math.min(n,i+this.directionSpan)].p);
   if(f.forward.lengthSq()<1e-10)f.forward.copy(i?this.frames[i-1].forward:new V(1,0,0));f.forward.normalize();
  }
  for(let j=0;j<=n;j++){
   const i=this.bank==='transport'?n-j:j,f=this.frames[i],previous=this.bank==='transport'?this.frames[i+1]:this.frames[i-1];
   const projected=UP.clone().addScaledVector(f.forward,-f.forward.y);
   if(this.bank==='transport'&&previous){this.rotation.setFromUnitVectors(previous.forward,f.forward);f.up.copy(previous.up).applyQuaternion(this.rotation)}
   else if(projected.lengthSq()>.025)f.up.copy(projected).normalize();
   else if(previous){this.rotation.setFromUnitVectors(previous.forward,f.forward);f.up.copy(previous.up).applyQuaternion(this.rotation)}
   else{f.up.copy(SIDE).addScaledVector(f.forward,-f.forward.z).normalize()}
   f.side.crossVectors(f.forward,f.up).normalize();f.up.crossVectors(f.side,f.forward).normalize();
  }
 }
 at(u:number){return this.frames[Math.round(THREE.MathUtils.clamp(u,0,1)*this.segments)]}
}
/** A deterministic time history resampled by distance, with no shared cast state. */
export class DragonTrail {
 private readonly points=Array.from({length:257},()=>new V());private readonly distances=new Float64Array(257);private total=0;
 update(time:number,privateLength:number,path:(t:number)=>THREE.Vector3){
  this.length=privateLength;this.total=0;
  for(let i=0;i<this.points.length;i++){this.points[i].copy(path(time-i*.04));if(i)this.total+=this.points[i].distanceTo(this.points[i-1]);this.distances[i]=this.total}
 }
 private length=1;
 sample(u:number){const d=THREE.MathUtils.clamp(u,0,1)*this.length;if(d>=this.total){const last=this.points.at(-1)!,dir=last.clone().sub(this.points.at(-2)!);if(dir.lengthSq()<1e-10)dir.set(-1,0,0);return last.clone().addScaledVector(dir.normalize(),d-this.total)}let i=1;while(this.distances[i]<d)i++;return this.points[i-1].clone().lerp(this.points[i],(d-this.distances[i-1])/Math.max(1e-9,this.distances[i]-this.distances[i-1]))}
}
