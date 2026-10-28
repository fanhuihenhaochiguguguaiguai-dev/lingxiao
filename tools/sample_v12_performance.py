from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/v12'
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);samples={}
 for label,button,t in [('skill1','cast',2.45),('skill2','cast2',3.8),('ultimate','cast3',3.1)]:
  page.locator('#'+button).click();page.locator('#panel-toggle').click();page.locator('#pause').click();page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(3000);s=page.evaluate('window.__lingSkill');assert s['dragonVisible'] and not s['errors'];samples[label]={'time':t,'fps':s['fps'],'drawCalls':s['drawCalls'],'triangles':s['triangles'],'renderer':s['renderer'],'software':s['software']};page.locator('#panel-toggle').click()
 (out/'performance.json').write_text(json.dumps({'scope':'single-time desktop software sample, no prior comparable baseline and not phone performance','samples':samples},indent=2));print(json.dumps(samples),flush=True);b.close()
