"""Runtime geometry/timeline inspection of the Moon Frost visual study."""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/moon-frost';out.mkdir(parents=True,exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2',wait_until='domcontentloaded');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 page.locator('#panel-toggle').click();page.locator('#open-characters').click();page.locator('[data-character="yueli"]').click();page.wait_for_function("window.__lingSkill.character==='yueli' && !window.__lingSkill.characterLoading",timeout=90000)
 page.locator('#cast-yueli').click();page.wait_for_function('window.__lingSkill.moonVisible',timeout=30000)
 samples={}
 for t in (.5,1.7,2.8,4.4):
  page.evaluate("t=>{let s=document.getElementById('seek');s.value=String(t);s.dispatchEvent(new Event('input',{bubbles:true}))}",t)
  samples[str(t)]=page.evaluate('({visible:window.__lingSkill.moonVisible,...window.__lingSkill.moonSample})')
 assert samples['0.5']['visible'] and samples['1.7']['crescentX']>samples['0.5']['crescentX']+.3
 assert samples['2.8']['lotusScale']>.5 and not samples['4.4']['visible']
 page.evaluate("()=>{let s=document.getElementById('seek');s.value='2.8';s.dispatchEvent(new Event('input',{bubbles:true}))}")
 for view in ('front','side','back','top','angle'):
  previous=page.evaluate('window.__lingSkill.frames');page.evaluate("v=>document.querySelector('[data-view='+v+']').click()",view)
  page.wait_for_function('n=>window.__lingSkill.frames>n',arg=previous,timeout=30000)
  page.screenshot(path=str(out/(view+'.png')))
 assert not errors,errors
 result={'status':'PASS_RUNTIME_STRUCTURE_ONLY','scope':'desktop software WebGL2; visual timeline only; artistic quality and real phone unaccepted','samples':samples,'errors':errors}
 (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS',json.dumps(result,ensure_ascii=False),flush=True);b.close()
