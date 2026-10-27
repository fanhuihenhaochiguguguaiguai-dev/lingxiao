from pathlib import Path
import json,sys
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification'
with display() as env:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
  page=b.new_page(viewport={'width':1280,'height':720});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000)
  assert page.evaluate('window.__lingSkill.ready'),page.evaluate('window.__lingSkill.errors')
  def seek(t):
   page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(1300)
  page.locator('#cast3').click();page.locator('#pause').click();states=[]
  for t in [.5,1.3,3.0,4.65,5.15,6.4]:
   seek(t);state=page.evaluate('window.__lingSkill');states.append({'time':state['time'],'stage':state['stage'],'visible':state['starVisible'],'dragon':state['dragonVisible'],'dragonX':state['dragonX'],'drawCalls':state['drawCalls']});page.screenshot(path=str(out/f'skill03-{t:.2f}.png'))
  assert len({s['stage'] for s in states})==6 and all(s['visible'] for s in states),states
  assert states[1]['dragon'] and states[2]['dragon'] and states[1]['dragonX']!=states[2]['dragonX']
  seek(3);page.locator('[data-view=front]').click();page.wait_for_timeout(1100);page.screenshot(path=str(out/'skill03-front.png'))
  page.locator('[data-view=side]').click();page.wait_for_timeout(1100);page.screenshot(path=str(out/'skill03-side.png'))
  page.locator('[data-view=top]').click();page.wait_for_timeout(1100);page.screenshot(path=str(out/'skill03-top.png'))
  time=page.evaluate('window.__lingSkill.time');page.locator('#step').click();assert page.evaluate('window.__lingSkill.time')>time
  page.locator('#slow').click();assert page.evaluate('window.__lingSkill.slow');page.locator('#slow').click()
  page.locator('#cast3').click();page.wait_for_function('window.__lingSkill.starCues.includes("awaken")',timeout=30000);page.locator('#pause').click();seek(4.9);page.locator('#pause').click();page.wait_for_function('window.__lingSkill.starCues.includes("burst")',timeout=30000);page.locator('#pause').click()
  seek(7.35);page.locator('#loop').click();page.locator('#pause').click();page.wait_for_function('window.__lingSkill.time < 1 && window.__lingSkill.playing',timeout=40000);page.locator('#pause').click();page.locator('#loop').click()
  seek(7.4);assert not page.evaluate('window.__lingSkill.starVisible')
  for button,t in [('cast',2.45),('cast2',3.8)]:
   page.locator('#'+button).click();page.locator('#pause').click();seek(t);s=page.evaluate('window.__lingSkill');assert s['dragonVisible'] and not s['starVisible'],s
  page.locator('#cast3').click();page.locator('#pause').click();seek(3);final=page.evaluate('window.__lingSkill');assert not any(final['layerRendered'].values()) and not final['errors'] and not errors
  result={'stages':states,'final':final,'pageerrors':errors};(out/'skill03-controls.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'status':'PASS','stages':states,'fps':final['fps'],'drawCalls':final['drawCalls'],'errors':errors},ensure_ascii=False),flush=True)
  page.close()
  mobile=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);mobile.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');mobile.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);mobile.locator('#cast3').click();mobile.locator('#pause').click();mobile.locator('#seek').evaluate('(e)=>{e.value="3";e.dispatchEvent(new Event("input",{bubbles:true}))}');mobile.wait_for_timeout(1600);mobile.screenshot(path=str(out/'skill03-landscape.png'));assert mobile.evaluate('window.__lingSkill.skill')==3;mobile.close();b.close()
