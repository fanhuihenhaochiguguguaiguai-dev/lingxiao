"""Actual runtime stage/angle, geometric deformation and independent ultimate checks."""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/moonfall/runtime';out.mkdir(parents=True,exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready&&window.__lingSkill.ultimateAssetsReady',timeout=120000);page.evaluate('window.__lingQA.freeze(true)');page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading',timeout=90000)
 def capture(name,view='angle'):
  page.evaluate('v=>window.__lingQA.view(v)',view);frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('n=>window.__lingSkill.frames>n',arg=frame,timeout=90000);page.screenshot(path=str(out/(name+'.png')))
 page.locator('#cast-yueli3').click();samples={}
 for age in [.5,2.2,3.5,4.2,6.5,10.2]:
  page.evaluate('t=>window.__lingQA.instanceSeek(t)',age);samples[str(age)]=page.evaluate('window.__lingSkill.ultimateSample');capture('phase-'+str(age))
 assert samples['2.2']['rings']==9 and samples['2.2']['dragonCount']==1,samples
 assert samples['2.2']['dragon']['bodyY']!=samples['6.5']['dragon']['bodyY'] and samples['3.5']['moonY']<samples['2.2']['moonY']
 for view in ['front','side','back','top']:
  page.evaluate('window.__lingQA.instanceSeek(2.2)');capture('view-'+view,view)
 page.evaluate('window.__lingQA.reset()');page.evaluate('for(let i=0;i<10;i++)document.getElementById("cast-yueli3").click();window.__lingQA.advance(2.3)');state=page.evaluate('window.__lingQA.inspect()');assert state['instances']['activeCount']==10 and sum(i['dragonCount'] for i in state['instances']['active'])==10;assert len({tuple(round(x,4) for x in i['iceDragon']['head']) for i in state['instances']['active']})==10;ids={i['id'] for i in state['instances']['active']};capture('ten-ice-dragons')
 page.evaluate('window.__lingQA.advance(2.3)');state=page.evaluate('window.__lingSkill');hit_ids={h.get('instanceId') for h in state['hitEvents']};assert ids<=hit_ids,(ids,hit_ids);page.evaluate('window.__lingQA.advance(12)');assert page.evaluate('window.__lingSkill.instances.activeCount')==0;page.wait_for_function('window.__lingQA.inspect().instanceAudio.voices===0&&window.__lingSkill.instanceAudio.pending===0',timeout=15000)
 assert not errors,errors
 (out/'result.json').write_text(json.dumps({'scope':'desktop Chromium software WebGL2; actual geometry/time/deformation, not art or phone acceptance','stages':samples,'independentDragonsAt2_3Seconds':len(ids),'independentHitIds':len(ids&hit_ids),'activeAndVoicesReturnToZero':True,'errors':errors},ensure_ascii=False,indent=2));print('PASS_ULTIMATE_RUNTIME',flush=True);b.close()
