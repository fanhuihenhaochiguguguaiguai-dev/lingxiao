import sys,time,json
sys.path.insert(0,'/workspace/sites/henan-campus-lab/tools')
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
root='/workspace/sites/lingyuan-character-lab'
with display() as env:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
  page=browser.new_page(viewport={'width':1280,'height':800},device_scale_factor=1)
  page.goto('http://127.0.0.1:8765/',wait_until='domcontentloaded',timeout=30000)
  page.wait_for_function('window.__lingyuan?.ready || window.__lingyuan?.errors?.length',timeout=90000)
  time.sleep(4)
  print('INITIAL',json.dumps(page.evaluate('window.__lingyuan'),ensure_ascii=False))
  page.screenshot(path=root+'/verification/browser-front.png')
  page.locator('[data-view="back"]').click();time.sleep(2);page.screenshot(path=root+'/verification/browser-back.png')
  page.locator('#motion').select_option('walk');time.sleep(2);a=page.evaluate('window.__lingBone()');time.sleep(.4);b=page.evaluate('window.__lingBone()');print('WALK',json.dumps({'state':page.evaluate('window.__lingyuan'),'bone_a':a,'bone_b':b,'bone_changed':a!=b},ensure_ascii=False))
  page.locator('#lod').select_option('2');time.sleep(2);print('LOD2',json.dumps(page.evaluate('window.__lingyuan'),ensure_ascii=False))
  page.locator('#gray').click();time.sleep(1);page.screenshot(path=root+'/verification/browser-gray.png')
  page.goto('http://127.0.0.1:8765/?renderer=webgl2',wait_until='domcontentloaded');page.wait_for_function('window.__lingyuan?.ready || window.__lingyuan?.errors?.length',timeout=90000);time.sleep(2);print('WEBGL',json.dumps(page.evaluate('window.__lingyuan'),ensure_ascii=False))
  mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True);mobile.goto('http://127.0.0.1:8765/?renderer=webgl2',wait_until='domcontentloaded');mobile.wait_for_function('window.__lingyuan?.ready || window.__lingyuan?.errors?.length',timeout=90000);time.sleep(2);mobile.screenshot(path=root+'/verification/browser-mobile.png');print('MOBILE_LAYOUT',json.dumps(mobile.evaluate('window.__lingyuan'),ensure_ascii=False));browser.close()
