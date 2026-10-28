from pathlib import Path
import json,math
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/moon-tide'
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready',timeout=120000);page.locator('#open-characters').tap();page.locator('[data-character=yueli]').tap();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading',timeout=90000)
 page.locator('#panel-toggle').tap();assert page.locator('#panel .aside-title').all_text_contents()==['声音','画质'];page.locator('#panel-toggle').tap()
 cdp=page.context.new_cdp_session(page);results=[]
 def send(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
 for count in [3,5,10]:
  page.evaluate('window.__lingQA.reset();window.__lingQA.freeze(false)');j=page.locator('#joystick').bounding_box();r=page.locator('#cast-yueli2').bounding_box();jx=j['x']+j['width']/2;jy=j['y']+j['height']/2;finger={'id':1,'x':jx,'y':jy-j['width']*.30};tap={'id':2,'x':r['x']+r['width']/2,'y':r['y']+r['height']/2}
  send('touchStart',[{'id':1,'x':jx,'y':jy}]);send('touchMove',[finger]);page.wait_for_function('window.__lingSkill.speed>.2',timeout=30000);page.evaluate('window.__lingQA.freeze(true)');before=page.evaluate('window.__lingQA.inspect()')
  for i in range(count):send('touchStart',[finger,tap]);send('touchEnd',[tap])
  page.wait_for_function('n=>window.__lingSkill.instances.created>=n',arg=before['instances']['created']+count,timeout=30000);page.evaluate('window.__lingQA.advance(.4)');after=page.evaluate('window.__lingQA.inspect()');assert after['instances']['created']-before['instances']['created']==count and after['instances']['activeCount']==count,after['instances']
  d=math.hypot(after['position'][0]-before['position'][0],after['position'][2]-before['position'][2]);assert d>.025,d
  ids={i['id'] for i in after['instances']['active']};events=[e for e in after['instanceAudio']['events'] if e['instanceId'] in ids and e['phase']=='cast'];assert len(events)==count and all(e['status']=='playing' for e in events),events
  send('touchEnd',[]);results.append({'touches':count,'instances':after['instances']['activeCount'],'audioCastEvents':len(events),'movementDistance':d})
 frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('n=>window.__lingSkill.frames>n',arg=frame,timeout=60000);page.screenshot(path=str(out/'landscape-touch-ten.png'))
 page.evaluate('window.__lingQA.reset()');before=page.evaluate('window.__lingQA.inspect().instances.created');page.locator('#cast-yueli2').tap();r=page.locator('#cast-yueli2').bounding_box();page.mouse.click(r['x']+r['width']/2,r['y']+r['height']/2);after=page.evaluate('window.__lingQA.inspect()');assert after['instances']['created']-before==2,after['instances'];results.append({'hybridTouchThenMouse':'two distinct inputs create two instances'})
 page.screenshot(path=str(out/'hybrid-touch-mouse.png'));assert not errors,errors
 (out/'touch.json').write_text(json.dumps({'scope':'Chromium CDP simulated two-finger landscape touch; no actual phone test','checks':results,'errors':errors},ensure_ascii=False,indent=2));print('PASS_TOUCH',json.dumps(results),flush=True);b.close()
