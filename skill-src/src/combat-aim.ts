import * as THREE from 'three/webgpu';
import {skillRegistry} from './skill-registry';
import type {CastKind} from './instance-audio';
/** A quiet preview only; its meshes never participate in damage. */
export class CombatAim {
 private root=new THREE.Group();private ring:THREE.Mesh;private arrow:THREE.Mesh;private material=new THREE.MeshBasicMaterial({color:0x9bd9ed,transparent:true,opacity:.60,depthWrite:false});
 constructor(scene:THREE.Scene){scene.add(this.root);this.root.name='仅瞄准预览 · 无伤害';this.root.visible=false;this.ring=new THREE.Mesh(new THREE.RingGeometry(.975,1,64),this.material);this.ring.rotation.x=-Math.PI/2;this.root.add(this.ring);this.arrow=new THREE.Mesh(new THREE.ConeGeometry(.12,.45,3),this.material);this.arrow.rotation.z=-Math.PI/2;this.root.add(this.arrow)}
 update(kind:CastKind|null,position:THREE.Vector3,yaw:number,cancelled=false){this.root.visible=!!kind;if(!kind)return;const p=skillRegistry[kind].aim;this.root.position.copy(position);this.root.position.y=.045;this.root.rotation.y=yaw;this.material.color.setHex(cancelled?0xe99a93:0x9bd9ed);this.ring.position.x=p.reach;this.ring.scale.setScalar(p.radius);this.arrow.position.set(p.reach*.5,.03,0);this.arrow.scale.set(.8,p.shape==='direction'?Math.max(1,p.reach):1,.8);this.arrow.visible=p.shape==='direction'}
}
