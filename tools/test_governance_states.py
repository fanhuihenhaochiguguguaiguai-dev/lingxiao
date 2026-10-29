"""Real page state regressions. Background visibility is simulated, no phone claim."""
from pathlib import Path
import json,os
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/governance';out.mkdir(exist_ok=True)
label=os.environ.get('GOVERNANCE_PASS','before')
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(90000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)')
 page.locator('#cast3').click();page.evaluate('window.__lingQA.advance(.8);window.__lingQA.pause()');page.wait_for_timeout(200);start=page.evaluate('window.__lingQA.audioClock()');age=page.evaluate('window.__lingSkill.instances.active[0].age');page.wait_for_timeout(500);page.evaluate('window.__lingQA.advance(.5)');end=page.evaluate('window.__lingQA.audioClock()');age_end=page.evaluate('window.__lingSkill.instances.active[0].age')
 paused={'audioState':end['state'],'audioClockDelta':end['time']-start['time'],'simulationAgeDelta':age_end-age}
 page.locator('#cast').click();page.evaluate('window.__lingQA.advance(.2)');cast_resume={'paused':page.evaluate('window.__lingQA.isPaused()'),'latestAge':page.evaluate('window.__lingSkill.instances.active.at(-1).age')}
 page.evaluate('window.__lingQA.reset()');page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading');page.locator('#cast-yueli2').click();page.evaluate('window.__lingQA.advance(1.2)');during=page.evaluate('window.__lingQA.bonePose("handR")');page.evaluate('window.__lingQA.reset();window.__lingQA.advance(.6)');after=page.evaluate('window.__lingQA.bonePose("handR")')
 page.evaluate('window.__lingQA.view("front")');frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=frame);page.screenshot(path=str(out/f'{label}-idle.png'))
 assert not errors,errors
 result={'scope':'actual desktop software WebGL2; pause and hand-state checks, not artistic or phone acceptance','pause':paused,'castFromPaused':cast_resume,'handDuring':during,'handAfterCancel':after,'errors':errors}
 (out/f'{label}-states.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));b.close();print(json.dumps(result),flush=True)
 if label=='after':
  assert paused['audioState']=='suspended' and paused['audioClockDelta']<.03 and paused['simulationAgeDelta']==0
  assert not cast_resume['paused'] and cast_resume['latestAge']>.15
  assert after['error']<1e-6
