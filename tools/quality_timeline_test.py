from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/quality';record={'tests':[],'errors':[]}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720});page.on('pageerror',lambda e:record['errors'].append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000)
 for button,skill,times in [('cast',1,[.2,.7,1.3,2.45,3.45,4.35]),('cast2',2,[.2,.9,1.8,3.8,5.5,6.3]),('cast3',3,[.2,1.3,3,4.65,5.15,6.9])]:
  page.locator('#'+button).click();page.locator('#pause').click();poses=[]
  for t in times:
   page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(450);s=page.evaluate('window.__lingSkill');assert s['skill']==skill and not s['errors'];poses.append({'time':t,'stage':s['stage'],'dragonVisible':s['dragonVisible'],'bone':s['boneSample'],'drawCalls':s['drawCalls']})
  assert len({p['stage'] for p in poses})>=4 and len({round(p['bone'],5) for p in poses})>=3
  record['tests'].append({'skill':skill,'samples':poses,'status':'PASS'})
 assert not record['errors'];record['status']='PASS_TIMELINE_SAMPLES_ONLY';(out/'timeline.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({'status':record['status'],'skills':len(record['tests']),'errors':record['errors']},ensure_ascii=False));b.close()
