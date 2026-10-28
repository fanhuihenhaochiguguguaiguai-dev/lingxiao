import * as THREE from 'three/webgpu';
const TAU=Math.PI*2;
const ease=(a:number,b:number,t:number)=>{const x=THREE.MathUtils.clamp((t-a)/(b-a),0,1);return x*x*(3-2*x)};

/** Real-time 3D visual study. Character rig, damage and sound are not included. */
export class MoonFrost {
 readonly group=new THREE.Group();
 private readonly crescent=new THREE.Group();
 private readonly ground=new THREE.Group();
 private readonly bloom=new THREE.Group();
 private readonly feathers:THREE.InstancedMesh;
 private readonly dummy=new THREE.Object3D();
 private quality:'high'|'ultra'='high';
 constructor(parent:THREE.Object3D){
  this.group.name='月华霜羽 · 特效工作稿';this.group.visible=false;parent.add(this.group);
  const silver=new THREE.MeshStandardMaterial({color:0xc7d8ff,metalness:.45,roughness:.24,emissive:0x26336e,emissiveIntensity:.35});
  const ice=new THREE.MeshPhysicalMaterial({color:0xb4c5ff,metalness:.15,roughness:.18,transparent:true,opacity:.72,depthWrite:false,side:THREE.DoubleSide,emissive:0x1c2866,emissiveIntensity:.32});
  const glow=new THREE.MeshBasicMaterial({color:0xc8d8ff,transparent:true,opacity:.62,blending:THREE.AdditiveBlending,depthWrite:false});
  const gold=new THREE.MeshStandardMaterial({color:0xd5bd93,metalness:.8,roughness:.32});
  this.group.add(this.crescent);this.crescent.position.set(.15,1.15,0);
  for(let i=0;i<3;i++){
   const arc=new THREE.Mesh(new THREE.TorusGeometry(.72+i*.075,.027-i*.006,8,64,Math.PI*1.3),i===1?glow:silver);
   arc.rotation.z=-Math.PI*.65;arc.rotation.y=(i-1)*.1;this.crescent.add(arc);
  }
  for(const y of [-.55,.55]){const tip=new THREE.Mesh(new THREE.OctahedronGeometry(.11,0),ice);tip.position.set(.55,y,0);tip.scale.set(.6,1.65,.5);this.crescent.add(tip)}
  this.group.add(this.ground);this.ground.position.y=.035;
  for(const r of [.45,.95,1.25]){const torus=new THREE.Mesh(new THREE.TorusGeometry(r,.012,6,72),r===.95?gold:glow);torus.rotation.x=Math.PI/2;this.ground.add(torus)}
  this.group.add(this.bloom);this.bloom.position.set(4.1,.20,0);
  for(let i=0;i<12;i++){
   const petal=new THREE.Mesh(new THREE.SphereGeometry(1,12,8),ice);const a=i*TAU/12;
   petal.position.set(Math.cos(a)*.30,.16,Math.sin(a)*.30);petal.scale.set(.13,.52,.08);petal.rotation.set(.55*Math.sin(a),0,-.55*Math.cos(a));this.bloom.add(petal);
  }
  const core=new THREE.Mesh(new THREE.OctahedronGeometry(.22,0),glow);core.position.y=.24;this.bloom.add(core);
  const featherGeometry=new THREE.OctahedronGeometry(1,0);featherGeometry.scale(.18,.045,.055);
  this.feathers=new THREE.InstancedMesh(featherGeometry,ice,72);this.feathers.frustumCulled=false;this.group.add(this.feathers);
 }
 setQuality(q:'high'|'ultra'){this.quality=q;this.feathers.count=q==='ultra'?72:42}
 sample(){return {crescentX:this.crescent.position.x,lotusScale:this.bloom.scale.x,featherCount:this.feathers.count}}
 update(t:number,active:boolean){
  this.group.visible=active&&t<4.4;if(!this.group.visible)return;
  const charge=ease(.05,.6,t),fade=1-ease(3.55,4.35,t),travel=ease(.85,2.5,t),impact=ease(2.1,2.55,t)*(1-ease(3.3,4.25,t));
  this.crescent.scale.setScalar(charge*fade);this.crescent.rotation.y=t*.8;this.crescent.position.x=.15+travel*2.9;
  this.ground.scale.setScalar(charge*fade);this.ground.rotation.y=t*.36;
  this.bloom.scale.setScalar(impact);this.bloom.rotation.y=t*.28;
  for(let i=0;i<this.feathers.count;i++){
   const a=i*2.399+t*(1.2+(i%3)*.17),radius=.35+(i%7)*.13;
   this.dummy.position.set(.25+travel*(2.8+(i%5)*.20)+Math.cos(a)*radius,.65+(i%11)*.10+Math.sin(a)*.28,Math.sin(a)*radius*.55);
   this.dummy.rotation.set(a*.25,-a,t*.5+i);this.dummy.scale.setScalar(charge*fade*(.55+(i%4)*.12));this.dummy.updateMatrix();this.feathers.setMatrixAt(i,this.dummy.matrix);
  }this.feathers.instanceMatrix.needsUpdate=true;
 }
}
