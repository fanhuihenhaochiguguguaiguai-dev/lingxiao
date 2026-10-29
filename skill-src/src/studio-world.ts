import * as THREE from 'three/webgpu';
export const ORIGINAL_MOVE_RADIUS=9.5;
export const MOVE_RADIUS=ORIGINAL_MOVE_RADIUS*Math.sqrt(5);
export const PLATFORM_RADIUS=MOVE_RADIUS+7.5;
/** Training feedback only: no health, damage or combat authority is implied. */
export interface TrainingHit {scope:'training';instanceId?:number;character:string;skill:number;target:number;time:number;tick?:number;position:number[]}
/** Shared radial collision boundary; preserve tangential motion at its edge. */
export function constrainPosition(position:THREE.Vector3,velocity?:THREE.Vector3){
 const radius=Math.hypot(position.x,position.z);if(radius<=MOVE_RADIUS)return;
 const nx=position.x/radius,nz=position.z/radius;position.x=nx*MOVE_RADIUS;position.z=nz*MOVE_RADIUS;
 if(velocity){const outward=velocity.x*nx+velocity.z*nz;if(outward>0){velocity.x-=outward*nx;velocity.z-=outward*nz}}
}
export class PracticeTargets {
 readonly group=new THREE.Group();
 readonly hits:TrainingHit[]=[];
 readonly slowStates:{until:number;factor:number;velocity:THREE.Vector3}[]=[0,1,2].map(()=>({until:0,factor:1,velocity:new THREE.Vector3()}));
 private readonly slowSources=[0,1,2].map(()=>new Map<number,{until:number;factor:number}>());
 clock=0;
 get centers(){return this.positions}
 reset(){const initial=[[4.1,.6,0],[-6,.6,3],[2,.6,-7]];this.positions.forEach((p,i)=>{p.fromArray(initial[i]);this.group.children[i].position.copy(p)});this.hits.length=0;this.clock=0;this.lastHit.clear();for(const sources of this.slowSources)sources.clear();for(const s of this.slowStates){s.until=0;s.factor=1;s.velocity.set(0,0,0)}}
 private readonly positions=[new THREE.Vector3(4.1,.6,0),new THREE.Vector3(-6,.6,3),new THREE.Vector3(2,.6,-7)];
 private readonly lastHit=new Map<number,number>();private readonly seen=new Set<number>();private previous=new THREE.Vector3();private hasPrevious=false;
 constructor(parent:THREE.Object3D){parent.add(this.group);this.group.name='技能反馈晶体';for(const p of this.positions){const mesh=new THREE.Mesh(new THREE.OctahedronGeometry(.45),new THREE.MeshStandardMaterial({color:0x537a9e,metalness:.4,roughness:.3,emissive:0x193457,emissiveIntensity:.3}));mesh.position.copy(p);this.group.add(mesh)}}
 begin(){this.seen.clear();this.hasPrevious=false}
 applyInstanceHit(instanceId:number,character:string,skill:number,target:number,age:number,tick:number,slow=1){const hit:TrainingHit={scope:'training',instanceId,character,skill,target,time:age,tick,position:this.positions[target].toArray()};this.hits.push(hit);if(this.hits.length>2048)this.hits.shift();this.lastHit.set(target,1);if(slow<1){this.slowSources[target].set(instanceId,{until:this.clock+1.2,factor:slow});this.slowStates[target].until=this.clock+1.2;this.slowStates[target].factor=Math.min(this.slowStates[target].factor,slow)}window.dispatchEvent(new CustomEvent('lingyuan:skill-hit',{detail:hit}))}
 update(dt:number){this.clock+=dt;this.slowStates.forEach((s,i)=>{const sources=this.slowSources[i];for(const [id,entry] of sources)if(this.clock>=entry.until)sources.delete(id);s.factor=Math.min(1,...[...sources.values()].map(v=>v.factor));s.until=Math.max(0,...[...sources.values()].map(v=>v.until));this.positions[i].addScaledVector(s.velocity,dt*s.factor);this.group.children[i].position.copy(this.positions[i])});for(let i=0;i<this.group.children.length;i++){const o=this.group.children[i] as THREE.Mesh;const energy=Math.max(0,(this.lastHit.get(i)||0)-dt);this.lastHit.set(i,energy);(o.material as THREE.MeshStandardMaterial).emissiveIntensity=.3+energy*3;o.rotation.y+=dt*.3}}
 test(point:THREE.Vector3,radius:number,character:string,skill:number,time:number){
  const a=this.hasPrevious?this.previous:point,segment=point.clone().sub(a),length=segment.lengthSq();
  this.positions.forEach((target,i)=>{if(this.seen.has(i))return;const u=length?THREE.MathUtils.clamp(target.clone().sub(a).dot(segment)/length,0,1):0;const nearest=a.clone().addScaledVector(segment,u);if(nearest.distanceTo(target)>radius+.45)return;this.seen.add(i);this.lastHit.set(i,1);const hit:TrainingHit={scope:'training',character,skill,target:i,time,position:target.toArray()};this.hits.push(hit);if(this.hits.length>30)this.hits.shift();window.dispatchEvent(new CustomEvent('lingyuan:skill-hit',{detail:hit}))});
  this.previous.copy(point);this.hasPrevious=true;
 }
}
