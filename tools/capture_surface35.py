"""Identical page/cameras/light/time; baseline JS is served in-memory via routing."""
from pathlib import Path
import json,os,sys
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v35/web';out.mkdir(parents=True,exist_ok=True)
label=sys.argv[1];assert label in ('before','after');rows={}
cases=[('binding','#cast2',3.6,[2.95,.5,0],[1.7,.6,2.2]),('frost','#cast-yueli',2.8,[4.1,.5,0],[1.5,.8,2.4]),('tide','#cast-yueli2',3.5,[2.4,.40,0],[1.8,1,2.6]),('moonfall','#cast-yueli3',4.4,[1.5,.6,0],[2.4,1.4,3.2])]
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 if label=='before':page.route('**/app.js*',lambda r:r.fulfill(body=Path('/tmp/surface35-before-app.js').read_bytes(),content_type='text/javascript'))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)')
 for case,button,t,point,offset in cases:
  if os.environ.get('SURFACE35_CASE') and os.environ['SURFACE35_CASE']!=case:continue
  page.evaluate('window.__lingQA.reset()')
  if case!='binding' and page.evaluate('window.__lingSkill.character')!='yueli':
   page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading')
  page.locator(button).click();page.evaluate('t=>window.__lingQA.instanceSeek(t)',t);stats={}
  for view in ['angle','detail']:
   if view=='detail':page.evaluate('([p,o])=>window.__lingQA.effectDetail(p,o)',[point,offset])
   else:page.evaluate('window.__lingQA.view("angle")')
   f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/f'{label}-{case}-{view}.png'));s=page.evaluate('window.__lingQA.inspect()');stats[view]={k:s[k] for k in ['cameraTarget','cameraPosition','drawCalls','triangles']}
  rows[case]=stats;assert not errors and not s['errors'];print('SURFACE35_CAPTURED',label,case,flush=True)
 b.close()
(out/f'{label}.json').write_text(json.dumps({'cases':rows,'errors':errors,'scope':'fixed actual software WebGL2 frames, not phone data'},indent=2))
