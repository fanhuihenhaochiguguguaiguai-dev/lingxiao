import * as THREE from 'three/webgpu';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CharacterAssets, characters, type CharacterId } from './characters';
import { DragonEffect } from './dragon';
import { BindStar } from './bind-star';
import { StarVortex } from './star-vortex';
import { MoonFrost } from './moon-frost';
import { findSpearTip } from './spear-anchor';
import { SkillAudio } from './skill-audio';
import { pass } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';

const $ = <T extends HTMLElement>(id:string):T => {const e=document.getElementById(id);if(!e)throw new Error('Missing interface element: '+id);return e as T;};
const canvas=$<HTMLCanvasElement>('scene');
const params=new URLSearchParams(location.search);
const state={ready:false,character:'lingyuan' as CharacterId,characterLoading:false,renderer:'',software:false,playing:false,time:0,frames:0,drawCalls:0,triangles:0,errors:[] as string[],quality:'high',cameraMode:'actor',cameraTarget:[.1,1,0] as number[],cameraPosition:[0,0,0] as number[],stagePosition:[0,0,0] as number[],stageYaw:0,clips:[] as string[],hasCharacter:false,hasWeaponBone:false,dragonVisible:false,moonVisible:false,moonSample:{crescentX:0,lotusScale:0,featherCount:0},stage:'准备就绪',boneSample:0,actorX:0,actorY:0,dragonX:0,boneNames:[] as string[],bloom:false,bloomError:'',fps:0,looping:false,slow:false,skill:1,layerVisibility:{dragon:true,circle:true,crystals:true,beams:true,chains:true,particles:true},layerRendered:{dragon:false,circle:false,crystals:false,beams:false,chains:false,particles:false},starVisible:false,starCues:[] as string[],dragonWorld:[0,0,0] as number[],spearTipWorld:[0,0,0] as number[],spearTipValid:false,firstDragonWorld:[0,0,0] as number[],position:[0,0,0] as number[],speed:0,motion:'idle',transition:0,casting:false,audioStatus:'loading',audioBuffers:0,audioPeak:0,audioVoices:0,audioEvents:[] as {skill:number;cue:number;at:number;audioNow:number;scheduledAudioTime:number;lateBy:number}[]};
(window as unknown as {__lingSkill:typeof state}).__lingSkill=state;
window.addEventListener('error',e=>state.errors.push(e.message));window.addEventListener('unhandledrejection',e=>state.errors.push(String(e.reason)));
let renderer:THREE.WebGPURenderer,scene:THREE.Scene,camera:THREE.PerspectiveCamera,controls:OrbitControls,dragon:DragonEffect,bindStar:BindStar,starVortex:StarVortex,moonFrost:MoonFrost,actor:THREE.Group,mixer:THREE.AnimationMixer,stage:THREE.Group;
let idleAction:THREE.AnimationAction|undefined,walkAction:THREE.AnimationAction|undefined, locomotionAction:THREE.AnimationAction|undefined;
const sound=new SkillAudio();void sound.preload();
const characterAssets=new CharacterAssets();
const keys=new Set<string>();let stickX=0,stickY=0,moveX=0,moveZ=0,heading=0;let fitDistance=0,fitActive=false,returnToIdle=false;const world=new THREE.Vector3(),velocity=new THREE.Vector3();
let post:THREE.PostProcessing|null=null;let bloomEffect:ReturnType<typeof bloom>|null=null;
let time=0,playing=false,loop=false,slow=false,started=false,last=0,previousFrame=0,metricFrames=0,rendering=false,software=false;
const duration=()=>state.skill===1?4.4:state.skill===2?6.4:7.4;
let spearTipLocal:THREE.Vector3|null=null;
const bones=new Map<string,THREE.Bone>(),rest=new Map<string,THREE.Quaternion>();
const transitionBones=new Map<string,THREE.Quaternion>();let transitionRemaining=0;const transitionDuration=.24,transitionActor=new THREE.Quaternion(),neutralActor=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,Math.PI/2,0));
const ease=(a:number,b:number,t:number)=>{const x=THREE.MathUtils.clamp((t-a)/(b-a),0,1);return x*x*(3-2*x)};
function setError(err:unknown){const message=err instanceof Error?err.message:String(err);state.errors.push(message);const out=$<HTMLElement>('error');out.hidden=false;out.textContent=message;$<HTMLElement>('loading-text').textContent='加载失败：'+message;if(state.ready){$<HTMLElement>('runtime-error-text').textContent=message;$<HTMLElement>('runtime-error').hidden=false;}}
function setPhase(t:number){const label=state.character==='yueli'?(!started?'静态工作稿 · 动作尚未完成':t<.8?'月光凝聚 · 特效试作':t<2.1?'月轮与霜羽 · 飞行':t<3.5?'冰莲绽放 · 特效试作':'余辉消散 · 特效试作'):state.skill===3?(!started?'准备就绪':t<.85?'觉醒 · 星辰汇聚':t<1.7?'龙魂 · 显现':t<4.4?'龙卷 · 星环盘旋':t<4.95?'引力 · 核心压缩':t<5.6?'爆发 · 金蓝冲击':t<7.3?'余波 · 星渊消散':'动作结束'):state.skill===2?(!started?'准备就绪':t<.9?'聚灵 · 龙魂初现':t<2.2?'法阵 · 星轨展开':t<3.3?'青龙 · 盘旋':t<5.3?'缚星 · 阵域禁锢':t<6.3?'灵力 · 消散':'动作结束'):!started?'准备就绪':t<.95?'蓄力 · 龙魂初现':t<1.72?'突进 · 龙影随枪':t<3.2?'挥击 · 回旋龙影':t<4.25?'终结 · 能量消散':'动作结束';state.stage=label;$<HTMLElement>('phase').textContent=label;$<HTMLElement>('time').textContent=t.toFixed(2);$<HTMLElement>('phase-time').textContent=t.toFixed(2);$<HTMLInputElement>('seek').value=String(t);}
function rotateBone(name:string,x:number,y:number,z:number){const key=name.replace(/\./g,'');const b=bones.get(key),q=rest.get(key);if(!b||!q)return;const delta=new THREE.Quaternion().setFromEuler(new THREE.Euler(x,y,z));b.quaternion.copy(q).multiply(delta);}
// Keep the walk clip on the lower body when translating during a cast.
function resetCastingBones(){for(const [name,b] of bones){if(state.speed>.08&&state.skill!==3&&/^(thigh|shin|foot|toe)/i.test(name))continue;const q=rest.get(name);if(q)b.quaternion.copy(q)}}
function pose(t:number){
 const wind=ease(.05,.72,t)*(1-ease(1.05,1.55,t));const dash=ease(.82,1.22,t)*(1-ease(1.7,2.0,t));const sweep=Math.sin(Math.PI*ease(1.65,3.15,t));const end=ease(3.25,4.3,t);
 resetCastingBones();
 rotateBone('chest',-.04*wind+.13*dash, -.12*wind+.35*sweep, .05*sweep);
 rotateBone('pelvis',0,.22*sweep,0);
 rotateBone('upper_arm.R',-.34*wind-.66*dash-.48*sweep,0,-.18*wind+.16*sweep);
 rotateBone('forearm.R',-.45*wind-.58*dash-.65*sweep,0,.12*sweep);
 rotateBone('hand.R',-.12*wind,-.12*sweep,.18*sweep);
 rotateBone('weapon.R',0,.15*sweep,.12*sweep);
 rotateBone('upper_arm.L',.12*wind+.20*dash,0,.18*sweep);
 if(state.speed<=.08){rotateBone('thigh.L',.12*dash-.18*sweep,0,0);rotateBone('thigh.R',-.18*dash+.18*sweep,0,0)}
 for(const side of ['L','R']){rotateBone('hair01.'+side,.08*Math.sin(t*8)*(wind+dash+sweep),0,0);rotateBone('hair02.'+side,.13*Math.sin(t*8-.8)*(wind+dash+sweep),0,0);rotateBone('cape01.'+side,.08*Math.sin(t*7-.5)*(wind+dash+sweep),0,0);}
 actor.position.x=-1+2.25*ease(.95,1.72,t);actor.position.y=0;actor.rotation.y=Math.PI/2+(.50*sweep)*(1-end);stage.updateWorldMatrix(true,false);const position=stage.localToWorld(actor.position.clone()),radius=Math.hypot(position.x,position.z);if(radius>9.5){position.x*=9.5/radius;position.z*=9.5/radius;actor.position.copy(stage.worldToLocal(position))}
 const bone=bones.get('forearmR');state.boneSample=bone?.quaternion.x??0;
}
function poseBind(t:number){
 const raise=ease(.05,.85,t)*(1-ease(5.45,6.3,t)),hold=ease(.8,2.1,t)*(1-ease(5.4,6.3,t));
 resetCastingBones();
 rotateBone('chest',-.06*raise,.12*hold,0);rotateBone('upper_arm.R',-.72*raise,0,-.28*raise);rotateBone('forearm.R',-.72*raise,0,.14*raise);rotateBone('hand.R',-.15*raise,0,.15*raise);rotateBone('weapon.R',0,0,-.16*raise);
 rotateBone('upper_arm.L',-.25*raise,0,.42*raise);rotateBone('forearm.L',-.2*raise,0,-.2*raise);
 for(const side of ['L','R']){rotateBone('hair01.'+side,.07*Math.sin(t*4)*hold,0,0);rotateBone('hair02.'+side,.12*Math.sin(t*4-.7)*hold,0,0);rotateBone('cape01.'+side,.10*Math.sin(t*4-.4)*hold,0,0)}
 actor.position.set(0,0,0);actor.rotation.y=Math.PI/2;state.boneSample=bones.get('forearmR')?.quaternion.x??0;
}
function poseUltimate(t:number){
 const charge=ease(.05,.9,t)*(1-ease(6.2,7.3,t));const lift=ease(.85,1.8,t)*(1-ease(5.25,6.45,t));const impact=Math.sin(Math.PI*ease(4.4,5.3,t));
 resetCastingBones();
 rotateBone('pelvis',-.06*lift,0,.05*impact);rotateBone('chest',-.12*charge+.12*impact,.10*lift,.05*impact);
 rotateBone('upper_arm.R',-1.0*charge-.25*impact,0,-.28*charge);rotateBone('forearm.R',-.85*charge-.2*impact,0,.12*charge);rotateBone('hand.R',-.15*charge,0,.12*charge);rotateBone('weapon.R',0,0,-.18*charge);
 rotateBone('upper_arm.L',-.35*charge,0,.48*charge);rotateBone('forearm.L',-.22*charge,0,-.2*charge);
 rotateBone('thigh.L',-.20*lift,0,0);rotateBone('thigh.R',.25*lift,0,0);rotateBone('shin.L',.20*lift,0,0);rotateBone('shin.R',-.20*lift,0,0);
 for(const side of ['L','R']){rotateBone('hair01.'+side,.08*Math.sin(t*4)*charge,0,0);rotateBone('hair02.'+side,.14*Math.sin(t*4-.7)*charge,0,0);rotateBone('cape01.'+side,.11*Math.sin(t*4-.4)*charge,0,0)}
 actor.position.set(0,.65*lift,0);actor.rotation.y=Math.PI/2+.12*impact;state.boneSample=bones.get('forearmR')?.quaternion.x??0;
}
function resize(){if(!renderer||!camera)return;const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight);renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
function cameraView(view:string){
 const target=stage?stage.position.clone():new THREE.Vector3();target.y=state.skill===3?2.2:.95;controls.target.copy(target);
 const d=state.skill===3?11.5:7.35;
 if(view==='front')camera.position.set(target.x+d,target.y+1.2,target.z);
 else if(view==='side')camera.position.set(target.x,target.y+1.2,target.z+d);
 else if(view==='right')camera.position.set(target.x,target.y+1.2,target.z-d);
 else if(view==='back')camera.position.set(target.x-d,target.y+1.2,target.z);
 else if(view==='angle')camera.position.set(target.x+d*.7,target.y+d*.34,target.z+d*.7);
 else if(view==='up')camera.position.set(target.x+d,.22,target.z);
 else camera.position.set(target.x+.01,state.skill===3?12:8.1,target.z+.01);
 controls.update();
}
function followCamera(dt:number){
 if(state.cameraMode==='free'||!actor)return;
 const aim=new THREE.Vector3();
 if(state.cameraMode==='dragon'&&state.dragonVisible){const head=state.skill===1?dragon.head:state.skill===2?bindStar.dragon.head:starVortex.head;head.getWorldPosition(aim)}
 else if(started&&state.skill===3){stage.getWorldPosition(aim);aim.y+=2.2}else {actor.getWorldPosition(aim);aim.y+=1.05}
 const alpha=1-Math.exp(-Math.min(dt,.1)*3.2),delta=aim.sub(controls.target).multiplyScalar(alpha);controls.target.add(delta);camera.position.add(delta);
}
function setQuality(q:'high'|'ultra'){state.quality=q;dragon.setQuality(q);bindStar.setQuality(q);starVortex.setQuality(q);moonFrost.setQuality(q);if(bloomEffect)bloomEffect.strength.value=q==='ultra'?.30:.18;renderer.setPixelRatio(Math.min(devicePixelRatio,q==='ultra'?1.5:1));renderer.shadowMap.enabled=q==='ultra';document.querySelectorAll<HTMLButtonElement>('[data-quality]').forEach(b=>b.classList.toggle('selected',b.dataset.quality===q));resize();}
function cast(skill=state.skill){if(!state.ready||!characters[state.character].hasSkills||state.characterLoading)return;const audioUnlock=sound.unlock();sound.start(skill,0);transitionRemaining=0;state.transition=0;transitionBones.clear();actor.getWorldPosition(world);state.skill=skill;started=true;playing=true;returnToIdle=false;time=0;state.casting=true;stage.position.copy(world);if(skill===1)stage.position.add(new THREE.Vector3(1,0,0).applyAxisAngle(new THREE.Vector3(0,1,0),heading));stage.rotation.y=heading;state.stageYaw=stage.rotation.y;state.stagePosition=stage.position.toArray();fitDistance=skill===3?12:skill===2?9:8;fitActive=true;locomotionAction=undefined;document.querySelectorAll<HTMLButtonElement>('[data-skill]').forEach(b=>b.classList.toggle('selected',Number(b.dataset.skill)===skill));$<HTMLInputElement>('seek').max=String(duration());$<HTMLElement>('duration').textContent=duration().toFixed(2)+' s';$<HTMLElement>('skill-name').textContent=skill===1?'破云·龙影斩':skill===2?'青龙·缚星阵':'龙吟·苍穹破';$<HTMLElement>('skill-subtitle').textContent=skill===1?'LINGYUAN · SKILL 01':skill===2?'LINGYUAN · SKILL 02':'LINGYUAN · ULTIMATE';state.starCues=[];mixer.stopAllAction();state.playing=true;$<HTMLButtonElement>('pause').textContent='暂停';setPhase(time);void audioUnlock.then(()=>{if(started&&playing&&state.skill===skill)sound.tick(time,true,slow)});}
function castMoon(){
 if(!state.ready||state.character!=='yueli'||state.characterLoading)return;
 sound.stop();transitionRemaining=0;state.transition=0;transitionBones.clear();actor.getWorldPosition(world);
 stage.position.copy(world);stage.rotation.y=heading;state.stageYaw=stage.rotation.y;state.stagePosition=stage.position.toArray();actor.position.set(0,0,0);actor.rotation.y=Math.PI/2;
 state.skill=1;started=true;playing=true;returnToIdle=false;time=0;state.casting=true;state.playing=true;
 fitDistance=7;fitActive=true;$<HTMLElement>('skill-name').textContent='月华霜羽';$<HTMLElement>('skill-subtitle').textContent='月璃 · 特效试作 / 无角色动画和音效';setPhase(0);
}
function pauseToggle(){if(!characters[state.character].hasSkills)return;if(!started){started=true;time=0;mixer.stopAllAction()}playing=!playing;if(playing){sound.start(state.skill,time);void sound.unlock().then(()=>{if(started&&playing)sound.tick(time,true,slow)})}else sound.stop();state.playing=playing;$<HTMLButtonElement>('pause').textContent=playing?'暂停':'继续';}
function step(){if(!characters[state.character].hasSkills)return;sound.stop();if(!started){started=true;mixer.stopAllAction()}playing=false;state.playing=false;time=Math.min(duration(),time+1/30);$<HTMLButtonElement>('pause').textContent='继续';updateScene(0);}
function playMotion(name:'idle'|'walk'){
 const next=name==='walk'?walkAction:idleAction;if(!next||locomotionAction===next)return;
 next.reset().setEffectiveWeight(1).play();if(locomotionAction)locomotionAction.crossFadeTo(next,.22,false);locomotionAction=next;state.motion=name;
}
function leaveSkill(){
 if(!started)return;sound.stop();transitionBones.clear();for(const [name,b] of bones)transitionBones.set(name,b.quaternion.clone());transitionActor.copy(actor.quaternion);transitionRemaining=transitionDuration;actor.getWorldPosition(world);stage.position.copy(world);stage.rotation.y=heading;state.stageYaw=stage.rotation.y;state.stagePosition=stage.position.toArray();actor.position.set(0,0,0);actor.rotation.y=Math.PI/2;started=false;playing=false;state.playing=false;state.casting=false;time=0;fitActive=true;fitDistance=7.2;locomotionAction=undefined;playMotion('idle');
 if(state.character==='yueli'){$<HTMLElement>('skill-name').textContent='月璃';$<HTMLElement>('skill-subtitle').textContent='YUELI · STATIC STUDY'}
}
function moveCharacter(dt:number){
 let x=stickX+(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0),y=stickY+(keys.has('s')||keys.has('arrowdown')?1:0)-(keys.has('w')||keys.has('arrowup')?1:0);const length=Math.hypot(x,y);if(length>1){x/=length;y/=length}if(length<.08){x=0;y=0}
 const forward=controls.target.clone().sub(camera.position);forward.y=0;forward.normalize();if(forward.lengthSq()<.001)forward.set(-1,0,0);const right=new THREE.Vector3(-forward.z,0,forward.x);const direction=right.multiplyScalar(x).addScaledVector(forward,-y);const running=keys.has('shift')||Math.hypot(stickX,stickY)>.92;const maxSpeed=(running?2.5:1.45)*(started&&state.skill===3?.7:1);const d=Math.min(dt,.08),alpha=1-Math.exp(-d*(length>.08?7:10));velocity.x+=(direction.x*maxSpeed-velocity.x)*alpha;velocity.z+=(direction.z*maxSpeed-velocity.z)*alpha;
 const speed=Math.hypot(velocity.x,velocity.z);state.speed=speed;if(speed>.055){stage.position.addScaledVector(velocity,d);const radius=Math.hypot(stage.position.x,stage.position.z);if(radius>9.5){stage.position.x*=9.5/radius;stage.position.z*=9.5/radius}const goal=Math.atan2(-velocity.z,velocity.x),delta=Math.atan2(Math.sin(goal-heading),Math.cos(goal-heading));heading+=delta*(1-Math.exp(-d*9));if(!started)stage.rotation.y=heading;playMotion('walk');state.motion=state.character==='yueli'?'static':running?'fast_walk':'walk';if(walkAction)walkAction.setEffectiveTimeScale(running?1.5:1)}else{velocity.set(0,0,0);playMotion('idle')}
 mixer.update(d);if(!started){actor.position.set(0,0,0);actor.rotation.y=Math.PI/2}if(transitionRemaining>0){transitionRemaining=Math.max(0,transitionRemaining-d);const alpha=1-transitionRemaining/transitionDuration;for(const [name,b] of bones){const from=transitionBones.get(name);if(from){const to=b.quaternion.clone();b.quaternion.slerpQuaternions(from,to,alpha)}}actor.quaternion.slerpQuaternions(transitionActor,neutralActor,alpha);if(!transitionRemaining)transitionBones.clear()}state.transition=transitionRemaining/transitionDuration;
}
function adjustSkillCamera(dt:number){
 if(!fitActive)return;const offset=camera.position.clone().sub(controls.target),distance=offset.length();if(distance<.01)return;const a=1-Math.exp(-Math.min(dt,.1)*2.8),next=distance+(fitDistance-distance)*a;camera.position.copy(controls.target).add(offset.multiplyScalar(next/distance));if(Math.abs(fitDistance-next)<.02)fitActive=false;
}
function updateScene(dt:number){
 if(playing){const before=time;time+=dt*(slow?.25:1);if(state.skill===3){for(const [at,cue] of [[0,'awaken'],[.85,'dragon'],[4.4,'collapse'],[4.95,'burst'],[5.6,'afterglow']] as const)if(before<=at&&time>at){state.starCues.push(cue);window.dispatchEvent(new CustomEvent('lingyuan:skill-cue',{detail:{skill:3,cue,time:at}}))}}if(time>=duration()){if(loop){time%=duration();if(state.character==='lingyuan')sound.start(state.skill,time);if(state.skill===3)state.starCues=[]}else{time=duration();playing=false;state.playing=false;returnToIdle=true;$<HTMLButtonElement>('pause').textContent='继续'}}}
 moveCharacter(dt);
 if(started&&state.character==='lingyuan'){if(state.skill===1)pose(time);else if(state.skill===2)poseBind(time);else poseUltimate(time)}
 dragon.group.position.set(0,0,0);dragon.update(time,state.character==='lingyuan'&&state.skill===1&&started&&time<duration());if(state.skill===1&&dragon.group.visible&&spearTipLocal){actor.updateMatrixWorld(true);const tip=bones.get('weaponR')!.localToWorld(spearTipLocal.clone());dragon.group.position.copy(stage.worldToLocal(tip)).sub(dragon.head.position).multiplyScalar(1-ease(1.3,1.95,time))}bindStar.update(time,state.character==='lingyuan'&&state.skill===2&&started&&time<duration(),state.layerVisibility);starVortex.update(time,state.character==='lingyuan'&&state.skill===3&&started&&time<duration());moonFrost.update(time,state.character==='yueli'&&started&&time<duration());state.moonVisible=moonFrost.group.visible;state.moonSample=moonFrost.sample();state.starVisible=starVortex.group.visible;for(const k of Object.keys(state.layerRendered) as Array<keyof typeof state.layerRendered>)state.layerRendered[k]=bindStar.layers[k].visible;state.dragonVisible=state.skill===1?dragon.group.visible:state.skill===2?bindStar.dragon.group.visible:starVortex.group.visible&&starVortex.dragon.visible;if(state.dragonVisible){const h=state.skill===1?dragon.head:state.skill===2?bindStar.dragon.head:starVortex.head;state.dragonWorld=h.getWorldPosition(new THREE.Vector3()).toArray()}if(state.skill===1&&dragon.group.visible&&spearTipLocal){actor.updateMatrixWorld(true);const tip=bones.get('weaponR')!.localToWorld(spearTipLocal.clone()),head=dragon.head.getWorldPosition(new THREE.Vector3());state.spearTipWorld=tip.toArray();state.firstDragonWorld=head.toArray()}actor.getWorldPosition(world);state.actorX=world.x;state.actorY=world.y;state.position=world.toArray();state.dragonX=state.skill===1?dragon.head.position.x:state.skill===2?bindStar.dragon.head.position.x:starVortex.head.position.x;state.time=time;if(state.character==='lingyuan')sound.tick(time,playing,slow);state.audioStatus=sound.error||(!sound.context?'等待交互':sound.context.state);const status=$<HTMLElement>('audio-status'),audioLabel=sound.error?'音效不可用，请检查网络或重新加载':sound.muted?'音效已静音':sound.buffers.size<9?'音效加载中':sound.context?.state==='running'?'音效已启用':'点击技能后启用音效';if(status.textContent!==audioLabel)status.textContent=audioLabel;$<HTMLElement>('audio-alert').hidden=!sound.error;state.audioEvents=sound.events;state.audioBuffers=sound.buffers.size;state.audioVoices=sound.voices.size;state.audioPeak=sound.sample();setPhase(time);followCamera(dt);adjustSkillCamera(dt);controls.update();state.cameraTarget=controls.target.toArray();state.cameraPosition=camera.position.toArray();state.stagePosition=stage.position.toArray();state.stageYaw=stage.rotation.y;if(returnToIdle){returnToIdle=false;leaveSkill()}
}
async function frame(now:number){
 if(rendering)return;rendering=true;const dt=last?Math.min((now-last)/1000,1):0;last=now;updateScene(dt);
 try{renderer.info.reset();if(post){try{post.render()}catch(e){state.bloomError=String(e);state.bloom=false;post.dispose();post=null;renderer.render(scene,camera)}}else renderer.render(scene,camera);state.frames++;metricFrames++;state.drawCalls=renderer.info.render.drawCalls;state.triangles=renderer.info.render.triangles;const elapsed=now-previousFrame;if(elapsed>1000){state.fps=Math.round(metricFrames*1000/elapsed);$<HTMLElement>('fps').textContent=String(state.fps);$<HTMLElement>('calls').textContent=String(state.drawCalls);previousFrame=now;metricFrames=0;}
  if(software){const backend=renderer.backend as unknown as {device?:{queue?:{onSubmittedWorkDone?:()=>Promise<void>}}};await backend.device?.queue?.onSubmittedWorkDone?.();}
 }catch(e){setError(e);playing=false;rendering=false;return}
 rendering=false;if(software)setTimeout(()=>requestAnimationFrame(frame),90);else requestAnimationFrame(frame);
}
function timeout<T>(p:Promise<T>,ms:number,message:string):Promise<T>{let timer:ReturnType<typeof setTimeout>;return Promise.race([p,new Promise<T>((_,reject)=>{timer=setTimeout(()=>reject(new Error(message)),ms)})]).finally(()=>clearTimeout(timer))}
async function switchCharacter(id:CharacterId){
 if(!state.ready||state.characterLoading)return;
 if(id===state.character){$<HTMLElement>('character-picker').hidden=true;return}
 state.characterLoading=true;const message=$<HTMLElement>('character-message');message.textContent='正在加载'+characters[id].name+'…';
 document.querySelectorAll<HTMLButtonElement>('[data-character]').forEach(b=>b.disabled=true);
 try{
  const gltf=await timeout(characterAssets.load(id),45000,'人物加载超时，请检查网络后重试');
  if(started)leaveSkill();sound.stop();mixer.stopAllAction();stage.remove(actor);
  bones.clear();rest.clear();transitionBones.clear();transitionRemaining=0;state.transition=0;velocity.set(0,0,0);keys.clear();releaseStick();
  actor=gltf.scene;actor.position.set(0,0,0);actor.rotation.y=Math.PI/2;
  actor.traverse(obj=>{if((obj as THREE.Bone).isBone){const b=obj as THREE.Bone;bones.set(b.name,b);rest.set(b.name,b.quaternion.clone())}if((obj as THREE.Mesh).isMesh){obj.castShadow=true;obj.receiveShadow=true}});
  stage.add(actor);state.character=id;state.hasCharacter=true;state.boneNames=[...bones.keys()];state.hasWeaponBone=bones.has('weaponR');state.clips=gltf.animations.map(a=>a.name);
  spearTipLocal=state.hasWeaponBone?findSpearTip(actor,bones.get('weaponR')!):null;state.spearTipValid=!!spearTipLocal;
  mixer=new THREE.AnimationMixer(actor);idleAction=undefined;walkAction=undefined;locomotionAction=undefined;
  const idle=gltf.animations.find(a=>a.name==='idle'),walk=gltf.animations.find(a=>a.name==='walk');if(idle)idleAction=mixer.clipAction(idle);if(walk)walkAction=mixer.clipAction(walk);
  state.motion=id==='yueli'?'static':'idle';if(id==='lingyuan')playMotion('idle');
  fitDistance=id==='yueli'?4.2:7.2;fitActive=true;
  const skills=document.querySelector<HTMLElement>('.skill-buttons');if(skills)skills.hidden=false;$<HTMLButtonElement>('cast-yueli').hidden=id!=='yueli';
  document.querySelectorAll<HTMLButtonElement>('[data-skill]').forEach(b=>{b.disabled=!characters[id].hasSkills;b.hidden=!characters[id].hasSkills});
  $<HTMLElement>('skill-name').textContent=id==='yueli'?'月璃':state.skill===1?'破云·龙影斩':state.skill===2?'青龙·缚星阵':'龙吟·苍穹破';
  $<HTMLElement>('skill-subtitle').textContent=id==='yueli'?'YUELI · STATIC STUDY':'LINGYUAN · SKILL '+String(state.skill).padStart(2,'0');
  const mark=document.querySelector<HTMLElement>('.mark');if(mark)mark.textContent=id==='yueli'?'璃':'渊';
  const hint=document.querySelector<HTMLElement>('.stage-label small');if(hint)hint.textContent=id==='yueli'?'静态工作稿 · 拖动环绕 · 摇杆移动位置':'WASD 移动 · Shift 加速 · 1/2/3 技能 · 拖动环绕';
  document.querySelectorAll<HTMLButtonElement>('[data-character]').forEach(b=>b.classList.toggle('selected',b.dataset.character===id));
  setPhase(0);message.textContent='';$<HTMLElement>('character-picker').hidden=true;$<HTMLElement>('panel').hidden=true;$<HTMLButtonElement>('panel-toggle').setAttribute('aria-expanded','false');
 }catch(e){message.textContent='加载失败：'+(e instanceof Error?e.message:String(e));state.errors.push(message.textContent)}
 finally{state.characterLoading=false;document.querySelectorAll<HTMLButtonElement>('[data-character]').forEach(b=>b.disabled=false)}
}
async function main(){
 scene=new THREE.Scene();scene.background=new THREE.Color(0x071523);
 const forced=params.get('renderer')==='webgl2';let preInfo:{description?:string,vendor?:string,architecture?:string,isFallbackAdapter?:boolean}|undefined;try{const gpu=(navigator as Navigator & {gpu?:{requestAdapter:()=>Promise<{info?:typeof preInfo}|null>}}).gpu;if(!forced&&gpu)preInfo=(await timeout(gpu.requestAdapter(),4000,'GPU 检测超时'))?.info}catch{/* renderer handles compatibility */}renderer=new THREE.WebGPURenderer({canvas,antialias:true,alpha:false,forceWebGL:forced});
 try{await timeout(renderer.init(),forced?25000:15000,'图形初始化超时')}catch(e){if(!forced){const u=new URL(location.href);u.searchParams.set('renderer','webgl2');location.replace(u);return}throw e}
 const backend=renderer.backend as unknown as {isWebGPUBackend?:boolean,adapter?:{info?:{description?:string,vendor?:string,architecture?:string,isFallbackAdapter?:boolean}},device?:{queue?:unknown},gl?:WebGL2RenderingContext};
 renderer.onDeviceLost=()=>{if(!forced){const u=new URL(location.href);u.searchParams.set('renderer','webgl2');location.replace(u)}else setError('图形设备已中断，请刷新或使用其他浏览器')};
 renderer.info.autoReset=false;state.renderer=backend.isWebGPUBackend?'WebGPU':'WebGL2';const info=backend.adapter?.info||preInfo;software=!!(info?.isFallbackAdapter||/swiftshader|llvmpipe|software|lavapipe/i.test([info?.description,info?.vendor,info?.architecture].join(' ')));if(backend.gl){const ext=backend.gl.getExtension('WEBGL_debug_renderer_info');if(ext)software=/swiftshader|llvmpipe|software/i.test(String(backend.gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)))}state.software=software;$<HTMLElement>('backend').textContent=state.renderer+(software?' · 软件渲染':'');
 renderer.setPixelRatio(Math.min(devicePixelRatio,1));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
 camera=new THREE.PerspectiveCamera(46,1,.05,100);camera.position.set(5.2,4.1,5.8);controls=new OrbitControls(camera,canvas);controls.target.set(.1,1.0,0);controls.enableDamping=true;controls.minDistance=2.2;controls.maxDistance=30;controls.maxPolarAngle=Math.PI*.68;controls.update();
 scene.add(new THREE.HemisphereLight(0xb5dafa,0x15213b,1.8));const sun=new THREE.DirectionalLight(0xffe3af,2.3);sun.position.set(3,6,4);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);scene.add(sun);const rim=new THREE.DirectionalLight(0x287eff,1.8);rim.position.set(-4,2,-4);scene.add(rim);
 const platform=new THREE.Mesh(new THREE.CylinderGeometry(17,17.1,.15,96),new THREE.MeshStandardMaterial({color:0x121c28,metalness:.25,roughness:.78}));platform.position.y=-.095;platform.receiveShadow=true;scene.add(platform);
 const seams:number[]=[];for(let a=-16;a<=16;a+=1.25){const span=Math.sqrt(16.9*16.9-a*a);seams.push(a,-.017,-span,a,-.017,span,-span,-.017,a,span,-.017,a)}const seamGeo=new THREE.BufferGeometry();seamGeo.setAttribute('position',new THREE.Float32BufferAttribute(seams,3));scene.add(new THREE.LineSegments(seamGeo,new THREE.LineBasicMaterial({color:0x7294a7,transparent:true,opacity:.10,depthWrite:false})));
 for(const r of [3.25,7,10.5,16.9]){const ring=new THREE.Mesh(new THREE.TorusGeometry(r,.009,6,96),new THREE.MeshStandardMaterial({color:0x9b8053,metalness:.8,roughness:.3,emissive:0x29200f,emissiveIntensity:.25}));ring.rotation.x=Math.PI/2;ring.position.y=-.01;scene.add(ring)}
 stage=new THREE.Group();scene.add(stage);dragon=new DragonEffect(stage);bindStar=new BindStar(stage);starVortex=new StarVortex(stage);moonFrost=new MoonFrost(stage);dragon.setQuality('high');if(!software||params.get('bloom')==='1'){try{const scenePass=pass(scene,camera);const color=scenePass.getTextureNode('output');bloomEffect=bloom(color,.18,.35,1.0);post=new THREE.PostProcessing(renderer);post.outputNode=color.add(bloomEffect);state.bloom=true}catch(e){state.bloomError=String(e);state.bloom=false}}resize();window.addEventListener('resize',resize);
 const gltf=await timeout(characterAssets.load('lingyuan'),45000,'角色模型下载超时，请检查网络后重试');actor=gltf.scene;actor.position.set(0,0,0);actor.rotation.y=Math.PI/2;actor.traverse(obj=>{if((obj as THREE.Bone).isBone){const b=obj as THREE.Bone;bones.set(b.name,b);rest.set(b.name,b.quaternion.clone())}if((obj as THREE.Mesh).isMesh){obj.castShadow=true;obj.receiveShadow=true}});stage.add(actor);
 state.hasCharacter=true;state.boneNames=[...bones.keys()];state.hasWeaponBone=bones.has('weaponR');state.clips=gltf.animations.map(a=>a.name);if(!state.hasWeaponBone)throw new Error('角色缺少长枪绑定骨骼');spearTipLocal=findSpearTip(actor,bones.get('weaponR')!);state.spearTipValid=!!spearTipLocal;if(!spearTipLocal)throw new Error('无法识别长枪枪尖的骨骼绑定');
 mixer=new THREE.AnimationMixer(actor);const idle=gltf.animations.find(a=>a.name==='idle'),walk=gltf.animations.find(a=>a.name==='walk');if(idle)idleAction=mixer.clipAction(idle);if(walk)walkAction=mixer.clipAction(walk);playMotion('idle');
 setQuality('high');state.ready=true;$<HTMLElement>('loading').hidden=true;requestAnimationFrame(frame);
}
function bindSkillButton(id:string,action:()=>void){
 const button=$<HTMLButtonElement>(id);let lastTouch=-1000;
 button.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'&&!button.disabled){e.preventDefault();lastTouch=performance.now();action()}});
 button.addEventListener('click',e=>{if(e.detail!==0&&performance.now()-lastTouch<800)return;action()});
}
bindSkillButton('cast',()=>cast(1));bindSkillButton('cast2',()=>cast(2));bindSkillButton('cast3',()=>cast(3));bindSkillButton('cast-yueli',castMoon);
document.querySelectorAll<HTMLInputElement>('[data-layer]').forEach(input=>input.addEventListener('change',()=>{const key=input.dataset.layer as keyof typeof state.layerVisibility;state.layerVisibility[key]=input.checked;if(state.ready)updateScene(0)}));$<HTMLButtonElement>('pause').addEventListener('click',pauseToggle);$<HTMLButtonElement>('step').addEventListener('click',step);
$<HTMLButtonElement>('slow').addEventListener('click',e=>{sound.stop();sound.start(state.skill,time);slow=!slow;state.slow=slow;(e.currentTarget as HTMLButtonElement).textContent=slow?'慢动作：开':'慢动作'});
$<HTMLButtonElement>('loop').addEventListener('click',e=>{loop=!loop;state.looping=loop;(e.currentTarget as HTMLButtonElement).textContent=loop?'循环：开':'循环：关'});
$<HTMLInputElement>('seek').addEventListener('input',e=>{if(!state.ready)return;time=Number((e.currentTarget as HTMLInputElement).value);started=true;playing=false;sound.stop();state.playing=false;mixer.stopAllAction();$<HTMLButtonElement>('pause').textContent='继续';updateScene(0)});
document.querySelectorAll<HTMLButtonElement>('[data-follow]').forEach(b=>b.addEventListener('click',()=>{state.cameraMode=b.dataset.follow||'free';document.querySelectorAll<HTMLButtonElement>('[data-follow]').forEach(v=>v.classList.toggle('selected',v===b))}));
document.querySelectorAll<HTMLButtonElement>('[data-view]').forEach(b=>b.addEventListener('click',()=>{fitActive=false;cameraView(b.dataset.view||'front')}));document.querySelectorAll<HTMLButtonElement>('[data-quality]').forEach(b=>b.addEventListener('click',()=>setQuality(b.dataset.quality==='ultra'?'ultra':'high')));
$<HTMLButtonElement>('portrait-anyway').addEventListener('click',()=>$<HTMLElement>('rotate').classList.add('bypass'));
$<HTMLButtonElement>('landscape').addEventListener('click',async()=>{try{await document.documentElement.requestFullscreen?.();const orientation=screen.orientation as ScreenOrientation & {lock?:(s:string)=>Promise<void>};await orientation?.lock?.('landscape');}catch{/* browser may prohibit orientation lock; the prompt remains */}});
const joystick=$<HTMLElement>('joystick'),knob=$<HTMLElement>('joystick-knob');
function stickMove(e:PointerEvent){const r=joystick.getBoundingClientRect(),limit=r.width*.33;let x=e.clientX-r.left-r.width/2,y=e.clientY-r.top-r.height/2;const n=Math.hypot(x,y);if(n>limit){x*=limit/n;y*=limit/n}stickX=x/limit;stickY=y/limit;knob.style.transform=`translate(${x}px,${y}px)`}
joystick.addEventListener('pointerdown',e=>{e.preventDefault();joystick.setPointerCapture(e.pointerId);stickMove(e)});joystick.addEventListener('pointermove',e=>{if(joystick.hasPointerCapture(e.pointerId))stickMove(e)});function releaseStick(){stickX=stickY=0;knob.style.transform=''}joystick.addEventListener('pointerup',releaseStick);joystick.addEventListener('pointercancel',releaseStick);joystick.addEventListener('lostpointercapture',releaseStick);
window.addEventListener('keydown',e=>{const picker=$<HTMLElement>('character-picker');if(!picker.hidden){if(e.key==='Escape'&&!state.characterLoading){picker.hidden=true;$<HTMLButtonElement>('open-characters').focus()}return}if(['INPUT','SELECT','TEXTAREA'].includes((document.activeElement as HTMLElement)?.tagName))return;const k=e.key.toLowerCase();if(['1','2','3'].includes(k)&&!e.repeat){if(state.character==='yueli'&&k==='1')castMoon();else cast(Number(k));e.preventDefault();return}if(['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright','shift'].includes(k)){keys.add(k);e.preventDefault()}});window.addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));window.addEventListener('blur',()=>{keys.clear();releaseStick()});
$<HTMLButtonElement>('camera-reset').addEventListener('click',()=>{state.cameraMode='actor';fitActive=false;cameraView('angle');document.querySelectorAll<HTMLButtonElement>('[data-follow]').forEach(b=>b.classList.toggle('selected',b.dataset.follow==='actor'))});
$<HTMLButtonElement>('mute').addEventListener('click',()=>{sound.muted=!sound.muted;sound.applyVolume();$<HTMLButtonElement>('mute').textContent=sound.muted?'取消静音':'静音'});
$<HTMLInputElement>('volume').addEventListener('input',e=>{sound.volume=Number((e.currentTarget as HTMLInputElement).value);sound.applyVolume()});
$<HTMLButtonElement>('panel-toggle').addEventListener('click',()=>{const p=$<HTMLElement>('panel');p.hidden=!p.hidden;$<HTMLButtonElement>('panel-toggle').setAttribute('aria-expanded',String(!p.hidden))});
$<HTMLButtonElement>('open-characters').addEventListener('click',()=>{$<HTMLElement>('character-picker').hidden=false;$<HTMLElement>('character-message').textContent='';$<HTMLButtonElement>('close-characters').focus();});
$<HTMLButtonElement>('close-characters').addEventListener('click',()=>{$<HTMLElement>('character-picker').hidden=true});
document.querySelectorAll<HTMLButtonElement>('[data-character]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.character;if(id==='lingyuan'||id==='yueli')void switchCharacter(id)}));
$<HTMLButtonElement>('clean-mode').addEventListener('click',()=>{document.querySelector('.shell')?.classList.toggle('clean');const on=document.querySelector('.shell')?.classList.contains('clean');$<HTMLButtonElement>('clean-mode').textContent=on?'退出纯净':'纯净';});
canvas.addEventListener('pointerdown',()=>{fitActive=false});canvas.addEventListener('wheel',()=>{fitActive=false},{passive:true});
$<HTMLButtonElement>('runtime-retry').addEventListener('click',()=>location.reload());
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();playing=false;state.playing=false;sound.stop();setError('图形上下文已中断，请重新加载页面。')});
document.addEventListener('visibilitychange',()=>{last=0;keys.clear();releaseStick();if(document.hidden&&started&&playing){playing=false;state.playing=false;sound.stop();$<HTMLButtonElement>('pause').textContent='继续'}});
main().catch(setError);
