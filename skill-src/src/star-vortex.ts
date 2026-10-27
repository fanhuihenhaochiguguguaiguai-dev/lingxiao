import * as THREE from 'three/webgpu';
import {color,mix,positionLocal,sin,uniform} from 'three/tsl';
const V=THREE.Vector3, TAU=Math.PI*2;
const smooth=(a:number,b:number,t:number)=>{const x=THREE.MathUtils.clamp((t-a)/(b-a),0,1);return x*x*(3-2*x)};
const path=(u:number,t:number)=>{const a=2.1*TAU*u+t*.68,r=.42+2.15*u;return new V(Math.cos(a)*r,.25+u*4.45,Math.sin(a)*r)};
function tube(points:THREE.Vector3[],radius:number,mat:THREE.Material,segments=70){return new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),segments,radius,6,false),mat)}
function torus(r:number,thick:number,material:THREE.Material){const m=new THREE.Mesh(new THREE.TorusGeometry(r,thick,7,96),material);m.rotation.x=Math.PI/2;return m}
export class StarVortex {
 readonly group=new THREE.Group(); readonly dragon=new THREE.Group();readonly head=new THREE.Group();
 private readonly rails:THREE.Group[]=[];private readonly flows:THREE.Mesh[]=[];private readonly dragonWisps:THREE.Mesh[]=[];private readonly flowTime=uniform(0);private readonly ground:THREE.Group;private readonly shock:THREE.Mesh[]=[];private readonly body:THREE.Mesh;private readonly positions:THREE.BufferAttribute;private readonly scales:THREE.InstancedMesh;private readonly particles:THREE.InstancedMesh;private readonly rocks:THREE.InstancedMesh;private readonly dummy=new THREE.Object3D();
 private readonly gold=new THREE.MeshStandardMaterial({color:0xc4954d,metalness:.85,roughness:.3,emissive:0x9a5313,emissiveIntensity:.28});
 private readonly blue=new THREE.MeshStandardNodeMaterial({color:0x236ec7,metalness:.25,roughness:.3,emissive:0x1053a0,emissiveIntensity:.8,transparent:true,opacity:.62,depthWrite:false,side:THREE.DoubleSide});
 private readonly glow=new THREE.MeshBasicMaterial({color:0x9ce4ff,transparent:true,opacity:.57,blending:THREE.AdditiveBlending,depthWrite:false});
 private readonly goldGlow=new THREE.MeshBasicMaterial({color:0xffc970,transparent:true,opacity:.65,blending:THREE.AdditiveBlending,depthWrite:false});
 private readonly rockMat=new THREE.MeshStandardMaterial({color:0x41424b,metalness:.2,roughness:.85});
 constructor(scene:THREE.Scene){
  const wave=sin(positionLocal.y.mul(7).sub(this.flowTime.mul(5))).mul(.5).add(.5);this.blue.colorNode=mix(color(0x1353aa),color(0x76cfff),wave.mul(.65));this.blue.emissiveNode=mix(color(0x063675),color(0x2285dc),wave.mul(.6));
  this.group.name='星渊龙卷 · real 3D';scene.add(this.group);this.group.visible=false;this.group.add(this.dragon);
  const seg=80,sides=10,pos=new Float32Array((seg+1)*(sides+1)*3),index:number[]=[];
  for(let i=0;i<seg;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;index.push(a,b,a+1,b,b+1,a+1)}
  const geo=new THREE.BufferGeometry();this.positions=new THREE.BufferAttribute(pos,3);this.positions.setUsage(THREE.DynamicDrawUsage);geo.setAttribute('position',this.positions);geo.setIndex(index);this.body=new THREE.Mesh(geo,this.blue);this.body.frustumCulled=false;this.dragon.add(this.body);this.makeHead();this.dragon.add(this.head);
  this.scales=new THREE.InstancedMesh(new THREE.ConeGeometry(.075,.18,5),this.glow,120);this.scales.frustumCulled=false;this.dragon.add(this.scales);
  for(let k=0;k<3;k++){
   const g=new THREE.Group();g.position.y=.75+k*1.38;g.rotation.z=(k%2?-.11:.11);this.group.add(g);this.rails.push(g);const r=2.1+k*.43;
   for(const dr of [-.12,.12])g.add(torus(r+dr,.025,this.gold));g.add(torus(r,.008,this.goldGlow));
   const ticks=new THREE.InstancedMesh(new THREE.BoxGeometry(.04,.025,.25),this.gold,40);for(let i=0;i<40;i++){const a=i*TAU/40;this.dummy.position.set(Math.cos(a)*r,0,Math.sin(a)*r);this.dummy.rotation.set(0,-a,0);this.dummy.scale.setScalar(1);this.dummy.updateMatrix();ticks.setMatrixAt(i,this.dummy.matrix)}g.add(ticks);
   // Three-dimensional repeating glyph strokes share a single instanced draw.
   const glyphs=new THREE.InstancedMesh(new THREE.BoxGeometry(.035,.025,.18),this.gold,72);for(let i=0;i<72;i++){const n=Math.floor(i/3),stroke=i%3,a=n*TAU/24,runeR=r+(stroke===0?-.04:stroke===1?.04:0);this.dummy.position.set(Math.cos(a)*runeR,.035,Math.sin(a)*runeR);this.dummy.rotation.set(0,-a+(stroke===2?Math.PI/2:0),0);this.dummy.scale.set(1,1,stroke===2?.6:1);this.dummy.updateMatrix();glyphs.setMatrixAt(i,this.dummy.matrix)}g.add(glyphs);
  }
  for(let k=0;k<8;k++){const pts:THREE.Vector3[]=[];for(let i=0;i<=100;i++){const u=i/100,a=2.1*TAU*u+k*.38,r=.42+2.15*u+.08*Math.sin(u*TAU*6+k);pts.push(new V(Math.cos(a)*r,.25+u*4.45+.08*Math.cos(u*TAU*5+k),Math.sin(a)*r))}const w=tube(pts,k%3===0?.014:.009,k%3===0?this.goldGlow:this.glow,120);this.group.add(w);this.dragonWisps.push(w)}
  this.ground=new THREE.Group();this.group.add(this.ground);for(const r of [.7,1.3,2.15,3.15,3.5])this.ground.add(torus(r,.013,r===2.15?this.gold:this.glow));
  const pts:THREE.Vector3[]=[];for(let i=0;i<=120;i++){const a=i/120*TAU*3,r=.15+i/120*3.15;pts.push(new V(Math.cos(a)*r,.02,Math.sin(a)*r))}this.ground.add(tube(pts,.012,this.glow,140));
  for(let k=0;k<9;k++){const points:THREE.Vector3[]=[];for(let i=0;i<=120;i++){const u=i/120,a=u*2.6*TAU+k*TAU/9,r=.4+2.5*u;points.push(new V(r*Math.cos(a),.16+u*4.4,r*Math.sin(a)))}const m=tube(points,k%3===0?.035:.016,k%3===0?this.glow:(k%2?this.goldGlow:this.blue),150);this.group.add(m);this.flows.push(m)}
  for(let i=0;i<3;i++){const m=torus(1,.035,i===1?this.goldGlow:this.glow);m.position.y=.1+i*.04;this.group.add(m);this.shock.push(m)}
  this.particles=new THREE.InstancedMesh(new THREE.OctahedronGeometry(.048,0),this.glow,180);this.particles.frustumCulled=false;this.group.add(this.particles);
  this.rocks=new THREE.InstancedMesh(new THREE.DodecahedronGeometry(.12,0),this.rockMat,36);this.rocks.frustumCulled=false;this.group.add(this.rocks);
 }
 private makeHead(){
  const m=(g:THREE.BufferGeometry,mat:THREE.Material,x:number,y:number,z:number,sx=1,sy=1,sz=1)=>{const a=new THREE.Mesh(g,mat);a.position.set(x,y,z);a.scale.set(sx,sy,sz);this.head.add(a);return a};
  m(new THREE.SphereGeometry(.28,24,16),this.blue,0,0,0,1.25,.8,.85);m(new THREE.SphereGeometry(.18,20,12),this.glow,.25,-.07,0,1.55,.54,.7);m(new THREE.SphereGeometry(.16,20,12),this.blue,.22,-.20,0,1.5,.35,.65);
  for(const side of [-1,1]){
   m(new THREE.SphereGeometry(.04,12,8),this.glow,.09,.06,side*.20,1,.8,.5);
   for(let k=0;k<2;k++){const horn=tube([new V(-.14,.13,side*.13),new V(-.23,.30+k*.05,side*.22),new V(-.45,.38+k*.09,side*.31),new V(-.60,.34+k*.09,side*.36)],.018-k*.004,this.gold,24);this.head.add(horn)}
   this.head.add(tube([new V(.28,-.09,side*.12),new V(.38,-.12,side*.27),new V(.55,-.03,side*.4)],.008,this.glow,24));
   for(let i=0;i<5;i++){const mane=tube([new V(-.18,.12-i*.05,side*.15),new V(-.40,.24-i*.05,side*.24),new V(-.75,.18-i*.08,side*(.3+i*.04))],.008,i%2?this.goldGlow:this.glow,24);this.head.add(mane)}
   for(let i=0;i<4;i++){const tooth=m(new THREE.ConeGeometry(.018,.07,5),this.glow,.08+i*.08,-.16,side*.11);tooth.rotation.z=Math.PI;}
  }
 }
 setQuality(q:'high'|'ultra'){this.particles.count=q==='ultra'?180:90;this.rocks.count=q==='ultra'?36:18;this.scales.count=q==='ultra'?120:70;this.flows.forEach((m,i)=>m.visible=q==='ultra'||i<6)}
 update(t:number,active:boolean){
  this.group.visible=active&&t<7.4;if(!this.group.visible)return;
  this.flowTime.value=t;const start=smooth(.02,.9,t),fade=1-smooth(6.1,7.35,t),grow=start*fade, dragonFade=smooth(.6,1.65,t)*(1-smooth(5.7,6.7,t));
  const compress=1-.54*smooth(4.4,4.9,t)*(1-smooth(4.95,5.25,t));this.dragon.visible=dragonFade>.005;
  const seg=80,sides=10,center=new V(),next=new V(),tangent=new V(),normal=new V(),binormal=new V(),temp=new V();
  for(let i=0;i<=seg;i++){
   const u=i/seg;center.copy(path(u,t));center.x*=compress;center.z*=compress;next.copy(path(Math.min(1,u+.002),t));next.x*=compress;next.z*=compress;tangent.copy(next).sub(center).normalize();if(tangent.lengthSq()<.1)tangent.set(1,0,0);normal.crossVectors(tangent,new V(0,1,0)).normalize();if(normal.lengthSq()<.1)normal.set(0,0,1);binormal.crossVectors(tangent,normal).normalize();const r=(.04+.24*u)*dragonFade;
   for(let j=0;j<=sides;j++){const a=j/sides*TAU;temp.copy(center).addScaledVector(normal,Math.cos(a)*r).addScaledVector(binormal,Math.sin(a)*r);this.positions.setXYZ(i*(sides+1)+j,temp.x,temp.y,temp.z)}
  }this.positions.needsUpdate=true;this.body.geometry.computeVertexNormals();const hp=path(1,t);hp.x*=compress;hp.z*=compress;this.head.position.copy(hp);this.head.scale.setScalar(dragonFade);const forward=path(.99,t);forward.x*=compress;forward.z*=compress;this.head.quaternion.setFromUnitVectors(new V(1,0,0),hp.clone().sub(forward).normalize());
  for(let i=0;i<this.scales.count;i++){const u=i/this.scales.count,p=path(u,t);this.dummy.position.set(p.x*compress,p.y+.15,p.z*compress);this.dummy.rotation.set(0,t+u*8,.5);this.dummy.scale.set(.45,dragonFade*.8,.45);this.dummy.updateMatrix();this.scales.setMatrixAt(i,this.dummy.matrix)}this.scales.instanceMatrix.needsUpdate=true;
  this.dragonWisps.forEach((w,i)=>{w.rotation.y=-t*.68;w.scale.set(compress,dragonFade,compress);w.visible=dragonFade>.01&&(this.particles.count>90||i<5)});
  this.rails.forEach((g,i)=>{g.rotation.y=t*(i%2?-.7:.45);g.scale.setScalar((.1+.9*start)*fade);g.position.y=(.30+i*1.38)*smooth(.15,1.4,t)});
  this.ground.scale.setScalar((.12+.88*start)*fade);this.ground.rotation.y=t*.22;
  this.flows.forEach((m,i)=>{m.rotation.y=t*(i%2?-.35:.55);m.scale.set((.3+.7*grow)*compress,grow,(.3+.7*grow)*compress)});
  const boom=smooth(4.85,5.05,t)*(1-smooth(5.25,5.85,t));this.shock.forEach((m,i)=>{m.visible=boom>.01;const r=.3+(i+1)*smooth(4.85,5.8,t)*1.15;m.scale.setScalar(r)});
  for(let i=0;i<this.particles.count;i++){const u=(i*.618+t*.15)%1,a=i*2.399+t*2.1,r=(.2+u*3.3)*compress+boom*u;this.dummy.position.set(Math.cos(a)*r,.12+((i*.181+t*.8)%4.7),Math.sin(a)*r);this.dummy.rotation.set(a,t,i);this.dummy.scale.setScalar(grow*(.35+(i%4)*.16));this.dummy.updateMatrix();this.particles.setMatrixAt(i,this.dummy.matrix)}this.particles.instanceMatrix.needsUpdate=true;
  for(let i=0;i<this.rocks.count;i++){const a=i*2.399+t*.42,r=(.7+(i%8)*.32)*compress+boom*(i%4)*.35;this.dummy.position.set(Math.cos(a)*r,.2+((i*.39+t*.42)%4.5)+boom*(i%3),Math.sin(a)*r);this.dummy.rotation.set(t+i,i,t*.5);this.dummy.scale.setScalar(grow*(.45+(i%5)*.17));this.dummy.updateMatrix();this.rocks.setMatrixAt(i,this.dummy.matrix)}this.rocks.instanceMatrix.needsUpdate=true;
 }
}
