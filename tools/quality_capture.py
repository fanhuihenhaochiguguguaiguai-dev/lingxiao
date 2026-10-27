from pathlib import Path
import json,sys,time
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
stage=sys.argv[1]; assert stage in ('before','after','experiment','ribbon')
out=Path(__file__).resolve().parents[1]/'verification/quality'; results={'stage':stage,'backend':'software WebGL2','cases':{},'errors':[]}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1);page.on('pageerror',lambda e:results['errors'].append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000);assert page.evaluate('window.__lingSkill.ready')
 def capture(name,button,t,view):
  page.locator('#'+button).click();page.locator('#pause').click();page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.locator('[data-view='+view+']').click();page.wait_for_timeout(2200);s=page.evaluate('window.__lingSkill');page.screenshot(path=str(out/f'{stage}-{name}.png'));results['cases'][name]={k:s[k] for k in ('time','skill','fps','drawCalls','renderer','software','errors')}
 capture('character','cast2',0,'front')
 for name,button,t in [('skill1','cast',2.45),('skill2','cast2',3.8),('skill3','cast3',3.0)]:capture(name,button,t,'front')
 assert not results['errors'];(out/f'{stage}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False),flush=True);b.close()
