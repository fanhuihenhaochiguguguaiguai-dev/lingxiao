type Cue={t:number;file:string;gain:number;pan:number};
const tracks:Record<number,Cue[]>={
 1:[{t:.08,file:'blade_01',gain:.65,pan:-.2},{t:.92,file:'blade_03',gain:.85,pan:.1},{t:1.04,file:'spell_01',gain:.48,pan:.3},{t:1.83,file:'stones_03',gain:.55,pan:0},{t:2.22,file:'blade_03',gain:.72,pan:.2}],
 2:[{t:.06,file:'spell_02',gain:.75,pan:0},{t:.45,file:'magical_2',gain:.65,pan:-.2},{t:2.15,file:'chain_02',gain:.75,pan:.25},{t:2.45,file:'spell_01',gain:.55,pan:-.15},{t:4.5,file:'magical_2',gain:.42,pan:.1}],
 3:[{t:.05,file:'spell_fire_03',gain:.48,pan:0},{t:.72,file:'magical_2',gain:.55,pan:-.15},{t:1.55,file:'creature_roar_02',gain:.65,pan:.1},{t:3.2,file:'spell_02',gain:.50,pan:.2},{t:4.92,file:'stones_03',gain:.80,pan:0},{t:4.95,file:'spell_fire_03',gain:.65,pan:.1},{t:5.6,file:'magical_2',gain:.35,pan:-.2}]
};
/** CC0 source recordings; scheduling follows the same clock as the skill animation. */
export class SkillAudio{
 context:AudioContext|null=null;master:GainNode|null=null;compressor:DynamicsCompressorNode|null=null;buffers=new Map<string,AudioBuffer>();data=new Map<string,ArrayBuffer>();voices=new Set<AudioBufferSourceNode>();skill=1;cursor=0;last=-1;volume=.65;muted=false;analyser:AnalyserNode|null=null;error='';events:{skill:number;cue:number;at:number;audioNow:number;scheduledAudioTime:number;lateBy:number}[]=[];
 constructor(){this.ensureContext()}
 ensureContext(){try{if(!this.context){this.context=new AudioContext();this.master=this.context.createGain();this.compressor=this.context.createDynamicsCompressor();this.analyser=this.context.createAnalyser();this.analyser.fftSize=1024;this.compressor.threshold.value=-8;this.compressor.knee.value=6;this.compressor.ratio.value=8;this.master.connect(this.compressor);this.compressor.connect(this.analyser);this.analyser.connect(this.context.destination);this.applyVolume()}}catch(e){this.error=String(e)}}
 async preload(){await Promise.all([...new Set(Object.values(tracks).flat().map(c=>c.file))].map(async name=>{try{const r=await fetch(`audio/${name}.ogg`);if(!r.ok)throw Error(`HTTP ${r.status}`);this.data.set(name,await r.arrayBuffer())}catch(e){this.error=`音频加载失败: ${name} ${String(e)}`}}));if(this.context)await this.decode()}
 async decode(){if(!this.context)return;for(const [name,data] of this.data){if(!this.buffers.has(name))try{this.buffers.set(name,await this.context.decodeAudioData(data.slice(0)))}catch(e){this.error=`音频解码失败: ${name} ${String(e)}`}}}
 unlock():Promise<void>{this.ensureContext();if(!this.context)return Promise.resolve();if(this.buffers.size===0&&this.data.size>0)void this.decode();return this.context.resume().catch(e=>{this.error=String(e)})}
 sample(){if(!this.analyser)return 0;const samples=new Float32Array(this.analyser.fftSize);this.analyser.getFloatTimeDomainData(samples);let peak=0;for(const x of samples)peak=Math.max(peak,Math.abs(x));return peak}
 applyVolume(){if(this.master)this.master.gain.value=this.muted?0:this.volume}
 stop(){for(const v of this.voices)try{v.stop()}catch{}this.voices.clear()}
 start(skill:number,t:number){this.stop();this.skill=skill;this.cursor=0;while(this.cursor<tracks[skill].length&&tracks[skill][this.cursor].t<t-.03)this.cursor++;this.last=t-.001}
 tick(t:number,playing:boolean,slow:boolean){
  if(!this.context||!this.master||!playing||this.context.state!=='running')return;
  if(t<this.last-.05)this.start(this.skill,t);this.last=t;const speed=slow?.25:1,items=tracks[this.skill];
  while(this.cursor<items.length){const cue=items[this.cursor];if(!this.buffers.has(cue.file)){if(cue.t<t-.3){this.cursor++;continue}break}this.cursor++;if(cue.t<t-.35)continue;const src=this.context.createBufferSource(),g=this.context.createGain(),pan=this.context.createStereoPanner();src.buffer=this.buffers.get(cue.file)!;src.playbackRate.value=speed;g.gain.value=cue.gain;pan.pan.value=cue.pan;src.connect(g);g.connect(pan);pan.connect(this.master);this.voices.add(src);src.onended=()=>this.voices.delete(src);const audioNow=this.context.currentTime,scheduledAudioTime=audioNow+Math.max(0,(cue.t-t)/speed);src.start(scheduledAudioTime);this.events.push({skill:this.skill,cue:cue.t,at:t,audioNow,scheduledAudioTime,lateBy:Math.max(0,t-cue.t)});if(this.events.length>30)this.events.shift()}
 }
}
