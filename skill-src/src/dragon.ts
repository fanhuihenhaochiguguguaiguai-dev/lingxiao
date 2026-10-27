import * as THREE from 'three/webgpu';
import { EnergyRibbons } from './energy-ribbons';
import { color, mix, positionLocal, sin, uniform } from 'three/tsl';

const V = THREE.Vector3;
const smooth = (a:number,b:number,t:number) => { const x=THREE.MathUtils.clamp((t-a)/(b-a),0,1); return x*x*(3-2*x); };
const bodyMaterial = new THREE.MeshStandardNodeMaterial({color:0x1465c2,emissive:0x073a8b,emissiveIntensity:.85,metalness:.35,roughness:.3,transparent:true,opacity:.64,depthWrite:false,side:THREE.DoubleSide});
const flowTime=uniform(0);
const flow=sin(positionLocal.x.mul(11).add(positionLocal.y.mul(8)).sub(flowTime.mul(7))).mul(.5).add(.5);
bodyMaterial.colorNode=mix(color(0x0b58ba),color(0x8ad9ff),flow.mul(.6));
bodyMaterial.emissiveNode=mix(color(0x073578),color(0x348fe9),flow.mul(.6));
const core = new THREE.MeshStandardMaterial({color:0x92d7ff,emissive:0x287af3,emissiveIntensity:1.25,metalness:.22,roughness:.28,transparent:true,opacity:.82,depthWrite:false});
const gold = new THREE.MeshStandardMaterial({color:0xb58535,emissive:0x613707,emissiveIntensity:.28,metalness:.78,roughness:.29});
const luminous = new THREE.MeshBasicMaterial({color:0x95dcff,transparent:true,opacity:.8,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});
const dimBlue = new THREE.MeshBasicMaterial({color:0x2588ff,transparent:true,opacity:.4,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});
const orb = new THREE.MeshBasicMaterial({color:0xdffaff});
function mesh(parent:THREE.Object3D, geometry:THREE.BufferGeometry, material:THREE.Material, x:number,y:number,z:number, sx=1,sy=1,sz=1) {const m=new THREE.Mesh(geometry,material);m.position.set(x,y,z);m.scale.set(sx,sy,sz);parent.add(m);return m;}
function line(points:THREE.Vector3[],radius:number,material:THREE.Material){return new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),32,radius,6,false),material);}
function path(t:number):THREE.Vector3 {
 const dash=smooth(.95,1.72,t),actor=-1.0+2.25*dash;
 if(t<1.72){return new V(actor+.45,1.18+.16*Math.sin(t*3.3),.12*Math.sin(t*4));}
 const u=THREE.MathUtils.clamp((t-1.72)/1.48,0,1),angle=u*Math.PI*2,radius=.45+1.35*smooth(0,.2,u);
 return new V(actor+radius*Math.cos(angle),1.10+.23*Math.sin(angle*2),radius*Math.sin(angle));
}
export class DragonEffect {
 readonly group=new THREE.Group(); readonly head=new THREE.Group();
 private readonly body:THREE.Mesh; private readonly positions:THREE.BufferAttribute; private readonly ribbons=new EnergyRibbons({color:0x77ccff,opacity:.18,width:.055,count:4});
 private readonly rings:THREE.Mesh[]=[]; private readonly shards:THREE.InstancedMesh; private readonly scales:THREE.InstancedMesh;
 private readonly dummy=new THREE.Object3D(); private readonly segmentCount=64; private readonly sides=10;
 private readonly tmp=new V(); private readonly axis=new V(1,0,0); private readonly dir=new V(); private readonly quat=new THREE.Quaternion();
 private readonly windBands:THREE.Mesh[]=[]; private readonly sweepArcs=new THREE.Group(); private quality:'high'|'ultra'='high';
 constructor(scene:THREE.Scene){
  this.group.name='3D Dragon skill';scene.add(this.group);
  const positions=new Float32Array((this.segmentCount+1)*(this.sides+1)*3),idx:number[]=[];
  for(let i=0;i<this.segmentCount;i++)for(let j=0;j<this.sides;j++){const a=i*(this.sides+1)+j,b=a+this.sides+1;idx.push(a,b,a+1,b,b+1,a+1)}
  const geo=new THREE.BufferGeometry();this.positions=new THREE.BufferAttribute(positions,3);this.positions.setUsage(THREE.DynamicDrawUsage);geo.setAttribute('position',this.positions);geo.setIndex(idx);geo.computeVertexNormals();this.body=new THREE.Mesh(geo,bodyMaterial);this.body.frustumCulled=false;this.group.add(this.body);this.body.add(this.ribbons.mesh);
  this.makeHead();this.group.add(this.head);
  const scaleGeo=new THREE.OctahedronGeometry(.065,0);this.scales=new THREE.InstancedMesh(scaleGeo,core,72);this.scales.frustumCulled=false;this.group.add(this.scales);
  const shardGeo=new THREE.OctahedronGeometry(.045,0);this.shards=new THREE.InstancedMesh(shardGeo,luminous,160);this.shards.frustumCulled=false;this.group.add(this.shards);
  for(let i=0;i<3;i++){const ring=mesh(this.group,new THREE.TorusGeometry(1,.008,6,100),i===1?dimBlue:luminous,0,.035+i*.025,0);ring.rotation.x=Math.PI/2;this.rings.push(ring)}
  for(let i=0;i<4;i++){const ribbon=mesh(this.group,new THREE.TorusGeometry(1,.012,5,70,Math.PI*1.5),i%2?luminous:dimBlue,0,.85,0);ribbon.rotation.set(Math.PI/2,.18*i,.5*i);this.windBands.push(ribbon)}
  // Irregular multi-layered arcs are actual curved 3D tubes, not flat image cards.
  for(let k=0;k<14;k++){const points:THREE.Vector3[]=[];const radius=1.04+(k%5)*.22;const start=k*.77;const span=1.9+(k%3)*.55;for(let i=0;i<=45;i++){const a=start+span*i/45,r=radius+.045*Math.sin(a*11+k);points.push(new V(r*Math.cos(a),.06+(k%4)*.035+.045*Math.sin(a*4+k),r*Math.sin(a)))}const arc=line(points,k%3===0?.008:.0045,k%3===0?luminous:dimBlue);this.sweepArcs.add(arc)}this.group.add(this.sweepArcs);
  this.group.visible=false;
 }
 private makeHead(){
  const h=this.head;h.name='Dragon head: actual 3D geometry';
  const skull=mesh(h,new THREE.SphereGeometry(.24,24,16),bodyMaterial,0,0,0,1.18,.82,.82);
  mesh(h,new THREE.SphereGeometry(.18,20,12),core,.23,-.06,0,1.55,.55,.68);
  mesh(h,new THREE.SphereGeometry(.16,20,12),bodyMaterial,.20,-.16,0,1.45,.38,.60);
  for(const side of [-1,1]){
   mesh(h,new THREE.SphereGeometry(.032,14,10),orb,.075,.065,side*.177,1,.75,.5);
   const brow=line([new V(-.10,.13,side*.14),new V(.03,.16,side*.20),new V(.18,.12,side*.16)],.013,gold);h.add(brow);
   const horn=line([new V(-.15,.10,side*.11),new V(-.25,.24,side*.18),new V(-.40,.30,side*.23),new V(-.51,.27,side*.25)],.018,gold);h.add(horn);
   const whisker=line([new V(.23,-.09,side*.11),new V(.34,-.11,side*.22),new V(.47,-.04,side*.33),new V(.57,.03,side*.35)],.006,luminous);h.add(whisker);
   for(let i=0;i<4;i++){const spike=mesh(h,new THREE.ConeGeometry(.023,.095,6),core,.06+i*.07,-.18,side*.11);spike.rotation.z=Math.PI;}
   const crest=line([new V(-.02,.16,side*.11),new V(-.18,.30,side*.15),new V(-.34,.25,side*.23)],.011,luminous);h.add(crest);
  }
  skull.userData.actual3D=true;
 }
 setQuality(q:'high'|'ultra'){this.quality=q;this.shards.count=q==='ultra'?160:80;this.scales.count=q==='ultra'?72:48;}
 update(t:number,active:boolean,orbit?:{sample:(u:number)=>THREE.Vector3;phase:number}){
  const phase=orbit?orbit.phase:smooth(.05,.60,t)*(1-smooth(3.65,4.35,t));this.group.visible=active&&phase>.001;if(!this.group.visible)return;
  flowTime.value=t;bodyMaterial.opacity=.64*phase;core.opacity=.80*phase;luminous.opacity=.70*phase;dimBlue.opacity=.36*phase;
  const sample=(u:number)=>orbit?orbit.sample(Math.max(0,Math.min(1,u))):path(Math.max(0,t-u*.65)).add(new V(-u*.55,.15*Math.sin(t*7-u*7)*u,.20*Math.sin(t*5-u*8)*u));
  const headP=orbit?sample(0):path(t);this.head.position.copy(headP);if(orbit)this.dir.copy(sample(0)).sub(sample(.02));else this.dir.copy(path(Math.min(t+.025,3.2))).sub(path(Math.max(.0,t-.025)));if(this.dir.lengthSq()<.00001)this.dir.set(1,0,0);this.dir.normalize();this.quat.setFromUnitVectors(this.axis,this.dir);this.head.quaternion.copy(this.quat);this.head.scale.setScalar(.88+.12*Math.sin(t*4));
  const center=new V(),next=new V(),tangent=new V(),normal=new V(),binormal=new V();
  for(let i=0;i<=this.segmentCount;i++){
   const u=i/this.segmentCount,lag=u*.65;if(orbit){center.copy(sample(u));next.copy(sample(u+.018))}else{center.copy(path(Math.max(0,t-lag))).add(new V(-u*.55,.15*Math.sin(t*7-u*7)*u,.20*Math.sin(t*5-u*8)*u));next.copy(path(Math.max(0,t-lag-.012))).add(new V(-(u+.006)*.55,.15*Math.sin(t*7-(u+.006)*7)*(u+.006),.20*Math.sin(t*5-(u+.006)*8)*(u+.006)))}
   tangent.copy(center).sub(next).normalize();if(tangent.lengthSq()<.1)tangent.set(1,0,0);normal.crossVectors(tangent,new V(0,1,0)).normalize();if(normal.lengthSq()<.1)normal.set(0,0,1);binormal.crossVectors(tangent,normal).normalize();
   const radius=(.20*(1-u)+.016)*(.85+.15*Math.sin(t*9-u*12));
   for(let j=0;j<=this.sides;j++){const a=j/this.sides*Math.PI*2;this.tmp.copy(center).addScaledVector(normal,Math.cos(a)*radius).addScaledVector(binormal,Math.sin(a)*radius*.75);this.positions.setXYZ(i*(this.sides+1)+j,this.tmp.x,this.tmp.y,this.tmp.z)}
  }
  this.positions.needsUpdate=true;this.body.geometry.computeVertexNormals();this.ribbons.update(sample,t,phase);
  for(let i=0;i<this.scales.count;i++){
   const u=(i%36)/36,side=i<36?-1:1;const centerP=orbit?sample(u):path(Math.max(0,t-u*.65));this.dummy.position.copy(centerP).add(orbit?new V(0,.12,.12*side):new V(-u*.55,.13+(.2*(1-u))*side*.4,.14*side));this.dummy.rotation.set(0,u*4+t*2,side*.4);this.dummy.scale.set(.22,.34,.50);this.dummy.updateMatrix();this.scales.setMatrixAt(i,this.dummy.matrix);
  }this.scales.instanceMatrix.needsUpdate=true;
  const burst=smooth(2.95,3.35,t);for(let i=0;i<this.shards.count;i++){
   const a=i*2.399+t*.9,r=(.30+(i%19)*.075)*(0.3+burst);this.dummy.position.set(headP.x+Math.cos(a)*r,Math.max(.06,headP.y+Math.sin(a*1.7)*r*.55),headP.z+Math.sin(a)*r);const sz=(.4+(i%5)*.14)*phase;this.dummy.scale.setScalar(sz);this.dummy.rotation.set(a,t*2,a*.4);this.dummy.updateMatrix();this.shards.setMatrixAt(i,this.dummy.matrix);
  }this.shards.instanceMatrix.needsUpdate=true;
  const sweep=smooth(1.60,1.98,t)*(1-smooth(3.5,4.05,t));this.rings.forEach((m,i)=>{m.visible=sweep>.01;const size=(.55+i*.22+1.25*sweep);m.scale.set(size,size,size);m.position.x=1.25;m.rotation.z=t*(i%2?-.75:.55)});
  this.sweepArcs.visible=sweep>.01;this.sweepArcs.position.set(1.25,0,0);this.sweepArcs.rotation.y=t*.55;this.sweepArcs.scale.setScalar(.45+.55*sweep);
  this.windBands.forEach((m,i)=>{m.visible=t<3.8;m.position.set(headP.x,.85+i*.10,headP.z);m.rotation.z=t*(i%2?1:-1)+i;const k=.5+i*.12;m.scale.set(k,k,k)});
 }
}
