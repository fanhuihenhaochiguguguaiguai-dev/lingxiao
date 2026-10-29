"""Failure recovery, training timing, early visibility and allocation plateau.
All browser contexts run sequentially on the installed software graphics backend.
"""
from pathlib import Path
import json,subprocess
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/governance';out.mkdir(exist_ok=True)
old=subprocess.check_output(['git','show','a6f9570c6abf3fe8724c606709b39de6f460a697:dist/skill/app.js'],cwd=R)
results={}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 for label in ['before','after']:
  page=b.new_page(viewport={'width':900,'height':600});page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  if label=='before':page.route('**/skill/app.js',lambda r:r.fulfill(body=old,content_type='text/javascript'))
  page.add_init_script("""window.__testHidden=false;Object.defineProperty(document,'hidden',{configurable:true,get:()=>window.__testHidden});const timer=setInterval(()=>{if(!window.__lingQA||window.__lingSkill.ready)return;clearInterval(timer);window.__testHidden=true;document.dispatchEvent(new Event('visibilitychange'));window.__testHidden=false;document.dispatchEvent(new Event('visibilitychange'));window.__earlyVisibilityInjected=true},5)""")
  page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready');page.evaluate('window.__lingQA.freeze(true)');page.locator('#cast3').click();page.evaluate('window.__lingQA.advance(3.5)');early_hits=page.evaluate('window.__lingSkill.hitEvents');page.evaluate('window.__lingQA.advance(2.4)');hits=page.evaluate('window.__lingSkill.hitEvents');results[label]={'earlyVisibilityInjected':page.evaluate('!!window.__earlyVisibilityInjected'),'earlyVisibilityErrors':errors,'ultimateHitsBeforeShock':len(early_hits),'ultimateHitsAtEndOfShock':len(hits),'firstUltimateHit':hits[0] if hits else None}
  if label=='after':assert not errors and not early_hits and hits and all(h['time']>=4.85 for h in hits)
  page.close();print('TIMING_VISIBILITY',label,flush=True)
 # Missing audio must not block the other 65 buffers; failed character loads retry.
 page=b.new_page(viewport={'width':900,'height':600});page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 fail_audio=lambda r:r.fulfill(status=404,body='injected missing test asset')
 page.route('**/audio/lunar/lunar1-cast-0.ogg',fail_audio)
 fail_model=lambda r:r.fulfill(status=503,body='injected transient model failure')
 page.route('**/yueli-study.glb*',fail_model)
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.loaded===65');page.evaluate('window.__lingQA.freeze(true)');page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('!window.__lingSkill.characterLoading&&document.getElementById("character-message").textContent.includes("加载失败")');assert page.evaluate('window.__lingSkill.character')=='lingyuan'
 page.unroute('**/yueli-study.glb*',fail_model);page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading');page.locator('#cast-yueli2').click();page.wait_for_function('window.__lingSkill.instanceAudio.events.some(e=>e.kind==="yueli-2"&&e.status==="playing")');partial=page.evaluate('window.__lingQA.inspect().instanceAudio');assert partial['loaded']==65 and partial['failedFiles']==['lunar1-cast-0']
 page.unroute('**/audio/lunar/lunar1-cast-0.ogg',fail_audio);page.evaluate('window.__lingQA.retryAudio().then(()=>window.__lingQA.inspect())');page.wait_for_function('window.__lingSkill.instanceAudio.ready&&window.__lingSkill.instanceAudio.loaded===66');assert page.evaluate('window.__lingQA.assetStatus().pending.length')==0
 results['recovery']={'unaffectedAudioBuffers':partial['loaded'],'unaffectedSkillAudioPlays':True,'failedAudioRetryLoadsAll66':True,'failedCharacterRetainsOldActorAndRetries':True,'cache':page.evaluate('window.__lingQA.assetStatus()')};assert not errors,errors;page.close();print('FAILURE_RECOVERY_PASS',flush=True)
 page=b.new_page(viewport={'width':900,'height':600});page.set_default_timeout(120000);page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.ultimateAssetsReady&&window.__lingSkill.instanceAudio.ready');page.evaluate('window.__lingQA.freeze(true)');page.locator('#open-characters').click();page.locator('[data-character=yueli]').click();page.wait_for_function('window.__lingSkill.character==="yueli"&&!window.__lingSkill.characterLoading');waves=[]
 for wave in range(3):
  page.evaluate('for(let i=0;i<10;i++)document.getElementById("cast-yueli3").click();window.__lingQA.advance(2.3)');frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=frame);active=page.evaluate('window.__lingQA.resources()');assert page.evaluate('window.__lingSkill.instances.activeCount')==10
  page.evaluate('window.__lingQA.advance(12)');frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=frame);ended=page.evaluate('window.__lingQA.resources()');history=page.evaluate('window.__lingQA.inspect().instances.history');assert all(11.4-1e-8<=h['endedAt']-h['createdAt']<11.45 for h in history if h['endedAt'] is not None),history;waves.append({'wave':wave,'active':active,'ended':ended})
 assert waves[-1]['ended']['memory']==waves[-2]['ended']['memory'],waves
 page.evaluate('window.__lingQA.reset()');assert page.evaluate('window.__lingQA.inspect().instanceAudio.voices')==0
 results['allocationWaves']={'scope':'renderer.info allocation counters after drawing and recycling; not total GPU/heap proof','waves':waves};page.close();b.close()
(out/'lifecycle.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('PASS_GOVERNANCE_LIFECYCLE',flush=True)
