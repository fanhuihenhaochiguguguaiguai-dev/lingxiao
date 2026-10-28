"""Current exported face/blink, character-cache restoration and shared-head reuse.
Screenshots are evidence for manual art review, not an automatic likeness pass.
"""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/moonfall/character';out.mkdir(parents=True,exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.ultimateAssetsReady',timeout=120000);page.evaluate('window.__lingQA.freeze(true)')
 def select(who):
  page.locator('#open-characters').click();page.locator('[data-character='+who+']').click();page.wait_for_function('who=>window.__lingSkill.character===who&&!window.__lingSkill.characterLoading',arg=who,timeout=90000)
 def shot(name,view='face'):
  page.evaluate('v=>window.__lingQA.view(v)',view);frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=frame,timeout=90000);page.screenshot(path=str(out/(name+'.png')))
 select('yueli');page.evaluate('window.__lingQA.blink(0)');shot('web-face-open');page.evaluate('window.__lingQA.blink(1)');assert page.evaluate('window.__lingSkill.motionSample.blink')==1;shot('web-face-blink');page.evaluate('window.__lingQA.blink(null)')
 page.keyboard.down('w');page.keyboard.down('Shift');page.evaluate('window.__lingQA.advance(.8)');page.keyboard.up('w');page.keyboard.up('Shift');running=page.evaluate('window.__lingSkill.motionSample');assert running['gait']=='run' and running['ikLegs']==2,running
 page.evaluate('window.__lingQA.reset()');page.locator('#cast-yueli3').click();page.evaluate('window.__lingQA.advance(.9)');shot('web-cast-pose','front')
 active_ids=page.evaluate('window.__lingSkill.instances.active.map(i=>i.id)')
 for who in ['lingyuan','yueli']:select(who)
 page.evaluate('window.__lingQA.advance(1/60)');switched=page.evaluate('window.__lingQA.inspect()')
 assert not switched['casting'] and switched['motionSample']['gait']=='idle' and len(switched['boneNames'])==36,switched['motionSample']
 assert page.evaluate('window.__lingSkill.instances.active.map(i=>i.id)')==active_ids
 page.evaluate('window.__lingQA.reset();for(let i=0;i<10;i++)document.getElementById("cast-yueli3").click();window.__lingQA.advance(12)');assert page.evaluate('window.__lingSkill.instances.activeCount')==0
 page.evaluate('for(let i=0;i<3;i++)document.getElementById("cast-yueli3").click();window.__lingQA.advance(2.3)');snapshot=page.evaluate('window.__lingQA.inspect()');assert snapshot['instances']['activeCount']==3 and sum(i['dragonCount'] for i in snapshot['instances']['active'])==3
 shot('web-dragon-after-recycle','angle');assert not errors and not snapshot['errors'],(errors,snapshot['errors'])
 (out/'web.json').write_text(json.dumps({'scope':'desktop software WebGL2; geometry/render/control checks only; likeness not approved','bones':len(snapshot['boneNames']),'blinkOverrideApplied':True,'running':running,'characterSwitchRestoresState':True,'dragonsAfterTenExpiredAndThreeRespawned':3,'errors':errors},ensure_ascii=False,indent=2));print('PASS_FACE_BLINK_SWITCH_DRAGON_REUSE',flush=True);b.close()
