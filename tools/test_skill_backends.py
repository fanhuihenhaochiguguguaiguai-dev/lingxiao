import sys,json
sys.path.insert(0,'/workspace/sites/henan-campus-lab/tools')
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out='/workspace/sites/lingyuan-character-lab/verification'
with display() as env:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');results={}
  for name,query in [('webgpu',''),('webgpu_bloom','?bloom=1'),('webgl_bloom','?renderer=webgl2&bloom=1'),('webgl_auto','')]:
   page=b.new_page(viewport={'width':1100,'height':700});
   if name=='webgl_auto':page.add_init_script("Object.defineProperty(navigator, 'gpu', {value: undefined})")
   page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000);page.wait_for_function('window.__lingSkill.frames>1 || window.__lingSkill.errors.length',timeout=90000);page.locator('#seek').evaluate('(el)=>{el.value="2.4";el.dispatchEvent(new Event("input",{bubbles:true}))}');page.wait_for_timeout(1500);s=page.evaluate('window.__lingSkill');results[name]=s;page.screenshot(path=f'{out}/skill-{name}.png');assert s['ready'] and not s['errors'] and s['dragonVisible'];assert s['renderer']==('WebGPU' if name.startswith('webgpu') else 'WebGL2');
   if name.endswith('bloom'):assert s['bloom'] and not s['bloomError'],s
   page.close()
  print(json.dumps(results,ensure_ascii=False),flush=True);b.close()
