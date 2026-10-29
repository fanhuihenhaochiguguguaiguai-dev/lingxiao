from pathlib import Path
from urllib.parse import urlsplit
import json,subprocess
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v37';old={n:subprocess.check_output(['git','show','499215e:dist/skill/'+n],cwd=R) for n in ['index.html','app.js','style.css']};data={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for label in ['before','after']:
  page=b.new_page(viewport={'width':844,'height':390},device_scale_factor=1);page.set_default_timeout(180000)
  if label=='before':
   def route(r):
    path=urlsplit(r.request.url).path;n='index.html' if path=='/skill/' else path.removeprefix('/skill/');r.fulfill(body=old[n],content_type={'index.html':'text/html','app.js':'text/javascript','style.css':'text/css'}[n]) if n in old else r.continue_()
   page.route('**/*',route)
  page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready');page.evaluate('window.__lingQA.freeze(true);window.__lingQA.reset();window.__lingQA.blink(0)');f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/(label+'-hud.png')));s=page.evaluate('window.__lingQA.inspect()');data[label]={k:s[k] for k in ['cameraPosition','cameraTarget','stagePosition','quality','renderer','software','drawCalls','triangles']};data[label]['viewport']=[844,390];data[label]['DPR']=1;assert not s['errors'];page.close()
 b.close()
for field in ['cameraPosition','cameraTarget','stagePosition','viewport','DPR','quality','renderer']:assert data['before'][field]==data['after'][field],field
(out/'hud-comparison.json').write_text(json.dumps({'scope':'actual old/new browser render, same camera/pose/light/assets/viewport/DPR','baseline':'499215e','cases':data},indent=2));print('PASS_FIXED_HUD_COMPARISON',flush=True)
