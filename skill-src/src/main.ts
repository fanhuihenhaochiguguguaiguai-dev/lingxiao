import * as THREE from 'three/webgpu';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DragonEffect } from './dragon';
import { BindStar } from './bind-star';
import { StarVortex } from './star-vortex';
import { pass } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';

const $ = <T extends HTMLElement>(id:string):T => {const e=document.getElementById(id);if(!e)throw new Error('Missing interface element: '+id);return e as T;};
const canvas=$<HTMLCanvasElement>('scene');
const params=new URLSearchParams(location.search);
const state={ready:false,renderer:'',software:false,playing:false,time:0,frames:0,drawCalls:0,errors:[] as string[],quality:'high',clips:[] as string[],hasCharacter:false,hasWeaponBone:false,dragonVisible:false,stage:'准备就绪',boneSample:0,actorX:0,dragonX:0,boneNames:[] as string[],bloom:false,bloomError:'',fps:0,looping:false,slow:false,skill:1,layerVisibility:{dragon:true,circle:true,crystals:true,beams:true,chains:true,particles:true},layerRendered:{dragon:false,circle:false,crystals:false,beams:false,chains:false,particles:false},starVisible:false,starCues:[] as string[],dragonWorld:[0,0,0] as number[]};
(window as unknown as {__lingSkill:typeof state}).__lingSkill=state;
window.addEventListener('error',e=>state.errors.push(e.message));window.addEventListener('unhandledrejection',e=>state.errors.push(String(e.reason)));
let renderer:THREE.WebGPURenderer,scene:THREE.Scene,camera:THREE.PerspectiveCamera,controls:OrbitControls,dragon:DragonEffect,bindStar:BindStar,starVortex:StarVortex,actor:THREE.Group,mixer:THREE.AnimationMixer;
let post:THREE.PostProcessing|null=null;let bloomEffect:ReturnType<typeof bloom>|null=null;
let time=0,playing=false,loop=false,slow=false,started=false,last=0,previousFrame=0,metricFrames=0,rendering=false,software=false;
const duration=()=>state.skill===1?4.4:state.skill===2?6.4:7.4;
const bones=new Map<string,THREE.Bone>(),rest=new Map<string,THREE.Quaternion>();
const ease=(a:number,b:number,t:number)=>{const x=THREE.MathUtils.clamp((t-a)/(b-a),0,1);return x*x*(3-2*x)};
function setError(err:unknown){const message=err instanceof Error?err.message:String(err);state.errors.push(message);const out=$<HTMLElement>('error');out.hidden=false;out.textContent=message;$<HTMLElement>('loading-text').textContent='加载失败：'+message;}
function setPhase(t:number){const label=state.skill===3?(!started?'准备就绪':t<.85?'觉醒 · 星辰汇聚':t<1.7?'龙魂 · 显现':t<4.4?'龙卷 · 星环盘旋':t<4.95?'引力 · 核心压缩':t<5.6?'爆发 · 金蓝冲击':t<7.3?'余波 · 星渊消散':'动作结束'):state.skill===2?(!started?'准备就绪':t<.9?'聚灵 · 龙魂初现':t<2.2?'法阵 · 星轨展开':t<3.3?'青龙 · 盘旋':t<5.3?'缚星 · 阵域禁锢':t<6.3?'灵力 · 消散':'动作结束'):!started?'准备就绪':t<.95?'蓄力 · 龙魂初现':t<1.72?'突进 · 龙影随枪':t<3.2?'挥击 · 回旋龙影':t<4.25?'终结 · 能量消散':'动作结束';state.stage=label;$<HTMLElement>('phase').textContent=label;$<HTMLElement>('time').textContent=t.toFixed(2);$<HTMLElement>('phase-time').textContent=t.toFixed(2);$<HTMLInputElement>('seek').value=String(t);}
function rotateBone(name:string,x:number,y:number,z:number){const key=name.replace(/\./g,'');const b=bones.get(key),q=rest.get(key);if(!b||!q)return;const delta=new THREE.Quaternion().setFromEuler(new THREE.Euler(x,y,z));b.quaternion.copy(q).multiply(delta);}
function pose(t:number){
 const wind=ease(.05,.72,t)*(1-ease(1.05,1.55,t));const dash=ease(.82,1.22,t)*(1-ease(1.7,2.0,t));const sweep=Math.sin(Math.PI*ease(1.65,3.15,t));const end=ease(3.25,4.3,t);
 for(const [name,b] of bones){const q=rest.get(name);if(q)b.quaternion.copy(q)}
 rotateBone('chest',-.04*wind+.13*dash, -.12*wind+.35*sweep, .05*sweep);
 rotateBone('pelvis',0,.22*sweep,0);
 rotateBone('upper_arm.R',-.34*wind-.66*dash-.48*sweep,0,-.18*wind+.16*sweep);
 rotateBone('forearm.R',-.45*wind-.58*dash-.65*sweep,0,.12*sweep);
 rotateBone('hand.R',-.12*wind,-.12*sweep,.18*sweep);
 rotateBone('weapon.R',0,.15*sweep,.12*sweep);
 rotateBone('upper_arm.L',.12*wind+.20*dash,0,.18*sweep);
 rotateBone('thigh.L',.12*dash-.18*sweep,0,0);rotateBone('thigh.R',-.18*dash+.18*sweep,0,0);
 for(const side of ['L','R']){rotateBone('hair01.'+side,.08*Math.sin(t*8)*(wind+dash+sweep),0,0);rotateBone('hair02.'+side,.13*Math.sin(t*8-.8)*(wind+dash+sweep),0,0);rotateBone('cape01.'+side,.08*Math.sin(t*7-.5)*(wind+dash+sweep),0,0);}
 actor.position.x=-1+2.25*ease(.95,1.72,t);actor.rotation.y=Math.PI/2+(.50*sweep)*(1-end);
 const bone=bones.get('forearmR');state.boneSample=bone?.quaternion.x??0;
}
function poseBind(t:number){
 const raise=ease(.05,.85,t)*(1-ease(5.45,6.3,t)),hold=ease(.8,2.1,t)*(1-ease(5.4,6.3,t));
 for(const [name,b] of bones){const q=rest.get(name);if(q)b.quaternion.copy(q)}
 rotateBone('chest',-.06*raise,.12*hold,0);rotateBone('upper_arm.R',-.72*raise,0,-.28*raise);rotateBone('forearm.R',-.72*raise,0,.14*raise);rotateBone('hand.R',-.15*raise,0,.15*raise);rotateBone('weapon.R',0,0,-.16*raise);
 rotateBone('upper_arm.L',-.25*raise,0,.42*raise);rotateBone('forearm.L',-.2*raise,0,-.2*raise);
 for(const side of ['L','R']){rotateBone('hair01.'+side,.07*Math.sin(t*4)*hold,0,0);rotateBone('hair02.'+side,.12*Math.sin(t*4-.7)*hold,0,0);rotateBone('cape01.'+side,.10*Math.sin(t*4-.4)*hold,0,0)}
 actor.position.set(0,0,0);actor.rotation.y=Math.PI/2;state.boneSample=bones.get('forearmR')?.quaternion.x??0;
}
function resize(){if(!renderer||!camera)return;const w=Math.max(1,canvas.clientWidth),h=Math.max(1,canvas.clientHeight);renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
function cameraView(view:string){const target=state.skill===3?new THREE.Vector3(0,2.2,0):new THREE.Vector3(.15,.95,0);controls.target.copy(target);if(state.skill===3){if(view==='front')camera.position.set(11.5,4.5,0);else if(view==='side')camera.position.set(0,4.5,11.5);else if(view==='back')camera.position.set(-11.5,4.5,0);else camera.position.set(.01,12,0)}else if(state.skill===2){if(view==='front')camera.position.set(7.35,2.15,0);else if(view==='side')camera.position.set(.15,2.25,7.2);else if(view==='back')camera.position.set(-7.35,2.15,0);else camera.position.set(.15,8.1,.01)}else {if(view==='front')camera.position.set(.15,2.25,7.2);else if(view==='side')camera.position.set(7.35,2.15,0);else if(view==='back')camera.position.set(.15,2.25,-7.2);else camera.position.set(.15,8.1,.01);}controls.update();}
function setQuality(q:'high'|'ultra'){state.quality=q;dragon.setQuality(q);bindStar.setQuality(q);starVortex.setQuality(q);if(bloomEffect)bloomEffect.strength.value=q==='ultra'?.30:.18;renderer.setPixelRatio(Math.min(devicePixelRatio,q==='ultra'?1.5:1));renderer.shadowMap.enabled=q==='ultra';document.querySelectorAll<HTMLButtonElement>('[data-quality]').forEach(b=>b.classList.toggle('selected',b.dataset.quality===q));resize();}
function cast(skill=state.skill){state.skill=skill;started=true;playing=true;time=0;document.querySelectorAll<HTMLButtonElement>('[data-skill]').forEach(b=>b.classList.toggle('selected',Number(b.dataset.skill)===skill));$<HTMLInputElement>('seek').max=String(duration());$<HTMLElement>('duration').textContent=duration().toFixed(2)+' s';$<HTMLElement>('skill-name').textContent=skill===1?'破云·龙影斩':skill===2?'青龙·缚星阵':'星渊龙卷';$<HTMLElement>('skill-subtitle').textContent=skill===1?'LINGYUAN · SKILL 01':skill===2?'LINGYUAN · SKILL 02':'LINGYUAN · ULTIMATE';state.starCues=[];if(skill===3)cameraView('front');mixer.stopAllAction();state.playing=true;$<HTMLButtonElement>('pause').textContent='暂停';setPhase(time);}
function pauseToggle(){if(!started){started=true;time=0;mixer.stopAllAction()}playing=!playing;state.playing=playing;$<HTMLButtonElement>('pause').textContent=playing?'暂停':'继续';}
function step(){if(!started){started=true;mixer.stopAllAction()}playing=false;state.playing=false;time=Math.min(duration(),time+1/30);$<HTMLButtonElement>('pause').textContent='继续';updateScene(0);}
function updateScene(dt:number){
 if(playing){const before=time;time+=dt*(slow?.25:1);if(state.skill===3){for(const [at,cue] of [[0,'awaken'],[.85,'dragon'],[4.4,'collapse'],[4.95,'burst'],[5.6,'afterglow']] as const)if(before<=at&&time>at){state.starCues.push(cue);window.dispatchEvent(new CustomEvent('lingyuan:skill-cue',{detail:{skill:3,cue,time:at}}))}}if(time>=duration()){if(loop){time%=duration();if(state.skill===3)state.starCues=[]}else{time=duration();playing=false;state.playing=false;$<HTMLButtonElement>('pause').textContent='继续'}}}
 if(started){if(state.skill===1)pose(time);else poseBind(state.skill===3?time*6.3/7.4:time)}else mixer.update(dt);
 dragon.update(time,state.skill===1&&started&&time<duration());bindStar.update(time,state.skill===2&&started&&time<duration(),state.layerVisibility);starVortex.update(time,state.skill===3&&started&&time<duration());state.starVisible=starVortex.group.visible;for(const k of Object.keys(state.layerRendered) as Array<keyof typeof state.layerRendered>)state.layerRendered[k]=bindStar.layers[k].visible;state.dragonVisible=state.skill===1?dragon.group.visible:state.skill===2?bindStar.dragon.group.visible:starVortex.group.visible&&starVortex.dragon.visible;if(state.skill===2&&bindStar.dragon.group.visible){const world=bindStar.dragon.head.getWorldPosition(new THREE.Vector3());state.dragonWorld=[world.x,world.y,world.z]}state.actorX=actor.position.x;state.dragonX=state.skill===1?dragon.head.position.x:state.skill===2?bindStar.dragon.head.position.x:starVortex.head.position.x;state.time=time;setPhase(time);controls.update();
}
async function frame(now:number){
 if(rendering)return;rendering=true;const dt=last?Math.min((now-last)/1000,1):0;last=now;updateScene(dt);
 try{renderer.info.reset();if(post){try{post.render()}catch(e){state.bloomError=String(e);state.bloom=false;post.dispose();post=null;renderer.render(scene,camera)}}else renderer.render(scene,camera);state.frames++;metricFrames++;state.drawCalls=renderer.info.render.drawCalls;const elapsed=now-previousFrame;if(elapsed>1000){state.fps=Math.round(metricFrames*1000/elapsed);$<HTMLElement>('fps').textContent=String(state.fps);$<HTMLElement>('calls').textContent=String(state.drawCalls);previousFrame=now;metricFrames=0;}
  if(software){const backend=renderer.backend as unknown as {device?:{queue?:{onSubmittedWorkDone?:()=>Promise<void>}}};await backend.device?.queue?.onSubmittedWorkDone?.();}
 }catch(e){setError(e);playing=false;rendering=false;return}
 rendering=false;if(software)setTimeout(()=>requestAnimationFrame(frame),90);else requestAnimationFrame(frame);
}
function timeout<T>(p:Promise<T>,ms:number,message:string):Promise<T>{let timer:ReturnType<typeof setTimeout>;return Promise.race([p,new Promise<T>((_,reject)=>{timer=setTimeout(()=>reject(new Error(message)),ms)})]).finally(()=>clearTimeout(timer))}
async function main(){
 scene=new THREE.Scene();scene.background=new THREE.Color(0x071523);
 const forced=params.get('renderer')==='webgl2';let preInfo:{description?:string,vendor?:string,architecture?:string,isFallbackAdapter?:boolean}|undefined;try{const gpu=(navigator as Navigator & {gpu?:{requestAdapter:()=>Promise<{info?:typeof preInfo}|null>}}).gpu;if(!forced&&gpu)preInfo=(await timeout(gpu.requestAdapter(),4000,'GPU 检测超时'))?.info}catch{/* renderer handles compatibility */}renderer=new THREE.WebGPURenderer({canvas,antialias:true,alpha:false,forceWebGL:forced});
 try{await timeout(renderer.init(),forced?25000:15000,'图形初始化超时')}catch(e){if(!forced){const u=new URL(location.href);u.searchParams.set('renderer','webgl2');location.replace(u);return}throw e}
 const backend=renderer.backend as unknown as {isWebGPUBackend?:boolean,adapter?:{info?:{description?:string,vendor?:string,architecture?:string,isFallbackAdapter?:boolean}},device?:{queue?:unknown},gl?:WebGL2RenderingContext};
 renderer.onDeviceLost=()=>{if(!forced){const u=new URL(location.href);u.searchParams.set('renderer','webgl2');location.replace(u)}else setError('图形设备已中断，请刷新或使用其他浏览器')};
 renderer.info.autoReset=false;state.renderer=backend.isWebGPUBackend?'WebGPU':'WebGL2';const info=backend.adapter?.info||preInfo;software=!!(info?.isFallbackAdapter||/swiftshader|llvmpipe|software|lavapipe/i.test([info?.description,info?.vendor,info?.architecture].join(' ')));if(backend.gl){const ext=backend.gl.getExtension('WEBGL_debug_renderer_info');if(ext)software=/swiftshader|llvmpipe|software/i.test(String(backend.gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)))}state.software=software;$<HTMLElement>('backend').textContent=state.renderer+(software?' · 软件渲染':'');
 renderer.setPixelRatio(Math.min(devicePixelRatio,1));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
 camera=new THREE.PerspectiveCamera(46,1,.05,100);camera.position.set(3.2,2.4,4.9);controls=new OrbitControls(camera,canvas);controls.target.set(.1,1.0,0);controls.enableDamping=true;controls.minDistance=2.2;controls.maxDistance=18;controls.maxPolarAngle=Math.PI*.49;controls.update();
 scene.add(new THREE.HemisphereLight(0xb5dafa,0x15213b,1.8));const sun=new THREE.DirectionalLight(0xffe3af,2.3);sun.position.set(3,6,4);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);scene.add(sun);const rim=new THREE.DirectionalLight(0x287eff,1.8);rim.position.set(-4,2,-4);scene.add(rim);
 const platform=new THREE.Mesh(new THREE.CylinderGeometry(4.1,4.25,.15,96),new THREE.MeshStandardMaterial({color:0x121c28,metalness:.25,roughness:.78}));platform.position.y=-.095;platform.receiveShadow=true;scene.add(platform);
 for(const r of [1.1,2.1,3.25,4.02]){const ring=new THREE.Mesh(new THREE.TorusGeometry(r,.009,6,96),new THREE.MeshStandardMaterial({color:0x9b8053,metalness:.8,roughness:.3,emissive:0x29200f,emissiveIntensity:.25}));ring.rotation.x=Math.PI/2;ring.position.y=-.01;scene.add(ring)}
 dragon=new DragonEffect(scene);bindStar=new BindStar(scene);starVortex=new StarVortex(scene);dragon.setQuality('high');if(!software||params.get('bloom')==='1'){try{const scenePass=pass(scene,camera);const color=scenePass.getTextureNode('output');bloomEffect=bloom(color,.18,.35,1.0);post=new THREE.PostProcessing(renderer);post.outputNode=color.add(bloomEffect);state.bloom=true}catch(e){state.bloomError=String(e);state.bloom=false}}resize();window.addEventListener('resize',resize);
 const gltf=await timeout(new GLTFLoader().loadAsync('../lingyuan-lod1.glb'),45000,'角色模型下载超时，请检查网络后重试');actor=gltf.scene;actor.position.x=-1;actor.rotation.y=Math.PI/2;actor.traverse(obj=>{if((obj as THREE.Bone).isBone){const b=obj as THREE.Bone;bones.set(b.name,b);rest.set(b.name,b.quaternion.clone())}if((obj as THREE.Mesh).isMesh){obj.castShadow=true;obj.receiveShadow=true}});scene.add(actor);
 state.hasCharacter=true;state.boneNames=[...bones.keys()];state.hasWeaponBone=bones.has('weaponR');state.clips=gltf.animations.map(a=>a.name);if(!state.hasWeaponBone)throw new Error('角色缺少长枪绑定骨骼');
 mixer=new THREE.AnimationMixer(actor);const idle=gltf.animations.find(a=>a.name==='idle');if(idle)mixer.clipAction(idle).play();
 setQuality('high');state.ready=true;$<HTMLElement>('loading').hidden=true;requestAnimationFrame(frame);
}
$<HTMLButtonElement>('cast').addEventListener('click',()=>cast(1));$<HTMLButtonElement>('cast2').addEventListener('click',()=>cast(2));$<HTMLButtonElement>('cast3').addEventListener('click',()=>cast(3));
document.querySelectorAll<HTMLInputElement>('[data-layer]').forEach(input=>input.addEventListener('change',()=>{const key=input.dataset.layer as keyof typeof state.layerVisibility;state.layerVisibility[key]=input.checked;if(state.ready)updateScene(0)}));$<HTMLButtonElement>('pause').addEventListener('click',pauseToggle);$<HTMLButtonElement>('step').addEventListener('click',step);
$<HTMLButtonElement>('slow').addEventListener('click',e=>{slow=!slow;state.slow=slow;(e.currentTarget as HTMLButtonElement).textContent=slow?'慢动作：开':'慢动作'});
$<HTMLButtonElement>('loop').addEventListener('click',e=>{loop=!loop;state.looping=loop;(e.currentTarget as HTMLButtonElement).textContent=loop?'循环：开':'循环：关'});
$<HTMLInputElement>('seek').addEventListener('input',e=>{if(!state.ready)return;time=Number((e.currentTarget as HTMLInputElement).value);started=true;playing=false;state.playing=false;mixer.stopAllAction();$<HTMLButtonElement>('pause').textContent='继续';updateScene(0)});
document.querySelectorAll<HTMLButtonElement>('[data-view]').forEach(b=>b.addEventListener('click',()=>cameraView(b.dataset.view||'front')));document.querySelectorAll<HTMLButtonElement>('[data-quality]').forEach(b=>b.addEventListener('click',()=>setQuality(b.dataset.quality==='ultra'?'ultra':'high')));
$<HTMLButtonElement>('portrait-anyway').addEventListener('click',()=>$<HTMLElement>('rotate').classList.add('bypass'));
$<HTMLButtonElement>('landscape').addEventListener('click',async()=>{try{await document.documentElement.requestFullscreen?.();const orientation=screen.orientation as ScreenOrientation & {lock?:(s:string)=>Promise<void>};await orientation?.lock?.('landscape');}catch{/* browser may prohibit orientation lock; the prompt remains */}});
document.addEventListener('visibilitychange',()=>{last=0});
main().catch(setError);
