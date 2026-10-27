import sys,json,time,os
from pathlib import Path
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=str(Path(os.environ.get('LING_TEST_OUT',Path(__file__).resolve().parents[1]/'verification')));Path(out).mkdir(parents=True,exist_ok=True)
with display() as env:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
  page=b.new_page(viewport={'width':1280,'height':720});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000)
  assert page.evaluate('window.__lingSkill.ready'),page.evaluate('window.__lingSkill.errors')
  def seek(t):
   page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(1300)
  page.locator('#cast2').click();page.locator('#pause').click();seek(3.8)
  assert page.evaluate('window.__lingSkill.skill')==2 and page.evaluate('window.__lingSkill.dragonVisible')
  for name in ['dragon','circle','crystals','beams','chains','particles']:
   checkbox=page.locator(f'[data-layer={name}]');checkbox.uncheck();assert page.evaluate('(n)=>!window.__lingSkill.layerRendered[n]',name);checkbox.check();assert page.evaluate('(n)=>window.__lingSkill.layerRendered[n]',name)
  for view in ['front','side','back','top']:
   page.locator(f'[data-view={view}]').click();page.wait_for_timeout(1200);page.screenshot(path=f'{out}/skill02-{view}.png')
  page.locator('[data-view=front]').click();seek(1.1);page.screenshot(path=f'{out}/skill02-windup.png')
  seek(2.5);page.screenshot(path=f'{out}/skill02-dragon.png')
  seek(3.8);state=page.evaluate('window.__lingSkill');page.screenshot(path=f'{out}/skill02-detail.png')
  paused=state['time'];page.locator('#step').click();assert page.evaluate('window.__lingSkill.time')>paused
  page.locator('#slow').click();assert page.evaluate('window.__lingSkill.slow');page.locator('#slow').click()
  seek(6.35);page.locator('#loop').click();page.locator('#pause').click();page.wait_for_function('window.__lingSkill.time < 1 && window.__lingSkill.playing',timeout=40000);page.locator('#pause').click();page.locator('#loop').click()
  page.locator('#cast').click();page.locator('#pause').click();seek(2.45);s1=page.evaluate('window.__lingSkill');assert s1['skill']==1 and s1['dragonVisible'] and s1['actorX']>0 and not any(s1['layerRendered'].values())
  page.locator('#cast2').click();page.locator('#pause').click();seek(3.8);s2=page.evaluate('window.__lingSkill');assert s2['skill']==2 and abs(s2['actorX'])<.01
  assert not errors and not s2['errors'],(errors,s2['errors'])
  result={'skill02':s2,'skill01_regression':s1,'pageerrors':errors};open(out+'/skill02-controls.json','w').write(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False),flush=True)
  page.close()
  mobile=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);mobile.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');mobile.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);mobile.locator('#cast2').click();mobile.locator('#pause').click();mobile.locator('#seek').evaluate('(e)=>{e.value="3.8";e.dispatchEvent(new Event("input",{bubbles:true}))}');mobile.wait_for_timeout(1800);mobile.screenshot(path=out+'/skill02-landscape.png');assert mobile.evaluate('window.__lingSkill.skill')==2;mobile.close();b.close()
