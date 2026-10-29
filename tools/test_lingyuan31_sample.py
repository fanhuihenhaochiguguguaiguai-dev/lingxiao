"""Isolated LOD overlap comparison and opt-in head sample in the real website.
Software browsers only. Unapproved artwork is never made the default here.
"""
from pathlib import Path
import json,re,subprocess
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/lingyuan31/web';out.mkdir(parents=True,exist_ok=True)
old=subprocess.check_output(['git','show','650edf1:dist/lingyuan-lod1.glb'],cwd=R);results={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for label,query in [('before','?renderer=webgl2'),('repaired','?renderer=webgl2'),('sample','?renderer=webgl2&sample=lingyuan31-head'),('sample-webgpu','?sample=lingyuan31-head')]:
  page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  if label=='before':page.route('**/lingyuan-lod1.glb*',lambda r:r.fulfill(body=old,content_type='model/gltf-binary'))
  page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true);window.__lingQA.reset();window.__lingQA.blink(0);window.__lingQA.neutral()')
  def shot(name,view):
   page.evaluate('v=>window.__lingQA.view(v)',view);f=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=f);page.screenshot(path=str(out/(label+'-'+name+'.png')))
  shot('face','face');inventory=page.evaluate('window.__lingQA.modelInventory()');hair=sorted({int(re.search(r'Hair_Lod(\d)',m['name']+' '+m.get('owner','')).group(1)) for m in inventory if m['visible'] and re.search(r'Hair_Lod(\d)',m['name']+' '+m.get('owner',''))});state=page.evaluate('window.__lingQA.inspect()');results[label]={'renderer':state['renderer'],'software':state['software'],'activeHairLODs':hair,'drawCalls':state['drawCalls'],'triangles':state['triangles'],'cameraTarget':state['cameraTarget'],'bones':len(state['boneNames']),'errors':errors}
  assert hair==([0,1,2] if label=='before' else [1]),hair
  if label=='sample':
   page.evaluate('window.__lingQA.neutral();window.__lingQA.blink(1)');shot('blink','face');morphs=page.evaluate('window.__lingQA.morphState().filter(m=>m.key==="Blink")');assert morphs and all(m['weight']==1 for m in morphs);results[label]['closedBlinkMorphs']=morphs;page.evaluate('window.__lingQA.blink(null)');checks={}
   for skill in [1,2,3]:
    selector='#cast' if skill==1 else '#cast'+str(skill)
    for count in [1,3,5,10]:
     page.evaluate('window.__lingQA.reset()');page.evaluate('([s,n])=>{for(let i=0;i<n;i++)document.querySelector(s).click()}',[selector,count]);s=page.evaluate('window.__lingQA.inspect()');assert s['instances']['activeCount']==count and len({i['id'] for i in s['instances']['active']})==count
    page.keyboard.down('w');page.keyboard.down('Shift');page.evaluate('window.__lingQA.advance(.8)');page.keyboard.press('Space');page.evaluate('window.__lingQA.advance(.2)');s=page.evaluate('window.__lingQA.inspect()');assert s['speed']>.2 and s['jumpHeight']>0
    page.keyboard.up('w');page.keyboard.up('Shift');page.evaluate('window.__lingQA.advance(13)');assert page.evaluate('window.__lingQA.inspect().instances.activeCount')==0;checks[str(skill)]={'bursts':[1,3,5,10],'runJumpCast':True,'cleanup':True}
   results[label]['skillChecks']=checks;page.evaluate('window.__lingQA.reset()');page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading');page.locator('#cast-yueli').click();assert page.evaluate('window.__lingQA.inspect().instances.activeCount')==1;results[label]['yueliSwitchAndCast']=True
  assert not errors and not page.evaluate('window.__lingSkill.errors'),(errors,page.evaluate('window.__lingSkill.errors'));page.close();print('PASS',label,flush=True)
 b.close()
assert results['repaired']['drawCalls']<results['before']['drawCalls'] and results['repaired']['triangles']<results['before']['triangles']
(out/'results.json').write_text(json.dumps({'scope':'same website, viewport, neutral pose, software renderers; not mobile or artistic acceptance','checks':results},ensure_ascii=False,indent=2));print('PASS_LOD_AND_HEAD_SAMPLE',flush=True)
