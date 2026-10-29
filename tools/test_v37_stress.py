from pathlib import Path
from urllib.parse import urlsplit
import json,subprocess
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v37';old={n:subprocess.check_output(['git','show','499215e:dist/skill/'+n],cwd=R) for n in ['index.html','app.js','style.css']};result={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for label in ['before','after']:
  page=b.new_page(viewport={'width':960,'height':540});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  if label=='before':
   def route(r):
    path=urlsplit(r.request.url).path;n='index.html' if path=='/skill/' else path.removeprefix('/skill/');r.fulfill(body=old[n],content_type={'index.html':'text/html','app.js':'text/javascript','style.css':'text/css'}[n]) if n in old else r.continue_()
   page.route('**/*',route)
  page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready');page.evaluate('window.__lingQA.freeze(true);window.__lingQA.reset();window.__lingQA.view("top");for(let i=0;i<3;i++)window.__lingQA.targetPosition(i,60+i*2,.6,60);for(let i=0;i<10;i++)document.getElementById("cast2").click();window.__lingQA.advance(2.2)');state=page.evaluate('window.__lingQA.inspect()');n=state['frames'];page.wait_for_function('n=>window.__lingSkill.frames>n',arg=n);state=page.evaluate('window.__lingQA.inspect()');cost=page.evaluate('()=>{const t=performance.now();window.__lingQA.advance(.25);return performance.now()-t}');row={k:state[k] for k in ['drawCalls','triangles','software','renderer']};row['instances']=state['instances']['activeCount'];row['quarterGameSecondCpuMs']=cost;assert row['instances']==10;page.evaluate('window.__lingQA.advance(8)');end=page.evaluate('window.__lingQA.inspect()');assert end['instances']['activeCount']==0 and end['instances']['pooled']<=2;row['afterRelease']=end['instances']|{'active':[],'history':[]};assert not errors and not end['errors'];result[label]=row;print('PASS_TEN_FIELDS',label,row['drawCalls'],row['triangles'],cost,flush=True);page.close()
 b.close()
(out/'stress.json').write_text(json.dumps({'scope':'desktop software WebGL2; fixed camera; CPU synthetic simulation cost is not frame time, GPU time or phone FPS','cases':result,'drawCallDelta':result['after']['drawCalls']-result['before']['drawCalls'],'triangleDelta':result['after']['triangles']-result['before']['triangles']},indent=2))
