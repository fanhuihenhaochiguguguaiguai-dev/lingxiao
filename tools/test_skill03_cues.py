import json
from pathlib import Path
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
with display() as env, sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 page.evaluate("window.__cues=[];window.addEventListener('lingyuan:skill-cue', e=>window.__cues.push(e.detail))")
 page.locator('#cast3').click();page.wait_for_function('window.__cues.some(e=>e.cue==="awaken")',timeout=30000);page.locator('#pause').click()
 page.locator('#seek').evaluate('(e)=>{e.value="4.90";e.dispatchEvent(new Event("input",{bubbles:true}))}');page.locator('#pause').click();page.wait_for_function('window.__cues.some(e=>e.cue==="burst")',timeout=30000);page.locator('#pause').click();cues=page.evaluate('window.__cues');assert all(c['skill']==3 for c in cues)
 (Path(__file__).resolve().parents[1]/'verification/skill03-cues.json').write_text(json.dumps({'status':'PASS','events':cues},ensure_ascii=False,indent=2));print(json.dumps(cues,ensure_ascii=False),flush=True);b.close()
