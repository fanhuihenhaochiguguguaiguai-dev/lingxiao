from pathlib import Path
import json,math,sys
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
stage=sys.argv[1] if len(sys.argv)>1 else 'after';assert stage in ('before','after','webgpu')
out=Path(__file__).resolve().parents[1]/'verification/motion';out.mkdir(exist_ok=True)
result={'stage':stage,'samples':[],'errors':[]}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});page.on('pageerror',lambda e:result['errors'].append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/'+('' if stage=='webgpu' else '?renderer=webgl2'));page.wait_for_function('window.__lingSkill && window.__lingSkill.ready',timeout=90000);result['backend']=page.evaluate('window.__lingSkill.renderer');assert result['backend']==('WebGPU' if stage=='webgpu' else 'WebGL2');page.locator('#cast2').click()
 for threshold in [.8,1.5,2.2,2.9,3.6,4.3,5.0]:
  page.wait_for_function('(v)=>window.__lingSkill.time>=v',arg=threshold,timeout=30000);s=page.evaluate('window.__lingSkill');x,y,z=s['dragonWorld'];result['samples'].append({'time':s['time'],'x':x,'y':y,'z':z,'angle':math.atan2(z,x),'visible':s['dragonVisible'],'playing':s['playing']})
 page.locator('#pause').click();s=page.evaluate('window.__lingSkill');start=s['time'];page.wait_for_timeout(1000);assert abs(page.evaluate('window.__lingSkill.time')-start)<.001
 angles=[s['angle'] for s in result['samples']];travel=sum(math.remainder(b-a,2*math.pi) for a,b in zip(angles,angles[1:]));result['turns_observed']=travel/(2*math.pi)
 assert all(s['visible'] and s['playing'] for s in result['samples']) and not result['errors'],result
 if stage in ('after','webgpu'):
  assert result['turns_observed']>.95, result
 if stage=='after':
  page.locator('[data-view=top]').click()
  for t in [1.3,3.1]:
   page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(1200);page.screenshot(path=str(out/f'after-{t}.png'))
 (out/(stage+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False),flush=True);b.close()
