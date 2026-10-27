from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/v11';out.mkdir(exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.goto('http://127.0.0.1:8765/skill/');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);page.keyboard.down('d');page.wait_for_function('Math.abs(window.__lingSkill.position[0])+Math.abs(window.__lingSkill.position[2])>.05',timeout=45000);page.keyboard.up('d');m=page.evaluate('window.__lingSkill');assert abs(m['position'][0])+abs(m['position'][2])>.05
 page.locator('#cast3').click();page.wait_for_function('window.__lingSkill.dragonVisible && window.__lingSkill.audioEvents.some(e=>e.skill===3)',timeout=30000);s=page.evaluate('window.__lingSkill');assert s['renderer']=='WebGPU' and not s['errors'] and not errs;(out/'webgpu.json').write_text(json.dumps({'status':'PASS_SOFTWARE_ONLY','renderer':s['renderer'],'software':s['software'],'position':s['position'],'dragon':s['dragonWorld'],'audio':s['audioEvents'],'errors':errs},ensure_ascii=False,indent=2));page.screenshot(path=str(out/'webgpu-ultimate.png'));print('PASS software WebGPU movement and ultimate',flush=True);b.close()
