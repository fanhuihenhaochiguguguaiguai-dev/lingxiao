"""Offline mix and source differentiation, not a subjective or physical latency test."""
from pathlib import Path
import json,base64,subprocess
import numpy as np
from scipy.io import wavfile
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/moonfall';preview=out/'audio-preview';preview.mkdir(exist_ok=True)
manifest=json.loads((R/'dist/skill/audio/lunar/manifest.json').read_text());assert len(manifest['files'])==66 and len({f['sha256'] for f in manifest['files']})==66
centroids={}
for style in [1,2,3]:
 sr,data=wavfile.read(R/f'audio-production/lunar/lunar{style}-cast-0.wav');mono=data.mean(axis=1);spectrum=np.abs(np.fft.rfft(mono));centroids[style]=float(np.sum(spectrum*np.fft.rfftfreq(len(mono),1/sr))/np.sum(spectrum))
assert centroids[1]>centroids[2]*1.2,centroids
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page();page.goto('http://127.0.0.1:8765/skill/audio/lunar/manifest.json');results={}
 for style,count in [(1,1),(2,1),(3,1),(3,10)]:
  result=page.evaluate('''async ([style,count])=>{
   const sr=48000,ctx=new OfflineAudioContext(2,sr*15,sr),bus=ctx.createGain(),master=ctx.createGain(),comp=ctx.createDynamicsCompressor(),limiter=ctx.createWaveShaper();bus.gain.value=.8/Math.sqrt(count);master.gain.value=.65;comp.threshold.value=-8;comp.knee.value=6;comp.ratio.value=8;const curve=new Float32Array(4096);for(let i=0;i<curve.length;i++){const x=i/(curve.length-1)*2-1;curve[i]=.96*Math.tanh(x*1.2)/Math.tanh(1.2)}limiter.curve=curve;limiter.oversample='2x';bus.connect(master);master.connect(comp);comp.connect(limiter);limiter.connect(ctx.destination);
   const stages=style===3?[[0,'cast'],[.45,'moon'],[.9,'dragon'],[2.75,'crystal'],[3.8,'burst'],[4.4,'field'],[7.7,'field'],[9.5,'dissolve'],[3.8,'hit'],[4.8,'hit'],[5.8,'hit'],[6.8,'hit'],[7.8,'hit'],[8.8,'hit']]:style===1?[[0,'cast'],[.32,'moon'],[.66,'crystal'],[2.12,'burst'],[2.6,'field'],[3.6,'dissolve'],[2,'hit']]:[[0,'cast'],[.42,'moon'],[.95,'crystal'],[1.45,'burst'],[1.9,'field'],[5.1,'field'],[7,'dissolve'],[1.7,'hit'],[2.7,'hit'],[3.7,'hit'],[4.7,'hit'],[5.7,'hit'],[6.7,'hit']];const buffers=new Map();
   for(let id=0;id<count;id++)for(const [at,phase] of stages){const file=`lunar${style}-${phase}-${id%3}`;if(!buffers.has(file)){const r=await fetch(file+'.ogg');buffers.set(file,await ctx.decodeAudioData(await r.arrayBuffer()))}const source=ctx.createBufferSource(),gain=ctx.createGain(),pan=ctx.createStereoPanner();source.buffer=buffers.get(file);const seed=Math.sin((id+1)*91.17+phase.length*3.71)*.5+.5;source.playbackRate.value=2**((seed-.5)*.055);gain.gain.value=(phase==='field'?.32:phase==='hit'?.48:phase==='burst'?.62:.5)*(.94+seed*.12);pan.pan.value=(id%5-2)*.1;source.connect(gain);gain.connect(pan);pan.connect(bus);source.start(at+id*.015)}
   const audio=await ctx.startRendering(),left=audio.getChannelData(0),right=audio.getChannelData(1);let peak=0,clipped=0,sum=0;const pcm=new Int16Array(left.length*2);for(let i=0;i<left.length;i++)for(let ch=0;ch<2;ch++){const v=ch?right[i]:left[i];peak=Math.max(peak,Math.abs(v));if(Math.abs(v)>1)clipped++;sum+=v*v;pcm[i*2+ch]=Math.round(Math.max(-1,Math.min(1,v))*32767)}const bytes=new Uint8Array(pcm.buffer);let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));return {peak,clippedSamples:clipped,rms:Math.sqrt(sum/(left.length*2)),pcm:btoa(binary),scheduledSources:count*stages.length};
  }''',[style,count]);pcm=np.frombuffer(base64.b64decode(result.pop('pcm')),dtype='<i2').reshape(-1,2);key=f'lunar{style}-{count}casts';tmp=Path('/tmp')/(key+'.wav');wavfile.write(tmp,48000,pcm);dest=preview/(key+'.ogg');subprocess.run(['ffmpeg','-v','error','-y','-i',str(tmp),'-c:a','libvorbis','-q:a','5',str(dest)],check=True);tmp.unlink();assert result['peak']>0 and result['clippedSamples']==0,result;results[key]=result
 b.close()
(out/'audio.json').write_text(json.dumps({'scope':'48 kHz OfflineAudioContext with production gain/compressor/limiter; no subjective listening or physical device latency acceptance','sourceVariants':66,'castSpectralCentroidsHz':centroids,'mixes':results},indent=2));print('PASS_AUDIO',json.dumps(results),flush=True)
