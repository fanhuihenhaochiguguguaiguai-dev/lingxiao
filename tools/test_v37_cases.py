from pathlib import Path
import math,json
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v37';result={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':960,'height':540});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready');page.evaluate('window.__lingQA.freeze(true)')
 def s():return page.evaluate('window.__lingQA.inspect()')
 def adv(t):page.evaluate('t=>window.__lingQA.advance(t)',t)
 def seed(pos):page.evaluate('p=>{window.__lingQA.targetPosition(0,...p);window.__lingQA.blink(0)}',pos)
 def reset(button,age):
  page.evaluate('window.__lingQA.reset();for(let i=0;i<3;i++)window.__lingQA.targetPosition(i,60+i*2,.6,60);window.__lingQA.blink(0)');page.evaluate('q=>document.querySelector(q).click()',button);adv(age)
 for char in ['lingyuan','yueli']:
  if char=='yueli':page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading')
  for slot in [1,2,3]:
   kind=char+'-'+str(slot);button=('#cast' if slot==1 else '#cast'+str(slot)) if char=='lingyuan' else '#cast-yueli'+('' if slot==1 else str(slot));age={'lingyuan-1':2.2,'lingyuan-2':4.1,'lingyuan-3':2.5,'yueli-1':2.8,'yueli-2':3.1,'yueli-3':6}[kind];row={}
   cases={'lingyuan-1':([2,1.1,.9],[20,1.1,20]),'lingyuan-2':([0,.6,3.03+.45-.03],[0,.6,3.03+.45+.25]),'lingyuan-3':([0,.6,2.15+.45-.03],[0,.6,2.15+.45+.20]),'yueli-1':([4.1,.6,1.12+.45-.03],[4.1,.6,1.12+.45+.25]),'yueli-2':([2.4,.6,3.1+.45-.03],[2.4,.6,3.1+.45+.55]),'yueli-3':([1.5,.6,3.95+.45-.03],[1.5,.6,3.95+.45+.25])}[kind]
   for label,pos in zip(['edgeInside','outsideAllDamage'],cases):
    reset(button,age)
    if kind=='lingyuan-1':
     vs=page.evaluate('id=>window.__combatQA.volumes(id)',s()['instances']['active'][-1]['id'])['volumes'];v=next(v for v in vs if v['id']=='dragon:body:20');pos=[v['a']['x'],v['a']['y'],v['a']['z']] if label=='edgeInside' else pos
    seed(pos);adv(.04);events=s()['combat']['events'];assert bool(events)==(label=='edgeInside'),(kind,label,pos,events);row[label]={'position':pos,'events':events}
   reset(button,age);seed([cases[0][0],30,cases[0][2]]);adv(.04);assert not s()['combat']['events'];row['aboveVolumeMiss']=True
   # A fast target moves across a fully visible danger region, not teleported by the test.
   reset(button,age);center={'lingyuan-1':[2,1.1,0],'lingyuan-2':[0,.6,0],'lingyuan-3':[0,.6,0],'yueli-1':[4.1,.6,0],'yueli-2':[2.4,.6,0],'yueli-3':[1.5,.6,0]}[kind]
   if kind=='lingyuan-1':
    v=page.evaluate('id=>window.__combatQA.volumes(id)',s()['instances']['active'][-1]['id'])['volumes'][15];center=[v['a']['x'],v['a']['y'],v['a']['z']]
   seed([center[0],center[1],center[2]+5]);page.evaluate('window.__lingQA.targetVelocity(0,0,-65)');adv(.17);page.evaluate('window.__lingQA.targetVelocity(0,0,0)');ev=s()['combat']['events'];assert ev,(kind,'moving cross');row['movingCross']={'events':ev,'targetSpeed':65}
   # All skills retain input during running and turning, with post-layer foot contacts measured.
   reset(button,0);page.keyboard.down('w');page.keyboard.down('Shift');samples=[]
   for n in range(22):
    adv(.09)
    if n==9:page.keyboard.down('d')
    motion=s()['motionSample'];samples.append({'time':s()['time'],'before':motion.get('preContactErrors',[]),'after':motion['contactErrors']})
   page.keyboard.up('w');page.keyboard.up('d');page.keyboard.up('Shift');assert s()['speed']>.2 and s()['instances']['activeCount']>=1
   after=max([e for x in samples for e in x['after']] or [0]);before=max([e for x in samples for e in x['before']] or [0]);assert after<.035,(kind,before,after);row['runningTurningCast']={'maxPreContactError':before,'maxPostContactError':after,'samples':samples,'speed':s()['speed']};result[kind]=row;print('PASS_EDGE_CROSS_RUN',kind,before,after,flush=True)
 # Spear phantom range was removed rather than extending invisible damage back to 2.7m.
 page.locator('#open-characters').click();page.locator('[data-character=lingyuan]').click();page.wait_for_function('window.__lingSkill.character==="lingyuan"&&!window.__lingSkill.characterLoading');page.evaluate('window.__lingQA.reset();window.__lingQA.targetPosition(0,2.8,.6,0);document.getElementById("basic-attack").click();window.__lingQA.advance(.55)');assert not s()['combat']['events'];result['spearOutsideRealWeaponMiss']=True
 # Translated roots must update every sibling layer before sampling a crystal.
 page.evaluate('window.__lingQA.reset();window.__combatQA.position("player",10,2);for(let i=0;i<3;i++)window.__lingQA.targetPosition(i,60+i*2,.6,60);document.getElementById("cast2").click();window.__lingQA.advance(3)');ss=s();i=ss['instances']['active'][-1];vs=page.evaluate('id=>window.__combatQA.volumes(id)',i['id'])['volumes'];v=next(v for v in vs if v['id']=='binding-crystal:0:0');expected=[i['position'][0]+math.cos(i['yaw'])*2.95,i['position'][2]-math.sin(i['yaw'])*2.95];assert math.hypot(v['a']['x']-expected[0],v['a']['z']-expected[1])<.08,(v,expected);assert len({v['id'] for v in vs})==len(vs);result['siblingCrystalWorldTransform']={'volume':v,'expectedBaseXZ':expected,'uniqueRegionIds':True}
 assert not errors and not s()['errors'];b.close()
(out/'cases.json').write_text(json.dumps({'scope':'software WebGL2; real effect transforms with staged targets, clocks and keyboard; no physical phone claims','results':result,'errors':errors},ensure_ascii=False,indent=2));print('PASS_V37_EDGE_CROSS_MOTION',flush=True)
