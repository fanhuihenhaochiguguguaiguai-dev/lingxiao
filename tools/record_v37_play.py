"""Uncut real-time browser playback. No QA clock, position, seek or generated frames."""
from pathlib import Path
import json,time,shutil,os,playwright
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/v37/video';out.mkdir(parents=True,exist_ok=True)
meta=Path(playwright.__file__).parent/'driver/package/browsers.json';rev=next(x['revision'] for x in json.loads(meta.read_text())['browsers'] if x['name']=='ffmpeg');ff=Path(os.environ.get('PLAYWRIGHT_BROWSERS_PATH',str(Path.home()/'.cache/ms-playwright')))/('ffmpeg-'+rev)/'ffmpeg-linux'
if not ff.exists():ff.parent.mkdir(parents=True,exist_ok=True);ff.symlink_to(shutil.which('ffmpeg'))
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');ctx=b.new_context(viewport={'width':960,'height':540},record_video_dir=str(out),record_video_size={'width':960,'height':540});page=ctx.new_page();page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready&&window.__lingSkill.instanceAudio?.basicReady');start=time.monotonic();first=page.evaluate('window.__lingSkill.frames')
 def frame():
  n=page.evaluate('window.__lingSkill.frames');page.wait_for_function('n=>window.__lingSkill.frames>=n+2',arg=n)
 for key in ['d','s','Shift']:page.keyboard.down(key)
 page.wait_for_function('window.__lingSkill.position[0]>2.5')
 for key in ['d','s','Shift']:page.keyboard.up(key)
 page.keyboard.down('j');page.wait_for_function('window.__lingSkill.combat.events.filter(e=>e.kind==="lingyuan-basic").length>=2');page.keyboard.up('j');practice=page.evaluate('window.__lingSkill.combat')
 r=page.locator('#cast2').bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2;page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-50,y-20,steps=5);frame();page.screenshot(path=str(out/'aim.png'));page.mouse.up();page.wait_for_function('window.__lingSkill.combat.events.some(e=>e.kind==="lingyuan-2")');frame();page.screenshot(path=str(out/'field-hit.png'))
 count=page.evaluate('window.__lingSkill.instances.created');r=page.locator('#cast').bounding_box();page.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);page.mouse.down();r=page.locator('#cast-cancel').bounding_box();page.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2,steps=6);frame();page.screenshot(path=str(out/'cancel.png'));page.mouse.up();assert page.evaluate('window.__lingSkill.instances.created')==count
 page.locator('#combat-mode').click();page.wait_for_function('window.__lingSkill.combat.mode==="duel"');page.wait_for_function('window.__lingSkill.combat.events.some(e=>e.source==="opponent")');frame();page.screenshot(path=str(out/'duel.png'));s=page.evaluate('window.__lingSkill');elapsed=time.monotonic()-start;assert not errors and not s['errors'];v=page.video;ctx.close();Path(v.path()).replace(out/'actual-play.webm');b.close()
 (out/'record.json').write_text(json.dumps({'scope':'uncut real browser play with native keyboard/mouse, natural animation clock; no QA freeze/advance/seek/position','wallSeconds':elapsed,'renderedFrames':s['frames']-first,'practice':practice,'duel':s['combat'],'software':s['software'],'audioCaptured':False,'realPhoneTested':False,'errors':errors},ensure_ascii=False,indent=2));print('PASS_V37_REAL_VIDEO',elapsed,flush=True)
