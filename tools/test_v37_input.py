from pathlib import Path
import json,math
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v37';checks={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');context=b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True,device_scale_factor=3);page=context.new_page();page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)')
 def s():return page.evaluate('window.__lingQA.inspect()')
 def advance(t):page.evaluate('t=>window.__lingQA.advance(t)',t)
 def center(selector,id):
  r=page.locator(selector).bounding_box();return {'id':id,'x':r['x']+r['width']/2,'y':r['y']+r['height']/2}
 cdp=context.new_cdp_session(page)
 def send(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
 def frame(name):
  n=s()['frames'];page.wait_for_function('n=>window.__lingSkill.frames>n',arg=n);page.screenshot(path=str(out/name))
 # Viewport/CSS-pixel bounds; these are desktop emulations, not a physical safe-area measurement.
 layouts=[]
 for w,h,inset in [(568,320,0),(667,375,0),(844,390,0),(915,412,44),(1024,600,0),(1200,540,32)]:
  page.set_viewport_size({'width':w,'height':h});page.evaluate('r=>document.querySelector(".shell").style.setProperty("--hud-right",Math.max(18,r)+"px")',inset)
  rects=page.locator('#joystick,#basic-attack,#jump,.skill-buttons button:not([hidden]),#open-characters,#panel-toggle,#clean-mode,#combat-mode,#combat-reset,.identity').evaluate_all('(es)=>es.map(e=>({id:e.id||e.className,...e.getBoundingClientRect().toJSON()}))')
  for r in rects:assert r['x']>=0 and r['y']>=0 and r['right']<=w+.1 and r['bottom']<=h+.1,(w,h,r)
  for i,a in enumerate(rects):
   for c in rects[i+1:]:assert min(a['right'],c['right'])<=max(a['left'],c['left']) or min(a['bottom'],c['bottom'])<=max(a['top'],c['top']),(w,h,'overlap',a,c)
  assert next(r for r in rects if r['id']=='cast3')['width']>next(r for r in rects if r['id']=='cast')['width'];layouts.append({'viewport':[w,h],'DPR':3,'simulatedRightInset':inset,'rects':rects})
 checks['layouts']=layouts;page.set_viewport_size({'width':844,'height':390});page.evaluate('document.querySelector(".shell").style.removeProperty("--hud-right")');frame('after-hud.png')
 # Three fingers own movement, skill 1, and skill 2 independently; no cast on pointer-down.
 page.evaluate('window.__lingQA.reset()');j=center('#joystick',1);move={**j,'y':j['y']-28};a=center('#cast',2);c=center('#cast2',3);before=s()['instances']['created'];send('touchStart',[j]);send('touchMove',[move]);send('touchStart',[move,a]);send('touchStart',[move,a,c]);advance(.3);assert s()['instances']['created']==before and len(page.evaluate('window.__combatQA.input().pointers'))==2;pos=s()['position'];a1={**a,'x':a['x']-55,'y':a['y']-30};send('touchMove',[move,a1,c]);frame('three-finger-aim.png');aim_camera=s();f=[aim_camera['cameraTarget'][i]-aim_camera['cameraPosition'][i] for i in [0,2]];l=math.hypot(*f);fx,fz=[v/l for v in f];dx,dz=-fz*(-55)+fx*30,fx*(-55)+fz*30;expected_yaw=math.atan2(-dz,dx);send('touchEnd',[a1]);assert s()['instances']['created']==before+1,('first release',s()['instances'],page.evaluate('window.__combatQA.input()'));actual_yaw=s()['instances']['active'][-1]['yaw'];assert abs(math.atan2(math.sin(actual_yaw-expected_yaw),math.cos(actual_yaw-expected_yaw)))<1e-6;send('touchEnd',[c]);assert s()['instances']['created']==before+2,('second release',s()['instances'],page.evaluate('window.__combatQA.input()'));advance(.35);assert math.dist(pos,s()['position'])>.1;send('touchEnd',[move]);assert not page.evaluate('window.__combatQA.input().pointers');checks['threeFingerMoveTwoSkills']={'created':2,'noCastBeforeRelease':True,'movementContinues':True,'noSyntheticClickDuplicate':True,'dragYaw':actual_yaw,'expectedWorldYaw':expected_yaw}
 # Ten physical-style touch taps produce ten immediate, independent instances.
 for count in [1,3,5,10]:
  page.evaluate('window.__lingQA.reset()');before=s()['instances']['created'];a=center('#cast',2)
  for _ in range(count):send('touchStart',[a]);send('touchEnd',[])
  ss=s();assert ss['instances']['created']-before==count and ss['instances']['activeCount']==count;assert len({i['id'] for i in ss['instances']['active']})==count;checks['touchBurst'+str(count)]={'created':count,'independent':True,'allAgesZero':all(i['age']==0 for i in ss['instances']['active'])}
 # Cancel area, lost pointer, blur, character picker, and reset cannot release stale casts.
 before=s()['instances']['created'];a=center('#cast2',4);send('touchStart',[a]);cancel=center('#cast-cancel',4);send('touchMove',[cancel]);assert page.evaluate('window.__combatQA.input().pointers[0].cancelled');send('touchEnd',[]);assert s()['instances']['created']==before
 for event in ['touchCancel','blur','reset','character-picker']:
  a=center('#cast2',4);send('touchStart',[a]);
  if event=='touchCancel':send('touchCancel',[])
  elif event=='blur':page.evaluate('window.dispatchEvent(new Event("blur"))');send('touchEnd',[])
  elif event=='reset':page.evaluate('window.__combatQA.reset()');send('touchEnd',[])
  else:page.evaluate('document.getElementById("open-characters").click()');send('touchEnd',[]);page.locator('#close-characters').click()
  assert not page.evaluate('window.__combatQA.input().pointers') and s()['instances']['created']==before,event
 checks['cancelAndLifecycleOwnership']=True
 # Current common release gates preserve VFX while allowing natural recovery cancels.
 page.evaluate('window.__lingQA.reset();document.getElementById("basic-attack").click();window.__lingQA.advance(.1);document.getElementById("cast2").click();window.__lingQA.advance(.2);document.getElementById("basic-attack").click();window.__lingQA.advance(.9)');ss=s();assert any(e['phase']=='cancelled-before-release' for e in ss['basic']['events']);wind=[e for e in ss['basic']['events'] if e['phase']=='windup'];assert len(wind)==2 and wind[1]['time']>=.95 and wind[1]['time']<1.2 and ss['instances']['activeCount']==1;checks['basicSkillBasicBlend']={'bufferedBasicAt':wind[1]['time'],'skillVfxSurvives':True,'cancelledWindupNoGhostDamage':not any(e['kind']=='lingyuan-basic' for e in ss['combat']['events'])}
 page.locator('#panel-toggle').tap();assert page.locator('#panel .aside-title').all_text_contents()==['声音','画质'];page.locator('#panel-toggle').tap();checks['settingsPreserved']=True
 assert not errors and not s()['errors'],(errors,s()['errors']);context.close();b.close()
(out/'input.json').write_text(json.dumps({'scope':'real Chromium DOM/CDP simulated multi-touch and layout; no Android hardware claims','checks':checks,'errors':errors},ensure_ascii=False,indent=2));print('PASS_V37_INPUT',flush=True)
