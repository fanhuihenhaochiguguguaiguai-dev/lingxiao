"""Continuous real playback + actual rendered burst/recycle checks; no phone claim."""
from pathlib import Path
import json,time,os,shutil,playwright
from browser_display import display,ARGS
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];out=R/'verification/dragon32/runtime';out.mkdir(parents=True,exist_ok=True)
meta=Path(playwright.__file__).parent/'driver/package/browsers.json';revision=next(x['revision'] for x in json.loads(meta.read_text())['browsers'] if x['name']=='ffmpeg')
cache=Path(os.environ.get('PLAYWRIGHT_BROWSERS_PATH',str(Path.home()/'.cache/ms-playwright')))/('ffmpeg-'+revision)/'ffmpeg-linux'
if not cache.exists() and shutil.which('ffmpeg'):cache.parent.mkdir(parents=True,exist_ok=True);cache.symlink_to(shutil.which('ffmpeg'))
result={'scope':'installed Chromium software graphics; synthetic burst inputs; no real phone, physical audio latency or professional listening acceptance'}
with display() as env,sync_playwright() as p:
 b=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
 ctx=b.new_context(viewport={'width':960,'height':540},record_video_dir=str(out),record_video_size={'width':960,'height':540});page=ctx.new_page();page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/skill/?renderer=webgl2');page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');before=page.evaluate('window.__lingQA.inspect().stagePosition');page.keyboard.down('w');page.keyboard.down('Shift');page.keyboard.press('Space');start=time.monotonic();f=page.evaluate('window.__lingSkill.frames');page.locator('#cast').click();page.wait_for_function('!window.__lingSkill.casting');end=page.evaluate('window.__lingQA.inspect()');elapsed=time.monotonic()-start;page.keyboard.up('w');page.keyboard.up('Shift');assert sum((x-y)**2 for x,y in zip(before,end['stagePosition']))>1
 video=page.video;ctx.close();Path(video.path()).replace(out/'moving-cast.webm');result['continuousPlayback']={'file':'moving-cast.webm','wallSeconds':elapsed,'renderedFrames':end['frames']-f,'actualKeyboardMovingCast':True,'audioCaptured':False,'errors':errors};print('CONTINUOUS_VIDEO_SAVED',flush=True)
 for backend,query in [('webgl2','?renderer=webgl2'),('webgpu','')]:
  page=b.new_page(viewport={'width':1100,'height':700});page.set_default_timeout(180000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8765/skill/'+query);page.wait_for_function('window.__lingSkill?.ready&&window.__lingSkill.instanceAudio?.ready');page.evaluate('window.__lingQA.freeze(true)');waves=[]
  for wave in range(3 if backend=='webgl2' else 1):
   page.evaluate('for(let i=0;i<10;i++)document.getElementById("cast").click();window.__lingQA.advance(1.45);window.__lingQA.dragonView("angle")');frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=frame);active=page.evaluate('window.__lingQA.resources()');assert page.evaluate('window.__lingQA.inspect().instances.activeCount')==10
   if wave==0:page.screenshot(path=str(out/f'{backend}-ten.png'))
   page.evaluate('window.__lingQA.advance(5)');frame=page.evaluate('window.__lingSkill.frames');page.wait_for_function('f=>window.__lingSkill.frames>f',arg=frame);ended=page.evaluate('window.__lingQA.resources()');assert page.evaluate('window.__lingQA.inspect().instances.activeCount')==0;waves.append({'wave':wave,'active':active,'ended':ended})
  if backend=='webgl2':assert waves[-1]['ended']['memory']==waves[-2]['ended']['memory'],waves
  state=page.evaluate('window.__lingQA.inspect()');assert not errors and not state['errors'];result[backend]={'renderer':state['renderer'],'software':state['software'],'allocationWaves':waves,'errors':errors};page.close();print('PASS_BACKEND',backend,flush=True)
 b.close()
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS_CONTINUOUS_AND_RECYCLE',flush=True)
