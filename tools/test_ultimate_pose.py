from pathlib import Path
import json,sys
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
stage=sys.argv[1];assert stage in ('before','after');out=Path(__file__).resolve().parents[1]/'verification/ultimate-pose';out.mkdir(exist_ok=True);r={'stage':stage,'samples':[],'errors':[]}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720});page.on('pageerror',lambda e:r['errors'].append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);page.locator('#cast3').click();page.locator('#pause').click()
 for t in [.2,1.2,2.2,3.1,5.4,6.8,7.3]:
  page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(700);s=page.evaluate('window.__lingSkill');r['samples'].append({'time':t,'height':s['actorY'],'arm':s['boneSample'],'dragon':s['dragonVisible'],'errors':s['errors']});assert not s['errors']
  if t==3.1:page.screenshot(path=str(out/(stage+'-airborne.png')))
 assert not r['errors'];
 if stage=='after':assert max(x['height'] for x in r['samples'])>.4 and r['samples'][-1]['height']<.02,r
 r['status']='PASS';(out/(stage+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False),flush=True);b.close()
