from pathlib import Path
import json,os
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(os.environ.get('LING_TEST_OUT',Path(__file__).resolve().parents[1]/'verification/quality-modes'));out.mkdir(exist_ok=True);data={'modes':{},'errors':[]}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720});page.on('pageerror',lambda e:data['errors'].append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);page.locator('#cast2').click();page.locator('#pause').click();page.locator('#seek').evaluate('(e)=>{e.value="3.8";e.dispatchEvent(new Event("input",{bubbles:true}))}')
 for q in ['high','ultra']:
  old=page.evaluate('window.__lingSkill.frames');page.locator('[data-quality='+q+']').click();page.wait_for_function('(n)=>window.__lingSkill.frames>n',arg=old,timeout=30000);page.wait_for_timeout(500);s=page.evaluate('window.__lingSkill');assert s['quality']==q and s['dragonVisible'] and not s['errors'];data['modes'][q]={'triangles':s['triangles'],'drawCalls':s['drawCalls'],'fps':s['fps']}
 assert data['modes']['high']['triangles']<data['modes']['ultra']['triangles'],data
 assert not data['errors'];data['status']='PASS_SOFTWARE_ONLY';(out/'modes.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));print(json.dumps(data,ensure_ascii=False),flush=True);b.close()
