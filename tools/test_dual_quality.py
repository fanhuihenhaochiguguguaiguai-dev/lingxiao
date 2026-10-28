"""Browser functional and deformation checks. Software render; no phone/art approval."""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/dual-quality';out.mkdir(exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready',timeout=90000)
 results={}
 for char in ['lingyuan','yueli']:
  if char=='yueli':page.locator('#open-characters').click();page.locator('[data-character="yueli"]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading',timeout=90000)
  page.keyboard.down('w');page.evaluate('window.__lingQA.advance(.5)');walk=page.evaluate('window.__lingSkill');assert walk['motionSample']['ikLegs']==2,walk['motionSample']
  page.keyboard.down('Shift');page.evaluate('window.__lingQA.advance(.8)');run=page.evaluate('window.__lingSkill');page.evaluate('window.__lingQA.freeze(true);window.__lingQA.view("side")');page.wait_for_timeout(900);page.screenshot(path=str(out/f'{char}-run.png'));page.evaluate('window.__lingQA.freeze(false)');assert run['motion']=='run',run['motion']
  page.keyboard.up('Shift');page.keyboard.up('w');page.evaluate('window.__lingQA.advance(.5)')
  page.keyboard.press('Space');page.evaluate('window.__lingQA.advance(.25)');jump=page.evaluate('window.__lingSkill');page.evaluate('window.__lingQA.freeze(true)');page.wait_for_timeout(900);page.screenshot(path=str(out/f'{char}-jump.png'));page.evaluate('window.__lingQA.freeze(false)');assert jump['jumpHeight']>.3,jump['jumpHeight']
  page.evaluate('window.__lingQA.advance(1)');land=page.evaluate('window.__lingSkill');assert land['jumpHeight']==0
  page.evaluate('window.__lingQA.reset()');count=land['castCount'];page.locator('#cast' if char=='lingyuan' else '#cast-yueli').click();page.evaluate('window.__lingQA.advance(.5)');page.locator('#cast' if char=='lingyuan' else '#cast-yueli').click();queued=page.evaluate('window.__lingSkill');assert queued['castCount']==count+1 and queued['queuedSkill']==1
  page.evaluate('window.__lingQA.advance(4.1)');repeated=page.evaluate('window.__lingSkill');assert repeated['castCount']==count+2,(repeated['castCount'],count)
  page.evaluate('window.__lingQA.advance(5)');page.evaluate('window.__lingQA.reset()')
  for view in ['front','side','back','angle','face']:
   page.evaluate('(v)=>window.__lingQA.view(v)',view);page.wait_for_timeout(800);page.screenshot(path=str(out/f'{char}-{view}.png'))
  assert max(run['motionSample']['contactErrors'] or [0])<.025,run['motionSample']
  page.evaluate('window.__lingQA.blink(1);window.__lingQA.freeze(true);window.__lingQA.view("face")');page.wait_for_timeout(900);page.screenshot(path=str(out/f'{char}-blink.png'));page.evaluate('window.__lingQA.blink(null);window.__lingQA.freeze(false)')
  results[char]={'bones':len(land['boneNames']),'walk':walk['motionSample'],'run':run['motionSample'],'jump':jump['jumpHeight'],'land':land['jumpHeight'],'bufferedRepeat':repeated['castCount']-count,'hits':repeated['hitEvents']}
 assert not errors,errors
 results['errors']=errors;results['scope']='desktop software WebGL2; artistic quality and real phone not accepted'
 (out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False),flush=True);b.close()
