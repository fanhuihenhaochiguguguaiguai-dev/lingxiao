import type {Point3} from './combat-state';

/** World-space combat volumes. Decoration and warning geometry never enter this list. */
export interface DamageVolume {
 id:string;shape:'capsule'|'cylinder'|'ring';a:Point3;b?:Point3;radius:number;
 inner?:number;height?:number;start:number;end:number;
}
const sub=(a:Point3,b:Point3)=>({x:a.x-b.x,y:a.y-b.y,z:a.z-b.z});
const length=(v:Point3)=>Math.hypot(v.x,v.y,v.z);
const mix=(a:Point3,b:Point3,t:number)=>({x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t,z:a.z+(b.z-a.z)*t});
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
const clamp=(x:number,a=0,b=1)=>Math.max(a,Math.min(b,x));
export function volumeDistance(v:DamageVolume,p:Point3):number {
 if(v.shape==='capsule'){
  const b=v.b||v.a,d=sub(b,v.a),q=sub(p,v.a),l=d.x*d.x+d.y*d.y+d.z*d.z;
  const t=l?clamp((q.x*d.x+q.y*d.y+q.z*d.z)/l):0;
  return length(sub(p,mix(v.a,b,t)))-v.radius;
 }
 const radial=Math.hypot(p.x-v.a.x,p.z-v.a.z),outer=radial-v.radius;
 const side=v.shape==='ring'?Math.max(outer,(v.inner||0)-radial):outer;
 const vertical=Math.abs(p.y-v.a.y)-(v.height||0)/2;
 return Math.hypot(Math.max(0,side),Math.max(0,vertical))+Math.min(0,Math.max(side,vertical));
}
/** Distance between two segments, used for the full upright hurt capsule. */
function segmentDistance(a:Point3,b:Point3,c:Point3,d:Point3){
 const u=sub(b,a),v=sub(d,c),w=sub(a,c),dot=(x:Point3,y:Point3)=>x.x*y.x+x.y*y.y+x.z*y.z;
 const aa=dot(u,u),bb=dot(u,v),cc=dot(v,v),dd=dot(u,w),ee=dot(v,w),den=aa*cc-bb*bb;
 let s=aa<1e-12?0:den>1e-12?clamp((bb*ee-cc*dd)/den):0,t=cc<1e-12?0:(bb*s+ee)/cc;
 if(t<0){t=0;s=aa?clamp(-dd/aa):0}else if(t>1){t=1;s=aa?clamp((bb-dd)/aa):0}
 return length(sub(mix(a,b,s),mix(c,d,t)));
}
export function hurtDistance(v:DamageVolume,p:Point3,halfHeight=0){
 if(!halfHeight)return volumeDistance(v,p);
 if(v.shape==='capsule')return segmentDistance(v.a,v.b||v.a,{...p,y:p.y-halfHeight},{...p,y:p.y+halfHeight})-v.radius;
 return volumeDistance(v,{...p,y:clamp(v.a.y,p.y-halfHeight,p.y+halfHeight)});
}
/** Continuous relative motion, clipped to the real active interval. No frame-count damage. */
export function sweepVolume(previous:DamageVolume,current:DamageVolume,from:Point3,to:Point3,targetRadius:number,age0:number,age1:number,halfHeight=0):number|null {
 if(age1<=age0||age1<current.start||age0>current.end)return null;
 const lo=clamp((current.start-age0)/(age1-age0)),hi=clamp((current.end-age0)/(age1-age0));
 if(lo>hi)return null;
 const velocity=length(sub(to,from))+Math.max(length(sub(current.a,previous.a)),length(sub(current.b||current.a,previous.b||previous.a)))+Math.abs(current.radius-previous.radius)+Math.abs((current.inner||0)-(previous.inner||0))+Math.abs((current.height||0)-(previous.height||0))/2;
 // Signed distance is Lipschitz: never step across an untested contact, including fast projectiles.
 let t=lo;
 for(let iteration=0;iteration<192;iteration++){
  const v:DamageVolume={...current,a:mix(previous.a,current.a,t),b:mix(previous.b||previous.a,current.b||current.a,t),radius:lerp(previous.radius,current.radius,t),inner:lerp(previous.inner||0,current.inner||0,t),height:lerp(previous.height||0,current.height||0,t)};
  const distance=hurtDistance(v,mix(from,to,t),halfHeight)-targetRadius;
  if(distance<=1e-5)return age0+(age1-age0)*t;
  if(t>=hi||velocity<1e-10)return null;
  t=Math.min(hi,t+Math.max(1e-8,distance/velocity*.95));
 }
 return null;
}
