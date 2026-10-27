from pathlib import Path
import json,math,sys
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
stage=sys.argv[1];assert stage in ('before','after');out=Path(__file__).resolve().parents[1]/'verification/spear-sync';out.mkdir(exist_ok=True);report={'stage':stage,'samples':[],'errors':[]}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1280,'height':720});page.on('pageerror',lambda e:report['errors'].append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000);assert page.evaluate('window.__lingSkill.ready && window.__lingSkill.spearTipValid'),page.evaluate('window.__lingSkill')
 page.locator('#cast').click();page.locator('#pause').click()
 for t in [.6,1.0,1.3,1.65,2.2]:
  page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(800);s=page.evaluate('window.__lingSkill');d=math.dist(s['spearTipWorld'],s['firstDragonWorld']);report['samples'].append({'time':t,'distance':d,'tip':s['spearTipWorld'],'head':s['firstDragonWorld']});assert not s['errors']
  if t==1.0:page.screenshot(path=str(out/(stage+'-dash.png')))
 if stage=='after':assert all(row['distance']<.02 for row in report['samples'] if row['time']<=1.3),report
 assert not report['errors'];report['status']='PASS';(out/(stage+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True);b.close()
