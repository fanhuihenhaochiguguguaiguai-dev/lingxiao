import * as THREE from 'three/webgpu';
import { DragonEffect } from './dragon';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const TAU=Math.PI*2;
const smooth=(a:number,b:number,t:number)=>{const x=THREE.MathUtils.clamp((t-a)/(b-a),0,1);return x*x*(3-2*x)};
type Layer='dragon'|'circle'|'crystals'|'beams'|'chains'|'particles';
const lineMat=new THREE.MeshBasicMaterial({color:0x61c6ff,transparent:true,opacity:.78,blending:THREE.AdditiveBlending,depthWrite:false});
const goldMat=new THREE.MeshStandardMaterial({color:0xd4a75d,metalness:.8,roughness:.3,emissive:0x3f2007,emissiveIntensity:.3});
const crystalMat=new THREE.MeshPhysicalMaterial({color:0x2781ed,metalness:.24,roughness:.16,transparent:true,opacity:.72,depthWrite:false,side:THREE.DoubleSide,emissive:0x063780,emissiveIntensity:.35});
const beamMat=new THREE.MeshBasicMaterial({color:0x48aaff,transparent:true,opacity:.05,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});
function tube(points:THREE.Vector3[], radius:number, material:THREE.Material, closed=false){return new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points,closed),Math.max(24,points.length*3),radius,5,closed),material)}
function ring(radius:number,thick:number,material:THREE.Material){const m=new THREE.Mesh(new THREE.TorusGeometry(radius,thick,6,96),material);m.rotation.x=Math.PI/2;return m}
function mergeStatic(group:THREE.Group){
 group.updateMatrixWorld(true);const inv=group.matrixWorld.clone().invert();const buckets=new Map<THREE.Material,THREE.BufferGeometry[]>();
 group.traverse(o=>{if((o as THREE.Mesh).isMesh){const m=o as THREE.Mesh;const mat=m.material as THREE.Material;const geometry=m.geometry.clone().applyMatrix4(inv.clone().multiply(m.matrixWorld));const list=buckets.get(mat)||[];list.push(geometry);buckets.set(mat,list)}});
 group.clear();for(const [material,geometries] of buckets){const merged=mergeGeometries(geometries);if(merged)group.add(new THREE.Mesh(merged,material));for(const g of geometries)g.dispose()}
}
export class BindStar {
 readonly dragon:DragonEffect;
 readonly layers:Record<Layer,THREE.Group>;
 private circles:THREE.Group[]=[]; private crystals:THREE.Group[]=[]; private beams:THREE.Mesh[]=[];private chainLinks:THREE.InstancedMesh;private particles:THREE.InstancedMesh;private stones:THREE.InstancedMesh;private dummy=new THREE.Object3D();private quality:'high'|'ultra'='high';
 constructor(scene:THREE.Object3D){
  this.dragon=new DragonEffect(scene);this.dragon.group.name='Bind Star dragon';
  // The first-skill dragon's sweep rings are detached from this instance only.
  for(const child of [...this.dragon.group.children].slice(5))this.dragon.group.remove(child);
  this.layers={dragon:this.dragon.group,circle:new THREE.Group(),crystals:new THREE.Group(),beams:new THREE.Group(),chains:new THREE.Group(),particles:new THREE.Group()};
  for(const [name,g] of Object.entries(this.layers)){g.name='skill02 '+name;if(name!=='dragon')scene.add(g);g.visible=false;}
  for(let k=0;k<3;k++){
   const g=new THREE.Group();g.position.y=.045+k*.026;this.layers.circle.add(g);this.circles.push(g);
   for(const r of k===0?[.65,1.22]:k===1?[1.8,2.06]:[2.85,3.03])g.add(ring(r,k===2?.013:.009,k===1?goldMat:lineMat));
   const points:THREE.Vector3[]=[];const n=k===0?8:k===1?10:12;const radius=k===0?1.1:k===1?1.88:2.94;
   for(let i=0;i<n*2;i++){const a=i*TAU/(n*2),r=radius*(i%2?.88:1);points.push(new THREE.Vector3(Math.cos(a)*r,0,Math.sin(a)*r))}g.add(tube(points,.009,k===1?goldMat:lineMat,true));
   for(let i=0;i<n;i++){const a=i*TAU/n,r=radius*.91;const symbol=new THREE.Group();symbol.position.set(Math.cos(a)*r,.01,Math.sin(a)*r);symbol.rotation.y=-a;symbol.add(tube([new THREE.Vector3(-.05,0,-.07),new THREE.Vector3(0,0,.07),new THREE.Vector3(.05,0,-.07)],.006,k===1?goldMat:lineMat));g.add(symbol)}
   mergeStatic(g);
  }
  const crystalGeo=new THREE.OctahedronGeometry(1,0);crystalGeo.scale(.18,.55,.16);crystalGeo.translate(0,.55,0);
  for(let i=0;i<10;i++){const a=i*TAU/10;const g=new THREE.Group();g.position.set(Math.cos(a)*2.95,.03,Math.sin(a)*2.95);g.rotation.z=(i%2?-.12:.12);const main=new THREE.Mesh(crystalGeo,crystalMat);main.scale.set(1,1.15+(i%3)*.16,1);g.add(main);const small=new THREE.Mesh(crystalGeo,crystalMat);small.position.set(.22,0,.1);small.scale.set(.48,.55,.48);g.add(small);g.add(ring(.23,.012,goldMat));this.layers.crystals.add(g);this.crystals.push(g);
   const beam=new THREE.Mesh(new THREE.CylinderGeometry(.04,.15,1.9,12,1,true),beamMat);beam.position.set(Math.cos(a)*2.94,.95,Math.sin(a)*2.94);this.layers.beams.add(beam);this.beams.push(beam);
  }
  this.chainLinks=new THREE.InstancedMesh(new THREE.TorusGeometry(.09,.018,5,10),goldMat,100);this.chainLinks.frustumCulled=false;this.layers.chains.add(this.chainLinks);
  this.particles=new THREE.InstancedMesh(new THREE.OctahedronGeometry(.045,0),lineMat,120);this.particles.frustumCulled=false;this.layers.particles.add(this.particles);
  this.stones=new THREE.InstancedMesh(new THREE.DodecahedronGeometry(.09,0),new THREE.MeshStandardMaterial({color:0x293c53,metalness:.15,roughness:.8}),24);this.stones.frustumCulled=false;this.layers.particles.add(this.stones);
  const copies=new Map<THREE.Material,THREE.Material>();for(const layer of Object.values(this.layers))layer.traverse(o=>{const m=o as THREE.Mesh;if(m.isMesh){const clone=(mat:THREE.Material)=>{let c=copies.get(mat);if(!c){c=mat.clone();copies.set(mat,c)}return c};if(layer!==this.layers.dragon)m.material=Array.isArray(m.material)?m.material.map(clone):clone(m.material)}});
 }
 setQuality(q:'high'|'ultra'){this.quality=q;this.dragon.setQuality(q);this.chainLinks.count=q==='ultra'?100:70;this.particles.count=q==='ultra'?120:65;this.stones.count=q==='ultra'?24:12;}
 update(t:number,active:boolean,visibility:Record<Layer,boolean>){
  const envelope=smooth(.08,.6,t)*(1-smooth(5.45,6.25,t));const expand=smooth(.32,1.7,t);const bind=smooth(2.25,3.4,t)*(1-smooth(4.9,5.9,t));
  for(const [name,g] of Object.entries(this.layers))g.visible=active&&envelope>.001&&visibility[name as Layer];
  if(!active){this.dragon.update(0,false);return;}
  // Each body segment follows the same continuous orbit at an earlier angle.
  // This avoids rotating a frozen dragon as a rigid prop around the center.
  const angle=t*(TAU/3.5),rad=1.45+.8*expand;
  this.dragon.group.position.set(0,0,0);this.dragon.group.rotation.set(0,0,0);this.dragon.group.scale.setScalar(1);
  this.dragon.update(t,active&&visibility.dragon&&envelope>.01,{phase:envelope,sample:(u:number)=>{
   const a=angle-u*2.7,r=rad-(u*.16)+.045*Math.sin(t*3-u*8);
   return new THREE.Vector3(Math.cos(a)*r,1.18+.16*Math.sin(a*2+t*.4)+.12*Math.sin(t*4-u*8)*u,Math.sin(a)*r);
  }});
  for(let i=0;i<this.circles.length;i++){const g=this.circles[i];g.rotation.y=t*(i%2?-.35:.24);g.scale.setScalar((.12+.88*expand)*envelope);}
  this.crystals.forEach((g,i)=>{const k=bind*(.75+(i%3)*.12);g.scale.set(k,k,k)});this.beams.forEach((m,i)=>{m.scale.setScalar(bind*(.8+.2*Math.sin(t*5+i)));});
  for(let i=0;i<this.chainLinks.count;i++){const a=i*TAU/this.chainLinks.count+t*.55;this.dummy.position.set(2.5*Math.cos(a),.35+.16*Math.sin(a*6+t*2),2.5*Math.sin(a));this.dummy.rotation.set(Math.PI/2+(i%2)*Math.PI/2,0,-a);this.dummy.scale.setScalar(bind);this.dummy.updateMatrix();this.chainLinks.setMatrixAt(i,this.dummy.matrix)}this.chainLinks.instanceMatrix.needsUpdate=true;
  for(let i=0;i<this.particles.count;i++){const a=i*2.399+t*(.3+(i%3)*.1),r=.5+(i%27)*.096;this.dummy.position.set(Math.cos(a)*r,.12+((i*.137+t*.5)%2.2)*envelope,Math.sin(a)*r);this.dummy.rotation.set(a,t,i);this.dummy.scale.setScalar(envelope*(.45+(i%4)*.16));this.dummy.updateMatrix();this.particles.setMatrixAt(i,this.dummy.matrix)}this.particles.instanceMatrix.needsUpdate=true;
  for(let i=0;i<this.stones.count;i++){const a=i*TAU/this.stones.count+t*.12,r=2.25+(i%4)*.18;this.dummy.position.set(Math.cos(a)*r,.12+bind*(.15+(i%5)*.12),Math.sin(a)*r);this.dummy.rotation.set(t*.8+i,i,t*.4);this.dummy.scale.setScalar(bind*(.6+(i%4)*.2));this.dummy.updateMatrix();this.stones.setMatrixAt(i,this.dummy.matrix)}this.stones.instanceMatrix.needsUpdate=true;
 }
}
