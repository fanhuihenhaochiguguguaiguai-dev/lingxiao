import sys,json,time
sys.path.insert(0,'/workspace/sites/henan-campus-lab/tools')
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out='/workspace/sites/lingyuan-character-lab/verification'
with display() as env:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
  page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2',wait_until='domcontentloaded');page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000);page.wait_for_timeout(2000)
  initial=page.evaluate('window.__lingSkill');print('INITIAL',json.dumps(initial,ensure_ascii=False),flush=True);assert initial['ready'] and initial['hasCharacter'] and initial['hasWeaponBone'],errors
  page.locator('#cast').click();page.wait_for_function('window.__lingSkill.time > .05',timeout=40000);page.locator('#pause').click();before=page.evaluate('window.__lingSkill.time');page.wait_for_timeout(500);after=page.evaluate('window.__lingSkill.time');assert abs(before-after)<.005
  page.locator('#step').click();page.wait_for_timeout(300);assert page.evaluate('window.__lingSkill.time')>after
  states=[]
  for t in [.55,1.45,2.45,3.45]:
   page.locator('#seek').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(1500);s=page.evaluate('window.__lingSkill');states.append(s);page.screenshot(path=f'{out}/skill-{t:.2f}.png')
  print('PHASES',json.dumps(states,ensure_ascii=False),flush=True);assert all(x['dragonVisible'] for x in states);assert states[1]['actorX']>states[0]['actorX'];assert states[1]['boneSample']!=states[0]['boneSample'];assert len({x['stage'] for x in states})==4
  page.locator('#slow').click();assert page.evaluate('window.__lingSkill.slow');page.locator('#slow').click();assert not page.evaluate('window.__lingSkill.slow');page.locator('#seek').evaluate('(el)=>{el.value="4.35";el.dispatchEvent(new Event("input",{bubbles:true}))}');page.locator('#loop').click();assert page.evaluate('window.__lingSkill.looping');page.locator('#pause').click();page.wait_for_function('window.__lingSkill.time < 1 && window.__lingSkill.playing',timeout=40000);page.locator('#pause').click();
  page.locator('[data-view=top]').click();page.locator('[data-quality=ultra]').click();page.wait_for_timeout(500);assert page.evaluate('window.__lingSkill.quality')=='ultra';print('ERRORS',json.dumps(errors),flush=True);assert not errors;page.close()
  mobile=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);mobile.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');mobile.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000);mobile.wait_for_timeout(1000);ms=mobile.evaluate('window.__lingSkill');assert ms['ready'];mobile.locator('#cast').click();mobile.wait_for_function('window.__lingSkill.time>.05',timeout=40000);mobile.screenshot(path=f'{out}/skill-landscape.png');print('LANDSCAPE',json.dumps(ms),flush=True);mobile.close()
  portrait=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);portrait.goto('http://127.0.0.1:8765/skill/?renderer=webgl2',wait_until='domcontentloaded');assert portrait.locator('#rotate').is_visible();portrait.close();b.close()
