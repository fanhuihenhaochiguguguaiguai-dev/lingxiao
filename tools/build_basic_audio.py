"""Short basic-attack mixes derived from this project's CC0/original recordings."""
from pathlib import Path
import json,subprocess,numpy as np,scipy.signal as sig,scipy.io.wavfile as wav
R=Path(__file__).resolve().parents[1];out=R/'dist/skill/audio/basic';out.mkdir(parents=True,exist_ok=True);masters=R/'audio-production/basic';masters.mkdir(parents=True,exist_ok=True);SR=48000;rows=[]
def load(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar',str(SR),'-ac','2','-']),dtype='<f4').reshape(-1,2)
for style in ['spear','lunar']:
 for phase in ['release','hit']:
  for variant in range(3):
   if style=='spear':sources=[R/'dist/skill/audio'/('blade_01.ogg' if phase=='release' else 'blade_03.ogg'),R/'dist/skill/audio/stones_03.ogg'];duration=.32 if phase=='release' else .44;gains=[.85,.10 if phase=='release' else .22]
   else:sources=[R/f'dist/skill/audio/lunar/lunar1-{("crystal" if phase=="release" else "hit")}-{variant}.ogg',R/'dist/skill/audio/blade_01.ogg'];duration=.42 if phase=='release' else .50;gains=[.78,.15]
   n=int(duration*SR);audio=np.zeros((n,2))
   for source,gain in zip(sources,gains):
    s=load(source);s=sig.resample_poly(s,100,98+variant*2,axis=0);count=min(n,len(s));audio[:count]+=s[:count]*gain
   audio-=audio.mean(axis=0);fade=int(.008*SR);audio[:fade]*=np.linspace(0,1,fade)[:,None];tail=int(.09*SR);audio[-tail:]*=np.linspace(1,0,tail)[:,None];audio*=min(1,.60/max(np.max(np.abs(audio)),1e-9));audio=audio.astype(np.float32)
   stem=f'basic-{style}-{phase}-{variant}';tmp=Path('/tmp')/(stem+'.wav');wav.write(tmp,SR,audio)
   if variant==0:(masters/(stem+'.wav')).write_bytes(tmp.read_bytes())
   subprocess.run(['ffmpeg','-v','error','-y','-i',str(tmp),'-c:a','libvorbis','-q:a','4',str(out/(stem+'.ogg'))],check=True);tmp.unlink();rms=float(np.sqrt(np.mean(audio**2)));assert rms>.005
   rows.append({'file':stem+'.ogg','seconds':duration,'peak':float(np.max(np.abs(audio))),'rms':rms,'sources':[str(s.relative_to(R)) for s in sources]})
(out/'manifest.json').write_text(json.dumps({'scope':'basic attacks; original lunar design and existing CC0 recordings, not commercial game audio','variants':3,'sampleRate':SR,'files':rows},ensure_ascii=False,indent=2));print('BASIC_AUDIO_READY',len(rows))
