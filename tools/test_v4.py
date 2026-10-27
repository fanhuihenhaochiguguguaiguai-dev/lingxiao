from pathlib import Path
import json, math
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/v4-dragon';out.mkdir(parents=True,exist_ok=True)
result={'backends':{},'character':{},'note':'Desktop software renderer only; no Android or art acceptance'}
def seek(page,t):
 page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t))
 page.wait_for_timeout(700)
def delta(a,b):return math.dist(a,b)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for backend in ['webgl2','webgpu']:
  page=b.new_page(viewport={'width':1280,'height':720});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8765/skill/'+('' if backend=='webgpu' else '?renderer=webgl2'));page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
  assert page.locator('[data-quality]').count()==2 and page.locator('[data-quality=standard]').count()==0
  skills={}
  for label,button,t0,t1 in [('skill1','cast',1.0,2.45),('skill2','cast2',2.0,3.8),('ultimate','cast3',2.0,3.1)]:
   page.locator('#'+button).click();page.locator('#pause').click();seek(page,t0);a=page.evaluate('window.__lingSkill');seek(page,t1);c=page.evaluate('window.__lingSkill');assert a['dragonVisible'] and c['dragonVisible'] and delta(a['dragonWorld'],c['dragonWorld'])>.05,(label,a['dragonWorld'],c['dragonWorld'])
   page.locator('[data-view=angle]').click();page.wait_for_timeout(700)
   if backend=='webgl2':page.screenshot(path=str(out/(label+'-angle.png')))
   skills[label]={'headMoved':round(delta(a['dragonWorld'],c['dragonWorld']),3),'drawCalls':c['drawCalls']}
  page.locator('[data-follow=dragon]').click();before=page.evaluate('window.__lingSkill.cameraTarget');page.wait_for_timeout(3500);after=page.evaluate('window.__lingSkill.cameraTarget');assert delta(before,after)>.03,(before,after)
  page.locator('[data-follow=actor]').click();page.wait_for_timeout(1800);assert page.evaluate('window.__lingSkill.cameraMode')=='actor'
  page.locator('[data-follow=free]').click();assert page.evaluate('window.__lingSkill.cameraMode')=='free'
  page.locator('[data-quality=ultra]').click();assert page.evaluate('window.__lingSkill.quality')=='ultra';page.locator('[data-quality=high]').click()
  page.locator('#step').click();t=page.evaluate('window.__lingSkill.time');assert t>3.1
  state=page.evaluate('window.__lingSkill');assert not state['errors'] and not errors,(state['errors'],errors)
  result['backends'][backend]={'actual':state['renderer'],'software':state['software'],'skills':skills,'dragonCameraMoved':round(delta(before,after),3),'errors':errors}
  page.close()
 page=b.new_page(viewport={'width':1280,'height':720});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/?renderer=webgl2');page.wait_for_function('window.__lingyuan && window.__lingyuan.ready',timeout=90000)
 page.keyboard.down('w');page.wait_for_timeout(3000);a=page.evaluate('window.__lingyuan');page.keyboard.down('d');page.wait_for_timeout(2000);c=page.evaluate('window.__lingyuan');page.keyboard.up('w');page.keyboard.up('d');page.wait_for_function("window.__lingyuan.animation === 'idle'",timeout=20000);d=page.evaluate('window.__lingyuan');page.screenshot(path=str(out/'character-motion.png'))
 assert a['speed']>.01 and delta([a['position']['x'],a['position']['z']],[c['position']['x'],c['position']['z']])>.01
 assert d['speed']<a['speed'] and d['animation']=='idle',(a,d)
 assert not errors and not d['errors'],(errors,d['errors'])
 result['character']={'movingSpeed':a['speed'],'stoppedSpeed':d['speed'],'headingAfterTurn':c['heading'],'cameraTarget':d['cameraTarget'],'errors':errors}
 page.close();b.close()
 result['status']='PASS_DESKTOP_SOFTWARE_ONLY';(out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False),flush=True)
