"""Uncut real browser recording. No QA fast-forward or generated frames."""
from pathlib import Path
import json,time,shutil,os,playwright
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/lingyuan31/video';out.mkdir(parents=True,exist_ok=True)
# Reuse installed system FFmpeg when the Playwright-specific cache is absent.
# No browser or codec download is required in this environment.
meta=Path(playwright.__file__).parent/'driver/package/browsers.json'
revision=next(x['revision'] for x in json.loads(meta.read_text())['browsers'] if x['name']=='ffmpeg')
cache=Path(os.environ.get('PLAYWRIGHT_BROWSERS_PATH',str(Path.home()/'.cache/ms-playwright')))/('ffmpeg-'+revision)/'ffmpeg-linux'
if not cache.exists() and shutil.which('ffmpeg'):
 cache.parent.mkdir(parents=True,exist_ok=True);cache.symlink_to(shutil.which('ffmpeg'))
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium');ctx=b.new_context(viewport={'width':844,'height':480},record_video_dir=str(out),record_video_size={'width':844,'height':480});page=ctx.new_page();page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2&sample=lingyuan31-head');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.view("face")');page.wait_for_timeout(1000);start=time.monotonic();frames=page.evaluate('window.__lingSkill.frames');page.locator('#cast').click();page.wait_for_function('!window.__lingSkill.casting',timeout=180000);elapsed=time.monotonic()-start;end=page.evaluate('window.__lingSkill.frames');assert not errors,errors
 video=page.video;ctx.close();source=Path(video.path());dest=out/'head-and-first-skill.webm';source.replace(dest);b.close();(out/'record.json').write_text(json.dumps({'file':dest.name,'scope':'uncut actual Chromium software WebGL2; no fast-forward, generated frames or phone performance claim','wallSecondsForCast':elapsed,'renderedFramesDuringCast':end-frames,'audioCaptured':False,'artAccepted':False,'errors':errors},indent=2));print('REAL_BROWSER_VIDEO_SAVED',flush=True)
