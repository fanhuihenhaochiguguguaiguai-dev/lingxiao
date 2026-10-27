import sys,json,time
sys.path.insert(0,'/workspace/sites/henan-campus-lab/tools')
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
url='http://127.0.0.1:8765/'
def wait_state(p):p.wait_for_function('window.__lingyuan && (window.__lingyuan.ready || window.__lingyuan.errors.length)',timeout=90000);return p.evaluate('window.__lingyuan')
with display() as env:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');res={}
  page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);page.goto(url+'?renderer=webgl2');res['mobile_webgl']=wait_state(page);assert res['mobile_webgl']['ready'] and not res['mobile_webgl']['errors'] and res['mobile_webgl']['lod']==1
  page.wait_for_function('window.__lingyuan.frames>0',timeout=45000);page.screenshot(path='/workspace/sites/lingyuan-character-lab/verification/mobile-loading-fixed.png');page.close()
  page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);page.route('**/lingyuan-lod1.glb',lambda route:route.abort());page.goto(url+'?renderer=webgl2');res['lod_fallback']=wait_state(page);assert res['lod_fallback']['ready'] and res['lod_fallback']['lod']==2 and not res['lod_fallback']['errors'];page.close()
  page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);page.route('**/lingyuan-lod*.glb',lambda route:route.abort());page.goto(url+'?renderer=webgl2');res['all_models_blocked']=wait_state(page);assert not res['all_models_blocked']['ready'] and res['all_models_blocked']['errors'];assert page.locator('#load-help').is_visible() and page.locator('#load-compat').is_visible();page.close()
  stub='export class Vec3 { constructor(){} } export class Color { constructor(){} } export class StandardMaterial { update(){} } export const DEVICETYPE_WEBGPU="webgpu", DEVICETYPE_WEBGL2="webgl2"; export function createGraphicsDevice(){return Promise.reject(new Error("forced graphics failure"))}'
  page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);page.route('**/engine/playcanvas.min.mjs',lambda route:route.fulfill(status=200,content_type='text/javascript',body=stub));page.goto(url);page.wait_for_url('**/?renderer=webgl2',timeout=20000);res['graphics_fallback']=wait_state(page);assert not res['graphics_fallback']['ready'] and res['graphics_fallback']['errors'] and page.locator('#load-compat').is_visible();page.close()
  page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);page.clock.install();page.route('**/viewer.js*',lambda route:route.abort());page.goto(url);page.clock.fast_forward(16000);assert page.locator('#load-help').is_visible() and page.locator('#load-compat').is_visible();res['module_failure_help']='PASS';page.close()
  print(json.dumps(res,ensure_ascii=False),flush=True);b.close()
