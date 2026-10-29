"""Uncut actual UI/keyboard play; no QA freeze, advance, seeking or fake frames."""
from pathlib import Path
import json,time,shutil,os,playwright
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/combat/video';out.mkdir(parents=True,exist_ok=True)
meta=Path(playwright.__file__).parent/'driver/package/browsers.json';revision=next(x['revision'] for x in json.loads(meta.read_text())['browsers'] if x['name']=='ffmpeg');cache=Path(os.environ.get('PLAYWRIGHT_BROWSERS_PATH',str(Path.home()/'.cache/ms-playwright')))/('ffmpeg-'+revision)/'ffmpeg-linux'
if not cache.exists():cache.parent.mkdir(parents=True,exist_ok=True);cache.symlink_to(shutil.which('ffmpeg'))
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');ctx=b.new_context(viewport={'width':960,'height':540},record_video_dir=str(out),record_video_size={'width':960,'height':540});page=ctx.new_page();page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.basicReady');start=time.monotonic();first=page.evaluate('window.__lingSkill.frames')
 for key in ['d','s','Shift']:page.keyboard.down(key)
 page.wait_for_function('window.__lingSkill.position[0]>1.6');
 for key in ['d','s','Shift']:page.keyboard.up(key)
 page.keyboard.down('j');page.wait_for_function('window.__lingSkill.combat.events.filter(e=>e.kind==="lingyuan-basic").length>=3');page.keyboard.up('j');practice=page.evaluate('window.__lingSkill.combat');page.locator('#combat-mode').click();page.wait_for_function('window.__lingSkill.combat.mode==="duel"');page.wait_for_function('window.__lingSkill.opponent.skillCount>=1&&window.__lingSkill.combat.events.some(e=>e.source==="opponent"&&e.kind==="yueli-1")');
 for key in ['d','s','Shift']:page.keyboard.down(key)
 page.wait_for_function('Math.hypot(window.__lingSkill.position[0]-window.__lingSkill.opponent.position[0],window.__lingSkill.position[2]-window.__lingSkill.opponent.position[2])<2.6');page.keyboard.down('j');page.wait_for_function('window.__lingSkill.combat.events.some(e=>e.source==="player"&&e.kind==="lingyuan-basic")');page.keyboard.up('j');page.keyboard.press('1')
 for key in ['d','s','Shift']:page.keyboard.up(key)
 last_frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>=f+3',arg=last_frame);page.screenshot(path=str(out/'actual-play-final.png'));s=page.evaluate('window.__lingSkill');elapsed=time.monotonic()-start;assert not errors and not s['errors'];video=page.video;ctx.close();Path(video.path()).replace(out/'actual-play.webm');b.close()
 (out/'record.json').write_text(json.dumps({'scope':'uncut real Chromium WebGL2 playback, real keyboard/DOM interactions, no simulated clock','wallSeconds':elapsed,'renderedFrames':s['frames']-first,'practiceDamageEvents':practice['events'],'duelDamageEvents':s['combat']['events'],'duelGameSeconds':s['combat']['clock'],'audioCaptured':False,'software':s['software'],'phoneTested':False,'errors':errors},ensure_ascii=False,indent=2));print('REAL_COMBAT_VIDEO_SAVED',elapsed,flush=True)
