"""Verify Yueli loads in default renderer selection; software test only."""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/yueli-web'
with display() as env,sync_playwright() as p:
 browser=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 page=browser.new_page(viewport={'width':1100,'height':700});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/',wait_until='domcontentloaded')
 page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 page.locator('#panel-toggle').click();page.locator('#open-characters').click();page.locator('[data-character="yueli"]').click()
 page.wait_for_function("window.__lingSkill.character==='yueli' && !window.__lingSkill.characterLoading",timeout=90000)
 page.wait_for_function('window.__lingSkill.frames>5',timeout=30000)
 state=page.evaluate('window.__lingSkill');assert not errors and not state['errors'],(errors,state['errors'])
 result={'renderer':state['renderer'],'software':state['software'],'character':state['character'],'frames':state['frames'],'errors':errors,'scope':'desktop browser; no real-device test'}
 (out/'default-renderer.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS',json.dumps(result,ensure_ascii=False),flush=True)
 browser.close()
