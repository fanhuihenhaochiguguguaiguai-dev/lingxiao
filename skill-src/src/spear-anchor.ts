import * as THREE from 'three/webgpu';
/** Locate the uppermost vertex predominantly weighted to the existing weapon bone.
 * Returned point is in bone-local coordinates and follows the actual rig. */
export function findSpearTip(actor:THREE.Object3D,bone:THREE.Bone):THREE.Vector3|null {
 actor.updateMatrixWorld(true);let highest=-Infinity;let best:THREE.Vector3|null=null;
 actor.traverse(object=>{
  const mesh=object as THREE.SkinnedMesh;if(!mesh.isSkinnedMesh)return;
  const index=mesh.skeleton.bones.indexOf(bone);if(index<0)return;
  const geometry=mesh.geometry,position=geometry.getAttribute('position'),joints=geometry.getAttribute('skinIndex'),weights=geometry.getAttribute('skinWeight');if(!position||!joints||!weights)return;
  mesh.skeleton.update();const p=new THREE.Vector3();
  for(let i=0;i<position.count;i++){
   const ids=[joints.getX(i),joints.getY(i),joints.getZ(i),joints.getW(i)],ws=[weights.getX(i),weights.getY(i),weights.getZ(i),weights.getW(i)];let weight=0;for(let j=0;j<4;j++)if(ids[j]===index)weight+=ws[j]??0;
   if(weight<.8)continue;p.fromBufferAttribute(position,i);mesh.applyBoneTransform(i,p);mesh.localToWorld(p);
   if(p.y>highest){highest=p.y;best=p.clone()}
  }
 });
 if(!best||!Number.isFinite(highest))return null;
 return bone.worldToLocal(best);
}
