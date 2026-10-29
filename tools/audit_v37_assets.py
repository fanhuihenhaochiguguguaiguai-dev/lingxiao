from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];baseline='499215e';checks=[]
paths=subprocess.check_output(['git','ls-files','dist'],cwd=R,text=True).splitlines()
for name in paths:
 p=R/name
 if p.suffix.lower() not in ['.glb','.blend','.ogg','.wav','.webp','.png','.jpg','.jpeg']:continue
 data=p.read_bytes();old=subprocess.check_output(['git','show',baseline+':'+name],cwd=R);assert old==data,name;checks.append({'path':name,'sha256':hashlib.sha256(data).hexdigest(),'unchanged':True})
effects=['dragon.ts','slash-dragon.ts','bind-star.ts','star-vortex.ts','moon-frost.ts','moon-tide.ts','moonfall.ts','ice-dragon.ts']
for name in effects:
 file='skill-src/src/'+name;old=subprocess.check_output(['git','show',baseline+':'+file],cwd=R,text=True);now=(R/file).read_text();stripped='\n'.join(line for line in now.splitlines() if not line.lstrip().startswith(('combatBody(){','combatGeometry(){')))+'\n';assert stripped==old,file
(R/'verification/v37/assets.json').write_text(json.dumps({'baseline':baseline,'assets':checks,'effectsOnlyReadOnlyCombatGetters':effects,'meaning':'original visual geometry/shaders/textures/audio retained; procedural basic/foot/action changes are separately tested'},indent=2));print('PASS_V37_ASSET_PRESERVATION',len(checks),'assets and',len(effects),'visual implementations')
