import sys,json,os
from pathlib import Path
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=str(Path(os.environ.get('LING_TEST_OUT',Path(__file__).resolve().parents[1]/'verification')));Path(out).mkdir(parents=True,exist_ok=True)
with display() as env:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');results={}
  for name,query in [('webgpu',''),('webgpu_bloom','?bloom=1'),('webgl_bloom','?renderer=webgl2&bloom=1'),('webgl_auto','')]:
   page=b.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   if name=='webgl_auto':page.add_init_script("Object.defineProperty(navigator, 'gpu', {value: undefined})")
   page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000)
   page.locator('#cast3').click();page.locator('#pause').click();page.locator('#seek').evaluate('(e)=>{e.value="3";e.dispatchEvent(new Event("input",{bubbles:true}))}');page.wait_for_function('window.__lingSkill.frames>2 || window.__lingSkill.errors.length',timeout=90000);page.wait_for_timeout(1200)
   s=page.evaluate('window.__lingSkill');results[name]=s;page.screenshot(path=f'{out}/skill03-{name}.png');assert s['ready'] and not s['errors'] and not errors and s['dragonVisible'] and s['starVisible'] and not any(s['layerRendered'].values()),(name,s,errors)
   assert s['renderer']==('WebGPU' if name.startswith('webgpu') else 'WebGL2')
   if name.endswith('bloom'):assert s['bloom'] and not s['bloomError'],s
   page.close()
  open(out+'/skill03-backends.json','w').write(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps({k:{'backend':v['renderer'],'software':v['software'],'bloom':v['bloom'],'fps':v['fps'],'errors':v['errors']} for k,v in results.items()},ensure_ascii=False),flush=True);b.close()
