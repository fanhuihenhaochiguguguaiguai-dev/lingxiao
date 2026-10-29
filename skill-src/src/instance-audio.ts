import * as THREE from 'three/webgpu';
import { SkillAudio, tracks } from './skill-audio';
import { skillRegistry } from './skill-registry';
export type CastKind='lingyuan-1'|'lingyuan-2'|'lingyuan-3'|'yueli-1'|'yueli-2'|'yueli-3';
export type LunarPhase='cast'|'moon'|'crystal'|'burst'|'field'|'hit'|'dissolve'|'dragon';
export interface AudioEvent {instanceId:number;kind:CastKind;phase:string;variant:number;pitch:number;gain:number;simulationTime:number;requestedAudioTime:number;startedAudioTime:number|null;file:string;status:'pending'|'playing'|'failed'}
const phases:LunarPhase[]=['cast','moon','crystal','burst','field','hit','dissolve'];
export class InstanceAudio {
 readonly events:AudioEvent[]=[];readonly buffers=new Map<string,AudioBuffer>();ready=false;error='';
 private readonly pending:{event:AudioEvent;position:THREE.Vector3}[]=[];
 private readonly sources=new Map<AudioBufferSourceNode,{id:number;gain:GainNode;pan:PannerNode;pitch:number}>();
 private readonly failed=new Map<string,string>();private retry:Promise<void>|null=null;
 private bus:GainNode|null=null;private timeScale=1;private paused=false;
 setPaused(paused:boolean){
  if(this.paused===paused)return;this.paused=paused;const ctx=this.owner.context;if(!ctx)return;
  if(paused)void ctx.suspend().catch(e=>{this.error=String(e)});
  else void this.owner.unlock().then(()=>{if(this.paused)void ctx.suspend();else this.flush()});
 }
 setTimeScale(value:number){if(value===this.timeScale)return;this.timeScale=value;const ctx=this.owner.context;if(ctx)for(const [source,entry] of this.sources)source.playbackRate.setTargetAtTime(value*entry.pitch,ctx.currentTime,.025)}
 constructor(readonly owner:SkillAudio){void this.preload()}
 private async preload(){
  try{const ctx=this.owner.context;if(!ctx)throw Error('AudioContext unavailable');
   // Decode a bounded batch to keep startup memory and CPU predictable.
   const names:string[]=[];for(const style of [1,2,3])for(const phase of style===3?[...phases,'dragon']:phases)for(let v=0;v<3;v++)names.push(`lunar${style}-${phase}-${v}`);
   for(let at=0;at<names.length;at+=4)await Promise.all(names.slice(at,at+4).map(name=>this.loadBuffer(name,ctx)));
   this.finishLoad();
  }catch(e){this.error=String(e);for(const p of this.pending)p.event.status='failed';this.pending.length=0}
 }
 private async loadBuffer(name:string,ctx:AudioContext){try{const r=await fetch(`audio/lunar/${name}.ogg`);if(!r.ok)throw Error(`HTTP ${r.status}`);this.buffers.set(name,await ctx.decodeAudioData(await r.arrayBuffer()));this.failed.delete(name)}catch(e){this.failed.set(name,String(e))}}
 private finishLoad(){this.ready=this.failed.size===0;this.error=[...this.failed].map(([n,e])=>`${n}: ${e}`).join('; ');this.flush()}
 retryFailed(){if(this.retry)return this.retry;const ctx=this.owner.context;if(!ctx)return Promise.resolve();this.retry=Promise.all([...this.failed.keys()].map(name=>this.loadBuffer(name,ctx))).then(()=>this.finishLoad()).finally(()=>{this.retry=null});return this.retry}
 private ensureBus(){const ctx=this.owner.context;if(!ctx||!this.owner.master)return null;if(!this.bus){this.bus=ctx.createGain();this.bus.gain.value=.8;this.bus.connect(this.owner.master)}return this.bus}
 fire(id:number,kind:CastKind,phase:string,variant:number,age:number,position:THREE.Vector3){
  const style=skillRegistry[kind].audioStyle,lunar=style!==0;let file:string,gain=.55;
  if(lunar){const base=phase.split(':')[0];file=`lunar${style}-${base}-${variant}`;gain=base==='field'?.32:base==='hit'?.48:base==='burst'?.62:.50}
  else{const skill=skillRegistry[kind].slot,index=Number(phase.split(':')[1]);const cue=phase.startsWith('hit:')?skillRegistry[kind].hitAudio:tracks[skill][index];if(!cue)return;file=cue.file;gain=cue.gain*.75}
  const seed=Math.sin(id*91.17+phase.length*3.71)*.5+.5,pitch=2**((seed-.5)*.055);gain*=.94+seed*.12;
  const event:AudioEvent={instanceId:id,kind,phase,variant,pitch,gain,simulationTime:age,requestedAudioTime:this.owner.context?.currentTime||0,startedAudioTime:null,file,status:'pending'};
  this.events.push(event);if(this.events.length>2048)this.events.shift();this.pending.push({event,position:position.clone()});if(!this.paused)void this.owner.unlock().then(()=>{if(this.paused)void this.owner.context?.suspend();else this.flush()});this.flush();
 }
 private flush(){
  const ctx=this.owner.context,bus=this.ensureBus();if(this.paused||!ctx||!bus||ctx.state!=='running')return;
  for(let i=this.pending.length-1;i>=0;i--){const item=this.pending[i],e=item.event,buffer=this.buffers.get(e.file)||this.owner.buffers.get(e.file);if(!buffer){if(this.failed.has(e.file)||(!e.kind.startsWith('yueli')&&this.owner.error)){e.status='failed';this.pending.splice(i,1)}continue}this.pending.splice(i,1);
   const src=ctx.createBufferSource(),gain=ctx.createGain(),pan=ctx.createPanner();src.buffer=buffer;src.playbackRate.value=e.pitch*this.timeScale;gain.gain.value=e.gain;pan.panningModel='equalpower';pan.distanceModel='inverse';pan.refDistance=5;pan.maxDistance=60;pan.rolloffFactor=.6;pan.positionX.value=item.position.x;pan.positionY.value=item.position.y;pan.positionZ.value=item.position.z;src.connect(gain);gain.connect(pan);pan.connect(bus);this.sources.set(src,{id:e.instanceId,gain,pan,pitch:e.pitch});
   e.startedAudioTime=ctx.currentTime;e.status='playing';src.onended=()=>{const entry=this.sources.get(src);src.disconnect();entry?.gain.disconnect();entry?.pan.disconnect();this.sources.delete(src);this.normalize()};this.normalize();src.start(ctx.currentTime);
  }
 }
 private normalize(){const ctx=this.owner.context;if(!ctx||!this.bus)return;const groups=new Set([...this.sources.values()].map(s=>s.id)).size;this.bus.gain.setTargetAtTime(.8/Math.sqrt(Math.max(1,groups)),ctx.currentTime,.025)}
 update(camera:THREE.PerspectiveCamera){
  this.flush();const ctx=this.owner.context;if(!ctx)return;const p=camera.getWorldPosition(new THREE.Vector3()),forward=new THREE.Vector3(0,0,-1).applyQuaternion(camera.quaternion),up=new THREE.Vector3(0,1,0).applyQuaternion(camera.quaternion),l=ctx.listener;
  for(const [param,value] of [[l.positionX,p.x],[l.positionY,p.y],[l.positionZ,p.z],[l.forwardX,forward.x],[l.forwardY,forward.y],[l.forwardZ,forward.z],[l.upX,up.x],[l.upY,up.y],[l.upZ,up.z]] as [AudioParam,number][])param.value=value;
 }
 snapshot(){return {paused:this.paused,ready:this.ready,loaded:this.buffers.size,failedFiles:[...this.failed.keys()],voices:this.sources.size,pending:this.pending.length,error:this.error,events:this.events}}
 stopAll(){for(const [s,entry] of this.sources){s.onended=null;try{s.stop()}catch{}s.disconnect();entry.gain.disconnect();entry.pan.disconnect()}this.sources.clear();for(const p of this.pending)p.event.status='failed';this.pending.length=0;this.normalize()}
}
