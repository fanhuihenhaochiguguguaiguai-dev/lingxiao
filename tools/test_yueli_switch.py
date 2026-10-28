"""Browser regression: real GLBs, character switching and settings.

Runs on desktop Chromium software WebGL2; not a real-phone performance test.
Requires the existing static server on 127.0.0.1:8765.
"""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright

out=Path(__file__).resolve().parents[1]/'verification/yueli-web';out.mkdir(parents=True,exist_ok=True)
result={'scope':'desktop Chromium software WebGL2, not a real mobile device','tests':{}}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 page=b.new_page(viewport={'width':1100,'height':700});errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda req:requests.append(req.url))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2',wait_until='domcontentloaded')
 page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 assert page.evaluate('window.__lingSkill.character')=='lingyuan'
 page.locator('#cast2').click();page.wait_for_function('window.__lingSkill.skill===2 && window.__lingSkill.playing',timeout=30000)
 page.locator('#panel-toggle').click();panel=page.locator('#panel')
 assert panel.locator('.aside-title').all_text_contents()==['声音','画质','切换人物']
 page.locator('#mute').click();assert page.locator('#mute').inner_text()=='取消静音';page.locator('#mute').click()
 page.locator('[data-quality="ultra"]').click();assert page.evaluate('window.__lingSkill.quality')=='ultra';page.locator('[data-quality="high"]').click()
 page.locator('#open-characters').click();page.keyboard.press('Escape');assert not page.locator('#character-picker').is_visible()
 page.locator('#open-characters').click();page.locator('[data-character="yueli"]').click()
 page.wait_for_function("window.__lingSkill.character==='yueli' && !window.__lingSkill.characterLoading",timeout=90000)
 s=page.evaluate('window.__lingSkill');assert s['clips']==[] and not s['hasWeaponBone'] and not s['playing']
 assert not page.locator('.skill-buttons').is_visible()
 assert '静态工作稿' in page.locator('#phase').inner_text()
 page.wait_for_timeout(1200);page.screenshot(path=str(out/'yueli-initial.png'))
 camera_before=page.evaluate('window.__lingSkill.cameraPosition');page.mouse.move(500,350);page.mouse.down();page.mouse.move(620,350,steps=8);page.mouse.up();page.wait_for_timeout(600);camera_after=page.evaluate('window.__lingSkill.cameraPosition');assert sum(abs(a-b) for a,b in zip(camera_before,camera_after))>.05
 page.keyboard.press('1');page.wait_for_timeout(200);assert not page.evaluate('window.__lingSkill.playing')
 before=page.evaluate('window.__lingSkill.position');page.keyboard.down('w');page.wait_for_function('window.__lingSkill.speed>.2',timeout=30000);page.wait_for_timeout(300);page.keyboard.up('w');after=page.evaluate('window.__lingSkill.position');assert abs(after[0]-before[0])+abs(after[2]-before[2])>.02
 page.screenshot(path=str(out/'yueli-webgl.png'));result['tests']['yueli']={'character':s['character'],'clips':s['clips'],'movement_before':before,'movement_after':after,'camera_before':camera_before,'camera_after':camera_after,'skills_hidden':True}
 page.locator('#panel-toggle').click();page.locator('#open-characters').click();page.locator('[data-character="lingyuan"]').click();page.wait_for_function("window.__lingSkill.character==='lingyuan' && !window.__lingSkill.characterLoading",timeout=30000)
 assert page.locator('.skill-buttons').is_visible();page.locator('#cast').click();page.wait_for_function('window.__lingSkill.skill===1 && window.__lingSkill.playing',timeout=30000)
 page.locator('#cast3').click();page.wait_for_function('window.__lingSkill.skill===3 && window.__lingSkill.playing',timeout=30000)
 page.locator('#panel-toggle').click();page.locator('#open-characters').click();page.locator('[data-character="yueli"]').click();page.wait_for_function("window.__lingSkill.character==='yueli' && !window.__lingSkill.characterLoading",timeout=30000)
 assert sum('/yueli-study.glb' in url for url in requests)==1
 assert not errors,errors
 result['tests']['switch_back_and_cache']='three first-character skill controls trigger; second model fetched once'
 result['errors']=errors;page.close()
 mobile=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True,device_scale_factor=1)
 mobile.on('pageerror',lambda e:errors.append(str(e)))
 mobile.goto('http://127.0.0.1:8765/skill/?renderer=webgl2',wait_until='domcontentloaded')
 mobile.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 def tap(selector):
  box=mobile.locator(selector).bounding_box();assert box
  mobile.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2)
 tap('#panel-toggle');tap('#open-characters');tap('[data-character="yueli"]')
 mobile.wait_for_function("window.__lingSkill.character==='yueli' && !window.__lingSkill.characterLoading",timeout=90000)
 assert '静态工作稿' in mobile.locator('#phase').inner_text()
 mobile.wait_for_timeout(1200)
 mobile.screenshot(path=str(out/'landscape-simulated.png'))
 result['tests']['landscape_touch_simulation']='touch taps open settings, choose and load Yueli in simulated landscape; real device not tested'
 assert not errors,errors
 mobile.close();b.close()
result['status']='PASS_DESKTOP_SOFTWARE_ONLY';(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS',json.dumps(result,ensure_ascii=False),flush=True)
