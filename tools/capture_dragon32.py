"""Same site, frozen skill time, fixed inspection camera. Software render only."""
from pathlib import Path
import json,os
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/dragon32/web';out.mkdir(parents=True,exist_ok=True);results=json.loads((out/'comparison.json').read_text()) if (out/'comparison.json').exists() else {}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for label,query in [('before','?renderer=webgl2&dragon=legacy'),('after','?renderer=webgl2')]:
  if os.environ.get('DRAGON32_ONLY') and os.environ['DRAGON32_ONLY']!=label:continue
  page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true);window.__lingQA.reset()');page.locator('#cast').click();page.evaluate('window.__lingQA.instanceSeek(1.45)')
  for view in ['side','front','back','angle','top','close']:
   page.evaluate('v=>window.__lingQA.dragonView(v)',view);f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/f'{label}-{view}.png'))
   if view=='side':results[label]={'state':page.evaluate('window.__lingQA.inspect()'),'sample':page.evaluate('window.__lingQA.dragonSample()'),'errors':errors}
  assert not errors and not page.evaluate('window.__lingSkill.errors');page.close();print('CAPTURED',label,flush=True)
 b.close()
(out/'comparison.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
