from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/v12'
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.route('**/audio/spell_01.ogg',lambda route:route.abort());page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);page.wait_for_function("window.__lingSkill.audioStatus.includes('音频加载失败')",timeout=30000);assert page.locator('#audio-alert').is_visible();page.locator('#panel-toggle').click();assert '音效不可用' in page.locator('#audio-status').inner_text();page.screenshot(path=str(out/'audio-failure.png'));(out/'audio-failure.json').write_text(json.dumps({'status':'PASS_INJECTED_LOAD_FAILURE','global_visible':True,'detail_visible':True,'scope':'desktop software browser, intentionally blocked audio request'},indent=2));print('PASS visible feedback for failed audio request',flush=True);b.close()
