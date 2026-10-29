"""Actual backend rendering/framing, fixed-angle cost and repeated mode reuse."""
from pathlib import Path
import os,json,subprocess
from urllib.parse import urlsplit
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/os.environ.get('LINGYUAN_COMBAT_REPORT_DIR','verification/combat');out.mkdir(parents=True,exist_ok=True);result={}
old={p:subprocess.check_output(['git','show',os.environ.get('LINGYUAN_BASELINE','499215e')+':dist/skill/'+p],cwd=R) for p in ['index.html','app.js','style.css']}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for label,query in [('before','?renderer=webgl2'),('practice','?renderer=webgl2'),('duel-webgl2','?renderer=webgl2'),('duel-webgpu','')]:
  page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  if label=='before':
   def route(r):
    path=urlsplit(r.request.url).path;name='index.html' if path=='/skill/' else path.removeprefix('/skill/');r.fulfill(body=old[name],content_type={'index.html':'text/html','app.js':'text/javascript','style.css':'text/css'}[name]) if name in old else r.continue_()
   page.route('**/*',route)
  page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true);window.__lingQA.reset();window.__lingQA.view("angle")')
  def frame():
   f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f)
  if label.startswith('duel'):
   page.locator('#combat-mode').click();page.wait_for_function('window.__lingQA.inspect().combat.mode==="duel"');page.evaluate('window.__combatQA.ai(false);window.__lingQA.advance(1.8)');framing=page.evaluate('window.__combatQA.framing()');assert all(abs(u['ndc'][0])<.9 and abs(u['ndc'][1])<.9 and -1<u['ndc'][2]<1 for u in framing),framing
  else:framing=None
  if label in ('before','practice'):
   # Include the actual target rather than measuring an off-camera object.
   page.mouse.move(500,350);page.mouse.wheel(0,900);page.evaluate('window.__lingQA.blink(0)')
  frame();page.screenshot(path=str(out/(label+'.png')));s=page.evaluate('window.__lingQA.inspect()');row={k:s[k] for k in ['renderer','software','drawCalls','triangles','cameraPosition','cameraTarget']};row['framing']=framing
  if label=='duel-webgl2':
   waves=[]
   for wave in range(4):
    page.locator('#combat-mode').click();frame();ended=page.evaluate('window.__lingQA.resources()');assert not page.evaluate('window.__lingQA.inspect().opponent.visible');page.locator('#combat-mode').click();page.evaluate('window.__lingQA.advance(.2)');frame();active=page.evaluate('window.__lingQA.resources()');assert page.evaluate('window.__lingQA.inspect().opponent.cachedActors')<=2;waves.append({'active':active,'practice':ended})
   assert waves[-1]['practice']['memory']==waves[-2]['practice']['memory'];row['modeReuseWaves']=waves
   # Verify preserved spear-tip synchronization through the shared choreography.
   page.locator('#combat-mode').click();page.locator('#cast').click();samples=[]
   previous=0
   for t in [.6,1,1.3]:
    page.evaluate('t=>window.__lingQA.advance(t)',t-previous);previous=t;ss=page.evaluate('window.__lingQA.inspect()');import math
    distance=math.dist(ss['spearTipWorld'],ss['firstDragonWorld']);assert distance<.02,(t,distance);samples.append({'requestedTime':t,'actualTime':ss['time'],'distance':distance})
   row['spearSync']=samples
   page.evaluate('window.__lingQA.instanceSeek(.6)');seek=page.evaluate('window.__lingQA.inspect()');assert math.dist(seek['spearTipWorld'],seek['firstDragonWorld'])<.02;row['pausedSeekUsesCurrentPoseAnchor']=True
  if label=='duel-webgpu':
   page.evaluate('window.__combatQA.position("opponent",2.0,0)');page.locator('#basic-attack').click();page.evaluate('window.__lingQA.advance(.6)');page.locator('#cast2').click();page.evaluate('window.__lingQA.advance(1.8)');frame();ss=page.evaluate('window.__lingQA.inspect()');assert any(e['kind']=='lingyuan-basic' for e in ss['combat']['events']) and any(e['kind']=='lingyuan-2' for e in ss['combat']['events']);page.screenshot(path=str(out/'webgpu-basic-and-skill-hit.png'));row['basicAndSkillSettleDamage']=True
  assert not errors and not page.evaluate('window.__lingSkill.errors');row['errors']=errors;result[label]=row;print('PASS_RENDER',label,flush=True);page.close()
 b.close()
(out/'rendering.json').write_text(json.dumps({'scope':'actual desktop software WebGPU/WebGL2; draw/allocation counts only, not phone FPS, heap/VRAM or long-term leak proof','cases':result},indent=2))
