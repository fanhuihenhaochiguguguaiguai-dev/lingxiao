"""All promoted dragons: actual rendered concurrent instances and allocation plateau."""
from pathlib import Path
import json,os
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'verification/promotion/runtime';out.mkdir(parents=True,exist_ok=True);result={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for backend,query in [('webgl2','?renderer=webgl2'),('webgpu','')]:
  page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)');rows={}
  for kind,button,t in [('binding','#cast2',3.3),('sovereign','#cast3',3.2),('lunar','#cast-yueli3',4.4)]:
   if os.environ.get('PROMOTION_FILTER') and os.environ['PROMOTION_FILTER']!=kind:continue
   if kind=='lunar':page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading')
   waves=[]
   for wave in range(3 if backend=='webgl2' else 1):
    page.evaluate('window.__lingQA.reset()');page.evaluate('s=>{for(let i=0;i<10;i++)document.querySelector(s).click()}',button);page.evaluate('t=>{window.__lingQA.advance(t);window.__lingQA.view("angle")}',t);f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);s=page.evaluate('window.__lingQA.inspect()');assert s['instances']['activeCount']==10 and len({i['id'] for i in s['instances']['active']})==10;active=page.evaluate('window.__lingQA.resources()')
    if wave==0:page.screenshot(path=str(out/f'{backend}-{kind}-ten.png'))
    page.evaluate('window.__lingQA.advance(13)');f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);assert page.evaluate('window.__lingQA.inspect().instances.activeCount')==0;ended=page.evaluate('window.__lingQA.resources()');waves.append({'active':active,'ended':ended})
   if len(waves)>1:assert waves[-1]['ended']['memory']==waves[-2]['ended']['memory'],waves
   rows[kind]=waves;print('PASS_PROMOTED_LIFECYCLE',backend,kind,flush=True)
  assert not errors and not page.evaluate('window.__lingSkill.errors');result[backend]={'renderer':page.evaluate('window.__lingSkill.renderer'),'software':page.evaluate('window.__lingSkill.software'),'waves':rows,'errors':errors};page.close()
 b.close()
(out/('lunar-final.json' if os.environ.get('PROMOTION_FILTER') else 'lifecycle.json')).write_text(json.dumps({'scope':'desktop software renderers; counters are not total memory, phone performance or long-term leak proof','backends':result},ensure_ascii=False,indent=2))
