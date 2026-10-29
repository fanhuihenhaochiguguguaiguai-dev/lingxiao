import * as THREE from 'three/webgpu';
import type {SkillEffect} from './skill-registry';
import type {CastKind} from './instance-audio';
import type {DamageVolume} from './damage-volumes';
import {DragonEffect} from './dragon';
import {BindStar} from './bind-star';
import {StarVortex} from './star-vortex';
import {MoonFrost} from './moon-frost';
import {MoonTide} from './moon-tide';
import {Moonfall} from './moonfall';
const V=THREE.Vector3;
type Body={space:THREE.Object3D;head:THREE.Object3D;mesh:THREE.Mesh;segments:number;sides:number;body?:{point:THREE.Vector3;radius:number}[]};
/** Read current render transforms/buffers, never a second approximate dragon path. */
export function skillVolumes(kind:CastKind,effect:SkillEffect):DamageVolume[]{
 const out:DamageVolume[]=[];
 const capsule=(id:string,space:THREE.Object3D,a:THREE.Vector3,b:THREE.Vector3,radius:number,start:number,end:number)=>{
  const scale=space.getWorldScale(new V());out.push({id,shape:'capsule',a:space.localToWorld(a),b:space.localToWorld(b),radius:radius*Math.max(scale.x,scale.y,scale.z),start,end});
 };
 const cylinder=(id:string,space:THREE.Object3D,center:THREE.Vector3,radius:number,height:number,start:number,end:number,inner?:number)=>{
  const scale=space.getWorldScale(new V()),r=Math.max(scale.x,scale.z);out.push({id,shape:inner===undefined?'cylinder':'ring',a:space.localToWorld(center),radius:radius*r,inner:inner===undefined?undefined:Math.max(0,inner*r),height:height*scale.y,start,end});
 };
 const body=(g:Body,start:number,end:number,prefix='dragon')=>{
  const samples=g.body||Array.from({length:33},(_,i)=>{
   const row=Math.round(i/32*g.segments),attribute=g.mesh.geometry.getAttribute('position'),p=new V();
   for(let j=0;j<g.sides;j++)p.add(new V().fromBufferAttribute(attribute,row*(g.sides+1)+j));p.divideScalar(g.sides);let radius=0;
   for(let j=0;j<g.sides;j++)radius=Math.max(radius,p.distanceTo(new V().fromBufferAttribute(attribute,row*(g.sides+1)+j)));
   return {point:p,radius};
  });
  for(let i=1;i<samples.length;i++)capsule(prefix+':body:'+i,g.space,samples[i-1].point.clone(),samples[i].point.clone(),Math.max(samples[i-1].radius,samples[i].radius),start,end);
  capsule(prefix+':head',g.head,new V(-.30,0,0),new V(.45,-.035,0),.21,start,end);
 };
 const crystal=(id:string,mesh:THREE.Mesh,matrix:THREE.Matrix4,start:number,end:number)=>{
  if(!mesh.geometry.boundingBox)mesh.geometry.computeBoundingBox();const box=mesh.geometry.boundingBox!;const hx=(box.max.x-box.min.x)/2,hz=(box.max.z-box.min.z)/2,r=Math.max(hx,hz),cx=(box.max.x+box.min.x)/2,cz=(box.max.z+box.min.z)/2;
  const a=new V(cx,box.min.y+Math.min(r,(box.max.y-box.min.y)/2),cz).applyMatrix4(matrix),b=new V(cx,box.max.y-Math.min(r,(box.max.y-box.min.y)/2),cz).applyMatrix4(matrix),scale=new V().setFromMatrixScale(matrix);
  out.push({id,shape:'capsule',a,b,radius:r*Math.max(scale.x,scale.z),start,end});
 };
 const crystals=(mesh:THREE.InstancedMesh,start:number,end:number,prefix='crystal')=>{for(let i=0;i<mesh.count;i++){const m=new THREE.Matrix4();mesh.getMatrixAt(i,m);m.premultiply(mesh.matrixWorld);crystal(prefix+':'+i,mesh,m,start,end)}};
 (effect instanceof BindStar?effect.layers.circle.parent!:effect.group).updateWorldMatrix(true,true);
 switch(kind){
  case 'lingyuan-1':body((effect as DragonEffect).combatGeometry(),.95,3.65);break;
  case 'lingyuan-2':{
   const f=(effect as BindStar).combatGeometry();body(f.dragon.combatGeometry(),1,5.45);
   // The bounded rune interior is the binding field; beam/glitter outside it is decoration.
   cylinder('binding-field',f.circles[2],new V(0,1,0),3.03,2.3,1,5.45);
   for(let i=0;i<f.crystals.length;i++)f.crystals[i].children.forEach((object,j)=>{const mesh=object as THREE.Mesh;if(mesh.isMesh&&mesh.geometry.type!=='TorusGeometry')crystal(`binding-crystal:${i}:${j}`,mesh,mesh.matrixWorld,2.25,5.45)});
   break;
  }
  case 'lingyuan-3':{
   const f=(effect as StarVortex).combatGeometry();body(f,1.1,5.85);
   cylinder('vortex-core',f.ground,new V(0,2.4,0),2.15,4.8,1.7,4.85);
   const shock=f.shock[2];if(shock.visible)cylinder('vortex-burst',shock.parent!,new V(0,.95,0),shock.scale.x,2.2,4.85,5.85);
   break;
  }
  case 'yueli-1':{
   const f=(effect as MoonFrost).combatGeometry();
   for(let i=0;i<24;i++){const a=.25+(Math.PI*2-.5)*i/24,b=.25+(Math.PI*2-.5)*(i+1)/24;capsule('crescent:'+i,f.crescent,new V(.78*Math.cos(a),.78*Math.sin(a),0),new V(.78*Math.cos(b),.78*Math.sin(b),0),.12,.85,2.15)}
   crystals(f.feathers,.85,2.8,'frost-feather');
   cylinder('ice-lotus',f.bloom,new V(0,.4,0),1.12,1.6,2.12,3.3);
   break;
  }
  case 'yueli-2':{
   const f=(effect as MoonTide).combatGeometry();cylinder('tide-field',f.ground,new V(0,1.1,0),3.10,2.4,1.45,7);
   crystals(f.crystals,1.45,7);
   // The expanding frosted wave is an annulus, not a filled four-metre disk.
   if(f.wave.visible){const p=f.wave.geometry.getAttribute('position'),r=Math.hypot(p.getX(0),p.getZ(0));cylinder('tide-front',f.wave,new V(0,.24,0),r+.68,.65,1.45,2.8,r)}
   break;
  }
  case 'yueli-3':{
   const ultimate=effect as Moonfall,f=ultimate.combatGeometry();body(f.dragon.combatGeometry(),1.65,9.4,'ice-dragon');
   // Nine rune rings bound a 3.95m storm; the larger fading shock is a separate front.
   cylinder('moonfall-domain',ultimate.group,new V(1.5,1.7,0),3.95,3.7,3.8,9.4);
   crystals(f.crystals,3.8,9.4);
   for(let i=0;i<3;i++){const m=new THREE.Matrix4();f.shock.getMatrixAt(i,m);const scale=new V().setFromMatrixScale(m);cylinder('moonfall-shock:'+i,ultimate.group,new V(1.5,.32,0),scale.x+.025,.7,3.75+i*.2,4.65+i*.3,Math.max(0,scale.x-.025))}
   break;
  }
 }
 return out;
}
