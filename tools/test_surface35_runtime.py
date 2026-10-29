"""Only four affected skills. Rendered backend checks and repeated resource reuse."""
from pathlib import Path
import json,time
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v35/runtime';out.mkdir(parents=True,exist_ok=True);result={}
cases=[('lingyuan-2','#cast2',3.6),('yueli-1','#cast-yueli',2.8),('yueli-2','#cast-yueli2',3.5),('yueli-3','#cast-yueli3',4.4)]
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for backend,query in [('webgl2','?renderer=webgl2'),('webgpu','')]:
  page=b.new_page(viewport={'width':760,'height':480});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)');rows={}
  for kind,button,t in cases:
   if kind.startswith('yueli') and page.evaluate('window.__lingSkill.character')!='yueli':
    page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading')
   waves=[]
   for wave in range(3 if backend=='webgl2' else 1):
    page.evaluate('window.__lingQA.reset()');page.evaluate('s=>{for(let i=0;i<10;i++)document.querySelector(s).click()}',button);page.evaluate('t=>{window.__lingQA.advance(t);window.__lingQA.view("angle")}',t)
    f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);s=page.evaluate('window.__lingQA.inspect()');assert s['instances']['activeCount']==10;active=page.evaluate('window.__lingQA.resources()')
    page.evaluate('window.__lingQA.advance(13)');f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);s=page.evaluate('window.__lingQA.inspect()');assert s['instances']['activeCount']==0;audio_start=time.monotonic();page.wait_for_function('window.__lingQA.inspect().instanceAudio.voices===0&&window.__lingQA.inspect().instanceAudio.pending===0',timeout=15000);audio_tail_ms=round((time.monotonic()-audio_start)*1000,1);ended=page.evaluate('window.__lingQA.resources()');waves.append({'active':active,'ended':ended,'nativeAudioTailDrainWallMs':audio_tail_ms})
   if len(waves)>1:assert waves[-1]['ended']['memory']==waves[-2]['ended']['memory'],(kind,waves)
   rows[kind]=waves;print('PASS_SURFACE35',backend,kind,flush=True)
  assert not errors and not page.evaluate('window.__lingSkill.errors');result[backend]={'renderer':page.evaluate('window.__lingSkill.renderer'),'software':page.evaluate('window.__lingSkill.software'),'waves':rows,'errors':errors};page.close()
 b.close()
(out/'surfaces.json').write_text(json.dumps({'scope':'desktop software Chromium; renderer counters, not heap/VRAM/mobile-FPS or long-run proof','backends':result},indent=2))
