"""Moving-cast behavior checks on desktop Chromium software WebGL2.

Touch input is simulated; this does not assess artistic animation or phone FPS.
"""
from pathlib import Path
import json,math
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/moving-cast';out.mkdir(parents=True,exist_ok=True)
def distance(a,b):return math.hypot(a[0]-b[0],a[2]-b[2])
with display() as env,sync_playwright() as p:
 browser=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 page=browser.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2',wait_until='domcontentloaded')
 page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 page.evaluate("document.getElementById('slow').click()")
 checks={}
 for skill in (1,2,3):
  for speed in ('walk','fast'):
   if speed=='fast':page.keyboard.down('Shift')
   page.keyboard.down('w');page.wait_for_function('window.__lingSkill.speed>.2',timeout=30000)
   previous_frames=page.evaluate('window.__lingSkill.frames')
   page.locator('#cast' if skill==1 else '#cast'+str(skill)).click()
   page.wait_for_function(f'frame=>window.__lingSkill.frames>frame && window.__lingSkill.skill==={skill} && window.__lingSkill.casting && window.__lingSkill.time>.15',arg=previous_frames,timeout=30000)
   before=page.evaluate('window.__lingSkill');page.wait_for_function('t=>window.__lingSkill.time>t+.25',arg=before['time'],timeout=30000);after=page.evaluate('window.__lingSkill')
   assert after['casting'] and after['time']>before['time'] and distance(before['stagePosition'],after['stagePosition'])>.025,(skill,speed,before,after)
   page.keyboard.up('w');page.keyboard.down('d');page.wait_for_function('t=>window.__lingSkill.time>t+.15',arg=after['time'],timeout=30000);turned=page.evaluate('window.__lingSkill')
   assert turned['casting'] and abs(turned['stageYaw']-before['stageYaw'])<.001,(skill,speed,{k:before[k] for k in ('time','stageYaw','casting','slow')},{k:turned[k] for k in ('time','stageYaw','casting','slow')})
   page.keyboard.up('d');page.keyboard.up('Shift')
   checks[f'{skill}_{speed}']={'distance':round(distance(before['stagePosition'],after['stagePosition']),3),'elapsed':round(after['time']-before['time'],3),'directionLocked':True}
 page.evaluate("document.getElementById('slow').click()")
 page.wait_for_function('!window.__lingSkill.casting',timeout=30000)
 assert not errors,errors
 page.close()
 mobile=browser.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True,device_scale_factor=1)
 mobile.on('pageerror',lambda e:errors.append(str(e)))
 mobile.goto('http://127.0.0.1:8765/skill/?renderer=webgl2',wait_until='domcontentloaded');mobile.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 joy=mobile.locator('#joystick').bounding_box();button=mobile.locator('#cast2').bounding_box();assert joy and button
 jx=joy['x']+joy['width']/2;jy=joy['y']+joy['height']/2;bx=button['x']+button['width']/2;by=button['y']+button['height']/2
 cdp=mobile.context.new_cdp_session(mobile)
 def send(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
 finger={'x':jx,'y':jy-joy['width']*.30,'id':1};target={'x':bx,'y':by,'id':2}
 send('touchStart',[{'x':jx,'y':jy,'id':1}]);send('touchMove',[finger]);mobile.wait_for_function('window.__lingSkill.speed>.2',timeout=30000)
 send('touchStart',[finger,target]);send('touchEnd',[target]);mobile.wait_for_function('window.__lingSkill.skill===2 && window.__lingSkill.casting && window.__lingSkill.time>.2',timeout=30000)
 before=mobile.evaluate('window.__lingSkill');mobile.wait_for_function('t=>window.__lingSkill.time>t+.25',arg=before['time'],timeout=30000);after=mobile.evaluate('window.__lingSkill');assert after['casting'] and distance(before['stagePosition'],after['stagePosition'])>.025
 send('touchEnd',[]);checks['two_finger']={'stageDistance':round(distance(before['stagePosition'],after['stagePosition']),3),'casting':after['casting']}
 assert not errors,errors
 mobile.close();browser.close()
result={'status':'PASS_DESKTOP_SOFTWARE_ONLY','scope':'Chromium software WebGL2 and simulated touch; no hardware phone or artistic acceptance','checks':checks,'errors':errors}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS',json.dumps(result,ensure_ascii=False),flush=True)
