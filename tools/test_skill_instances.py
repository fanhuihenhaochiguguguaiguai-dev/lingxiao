"""Exact burst counts, independent lifetimes, pooled reuse and movement regression.
Browser rendering is software; DOM bursts are explicitly synthetic input.
"""
from pathlib import Path
import json,time,os
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/os.environ.get('LINGYUAN_REPORT_DIR','verification/moon-tide');out.mkdir(exist_ok=True)
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1100,'height':700});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready&&window.__lingSkill.echoReady',timeout=120000);page.evaluate('window.__lingQA.freeze(true)');results={}
 for character in ['lingyuan','yueli']:
  if character=='yueli':page.locator('#open-characters').click();page.locator('[data-character="yueli"]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading',timeout=90000)
  for skill in ([1,2,3] if character=='lingyuan' else [1,2,3]):
   button=('#cast' if skill==1 else '#cast'+str(skill)) if character=='lingyuan' else '#cast-yueli'+(str(skill) if skill>1 else '')
   kind=f'{character}-{skill}';checks=[]
   for count in [1,3,5,10]:
    page.evaluate('window.__lingQA.reset()');before=page.evaluate('window.__lingQA.inspect().instances.created');wall=time.monotonic()
    page.evaluate('([selector,count])=>{const button=document.querySelector(selector);for(let i=0;i<count;i++)button.click()}',[button,count]);state=page.evaluate('window.__lingQA.inspect()');active=state['instances']['active'];assert len(active)==count and state['instances']['created']-before==count,(kind,count,state['instances']);assert len({x['id'] for x in active})==count and len({x['rootUuid'] for x in active})==count
    assert all(x['age']==0 for x in active),active
    ids={x['id'] for x in active};events=[e for e in state['instanceAudio']['events'] if e['instanceId'] in ids and e['phase'] in ['cast','legacy:0']];assert len(events)==count and all(e['status']=='playing' for e in events),(kind,events)
    if character=='yueli' and count>=3:assert len({e['variant'] for e in events})==3,events
    checks.append({'requested':count,'created':len(active),'uniqueRoots':len({x['rootUuid'] for x in active}),'immediateAgeZero':True,'castAudioEvents':len(events),'synchronousBurstWallMs':round((time.monotonic()-wall)*1000,2)})
   # Put one target inside each skill path/field, then verify true hit/audio identity.
   page.evaluate('window.__lingQA.targetPosition(0,2,.6,0)')
   # Moving and airborne casts keep all instances; older clocks never restart.
   page.keyboard.down('w');page.keyboard.down('Shift');page.evaluate('window.__lingQA.advance(.8)');page.keyboard.press('Space');page.evaluate('window.__lingQA.advance(.2)');old=page.evaluate('window.__lingSkill.instances.active');page.evaluate('selector=>document.querySelector(selector).click()',button);page.evaluate('window.__lingQA.advance(.2)');state=page.evaluate('window.__lingSkill');page.keyboard.up('w');page.keyboard.up('Shift');assert state['speed']>.2 and state['jumpHeight']>0 and state['instances']['activeCount']==11
   new_by_id={i['id']:i for i in state['instances']['active']};assert all(new_by_id[i['id']]['age']>i['age'] for i in old);assert all(new_by_id[i['id']]['position']==i['position'] for i in old)
   page.evaluate('window.__lingQA.advance(13)');state=page.evaluate('window.__lingQA.inspect()');assert state['instances']['activeCount']==0 and state['instances']['pooled']<=12
   hits=[h for h in state['hitEvents'] if h.get('instanceId') in ids and h['target']==0 and h.get('tick')==0];hit_audio=[e for e in state['instanceAudio']['events'] if e['instanceId'] in ids and e['phase']=='hit:0:0'];assert len(hits)==10 and len(hit_audio)==10,(kind,len(hits),len(hit_audio));assert all(any(e['instanceId']==h['instanceId'] and abs(e['simulationTime']-h['time'])<1e-8 and e['status']=='playing' for e in hit_audio) for h in hits)
   created=state['instances']['created'];reused=state['instances']['reused'];page.evaluate('selector=>document.querySelector(selector).click()',button);assert page.evaluate('window.__lingQA.inspect().instances.reused')>reused;page.evaluate('window.__lingQA.reset()');results[kind]={'bursts':checks,'movingJumpCast':True,'tenIndependentTargetHitsAndAudio':True,'independentAnchorsAndClocks':True,'cleanup':state['instances']|{'active':[],'history':[]},'reuse':True};print('PASS',kind,flush=True)
 assert not errors,errors
 (out/'instances.json').write_text(json.dumps({'scope':'desktop Chromium software WebGL2; exact synthetic DOM burst counts, not physical phone latency','checks':results,'errors':errors},ensure_ascii=False,indent=2));b.close()
