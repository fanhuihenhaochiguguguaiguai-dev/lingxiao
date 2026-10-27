from pathlib import Path
import json,hashlib
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/v4-dragon';out.mkdir(exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 page.locator('#cast2').click();page.locator('#pause').click();page.locator('#seek').evaluate('(e)=>{e.value="3.8";e.dispatchEvent(new Event("input",{bubbles:true}))}');page.wait_for_timeout(1200)
 canvas=page.locator('#scene');before=canvas.screenshot();page.mouse.move(500,350);page.mouse.down();page.mouse.move(720,400,steps=12);page.mouse.up();page.wait_for_timeout(1300);rotated=canvas.screenshot();page.mouse.wheel(0,-500);page.wait_for_timeout(1200);zoomed=canvas.screenshot()
 assert len({hashlib.sha256(x).hexdigest() for x in [before,rotated,zoomed]})==3
 mobile=b.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);mobile.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');mobile.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);mobile.locator('#cast2').click();mobile.locator('#pause').click();mobile.locator('[data-follow=dragon]').click();assert mobile.evaluate('window.__lingSkill.cameraMode')=='dragon';mobile.screenshot(path=str(out/'landscape-follow.png'))
 assert not errors and not mobile.evaluate('window.__lingSkill.errors')
 (out/'camera-controls.json').write_text(json.dumps({'status':'PASS_DESKTOP_SOFTWARE_AND_SIMULATED_LANDSCAPE_ONLY','mouse_orbit_changed_frame':True,'wheel_zoom_changed_frame':True,'simulated_touch_viewport':[844,390],'followButton':'dragon','errors':errors},indent=2));print('PASS desktop orbit, wheel and simulated landscape follow button',flush=True);b.close()
