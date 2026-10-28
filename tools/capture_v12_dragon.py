from pathlib import Path
import sys
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/v12';stage=sys.argv[1];assert stage in ('before','after')
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);page.locator('#cast2').click();page.locator('#panel-toggle').click();page.locator('#pause').click();page.locator('#seek').evaluate('(e)=>{e.value="3.8";e.dispatchEvent(new Event("input",{bubbles:true}))}');page.locator('[data-view=side]').click();page.locator('[data-follow=dragon]').click();page.locator('#panel-toggle').click();page.wait_for_timeout(6500);page.mouse.move(550,350);page.mouse.wheel(0,-900);page.wait_for_timeout(2800);page.screenshot(path=str(out/f'dragon-{stage}.png'));assert not page.evaluate('window.__lingSkill.errors');print('captured',stage,flush=True);b.close()
