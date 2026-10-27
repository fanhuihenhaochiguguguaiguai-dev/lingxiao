"""Test actual unsigned APK bytes via the same Java loopback server; no Android claim."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import hashlib,json,os,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'android-app/build';OUT=ROOT/'verification/android-build';report=json.loads((OUT/'unsigned.json').read_text());apk=ROOT/report['unsigned_apk'];jdk=Path(os.environ.get('LINGYUAN_JAVA_HOME',str(ROOT.parent.parent/'yaojing-environment/.runtime/tools/jdk-17')))
result={'status':'FAIL','apk_sha256':report['sha256'],'android_install_tested':False,'android_webview_tested':False,'android_browser_gpu_tested':False,'http':[],'browsers':[]};server=None
try:
 if hashlib.sha256(apk.read_bytes()).hexdigest()!=report['sha256']:raise RuntimeError('APK differs from unsigned build receipt')
 harness=WORK/'harness';harness.mkdir(exist_ok=True);proc=subprocess.run([str(jdk/'bin/javac'),'--release','8','-classpath',str(WORK/'classes'),'-d',str(harness),str(ROOT/'android-app/tools/ServerHarness.java')],capture_output=True,text=True,timeout=30)
 if proc.returncode:raise RuntimeError(proc.stderr)
 server=subprocess.Popen([str(jdk/'bin/java'),'-Xmx256m','-cp',str(harness)+os.pathsep+str(WORK/'classes'),'com.yaojing.lingyuan.ServerHarness',str(apk)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);url=server.stdout.readline().strip()
 if not url.startswith('http://127.0.0.1:'):raise RuntimeError('Loopback server unavailable')
 def check(name,path='',method='GET',headers=None,status=200,expected=None):
  try:
   with urlopen(Request(url+path,method=method,headers=headers or {}),timeout=20) as r:code=r.status;body=r.read();meta=dict(r.headers)
  except HTTPError as e:code=e.code;body=e.read();meta=dict(e.headers)
  ok=code==status and (expected is None or body==expected);result['http'].append({'name':name,'status':'PASS' if ok else 'FAIL','http_status':code})
  if not ok:raise RuntimeError('HTTP '+name)
  return meta
 with zipfile.ZipFile(apk) as z:html=z.read('assets/web/skill/index.html')
 headers=check('exact HTML','skill/index.html',expected=html)
 if headers.get('Cross-Origin-Embedder-Policy')!='require-corp':raise RuntimeError('Cross-origin isolation missing')
 check('GLB header','lingyuan-lod1.glb',headers={'Range':'bytes=0-3'},status=206,expected=b'glTF');check('read only','skill/index.html',method='POST',status=405);check('missing asset','missing.txt',status=404);check('foreign host','skill/index.html',headers={'Host':'external.invalid'},status=403);check('path traversal','%2e%2e/AndroidManifest.xml',status=400)
 sys.path.insert(0,str(ROOT/'tools'))
 from browser_display import display,ARGS
 from playwright.sync_api import sync_playwright
 with display() as env,sync_playwright() as p:
  browser=p.chromium.launch(headless=False,args=ARGS,env=env,executable_path='/usr/bin/chromium')
  for expected,query in [('WebGPU',''),('WebGL2','?renderer=webgl2')]:
   page=browser.new_page(viewport={'width':844,'height':390},is_mobile=True,has_touch=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url+'skill/index.html'+query);page.wait_for_function('window.__lingSkill && (window.__lingSkill.ready || window.__lingSkill.errors.length)',timeout=90000);state=page.evaluate('window.__lingSkill');assert state['ready'] and state['renderer']==expected and state['spearTipValid'],state
   for button,t in [('cast',1.0),('cast2',3.8),('cast3',3.1)]:
    page.locator('#'+button).click();page.locator('#pause').click();page.locator('#seek').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',str(t));page.wait_for_timeout(650);s=page.evaluate('window.__lingSkill');assert s['dragonVisible'] and not s['errors'] and not errors
    if button=='cast3':assert s['actorY']>.4
   page.locator('[data-quality=standard]').click();assert page.evaluate('window.__lingSkill.quality')=='standard';page.wait_for_timeout(1000);page.screenshot(path=str(OUT/('packaged-'+expected.lower()+'.png')));result['browsers'].append({'backend':expected,'software':s['software'],'status':'PASS','errors':errors});page.close()
  browser.close()
 result['status']='PASS_PACKAGED_DESKTOP_SOFTWARE_ONLY'
except Exception as e:result['error']=str(e)
finally:
 if server:
  if server.stdin:server.stdin.close()
  try:server.wait(timeout=8)
  except subprocess.TimeoutExpired:server.terminate();server.wait(timeout=5)
(OUT/'packaged-runtime.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'http_checks':len(result['http']),'browsers':result['browsers'],'error':result.get('error'),'android_install_tested':False},ensure_ascii=False));raise SystemExit(0 if result['status'].startswith('PASS_') else 1)
