"""Render actual runtime phase/angle checks and measure per-instance field ticks."""
from pathlib import Path
import json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/moon-tide'
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready&&window.__lingSkill.echoReady',timeout=120000);page.evaluate('window.__lingQA.freeze(true)');page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading',timeout=90000)
 def capture(name,view='angle'):
  page.evaluate('(v)=>window.__lingQA.view(v)',view);frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('n=>window.__lingSkill.frames>n',arg=frame,timeout=60000);page.screenshot(path=str(out/(name+'.png')))
 page.locator('#cast-yueli2').click();id=page.evaluate('window.__lingSkill.instances.active[0].id');phases={}
 for t in [.3,.9,1.8,3.5,7.6]:
  page.evaluate('t=>window.__lingQA.instanceSeek(t)',t);phases[str(t)]=page.evaluate('window.__lingSkill.tideSample');capture('phase-'+str(t))
 for v in ['front','side','back','top']:
  page.evaluate('window.__lingQA.instanceSeek(3.5)');capture('single-'+v,v)
 assert phases['3.5']['echoes']==3,phases
 page.evaluate('window.__lingQA.reset()');page.evaluate('document.getElementById("cast-yueli2").click();window.__lingQA.advance(3)');s=page.evaluate('window.__lingSkill');hits=[h for h in s['hitEvents'] if h.get('instanceId')==s['instances']['active'][0]['id']];assert len(hits)>=2 and len({h['tick'] for h in hits})==len(hits),hits
 start=s['targetStates'][0]['position'][0];page.evaluate('window.__lingQA.targetVelocity(0,1,0);window.__lingQA.advance(.5)');after=page.evaluate('window.__lingSkill');distance=after['targetStates'][0]['position'][0]-start;assert .26<distance<.29,(distance,after['targetStates'])
 page.evaluate('window.__lingQA.targetVelocity(0,0,0);window.__lingQA.reset()');page.evaluate('for(let i=0;i<10;i++)document.getElementById("cast-yueli2").click();window.__lingQA.advance(2.8)');capture('ten-fields');state=page.evaluate('window.__lingSkill');assert state['instances']['activeCount']==10
 ten_ids={i['id'] for i in state['instances']['active']};ten_hits=[h for h in state['hitEvents'] if h.get('instanceId') in ten_ids];assert {h['instanceId'] for h in ten_hits}==ten_ids,ten_hits;assert len({(h['instanceId'],h['target'],h['tick']) for h in ten_hits})==len(ten_hits),ten_hits
 perf={k:state[k] for k in ['renderer','software','fps','drawCalls','triangles','quality']};page.evaluate('window.__lingQA.advance(9)');assert page.evaluate('window.__lingSkill.instances.activeCount')==0
 page.wait_for_function('window.__lingQA.inspect().instanceAudio.voices===0&&window.__lingSkill.instanceAudio.pending===0',timeout=15000)
 assert not errors,errors
 (out/'visual-runtime.json').write_text(json.dumps({'scope':'actual desktop software WebGL2 images; no artistic or phone approval','phases':phases,'continuousHitTicks':hits,'slowDisplacementOverHalfSecond':distance,'tenFieldsIndependentHitIds':len(ten_ids),'tenFieldsHitRecords':len(ten_hits),'audioReturnedToZero':True,'tenFieldsSample':perf,'errors':errors},ensure_ascii=False,indent=2));print('PASS_VISUAL_STRUCTURE',json.dumps(perf),flush=True);b.close()
