import * as THREE from 'three/webgpu';
import { color, mix, positionLocal, sin, uniform, normalView } from 'three/tsl';
import { makeDragonHead, orientDragonHead } from './dragon-head';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
const V=THREE.Vector3,TAU=Math.PI*2;
const ease=(a:number,b:number,t:number)=>THREE.MathUtils.smoothstep(t,a,b);
function scaleGeometry(){const shape=new THREE.Shape();shape.moveTo(0,.10);shape.quadraticCurveTo(.105,.035,.067,-.045);shape.lineTo(0,-.11);shape.lineTo(-.067,-.045);shape.quadraticCurveTo(-.105,.035,0,.10);return new THREE.ExtrudeGeometry(shape,{depth:.012,bevelEnabled:true,bevelSize:.003,bevelThickness:.003,bevelSegments:1,steps:1,curveSegments:6})}
function limbGeometry(){const parts:THREE.BufferGeometry[]=[];const points=[new V(0,0,0),new V(.04,-.16,.14),new V(.19,-.29,.22),new V(.27,-.33,.23)];parts.push(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),18,.052,6,false));for(let k=0;k<3;k++){const z=.18+k*.05;parts.push(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new V(.23,-.32,.23),new V(.35,-.35,z),new V(.42,-.40,z-.01)]),9,.014,5,false))}const g=mergeGeometries(parts)!;parts.forEach(g=>g.dispose());return g}
type HeadPalette={shell:THREE.Material;light:THREE.Material;gold:THREE.Material;dark:THREE.Material;eye:THREE.Material};
let headTopology:{geometry:THREE.BufferGeometry;role:keyof HeadPalette}[]|null=null;
function sharedIceHead(palette:HeadPalette){
 if(!headTopology){const prototype=makeDragonHead(palette);headTopology=[];for(const child of prototype.children){const mesh=child as THREE.Mesh;const role=(Object.keys(palette) as (keyof HeadPalette)[]).find(k=>palette[k]===mesh.material)!;headTopology.push({geometry:mesh.geometry,role})}prototype.clear()}
 const group=new THREE.Group();group.name='冰龙首 · 共享拓扑/独立材质';for(const part of headTopology)group.add(new THREE.Mesh(part.geometry,palette[part.role]));return group;
}

const scaleGeo=scaleGeometry(),limbGeo=limbGeometry(),dorsalGeo=new THREE.ConeGeometry(.07,.25,5);
export class IceDragon {
 readonly group=new THREE.Group();readonly head=new THREE.Group();private readonly body:THREE.Mesh;private readonly positions:THREE.BufferAttribute;private readonly scales:THREE.InstancedMesh;private readonly dorsal:THREE.InstancedMesh;private readonly limbs:THREE.InstancedMesh;private readonly dummy=new THREE.Object3D();private readonly clock=uniform(0);private phaseSeed=0;private readonly segmentCount=88;private readonly sides=14;
 private readonly skin=new THREE.MeshPhysicalNodeMaterial({color:0x5f94db,roughness:.22,metalness:.08,clearcoat:.8,transparent:true,opacity:.72,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true});
 private readonly light=new THREE.MeshPhysicalMaterial({color:0xc1e8ff,roughness:.13,metalness:.12,clearcoat:1,transparent:true,opacity:.80,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true,emissive:0x1f4472,emissiveIntensity:.35});
 private readonly horn=new THREE.MeshStandardMaterial({color:0xa3d6ff,metalness:.45,roughness:.20,transparent:true,opacity:.92});private readonly dark=new THREE.MeshStandardMaterial({color:0x102348,roughness:.36,transparent:true,opacity:.9});private readonly eye=new THREE.MeshBasicMaterial({color:0xe0fcff,transparent:true,opacity:.95});
 constructor(parent:THREE.Object3D){parent.add(this.group);this.group.name='冰龙 · 独立实体';this.group.add(this.head);this.head.add(sharedIceHead({shell:this.skin,light:this.light,gold:this.horn,dark:this.dark,eye:this.eye}));
  const vein=sin(positionLocal.x.mul(22).add(positionLocal.y.mul(17)).sub(this.clock.mul(1.5))).mul(.5).add(.5).pow(8),rim=normalView.z.abs().oneMinus().pow(2);this.skin.colorNode=mix(color(0x285a9f),color(0xb6e1ff),rim.mul(.6).add(vein.mul(.2)));this.skin.emissiveNode=color(0x24599d).mul(vein.mul(.35).add(.15));
  const vertices=new Float32Array((this.segmentCount+1)*(this.sides+1)*3),idx:number[]=[];for(let i=0;i<this.segmentCount;i++)for(let j=0;j<this.sides;j++){const a=i*(this.sides+1)+j,b=a+this.sides+1;idx.push(a,a+1,b,b,a+1,b+1)}const geo=new THREE.BufferGeometry();this.positions=new THREE.BufferAttribute(vertices,3);this.positions.setUsage(THREE.DynamicDrawUsage);geo.setAttribute('position',this.positions);geo.setIndex(idx);this.body=new THREE.Mesh(geo,this.skin);this.body.frustumCulled=false;this.group.add(this.body);
  this.scales=new THREE.InstancedMesh(scaleGeo,this.light,160);this.scales.frustumCulled=false;this.group.add(this.scales);this.dorsal=new THREE.InstancedMesh(dorsalGeo,this.light,28);this.dorsal.frustumCulled=false;this.group.add(this.dorsal);this.limbs=new THREE.InstancedMesh(limbGeo,this.skin,4);this.limbs.frustumCulled=false;this.group.add(this.limbs);
 }
 private path(u:number,t:number){
  const a=t*.90-u*5.2+this.phaseSeed,r=2.65-u*.55,orbit=new V(1.5+Math.cos(a)*r,2.0+Math.sin(a*.85)*1.05+u*.15,Math.sin(a)*r);const lead=t-u*.75,dive=ease(2.9,3.95,lead)*(1-ease(4.35,5.4,lead));return orbit.lerp(new V(1.5,.42+u*.45,0),dive);
 }
 private frame(u:number,t:number){const p=this.path(u,t),next=this.path(Math.min(1,u+.012),t),tangent=p.clone().sub(next).normalize();if(tangent.lengthSq()<.1)tangent.set(1,0,0);let side=new V().crossVectors(tangent,new V(0,1,0)).normalize();if(side.lengthSq()<.1)side.set(0,0,1);const up=new V().crossVectors(side,tangent).normalize();return {p,tangent,side,up}}
 update(t:number,active:boolean,density=1,seed=0){this.phaseSeed=seed*2.399963;const appear=ease(.80,1.65,t),fade=1-ease(9.4,11.15,t),phase=appear*fade;this.group.visible=active&&phase>.001;if(!this.group.visible)return;this.clock.value=t;this.skin.opacity=.72*phase*density;this.light.opacity=.82*phase*density;this.horn.opacity=.92*phase;this.dark.opacity=.9*phase;this.eye.opacity=phase;
  const head=this.frame(0,t);this.head.position.copy(head.p);orientDragonHead(this.head,head.tangent);this.head.scale.setScalar(1.35*appear);
  for(let i=0;i<=this.segmentCount;i++){const u=i/this.segmentCount,f=this.frame(u,t),r=(.27*(1-u)+.012)*ease(.7+u*.5,1.6+u*.5,t);for(let j=0;j<=this.sides;j++){const a=j/this.sides*TAU,p=f.p.clone().addScaledVector(f.side,Math.cos(a)*r).addScaledVector(f.up,Math.sin(a)*r*.85);this.positions.setXYZ(i*(this.sides+1)+j,p.x,p.y,p.z)}}this.positions.needsUpdate=true;this.body.geometry.computeVertexNormals();
  const fracture=ease(9.45,10.9,t);
  for(let i=0;i<this.scales.count;i++){const row=i%40,u=.035+row/42,side=Math.floor(i/40),f=this.frame(u,t),angle=side*TAU/4,r=.27*(1-u)+.024;const normal=f.side.clone().multiplyScalar(Math.cos(angle)).addScaledVector(f.up,Math.sin(angle));this.dummy.position.copy(f.p).addScaledVector(normal,r+.35*fracture);this.dummy.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(new V().crossVectors(f.tangent,normal).normalize(),f.tangent,normal));this.dummy.rotateX(fracture*(i%3));this.dummy.scale.setScalar((.76+.25*(1-u))*appear*fade);this.dummy.updateMatrix();this.scales.setMatrixAt(i,this.dummy.matrix)}this.scales.instanceMatrix.needsUpdate=true;
  for(let i=0;i<this.dorsal.count;i++){const u=.05+i/31,f=this.frame(u,t),r=.27*(1-u)+.03;this.dummy.position.copy(f.p).addScaledVector(f.up,r*.85);this.dummy.quaternion.setFromUnitVectors(new V(0,1,0),f.up);this.dummy.scale.setScalar((1-u*.7)*phase);this.dummy.updateMatrix();this.dorsal.setMatrixAt(i,this.dummy.matrix)}this.dorsal.instanceMatrix.needsUpdate=true;
  for(let i=0;i<4;i++){const u=i<2?.23:.64,f=this.frame(u,t),sign=i%2?1:-1;this.dummy.position.copy(f.p).addScaledVector(f.side,sign*.18);this.dummy.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(f.tangent.clone().multiplyScalar(sign),f.up,f.side.clone().multiplyScalar(sign)));this.dummy.scale.setScalar(phase);this.dummy.updateMatrix();this.limbs.setMatrixAt(i,this.dummy.matrix)}this.limbs.instanceMatrix.needsUpdate=true;
 }
 sample(){return {visible:this.group.visible,head:this.head.position.toArray(),bodyY:this.positions.getY(29),scales:this.scales.count,limbs:this.limbs.count}}
 dispose(){this.scales.dispose();this.dorsal.dispose();this.limbs.dispose();this.body.geometry.dispose();for(const m of [this.skin,this.light,this.horn,this.dark,this.eye])m.dispose();this.group.clear()}
}
