import * as THREE from 'three/webgpu';
import type {DamageVolume} from './damage-volumes';
/** Ground hazard projection of active filled volumes. Warning glitter stays unfilled. */
export class DamageAreaView {
 private capacity=16;private disk:THREE.InstancedMesh;private border:THREE.InstancedMesh;private dummy=new THREE.Object3D();
 private diskGeometry=new THREE.CircleGeometry(1,64);private borderGeometry=new THREE.RingGeometry(.985,1,64);
 private fillMaterial=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.035,depthWrite:false});private borderMaterial=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.32,depthWrite:false});
 constructor(private scene:THREE.Scene){this.disk=new THREE.InstancedMesh(this.diskGeometry,this.fillMaterial,this.capacity);this.border=new THREE.InstancedMesh(this.borderGeometry,this.borderMaterial,this.capacity);this.attach()}
 private attach(){for(const m of [this.disk,this.border]){m.name='实际有效领域 · 只投影结算区域';m.frustumCulled=false;m.count=0;this.scene.add(m)}}
 update(instances:{owner:string;kind:string;age:number;volumes:DamageVolume[];valid:boolean}[]){const fields=instances.flatMap(i=>i.valid?i.volumes.filter(v=>v.shape==='cylinder'&&i.age>=v.start&&i.age<=v.end&&v.radius>.01).map(v=>({v,owner:i.owner,kind:i.kind})):[]);
  if(fields.length>this.capacity){this.capacity=2**Math.ceil(Math.log2(fields.length));for(const m of [this.disk,this.border]){m.removeFromParent();m.dispose()}this.disk=new THREE.InstancedMesh(this.diskGeometry,this.fillMaterial,this.capacity);this.border=new THREE.InstancedMesh(this.borderGeometry,this.borderMaterial,this.capacity);this.attach()}
  this.disk.count=this.border.count=fields.length;fields.forEach(({v,owner,kind},n)=>{this.dummy.position.set(v.a.x,.033+n*.0002,v.a.z);this.dummy.rotation.set(-Math.PI/2,0,0);this.dummy.scale.setScalar(v.radius);this.dummy.updateMatrix();const color=new THREE.Color(owner==='opponent'?0xe4918a:kind.startsWith('lingyuan')?0xd5bc81:0x9acfe8);for(const mesh of [this.disk,this.border]){mesh.setMatrixAt(n,this.dummy.matrix);mesh.setColorAt(n,color)}});for(const mesh of [this.disk,this.border]){mesh.instanceMatrix.needsUpdate=true;if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true}
 }
}
