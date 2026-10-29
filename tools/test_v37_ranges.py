"""Actual rendered effects drive combat; staged browser clock/input are explicit."""
from pathlib import Path
import json,math
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v37';out.mkdir(exist_ok=True);checks={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':844,'height':390});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)')
 def state():return page.evaluate('window.__lingQA.inspect()')
 def advance(t):page.evaluate('t=>window.__lingQA.advance(t)',t)
 def target(pos):page.evaluate('p=>window.__lingQA.targetPosition(0,...p)',pos)
 def start(button):
  page.evaluate('window.__lingQA.reset();for(let i=0;i<3;i++)window.__lingQA.targetPosition(i,70+i*2,.6,70)');page.evaluate('s=>document.querySelector(s).click()',button)
 def volumes():
  s=state();return page.evaluate('id=>window.__combatQA.volumes(id)',s['instances']['active'][-1]['id'])
 def frame(file):
  n=state()['frames'];page.wait_for_function('n=>window.__lingSkill.frames>n',arg=n);page.screenshot(path=str(out/file))
 for character in ['lingyuan','yueli']:
  if character=='yueli':page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading')
  for slot in [1,2,3]:
   kind=f'{character}-{slot}';button=('#cast' if slot==1 else '#cast'+str(slot)) if character=='lingyuan' else '#cast-yueli'+('' if slot==1 else str(slot));start(button)
   age={'lingyuan-1':2.15,'lingyuan-2':4.1,'lingyuan-3':2.2,'yueli-1':2.8,'yueli-2':3,'yueli-3':6}[kind];advance(age);vs=volumes();assert vs and vs['volumes'],(kind,state()['errors']);assert len({v['id'] for v in vs['volumes']})==len(vs['volumes']),(kind,'duplicate region IDs')
   region={'lingyuan-1':'dragon:body:20','lingyuan-2':'binding-field','lingyuan-3':'vortex-core','yueli-1':'ice-lotus','yueli-2':'tide-field','yueli-3':'moonfall-domain'}[kind];v=next(v for v in vs['volumes'] if v['id']==region);pos=[v['a']['x'],v['a']['y'],v['a']['z']]
   if kind=='lingyuan-2':pos[2]+=2.8
   if kind=='yueli-1':pos=[4.1,.6,1]
   if kind in ['lingyuan-3','yueli-2','yueli-3']:pos[1]=.6
   target(pos);advance(.05);s=state();ev=s['combat']['events'];assert ev,(kind,v,pos,s['errors']);assert all(e['target']=='target-0' for e in ev);advance(.1);assert len(state()['combat']['events'])==len(ev),'overlapping volumes duplicated hit';checks[kind]={'regionAtProbe':v,'targetPosition':pos,'events':ev,'noOverlappingVolumeDoubleDamage':True};print('PASS_RENDERED_REGION',kind,ev[0].get('region'),flush=True)
   if kind=='yueli-1':frame('after-frost-lotus-hit.png')
   # Outside all current geometry, warning, and dissolve must remain harmless.
   start(button);target([60,.6,-60]);advance(12);assert not state()['combat']['events'];checks[kind]['farOutsideMiss']=True
   start(button);target([0,.6,0]);pre={'lingyuan-1':.90,'lingyuan-2':.95,'lingyuan-3':1.05,'yueli-1':.80,'yueli-2':1.40,'yueli-3':1.60}[kind];advance(pre);assert not state()['combat']['events'],(kind,'warning damage');checks[kind]['warningNoDamage']=True
   # Reposition a target only after all damaging parts ended; no lingering visual damage.
   start(button);end={'lingyuan-1':3.75,'lingyuan-2':5.55,'lingyuan-3':5.95,'yueli-1':3.4,'yueli-2':7.1,'yueli-3':9.5}[kind];advance(end);target(pos);advance(.4);assert not state()['combat']['events'],(kind,'dissolve damage');checks[kind]['dissolveNoDamage']=True
 # Original spear hit now follows the rendered weapon; projectile still sweeps.
 for char in ['lingyuan','yueli']:
  if state()['character']!=char:page.locator('#open-characters').click();page.locator('[data-character='+char+']').click();page.wait_for_function('c=>window.__lingSkill.character===c&&!window.__lingSkill.characterLoading',arg=char)
  page.evaluate('window.__lingQA.reset();window.__lingQA.targetPosition(0,2.0,.6,0);document.getElementById("basic-attack").click();window.__lingQA.advance(.5)');s=state();assert any(e['kind']==char+'-basic' for e in s['combat']['events']),(char,s['basic'],s['combat']);checks[char+'-basic']={'events':s['combat']['events'],'strikes':s['basic']['strikes']};print('PASS_BASIC',char,flush=True)
 assert not errors and not state()['errors'],(errors,state()['errors']);b.close()
(out/'ranges.json').write_text(json.dumps({'scope':'actual Chromium software WebGL2, staged QA input/clock; no real phone or final art claim','checks':checks,'errors':errors},ensure_ascii=False,indent=2));print('PASS_V37_RANGE_SAMPLE_GATE',flush=True)
