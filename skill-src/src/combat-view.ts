import * as THREE from 'three/webgpu';
import {CombatState} from './combat-state';
export class CombatView {
 readonly wood=new THREE.Group();private trunk:THREE.Mesh;private debris:THREE.InstancedMesh;private dummy=new THREE.Object3D();private bars=new Map<string,HTMLElement>();
 constructor(scene:THREE.Scene,private combat:CombatState){
  this.wood.name='可击毁训练木桩';const timber=new THREE.MeshStandardMaterial({color:0x685044,roughness:.76,emissive:0x72452a,emissiveIntensity:0}),end=new THREE.MeshStandardMaterial({color:0x8c7454,roughness:.85});
  this.trunk=new THREE.Mesh(new THREE.CylinderGeometry(.31,.40,1.30,12),timber);this.trunk.position.y=.65;this.trunk.castShadow=true;this.wood.add(this.trunk);
  for(const y of [.20,1.05]){const band=new THREE.Mesh(new THREE.TorusGeometry(.36,.035,5,16),new THREE.MeshStandardMaterial({color:0x323d47,metalness:.6,roughness:.5}));band.rotation.x=Math.PI/2;band.position.y=y;this.wood.add(band)}
  for(const r of [.09,.17,.25]){const ring=new THREE.Mesh(new THREE.TorusGeometry(r,.005,3,20),end);ring.rotation.x=Math.PI/2;ring.position.y=1.303;this.wood.add(ring)}scene.add(this.wood);
  this.debris=new THREE.InstancedMesh(new THREE.BoxGeometry(.16,.45,.14),new THREE.MeshStandardMaterial({color:0x685044,roughness:.8,transparent:true,opacity:1}),8);this.debris.frustumCulled=false;scene.add(this.debris);
  const hud=document.getElementById('combat-labels')!;
  for(const id of ['player','opponent','target-0','target-1','target-2']){const box=document.createElement('div');box.className='unit-health';box.dataset.unit=id;box.innerHTML='<span></span><div><i></i></div><small></small>';hud.append(box);this.bars.set(id,box)}
 }
 update(camera:THREE.Camera){
  const u=this.combat.unit('target-0');this.wood.position.set(u.position.x,u.position.y-.6,u.position.z);this.wood.visible=this.combat.mode==='practice'&&u.alive;
  (this.trunk.material as THREE.MeshStandardMaterial).emissiveIntensity=u.hitFlash*3;this.wood.rotation.z=Math.sin(u.hitFlash*45)*u.hitFlash*.09;
  this.debris.visible=this.combat.mode==='practice'&&!u.alive&&u.deadFor<2.4;(this.debris.material as THREE.MeshStandardMaterial).opacity=Math.max(0,1-u.deadFor/2.4);
  if(this.debris.visible){for(let i=0;i<8;i++){const a=i*2.399,t=Math.min(u.deadFor,.75);this.dummy.position.set(u.position.x+Math.cos(a)*t*.8,Math.max(.08,.65+(1.1+i*.08)*t-2*t*t),u.position.z+Math.sin(a)*t*.8);this.dummy.rotation.set(t*(i+1),a,t*2);this.dummy.updateMatrix();this.debris.setMatrixAt(i,this.dummy.matrix)}this.debris.instanceMatrix.needsUpdate=true}
  const width=innerWidth,height=innerHeight;
  for(const [id,box] of this.bars){const unit=this.combat.unit(id),visible=this.combat.mode==='duel'?unit.character!=='target':id==='player'||id==='target-0'||unit.hitFlash>0;
   const p=new THREE.Vector3(unit.position.x,unit.position.y+(unit.character==='target'?.94:1.18),unit.position.z).project(camera);box.hidden=!visible||p.z< -1||p.z>1||Math.abs(p.x)>1.1||Math.abs(p.y)>1.1;if(box.hidden)continue;
   box.style.transform=`translate(${(p.x*.5+.5)*width}px,${(-p.y*.5+.5)*height}px) translate(-50%,-100%)`;
   const name=unit.character==='target'?(id==='target-0'?'训练木桩':'训练晶体'):unit.character==='lingyuan'?'凌渊':'月璃',label=name+(id==='opponent'?' · 对手':'')+(!unit.alive?' · 已倒下':'');if(box.children[0].textContent!==label)box.children[0].textContent=label;
   (box.querySelector('i') as HTMLElement).style.width=(unit.hp/unit.maxHp*100)+'%';box.classList.toggle('enemy',id==='opponent');const hp=`${unit.hp} / ${unit.maxHp}`;if(box.querySelector('small')!.textContent!==hp)box.querySelector('small')!.textContent=hp;
  }
  const status=document.getElementById('combat-status')!,player=this.combat.unit('player');const last=this.combat.events[this.combat.events.length-1];const label=this.combat.winner?(this.combat.winner==='player'?'胜利 · 点击重新开始':'已倒下 · 点击重新开始'):this.combat.mode==='duel'?'1v1 · 对手 AI 已启用':!u.alive?'木桩已击毁 · 点击重置':'靠近木桩 · J / 普攻';if(status.textContent!==label)status.textContent=label;
  const feedback=document.getElementById('damage-feedback')!;feedback.hidden=!last||this.combat.clock-last.time>.85;if(last){const text=`${last.source==='player'?'命中':'受击'} −${last.damage}`;if(feedback.textContent!==text)feedback.textContent=text}
  document.getElementById('basic-attack')!.setAttribute('aria-disabled',String(!this.combat.canAct('player')));
 }
}
