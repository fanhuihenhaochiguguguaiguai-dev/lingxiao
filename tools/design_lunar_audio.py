"""Original procedural sound design: granular ice, dispersive resonators and layered wind.
No commercial/game recordings. Reproducible 48 kHz stereo float WAV masters + Ogg variants.
"""
from pathlib import Path
import sys
import numpy as np, scipy.signal as sig, scipy.io.wavfile as wav,subprocess,json,hashlib
R=Path(__file__).resolve().parents[1];out=R/'dist/skill/audio/lunar';masters=R/'audio-production/lunar';out.mkdir(parents=True,exist_ok=True);masters.mkdir(parents=True,exist_ok=True)
SR=48000;stages=['cast','moon','crystal','burst','field','hit','dissolve','dragon'];records=[]
def band(x,lo,hi):return sig.sosfilt(sig.butter(3,[lo,hi],btype='bandpass',fs=SR,output='sos'),x)
def voice(style,stage,variant):
 rng=np.random.default_rng(9071+style*200+stages.index(stage)*17+variant*991);duration={'cast':1.15,'moon':1.9,'crystal':1.35,'burst':2.2,'field':3.6,'hit':.95,'dissolve':2.4,'dragon':2.6}[stage];n=int(duration*SR);t=np.arange(n)/SR
 noise=rng.normal(0,1,n);bright=style==1;ratio=2**((variant-1)*.018)
 # Broad moving air and glittery grains anchor every layer in a noise spectrum.
 wind=band(noise,220 if bright else 55,8200 if bright else 3900);wind/=max(np.std(wind),1e-9)
 env=(1-np.exp(-t*(18 if stage in ['hit','burst'] else 7)))*np.exp(-t*(4 if stage=='hit' else 1.7 if bright else .8));s=wind*.045*env
 # Dispersive, non-harmonic glass modes, gently detuned; not a single oscillator beep.
 fundamentals=([760,1131,1767,2461,3583,4697] if bright else [81,123,193,313,507,821] if style==3 else [131,207,337,547,887,1433]);modes=np.zeros(n)
 for k,f in enumerate(fundamentals):
  f*=ratio*(1+rng.uniform(-.005,.005));decay=(1.7+k*.4) if stage!='field' else .42+k*.10
  attack=1-np.exp(-t*(60 if stage in ['hit','burst','crystal'] else 8));modes+=np.sin(2*np.pi*f*t+.012*np.sin(2*np.pi*(11+k)*t)+rng.uniform(0,6.28))*np.exp(-t*decay)*attack/(k+1)**.78
 s+=modes*(.065 if stage!='burst' else .10)
 # Crystal nucleation: irregular clusters of short filtered-noise fractures.
 for k in range(18 if stage in ['hit','crystal','burst'] else 7):
  at=rng.uniform(.015,duration*(.45 if stage=='burst' else .85));start=int(at*SR);length=min(n-start,int(SR*rng.uniform(.012,.085)));u=np.arange(length)/SR
  grain=band(rng.normal(size=length),1800 if bright else 900,12500 if bright else 8200);grain*=np.exp(-u*rng.uniform(50,140));s[start:start+length]+=grain*rng.uniform(.06,.15)
 if stage=='burst':
  sweep=np.sin(2*np.pi*(80*t-35*t*t))*np.exp(-t*9);s+=sweep*(.24 if not bright else .09);s+=band(noise,70,1000)*np.exp(-t*4)*.25
 if style==3:
  growl=(np.sin(2*np.pi*(47*t-4*t*t)+2.6*np.sin(2*np.pi*1.7*t))+.45*np.sin(2*np.pi*93*t))*band(noise,110,1700)
  s+=growl*(.34 if stage=='dragon' else .065)*(1-np.exp(-t*17))*np.exp(-t*.9)
  if stage=='dragon':s+=band(noise,380,3200)*.18*np.exp(-t*1.2)*(1-np.exp(-t*13))
 if stage=='field':s*=.6+.2*np.sin(t*2.4)+.12*np.sin(t*3.67);s+=band(noise,200,2000)*.06*np.sin(np.pi*t/duration)**2
 if stage=='dissolve':s=s[::-1]*.45+s*.55;s*=np.sin(np.pi*np.minimum(t/duration,1))**.65
 # Short, controlled stereo diffusion with different left/right reflection timing.
 stereo=np.stack([s,s],axis=1)
 for channel in range(2):
  for delay,gain in [(.043+channel*.007,.17),(.091+channel*.013,.12),(.173-channel*.011,.075),(.281+channel*.017,.045)]:
   d=int(delay*SR);stereo[d:,channel]+=s[:-d]*gain
 fade=min(int(.018*SR),n//3);stereo[:fade]*=np.linspace(0,1,fade)[:,None];tail=int(.14*SR);stereo[-tail:]*=np.linspace(1,0,tail)[:,None]
 peak=np.max(np.abs(stereo));stereo*=.55/max(peak,.55);return stereo.astype(np.float32)
selected=[3] if '--ultimate-only' in sys.argv else [1,2,3]
existing=json.loads((out/'manifest.json').read_text()) if (out/'manifest.json').exists() else {'files':[]}
records=[r for r in existing['files'] if not any(r['file'].startswith(f'lunar{s}-') for s in selected)]
for style in selected:
 for stage in (stages if style==3 else stages[:-1]):
  for variant in range(3):
   audio=voice(style,stage,variant);stem=f'lunar{style}-{stage}-{variant}';tmp=Path('/tmp')/(stem+'.wav');wav.write(tmp,SR,audio)
   if variant==0:(masters/(stem+'.wav')).write_bytes(tmp.read_bytes())
   dest=out/(stem+'.ogg');subprocess.run(['ffmpeg','-v','error','-y','-i',str(tmp),'-c:a','libvorbis','-q:a','5',str(dest)],check=True);tmp.unlink()
   records.append({'file':dest.name,'samples':len(audio),'peak':float(np.max(np.abs(audio))),'rms':float(np.sqrt(np.mean(audio**2))),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(out/'manifest.json').write_text(json.dumps({'sampleRate':SR,'variants':3,'styles':{'1':'月华霜羽: bright granular feather and glass transients','2':'月影寒潮: low resonant lunar field and cold surf','3':'月陨天霜: glacial subharmonic dragon, descending lunar mass and fracture'},'files':records},ensure_ascii=False,indent=2))
(masters/'README.md').write_text('原创程序化声音设计母版。48 kHz 双声道 float32 WAV；一、二技能各七类、三技能八类声音，每类三个确定性变体，Web Ogg 保存全部变体，母版保存变体 0。源码 tools/design_lunar_audio.py 包含可复现种子、噪声、非整数比共振、颗粒碎裂与立体反射设计，不使用游戏录音。自动电平检查不能代替专业试听或真机扬声器验收。\n')
print(json.dumps({'ogg':len(records),'masters':22,'maxPeak':max(r['peak'] for r in records),'minRms':min(r['rms'] for r in records)}),flush=True)
