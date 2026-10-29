"""Preservation, playable basic audio and bounded static resource inventory."""
from pathlib import Path
import hashlib,json,subprocess,numpy as np
R=Path(__file__).resolve().parents[1];out=R/'verification/combat';rows=[]
paths=['dist/lingyuan-lod0.glb','dist/lingyuan-lod1.glb','dist/lingyuan-lod2.glb','dist/yueli-study.glb','dist/quality/lingyuan31-head.glb','dist/Lingyuan_working.blend','skill-src/src/dragon.ts','skill-src/src/slash-dragon.ts','skill-src/src/bind-star.ts','skill-src/src/star-vortex.ts','skill-src/src/moon-frost.ts','skill-src/src/moon-tide.ts','skill-src/src/moonfall.ts','skill-src/src/ice-dragon.ts','skill-src/src/crystal-geometry.ts']
for path in paths:
 data=(R/path).read_bytes();before=subprocess.check_output(['git','show','5324e33:'+path],cwd=R);assert data==before,path;rows.append({'file':path,'unchanged':True,'sha256':hashlib.sha256(data).hexdigest()})
audio=[]
for path in sorted((R/'dist/skill/audio/basic').glob('*.ogg')):
 data=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4');peak=float(np.max(np.abs(data)));rms=float(np.sqrt(np.mean(data**2)));assert peak<.98 and rms>.005;audio.append({'file':path.name,'peak':peak,'rms':rms,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert len(audio)==12 and len({a['sha256'] for a in audio})==12
(out/'resources.json').write_text(json.dumps({'baseline':'5324e33','preserved':rows,'basicAudio':audio,'basicAudioBytes':sum(r['bytes'] for r in audio),'scope':'resource identities and decoded levels; not professional listening or actual phone performance'},indent=2));print('PASS_COMBAT_RESOURCES',len(rows),'preserved assets;',sum(a['bytes'] for a in audio),'audio bytes')
