import sys,time,json
sys.path.insert(0,'/workspace/sites/henan-campus-lab/tools')
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out='/workspace/sites/lingyuan-character-lab/verification'
with display() as env:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
  page=b.new_page(viewport={'width':1280,'height':800})
  page.goto('http://127.0.0.1:8765/?renderer=webgl2');page.wait_for_function('window.__lingyuan?.ready || window.__lingyuan?.errors?.length',timeout=90000);page.wait_for_timeout(1200)
  initial=page.evaluate('window.__lingyuan');page.keyboard.down('w');page.wait_for_timeout(1400);moving=page.evaluate('window.__lingyuan');page.keyboard.up('w');page.wait_for_timeout(600);stop=page.evaluate('window.__lingyuan')
  page.locator('#lod').select_option('2');page.wait_for_function('window.__lingyuan.lod === 2',timeout=30000);lod=page.evaluate('window.__lingyuan')
  page.locator('#reset-position').click();page.wait_for_function('Math.abs(window.__lingyuan.position.z)<0.001',timeout=15000);reset=page.evaluate('window.__lingyuan')
  mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);mobile.goto('http://127.0.0.1:8765/?renderer=webgl2');mobile.wait_for_function('window.__lingyuan?.ready || window.__lingyuan?.errors?.length',timeout=90000);mobile.wait_for_timeout(500)
  box=mobile.locator('#joystick').bounding_box();cx=box['x']+box['width']/2;cy=box['y']+box['height']/2
  cdp=mobile.context.new_cdp_session(mobile);cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':cx,'y':cy,'id':1}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':cx+20,'y':cy,'id':1}]});mobile.wait_for_function('window.__lingyuan.position.x > 0.02',timeout=15000);joy=mobile.evaluate('window.__lingyuan');cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});mobile.wait_for_timeout(400);mobile.screenshot(path=out+'/mobile-controls.png');page.screenshot(path=out+'/desktop-controls.png');page.locator('[data-view=face]').click();page.wait_for_timeout(800);page.screenshot(path=out+'/browser-face.png')
  print('DIAGNOSTIC',json.dumps({'initial':initial,'moving':moving,'stopped':stop,'lod':lod,'reset':reset,'joystick':joy},ensure_ascii=False),flush=True);assert initial['ready'] and not initial['errors'];assert moving['position']['z'] < -.02 and moving['animation']=='walk';assert stop['animation']=='idle';assert abs(lod['position']['z']-stop['position']['z'])<.001;assert abs(reset['position']['z'])<.001;assert joy['position']['x']>.02 and joy['animation']=='walk';print(json.dumps({'initial':initial,'moving':moving,'stopped':stop,'lod':lod,'reset':reset,'joystick':joy},ensure_ascii=False));b.close()
