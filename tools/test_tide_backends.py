from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/moon-tide';results={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for label,query,count in [('webgl2-unbatched','?renderer=webgl2&qa-unbatched=1',10),('webgl2-batched','?renderer=webgl2',10),('default-backend','',1)]:
  page=b.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.echoReady',timeout=120000);page.evaluate('window.__lingQA.freeze(true)');page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading',timeout=90000)
  page.evaluate('n=>{for(let i=0;i<n;i++)document.getElementById("cast-yueli2").click();window.__lingQA.advance(2.8);window.__lingQA.view("angle")}',count);frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('n=>window.__lingSkill.frames>n',arg=frame,timeout=120000);page.screenshot(path=str(out/(label+'.png')));s=page.evaluate('window.__lingQA.inspect()');assert not errors and not s['errors'],(errors,s['errors']);assert s['instances']['activeCount']==count and s['tideVisible'];results[label]={k:s[k] for k in ['renderer','software','drawCalls','triangles','quality','tideSample']};results[label]['instances']=count;page.close();print('PASS',label,flush=True)
 b.close()
assert results['webgl2-batched']['drawCalls']<results['webgl2-unbatched']['drawCalls']*.7,results
(out/'backends.json').write_text(json.dumps({'scope':'same 1100x700 camera, quality and 2.8s simulation time; software GPU only; draw counts are not phone frame-rate results','checks':results},ensure_ascii=False,indent=2))
