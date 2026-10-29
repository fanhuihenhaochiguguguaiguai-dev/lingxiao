"""P0–P2 gate in the real site. Synthetic input/clock, actual game state/rendering."""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/combat';out.mkdir(parents=True,exist_ok=True);results={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready&&window.__lingSkill.instanceAudio?.basicReady');page.evaluate('window.__lingQA.freeze(true)')
 def snap():return page.evaluate('window.__lingQA.inspect()')
 def frame(name):
  f=snap()['frames'];page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/(name+'.png')))
 for character in ['lingyuan','yueli']:
  if character=='yueli':page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading')
  page.evaluate('window.__lingQA.reset();window.__lingQA.targetPosition(0,2.4,.6,0)');page.locator('#basic-attack').click();page.evaluate('window.__lingQA.advance(.12)');assert not snap()['combat']['events'];page.evaluate('window.__lingQA.advance(.55)');s=snap();events=s['combat']['events'];assert len(events)==1 and events[0]['damage']==(88 if character=='lingyuan' else 66);assert len([e for e in s['instanceAudio']['events'] if e['kind']==character+'-basic' and e['phase']=='hit'])>=1
  # Interval rejects repeated clicks, then the same attack continues freely moving.
  page.evaluate('for(let i=0;i<10;i++)document.getElementById("basic-attack").click()');assert len(snap()['basic']['events'])==3
  frame(character+'-basic-hit');page.evaluate('window.__lingQA.advance(.5)');page.keyboard.down('w');page.keyboard.down('Shift');page.locator('#basic-attack').click();page.evaluate('window.__lingQA.advance(.45)');moving=snap();page.keyboard.up('w');page.keyboard.up('Shift');assert moving['speed']>.2 and moving['position']!=[0,0,0]
  page.evaluate('window.__lingQA.reset();window.__lingQA.targetPosition(0,2.4,.6,0)');count=35 if character=='lingyuan' else 46
  page.evaluate('n=>{for(let i=0;i<n;i++){document.getElementById("basic-attack").click();window.__lingQA.advance(1.05)}}',count);dead=snap();target=next(u for u in dead['combat']['units'] if u['id']=='target-0');assert target['hp']==0 and not target['alive'];damage=[e for e in dead['combat']['events'] if e['target']=='target-0'];assert sum(e['damage'] for e in damage)==3000 and sum(e['killed'] for e in damage)==1
  frame(character+'-target-dead');page.locator('#combat-reset').click();reset=snap();assert next(u for u in reset['combat']['units'] if u['id']=='target-0')['hp']==3000 and reset['instances']['activeCount']==0 and reset['basic']['active']==0
  results[character]={'windupNoDamage':True,'singleDamage':events[0],'rapidClicksRespectInterval':True,'movingBasic':True,'attacksToDestroy':len(damage),'deathOnceAndNoOverkill':True,'reset':True}
 assert not errors and not snap()['errors'];results['errors']=errors;b.close()
(out/'practice.json').write_text(json.dumps({'scope':'real Chromium WebGL2, synthetic input and simulated clock; not hardware latency or art acceptance','results':results},ensure_ascii=False,indent=2));print('PASS_P0_P2_PRACTICE_GATE',flush=True)
