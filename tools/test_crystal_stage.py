from pathlib import Path
import json,sys
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
stage=sys.argv[1];assert stage in ('before','after');out=Path(__file__).resolve().parents[1]/'verification/crystal';out.mkdir(exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);page.locator('#cast2').click();page.locator('#pause').click();page.locator('#seek').evaluate('(e)=>{e.value="3.8";e.dispatchEvent(new Event("input",{bubbles:true}))}');page.locator('[data-view=front]').click();page.wait_for_timeout(2000);page.screenshot(path=str(out/(stage+'.png')));s=page.evaluate('window.__lingSkill');assert s['dragonVisible'] and s['layerRendered']['crystals'] and not s['errors'] and not errors;(out/(stage+'.json')).write_text(json.dumps({'quality':s['quality'],'fps':s['fps'],'drawCalls':s['drawCalls'],'errors':errors},indent=2));print(stage,'drawCalls',s['drawCalls'],'FPS',s['fps'],flush=True);b.close()
