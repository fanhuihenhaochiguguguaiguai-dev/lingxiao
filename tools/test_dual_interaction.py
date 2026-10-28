from pathlib import Path
import json,math
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/dual-quality';results={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':844,'height':390},has_touch=True,is_mobile=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready',timeout=90000)
 page.locator('#panel-toggle').tap();assert page.locator('#panel .aside-title').all_text_contents()==['声音','画质'];page.locator('#panel-toggle').tap();results['settings']='sound and quality only'
 page.evaluate('''window.pointerLog=[];for(const type of ["pointerdown","pointerup","pointercancel","lostpointercapture"]){document.addEventListener(type,e=>window.pointerLog.push({type,id:e.pointerId,target:e.target.id}),true)}''')
 cdp=page.context.new_cdp_session(page);joy=page.locator('#joystick').bounding_box();skill=page.locator('#cast2').bounding_box();jx=joy['x']+joy['width']/2;jy=joy['y']+joy['height']/2;finger={'id':1,'x':jx,'y':jy-joy['width']*.32};target={'id':2,'x':skill['x']+skill['width']/2,'y':skill['y']+skill['height']/2}
 def touch(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
 touch('touchStart',[{'id':1,'x':jx,'y':jy}]);touch('touchMove',[finger]);page.wait_for_function('window.__lingSkill.speed>.2',timeout=30000);touch('touchStart',[finger,target]);touch('touchEnd',[target]);page.wait_for_function('window.__lingSkill.casting&&window.__lingSkill.skill===2',timeout=30000);page.evaluate('window.__lingQA.advance(.4)');state=page.evaluate('window.__lingSkill');assert state['casting'] and state['skill']==2 and state['speed']>.2,{'state':{k:state[k] for k in ['casting','skill','speed','queuedSkill']},'pointers':page.evaluate('window.pointerLog')};touch('touchEnd',[]);results['twoFinger']='moving while casting skill 2';page.evaluate('window.__lingQA.reset()')
 for i in (1,2,3):
  page.locator('#cast' if i==1 else '#cast'+str(i)).tap();page.evaluate('window.__lingQA.advance(2)');state=page.evaluate('window.__lingSkill');assert state['casting'] and state['skill']==i and state['dragonVisible'];page.evaluate('window.__lingQA.reset()')
 page.locator('#open-characters').tap();page.locator('[data-character=yueli]').tap();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading',timeout=90000);page.evaluate('window.__lingQA.reset()')
 page.locator('#cast-yueli').tap();page.evaluate('window.__lingQA.advance(2.6)');state=page.evaluate('window.__lingSkill');assert any(h['character']=='yueli' for h in state['hitEvents']),state['hitEvents'];results['moonHit']=state['hitEvents'];results['moonAudioCues']=[e for e in state['audioEvents'] if e['skill']==4];assert results['moonAudioCues'];page.screenshot(path=str(out/'touch-moon.png'));page.evaluate('window.__lingQA.reset()')
 page.keyboard.down('w');page.keyboard.down('Shift');page.evaluate('window.__lingQA.advance(30)');page.keyboard.up('w');page.keyboard.up('Shift');state=page.evaluate('window.__lingSkill');radius=math.hypot(*[state['stagePosition'][i] for i in [0,2]]);assert 20<radius<=state['moveRadius']+.001,(radius,state['moveRadius']);results['boundary']={'radius':radius,'limit':state['moveRadius'],'areaRatio':state['areaRatio']}
 for char in ['lingyuan','yueli','lingyuan','yueli']:
  page.locator('#open-characters').tap();page.locator('[data-character='+char+']').tap();page.wait_for_function('(char)=>window.__lingSkill.character===char&&!window.__lingSkill.characterLoading',arg=char,timeout=60000);page.evaluate('window.__lingQA.advance(.5)');sample=page.evaluate('window.__lingSkill.motionSample');assert sample['ikLegs']==2 and all(e<.025 for e in sample['contactErrors']),sample
 results['cachedSwitches']='four successive character switches retain contact solver and rig state'
 assert not errors,errors;results['errors']=errors;results['scope']='simulated landscape touch / software WebGL2; no phone latency or art acceptance';(out/'interaction.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False),flush=True);b.close()
