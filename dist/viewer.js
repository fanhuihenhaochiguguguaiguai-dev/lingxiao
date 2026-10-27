import * as pc from './engine/playcanvas.min.mjs';
const $=id=>document.getElementById(id),canvas=$('canvas');
const state=window.__lingyuan={ready:false,errors:[],frames:0,renderer:null,lod:0,animation:'pose',triangles:0,drawCalls:0};
window.addEventListener('error',e=>state.errors.push(e.message));window.addEventListener('unhandledrejection',e=>state.errors.push(String(e.reason)));
let app,camera,character,device,key,fill,loaded={},gray=false,yaw=0,pitch=.04,radius=3.9,target=new pc.Vec3(0,1,0),lastX=0,lastY=0,dragging=false,prevPinch=0;
const counts=[61686,0,0];
async function fetchStats(){for(let n=0;n<3;n++){let b=await fetch(`lingyuan-lod${n}.glb`).then(r=>r.arrayBuffer());let v=new DataView(b),len=v.getUint32(12,true),doc=JSON.parse(new TextDecoder().decode(new Uint8Array(b,20,len)));counts[n]=doc.meshes.reduce((s,m)=>s+m.primitives.reduce((p,x)=>p+(x.indices===undefined?0:doc.accessors[x.indices].count/3),0),0)}}
function resize(){if(!app)return;let r=canvas.parentElement.getBoundingClientRect();app.resizeCanvas(Math.max(1,r.width),Math.max(1,r.height))}
function updateCamera(){let cp=Math.cos(pitch);camera.setPosition(target.x+radius*Math.sin(yaw)*cp,target.y+radius*Math.sin(pitch),target.z+radius*Math.cos(yaw)*cp);camera.lookAt(target)}
function loadModel(n){if(loaded[n])return Promise.resolve(loaded[n]);return new Promise((resolve,reject)=>app.assets.loadFromUrl(`lingyuan-lod${n}.glb`,'container',(e,a)=>{if(e)reject(e);else{loaded[n]=a;resolve(a)}}))}
let savedMaterials=[];const grayMat=new pc.StandardMaterial();grayMat.diffuse=new pc.Color(.52,.54,.56);grayMat.roughness=.65;grayMat.update();
function applyGray(){for(const {mesh,material} of savedMaterials)mesh.material=gray?grayMat:material}
async function showModel(n,animation='pose'){
 $('loading').hidden=false;$('loading').textContent='正在加载模型层级…';const asset=await loadModel(n);if(character)character.destroy();character=asset.resource.instantiateRenderEntity();app.root.addChild(character);savedMaterials=[];
 for(const c of character.findComponents('render'))for(const mesh of c.meshInstances)savedMaterials.push({mesh,material:mesh.material});applyGray();
 let clips=asset.resource.animations;state.clips=clips.map(a=>a.resource?.name||a.name);
 if(animation!=='pose'){
  character.addComponent('anim',{activate:true});
  for(const clip of clips){let name=clip.resource?.name||clip.name;character.anim.assignAnimation(name,clip.resource,undefined,1,true)}
  let found=clips.find(a=>(a.resource?.name||a.name)===animation);if(found)character.anim.baseLayer.transition(animation,0);else animation='pose';
 }
 window.__lingBone=()=>{let b=character.findByName('thigh.R');if(!b)return null;let q=b.getLocalRotation();return [q.x,q.y,q.z,q.w]};state.animation=animation;state.lod=n;state.triangles=counts[n];$('triangles').textContent=Math.round(counts[n]).toLocaleString('zh-CN');$('loading').hidden=true;
}
function view(name){const presets={front:[0,.03,3.9,[0,1.05,0]],side:[Math.PI/2,.03,3.9,[0,1.05,0]],back:[Math.PI,.03,3.9,[0,1.05,0]],full:[0,.03,3.9,[0,1.05,0]],face:[0,.02,.70,[0,1.76,0]],armor:[-.30,.12,1.25,[0,1.47,0]],waist:[0,.04,1.4,[0,1.05,0]],weapon:[.2,.02,3,[.4,1.05,0]]};let p=presets[name];[yaw,pitch,radius]=p;target.set(...p[3]);updateCamera();document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name))}
async function main(){
 device=await pc.createGraphicsDevice(canvas,{deviceTypes:new URLSearchParams(location.search).get('renderer')==='webgl2'?[pc.DEVICETYPE_WEBGL2]:[pc.DEVICETYPE_WEBGPU,pc.DEVICETYPE_WEBGL2],antialias:true,glslangUrl:'/engine/glslang.js',twgslUrl:'/engine/twgsl.js'});state.renderer=device.deviceType;$('renderer').textContent=device.deviceType==='webgpu'?'WebGPU':'WebGL 2 · 兼容模式';
 app=new pc.Application(canvas,{graphicsDevice:device});app.setCanvasFillMode(pc.FILLMODE_NONE);app.setCanvasResolution(pc.RESOLUTION_AUTO);device.maxPixelRatio=Math.min(devicePixelRatio,1.5);resize();app.scene.ambientLight=new pc.Color(.55,.58,.61);
 camera=new pc.Entity('Inspection camera');camera.addComponent('camera',{clearColor:new pc.Color(.16,.21,.26),fov:40,nearClip:.02,farClip:100});camera.camera.toneMapping=pc.TONEMAP_ACES;app.root.addChild(camera);updateCamera();
 key=new pc.Entity('Key');key.addComponent('light',{type:'directional',color:new pc.Color(1,.91,.78),intensity:1.5,castShadows:false});key.setEulerAngles(-35,35,0);app.root.addChild(key);
 fill=new pc.Entity('Fill');fill.addComponent('light',{type:'directional',color:new pc.Color(.63,.78,1),intensity:.75,castShadows:false});fill.setEulerAngles(25,-145,0);app.root.addChild(fill);
 const floorMat=new pc.StandardMaterial();floorMat.diffuse=new pc.Color(.20,.25,.30);floorMat.metalness=.25;floorMat.roughness=.6;floorMat.useMetalness=true;floorMat.update();const floor=new pc.Entity('Neutral platform');floor.addComponent('render',{type:'cylinder',material:floorMat});floor.setLocalScale(1.7,.035,1.7);floor.setPosition(0,-.035,0);app.root.addChild(floor);
 let info=device.gpuAdapter?.info;let sw=!!(info?.isFallbackAdapter||/swiftshader|llvmpipe|lavapipe/i.test([info?.vendor,info?.architecture,info?.device,info?.description].join(' ')));if(device.deviceType==='webgl2'){let gl=device.gl,e=gl.getExtension('WEBGL_debug_renderer_info');sw=!!(e&&/swiftshader|llvmpipe|software/i.test(gl.getParameter(e.UNMASKED_RENDERER_WEBGL)))}state.software=sw;
 if(sw&&device.wgpu){app.autoRender=false;app.renderNextFrame=true;app.on('postrender',()=>queueMicrotask(async()=>{await device.wgpu.queue.onSubmittedWorkDone();setTimeout(()=>{app.renderNextFrame=true},100)}))}
 app.start();await fetchStats();await showModel(0);state.ready=true;
 let then=performance.now(),frames=0;app.on('postrender',()=>{frames++;state.frames++;let now=performance.now();if(now-then>1000){$('fps').textContent=Math.round(frames*1000/(now-then));const dc=app.stats.drawCalls.total; $('draws').textContent=dc>0?dc:'—';state.drawCalls=dc>0?dc:null;then=now;frames=0}});
 window.addEventListener('resize',resize);
}
canvas.addEventListener('pointerdown',e=>{if(e.pointerType==='touch')return;dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!dragging)return;yaw-=(e.clientX-lastX)*.008;pitch=Math.max(-.8,Math.min(.8,pitch+(e.clientY-lastY)*.008));lastX=e.clientX;lastY=e.clientY;updateCamera()});canvas.addEventListener('pointerup',()=>dragging=false);canvas.addEventListener('pointercancel',()=>dragging=false);canvas.addEventListener('wheel',e=>{e.preventDefault();radius=Math.max(.45,Math.min(6,radius*Math.exp(e.deltaY*.001)));updateCamera()},{passive:false});
canvas.addEventListener('touchstart',e=>{e.preventDefault();if(e.touches.length===1){lastX=e.touches[0].clientX;lastY=e.touches[0].clientY}if(e.touches.length===2)prevPinch=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY)},{passive:false});canvas.addEventListener('touchmove',e=>{e.preventDefault();if(e.touches.length===1){let t=e.touches[0];yaw-=(t.clientX-lastX)*.008;pitch=Math.max(-.8,Math.min(.8,pitch+(t.clientY-lastY)*.008));lastX=t.clientX;lastY=t.clientY}else if(e.touches.length===2){let d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);if(prevPinch)radius=Math.max(.45,Math.min(6,radius*prevPinch/d));prevPinch=d}updateCamera()},{passive:false});canvas.addEventListener('touchend',()=>prevPinch=0);
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>view(b.dataset.view)));$('motion').addEventListener('change',()=>showModel(+$('lod').value,$('motion').value).catch(fail));$('lod').addEventListener('change',()=>showModel(+$('lod').value,$('motion').value).catch(fail));$('gray').addEventListener('click',()=>{gray=!gray;applyGray();$('gray').textContent=gray?'恢复原材质':'切换灰模检查'});$('light').addEventListener('change',()=>{key.light.color=$('light').value==='cool'?new pc.Color(.65,.8,1):new pc.Color(1,.91,.78);fill.light.intensity=$('light').value==='cool'?1.0:.75});
function fail(e){state.errors.push(String(e));$('loading').hidden=false;$('loading').textContent='模型或图形初始化失败：'+String(e.message||e)}
main().catch(fail);
