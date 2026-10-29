from pathlib import Path
import json,sys,os
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
label=sys.argv[1];assert label in ('before','after');out=Path(__file__).resolve().parents[1]/'verification/promotion/web';out.mkdir(parents=True,exist_ok=True);rows=json.loads((out/f'{label}.json').read_text()) if (out/f'{label}.json').exists() else {}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)')
 for case,button,t in [('binding','#cast2',3.3),('sovereign','#cast3',3.2),('ice-orbit','#cast-yueli3',2.4),('ice-dive','#cast-yueli3',4.15)]:
  if os.environ.get('PROMOTION_CASE') and os.environ['PROMOTION_CASE']!=case:continue
  page.evaluate('window.__lingQA.reset()')
  if case.startswith('ice') and page.evaluate('window.__lingSkill.character')!='yueli':page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading')
  page.locator(button).click();page.evaluate('t=>window.__lingQA.instanceSeek(t)',t)
  for view in ['side','angle','top']:
   page.evaluate('v=>window.__lingQA.view(v)',view);f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/f'{label}-{case}-{view}.png'))
  s=page.evaluate('window.__lingQA.inspect()');rows[case]={'cameraTarget':s['cameraTarget'],'cameraPosition':s['cameraPosition'],'drawCalls':s['drawCalls'],'triangles':s['triangles'],'renderer':s['renderer'],'errors':errors.copy()};assert not errors and not s['errors'];print('CAPTURED',label,case,flush=True)
  if label=='after':
   page.evaluate('window.__lingQA.currentDragonClose()');f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/f'{label}-{case}-close.png'))
 if label=='after' and (not os.environ.get('PROMOTION_CASE') or os.environ['PROMOTION_CASE'].startswith('ice')):
  page.evaluate('window.__lingQA.instanceSeek(4.5);window.__lingQA.currentDragonClose()');f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/'after-ice-return-close.png'))
 b.close()
(out/f'{label}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
