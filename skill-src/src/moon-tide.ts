import * as THREE from 'three/webgpu';
import { color, mix, positionLocal, sin, uniform, normalView } from 'three/tsl';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
const TAU=Math.PI*2,clamp=THREE.MathUtils.clamp;
const ease=(a:number,b:number,t:number)=>{const v=clamp((t-a)/(b-a),0,1);return v*v*(3-2*v)};
let echoGeometry:THREE.BufferGeometry|null=null;
export function setMoonEcho(geometry:THREE.BufferGeometry){echoGeometry=geometry}
function crescentGeometry(){const shape=new THREE.Shape();shape.absarc(0,0,1,.24,TAU-.24,false);shape.absarc(.32,0,.72,TAU-.42,.42,true);shape.closePath();return new THREE.ExtrudeGeometry(shape,{depth:.075,bevelEnabled:true,bevelSize:.015,bevelThickness:.014,bevelSegments:2,curveSegments:40,steps:1})}
function crystalGeometry(){const pos:number[]=[],idx:number[]=[];for(const [r,y] of [[.08,0],[.21,.18],[.16,1],[0,1.42]])for(let k=0;k<6;k++){const a=k*TAU/6;pos.push(Math.cos(a)*r,y,Math.sin(a)*r)}for(let j=0;j<3;j++)for(let k=0;k<6;k++){const a=j*6+k,b=j*6+(k+1)%6;idx.push(a,b,a+6,b,b+6,a+6)}const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setIndex(idx);g.computeVertexNormals();return g}
function petalGeometry(){const v:number[]=[],f:number[]=[];for(let i=0;i<=12;i++){const t=i/12;for(let j=0;j<=6;j++){const u=j/3-1;v.push(u*Math.sin(Math.PI*t)*.20,.54*t,.55*t*t+.055*u*u*Math.sin(Math.PI*t))}}for(let i=0;i<12;i++)for(let j=0;j<6;j++){const a=i*7+j;f.push(a,a+7,a+1,a+1,a+7,a+8)}const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));g.setIndex(f);g.computeVertexNormals();return g}
function runeGeometry(){const list:THREE.BufferGeometry[]=[];for(let k=0;k<24;k++){const a=k*TAU/24;const points=[new THREE.Vector3(-.05,0,-.09),new THREE.Vector3(.045,.008,0),new THREE.Vector3(-.04,0,.08),new THREE.Vector3(.08,.015,.03)];const g=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),9,.006,4,false);g.rotateY(-a).translate(Math.cos(a)*2.75,0,Math.sin(a)*2.75);list.push(g)}const result=mergeGeometries(list)!;for(const g of list)g.dispose();return result}
function ornamentGeometry(){const parts:THREE.BufferGeometry[]=[];for(let k=0;k<12;k++){const angle=k*TAU/12,cx=Math.cos(angle)*2.75,cz=Math.sin(angle)*2.75;for(let petal=0;petal<6;petal++){const a=petal*TAU/6,points:THREE.Vector3[]=[];for(let q=0;q<=12;q++){const t=q/12,r=Math.sin(Math.PI*t)*.10,side=Math.sin(TAU*t)*.034;points.push(new THREE.Vector3(cx+Math.cos(a)*r-Math.sin(a)*side,.018+Math.sin(Math.PI*t)*.035,cz+Math.sin(a)*r+Math.cos(a)*side))}parts.push(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),12,.0025,3,false))}}const g=mergeGeometries(parts)!;parts.forEach(g=>g.dispose());return g}
const assets={ornament:ornamentGeometry(),crescent:crescentGeometry(),crystal:crystalGeometry(),petal:petalGeometry(),runes:runeGeometry(),tiny:new THREE.OctahedronGeometry(.055),torus:new THREE.TorusGeometry(1,.009,5,72),mist:new THREE.SphereGeometry(1,12,7)};

const qaUnbatched=new URLSearchParams(location.search).get('qa-unbatched')==='1';
const staticBatches=new Map<string,THREE.BufferGeometry[]>();
function batchStatic(group:THREE.Group,key:string){
 if(qaUnbatched)return;
 group.updateMatrixWorld(true);const buckets=new Map<THREE.Material,THREE.Mesh[]>();
 for(const child of group.children){const mesh=child as THREE.Mesh;if(!mesh.isMesh)continue;const material=mesh.material as THREE.Material;const list=buckets.get(material)||[];list.push(mesh);buckets.set(material,list)}
 let baked=staticBatches.get(key);if(!baked){baked=[];for(const meshes of buckets.values()){const parts=meshes.map(mesh=>{mesh.updateMatrix();const g=mesh.geometry.clone().applyMatrix4(mesh.matrix).toNonIndexed();for(const a of Object.keys(g.attributes))if(!['position','normal'].includes(a))g.deleteAttribute(a);return g});baked.push(mergeGeometries(parts)!);parts.forEach(g=>g.dispose())}staticBatches.set(key,baked)}
 group.clear();let index=0;for(const material of buckets.keys())group.add(new THREE.Mesh(baked[index++],material));
}

/** Every effect has independent time/materials/instance buffers, sharing immutable topology. */
export class MoonTide {
 readonly group=new THREE.Group();readonly fieldCenter=new THREE.Vector3(2.4,0,0);
 private readonly orbits:THREE.Group[]=[];private readonly moons:THREE.Mesh[]=[];private readonly ground=new THREE.Group();private readonly lotus=new THREE.Group();private readonly echoes=new THREE.Group();
 private readonly crystals:THREE.InstancedMesh;private readonly motes:THREE.InstancedMesh;private readonly mist:THREE.InstancedMesh;private readonly broken:THREE.InstancedMesh;private readonly dummy=new THREE.Object3D();
 private readonly wave:THREE.Mesh;private readonly wavePositions:THREE.BufferAttribute;private readonly clock=uniform(0);
 private readonly ice=new THREE.MeshPhysicalNodeMaterial({color:0x8eaffe,metalness:.1,roughness:.19,clearcoat:1,clearcoatRoughness:.12,transparent:true,opacity:.73,depthWrite:false,side:THREE.DoubleSide,emissive:0x25396b,emissiveIntensity:.32});
 private readonly gold=new THREE.MeshStandardMaterial({color:0xd3bd8b,metalness:.82,roughness:.28,transparent:true});
 private readonly glow=new THREE.MeshBasicMaterial({color:0xc0d7ff,transparent:true,opacity:.38,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});
 private readonly fog=new THREE.MeshBasicMaterial({color:0x7d94cd,transparent:true,opacity:.025,depthWrite:false,side:THREE.DoubleSide});
 private readonly ghost=new THREE.MeshStandardMaterial({color:0xa8b9fb,emissive:0x5268ac,emissiveIntensity:.5,roughness:.38,transparent:true,opacity:.13,depthWrite:false,side:THREE.DoubleSide});
 private high=false;private density=1;private echoCount=0;
 setConcurrency(count:number){this.density=1/Math.sqrt(Math.max(1,count));this.motes.count=Math.max(16,Math.floor((this.high?120:64)*this.density));this.broken.count=Math.max(12,Math.floor((this.high?60:32)*this.density))}
 constructor(parent:THREE.Object3D){
  const vein=sin(positionLocal.y.mul(37).add(sin(positionLocal.x.mul(31))).add(positionLocal.z.mul(23))).mul(.5).add(.5).pow(9);const rim=normalView.z.abs().oneMinus().pow(2);this.ice.colorNode=mix(color(0x3158a9),color(0xc9ddff),vein.mul(.18).add(rim.mul(.52)).add(.12));this.ice.emissiveNode=color(0x214583).mul(vein.mul(.4).add(.18));
  this.ice.forceSinglePass=true;this.ghost.forceSinglePass=true;this.fog.forceSinglePass=true;this.glow.forceSinglePass=true;
  parent.add(this.group);this.group.name='月影寒潮 · 空间领域';this.group.position.copy(this.fieldCenter);this.group.visible=false;
  for(let i=0;i<3;i++){
   const orbit=new THREE.Group();orbit.position.y=.20+i*.83;orbit.rotation.set(.16*(i-1),0,.11*(i-1));this.group.add(orbit);this.orbits.push(orbit);
   const radius=2.95-i*.51;
   for(const [dr,material] of [[0,this.gold],[.06,this.glow]] as [number,THREE.Material][]){const mesh=new THREE.Mesh(assets.torus,material);mesh.rotation.x=Math.PI/2;mesh.scale.setScalar(radius+dr);orbit.add(mesh)}
   const ornament=new THREE.Mesh(assets.ornament,this.gold);ornament.scale.setScalar(radius/2.75);orbit.add(ornament);
   const rune=new THREE.Mesh(assets.runes,this.gold);rune.scale.setScalar(radius/2.75);orbit.add(rune);
   // Raised jewel/filigree supports preserve structural depth from side and above.
   for(let k=0;k<8;k++){const a=k*TAU/8;const jewel=new THREE.Mesh(assets.crystal,this.ice);jewel.scale.set(.20,.18,.20);jewel.position.set(Math.cos(a)*radius,-.08,Math.sin(a)*radius);orbit.add(jewel)}batchStatic(orbit,'orbit'+i);
   const moon=new THREE.Mesh(assets.crescent,this.ice);moon.position.set((i-1)*.36,.75+i*.42,0);moon.scale.setScalar(1.18-i*.16);moon.rotation.z=i*.22;this.group.add(moon);this.moons.push(moon);
  }
  this.group.add(this.ground);this.ground.position.y=.025;
  const frost=new THREE.MeshStandardNodeMaterial({color:0x344b86,roughness:.52,metalness:.18,transparent:true,opacity:.23,depthWrite:false,side:THREE.DoubleSide});
  const grain=sin(positionLocal.x.mul(17).add(sin(positionLocal.y.mul(9))).sub(this.clock.mul(.35))).mul(.5).add(.5);frost.colorNode=mix(color(0x172b52),color(0x7c9dcf),grain.mul(.55));
  const disk=new THREE.Mesh(new THREE.CircleGeometry(3.1,72),frost);disk.rotation.x=-Math.PI/2;this.ground.add(disk);
  this.ground.add(new THREE.Mesh(assets.runes,this.glow));for(let i=0;i<6;i++){const line=new THREE.Mesh(assets.torus,this.gold);line.rotation.x=Math.PI/2;line.scale.setScalar(.7+i*.44);line.position.y=i*.004;this.ground.add(line)}
  this.crystals=new THREE.InstancedMesh(assets.crystal,this.ice,36);this.crystals.frustumCulled=false;this.group.add(this.crystals);
  this.motes=new THREE.InstancedMesh(assets.tiny,this.glow,120);this.motes.frustumCulled=false;this.group.add(this.motes);
  this.broken=new THREE.InstancedMesh(assets.crystal,this.ice,60);this.broken.frustumCulled=false;this.group.add(this.broken);
  this.mist=new THREE.InstancedMesh(assets.mist,this.fog,10);this.mist.frustumCulled=false;this.group.add(this.mist);
  this.group.add(this.lotus);for(let j=0;j<2;j++)for(let k=0;k<9;k++){const a=(k+j*.5)*TAU/9,p=new THREE.Mesh(assets.petal,this.ice);p.position.set(Math.cos(a)*.20,.02+j*.06,Math.sin(a)*.20);p.rotation.y=Math.PI/2-a;p.scale.setScalar(1.15-j*.28);this.lotus.add(p)}batchStatic(this.lotus,'lotus');batchStatic(this.ground,'ground');
  const v=new Float32Array(97*7*3),indices:number[]=[];for(let i=0;i<96;i++)for(let j=0;j<6;j++){const a=i*7+j,b=a+7;indices.push(a,b,a+1,b,b+1,a+1)}const geometry=new THREE.BufferGeometry();this.wavePositions=new THREE.BufferAttribute(v,3);this.wavePositions.setUsage(THREE.DynamicDrawUsage);geometry.setAttribute('position',this.wavePositions);geometry.setIndex(indices);this.wave=new THREE.Mesh(geometry,this.ice);this.wave.frustumCulled=false;this.group.add(this.wave);this.group.add(this.echoes);
 }
 setQuality(q:'high'|'ultra'){this.high=q==='ultra';this.motes.count=this.high?120:64;this.broken.count=this.high?60:32}
 sample(t:number){return {radius:3.15*ease(1.1,2.2,t),height:2.6,echoes:this.echoCount,crystals:this.crystals.count,phase:t<.5?'凝月':t<1.4?'月影汇聚':t<2.2?'寒潮爆发':t<7?'持续领域':'消散'}}
 update(t:number,active:boolean,seed=0){
  this.group.visible=active&&t<8.6;if(!this.group.visible)return;this.clock.value=t;
  if(echoGeometry&&this.echoes.children.length===0){const echoes=new THREE.InstancedMesh(echoGeometry,this.ghost,3);echoes.frustumCulled=false;for(let i=0;i<3;i++){this.dummy.rotation.set(0,Math.PI/2,0);this.dummy.scale.setScalar(.92);this.dummy.position.set(-.8-i*.22,0,(i-1)*1.32);this.dummy.updateMatrix();echoes.setMatrixAt(i,this.dummy.matrix)}this.echoes.add(echoes);this.echoCount=3}
  const born=ease(.02,.65,t),expand=ease(.40,1.6,t),fade=1-ease(7,8.55,t),field=ease(1.35,2.2,t)*fade;
  this.ice.opacity=.64*fade*this.density;this.gold.opacity=fade;this.glow.opacity=.34*fade*this.density;this.fog.opacity=.018*field*this.density;this.ghost.opacity=.18*this.density*ease(.45,1.2,t)*fade;
  this.orbits.forEach((g,i)=>{g.scale.setScalar(born*(.24+.76*expand)*fade);g.rotation.y=t*(i%2?-.22:.17)+i*.4+seed*.137;g.position.y=(.20+i*.83)*expand});
  this.moons.forEach((m,i)=>{m.scale.setScalar((1.18-i*.16)*born*fade);m.rotation.y=Math.sin(t*.5+i)*.24;m.rotation.z=i*.22+t*(i%2?-.14:.10)});
  this.ground.scale.setScalar(born*(.24+.76*expand)*fade);this.ground.rotation.y=t*.08;this.lotus.scale.setScalar(field*(1+.07*Math.sin(t*2)));this.echoes.rotation.y=Math.sin(t*.23)*.08;
  for(let i=0;i<this.crystals.count;i++){const ring=i%3,angle=i*2.399963+seed*.025,radius=1.25+ring*.88;const growth=ease(1.0+ring*.20+(i%4)*.035,1.8+ring*.20,t)*fade;this.dummy.position.set(Math.cos(angle)*radius,.02,Math.sin(angle)*radius);this.dummy.rotation.set(Math.cos(angle)*.12,angle,Math.sin(angle)*.10);this.dummy.scale.set(.75+(i%3)*.16,growth*(.42+(i%7)*.12),.7+(i%2)*.2);this.dummy.updateMatrix();this.crystals.setMatrixAt(i,this.dummy.matrix)}this.crystals.instanceMatrix.needsUpdate=true;
  const radius=.15+3.6*ease(1.25,2.4,t),waveEnvelope=Math.sin(Math.PI*ease(1.25,2.8,t))*fade;
  for(let i=0;i<=96;i++){const a=i/96*TAU;for(let j=0;j<=6;j++){const u=j/6,r=radius+(u-.5)*.68;this.wavePositions.setXYZ(i*7+j,Math.cos(a)*r,.03+Math.sin(u*Math.PI)*(.30+.11*Math.sin(a*7-t*6))*waveEnvelope,Math.sin(a)*r)}}this.wavePositions.needsUpdate=true;this.wave.geometry.computeVertexNormals();this.wave.visible=t>1.25&&t<2.8;
  for(let i=0;i<this.motes.count;i++){const a=i*2.399+t*(.11+(i%3)*.12),r=(.35+(i%19)*.15)*expand;this.dummy.position.set(Math.cos(a)*r,.10+((i*.17+t*.22)%2.5)*born,Math.sin(a)*r);this.dummy.rotation.set(t+i,a,t*.3);this.dummy.scale.setScalar(born*fade*(.18+(i%4)*.10));this.dummy.updateMatrix();this.motes.setMatrixAt(i,this.dummy.matrix)}this.motes.instanceMatrix.needsUpdate=true;
  for(let i=0;i<this.mist.count;i++){const a=i*TAU/10+t*.06;this.dummy.position.set(Math.cos(a)*(1.6+.25*Math.sin(t+i)),.16,Math.sin(a)*2.1);this.dummy.scale.set(.70,.09+.03*Math.sin(t+i),.45);this.dummy.rotation.y=a;this.dummy.updateMatrix();this.mist.setMatrixAt(i,this.dummy.matrix)}this.mist.instanceMatrix.needsUpdate=true;
  const fracture=ease(7.0,8.15,t);for(let i=0;i<this.broken.count;i++){const a=i*2.399,r=2.1+fracture*(.4+(i%3)*.1);this.dummy.position.set(Math.cos(a)*r,.15+Math.sin(fracture*Math.PI)*(.3+(i%5)*.16),Math.sin(a)*r);this.dummy.rotation.set(t+i,a,t*.8);this.dummy.scale.setScalar(fracture*fade*.14);this.dummy.updateMatrix();this.broken.setMatrixAt(i,this.dummy.matrix)}this.broken.instanceMatrix.needsUpdate=true;
 }
 dispose(){this.group.traverse(o=>{if((o as THREE.InstancedMesh).isInstancedMesh)(o as THREE.InstancedMesh).dispose()});const mats=new Set<THREE.Material>();this.group.traverse(o=>{const m=o as THREE.Mesh;if(m.isMesh){for(const mat of Array.isArray(m.material)?m.material:[m.material])mats.add(mat)}});for(const m of mats)m.dispose();this.wave.geometry.dispose();this.group.removeFromParent();this.group.clear()}
}

// Immutable topology is shared with other lunar skills; instance state/materials stay local.
export const lunarGeometry=assets;
