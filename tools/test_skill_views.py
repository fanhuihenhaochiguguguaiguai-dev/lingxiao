from pathlib import Path
from PIL import Image
import hashlib,json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/skill-views';out.mkdir(exist_ok=True);result={'skills':{},'errors':[]}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720});page.on('pageerror',lambda e:result['errors'].append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 for label,button,t in [('skill1','cast',2.45),('skill2','cast2',3.8),('ultimate','cast3',3.1)]:
  page.locator('#'+button).click();page.locator('#pause').click();page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));hashes={}
  for view in ['front','side','right','back','angle','top','up']:
   page.locator('[data-view='+view+']').click();page.wait_for_timeout(1100);file=out/(label+'-'+view+'.png');page.screenshot(path=str(file));im=Image.open(file).crop((200,100,1000,600)).convert('RGB');hashes[view]=hashlib.sha256(im.tobytes()).hexdigest()
  s=page.evaluate('window.__lingSkill');assert s['dragonVisible'] and not s['errors'] and len(set(hashes.values()))==7;result['skills'][label]={'time':t,'views':hashes,'drawCalls':s['drawCalls']}
 assert not result['errors'];result['status']='PASS_SOFTWARE_VIEW_CAPTURE_ONLY';(out/'views.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS 21 real software-rendered view captures; no aesthetic acceptance',flush=True);b.close()
