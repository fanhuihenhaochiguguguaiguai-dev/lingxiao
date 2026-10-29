"""Candidate-only changed head: loading, real blink frame and locomotion/switch smoke."""
from pathlib import Path
import json,subprocess
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v35/runtime';out.mkdir(parents=True,exist_ok=True);result={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for backend,query in [('webgl2','?renderer=webgl2&sample=lingyuan31-head'),('webgpu','?sample=lingyuan31-head')]:
  page=b.new_page(viewport={'width':1000,'height':680});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true);window.__lingQA.reset();window.__lingQA.neutral();window.__lingQA.blink(0);window.__lingQA.view("face")')
  def frame():
   f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f)
  frame();page.screenshot(path=str(out/f'{backend}-head-open.png'));s=page.evaluate('window.__lingQA.inspect()')
  page.evaluate('window.__lingQA.blink(1)');frame();page.screenshot(path=str(out/f'{backend}-head-closed.png'));morphs=page.evaluate('window.__lingQA.morphState().filter(m=>m.key==="Blink")');assert morphs and all(m['weight']==1 for m in morphs)
  inventory=page.evaluate('window.__lingQA.modelInventory()');assert {m['owner'] for m in inventory if 'Hair_Lod' in m['owner']}=={'Hair_Lod1'}
  page.evaluate('window.__lingQA.blink(null)');page.keyboard.down('w');page.evaluate('window.__lingQA.advance(.6)');walk=page.evaluate('window.__lingQA.inspect().speed');page.keyboard.down('Shift');page.evaluate('window.__lingQA.advance(.8)');run=page.evaluate('window.__lingQA.inspect().speed');page.keyboard.press('Space');page.evaluate('window.__lingQA.advance(.15)');assert page.evaluate('window.__lingQA.inspect().jumpHeight')>0 and run>walk>0;page.keyboard.up('w');page.keyboard.up('Shift');page.evaluate('window.__lingQA.advance(2);window.__lingQA.reset()')
  for character in ['yueli','lingyuan']:
   page.locator('#open-characters').click();page.locator('[data-character='+character+']').click();page.wait_for_function('c=>window.__lingSkill.character===c&&!window.__lingSkill.characterLoading',arg=character)
  assert not errors and not page.evaluate('window.__lingSkill.errors');result[backend]={'renderer':s['renderer'],'software':s['software'],'drawCalls':s['drawCalls'],'triangles':s['triangles'],'bones':len(s['boneNames']),'blinkTargets':morphs,'walkSpeed':walk,'runSpeed':run,'jumpAndSwitchSmoke':True,'artAccepted':False,'errors':errors};print('PASS_HEAD35',backend,flush=True);page.close()
 b.close()
(out/'head.json').write_text(json.dumps(result,indent=2))
