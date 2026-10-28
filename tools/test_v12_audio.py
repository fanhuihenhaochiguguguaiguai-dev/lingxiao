from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];src=(root/'skill-src/src/skill-audio.ts').read_text();spec=src.split('const tracks:Record<number,Cue[]>=',1)[1].split(';',1)[0]
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page();page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 results=page.evaluate('''async spec=>{
 const tracks=Function('return ('+spec+')')(),results={};
 for(const [id,cues] of Object.entries(tracks)){
  const ctx=new OfflineAudioContext(2,48000*9,48000),master=ctx.createGain(),comp=ctx.createDynamicsCompressor();master.gain.value=.65;comp.threshold.value=-8;comp.knee.value=6;comp.ratio.value=8;master.connect(comp);comp.connect(ctx.destination);
  for(const cue of cues){const response=await fetch('audio/'+cue.file+'.ogg');if(!response.ok)throw Error('missing '+cue.file);const buffer=await ctx.decodeAudioData(await response.arrayBuffer()),source=ctx.createBufferSource(),gain=ctx.createGain(),pan=ctx.createStereoPanner();source.buffer=buffer;gain.gain.value=cue.gain;pan.pan.value=cue.pan;source.connect(gain);gain.connect(pan);pan.connect(master);source.start(cue.t)}
  const rendered=await ctx.startRendering();let peak=0,clipped=0;for(let channel=0;channel<2;channel++){const s=rendered.getChannelData(channel);for(let i=0;i<s.length;i++){const v=Math.abs(s[i]);peak=Math.max(peak,v);if(v>1)clipped++}}results[id]={peak,clippedSamples:clipped};
 }return results;
}''',spec)
 assert all(v['peak']>0 and v['clippedSamples']==0 for v in results.values()),results
 (root/'verification/v12/audio-mix.json').write_text(json.dumps({'status':'PASS_OFFLINE_MIX_ONLY','skills':results,'scope':'OfflineAudioContext at fixed 48kHz; not live device latency or subjective listening.'},indent=2));print(json.dumps(results),flush=True);b.close()
