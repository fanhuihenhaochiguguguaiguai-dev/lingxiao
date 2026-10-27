"""Build a reviewable, unsigned Android bundle of the existing character viewer.
This file is not installable until independently authorized signing is performed.
"""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1];APP=ROOT/'android-app';WORK=APP/'build';OUT=ROOT/'verification/android-build';OUT.mkdir(parents=True,exist_ok=True)
runtime=ROOT.parent.parent/'yaojing-environment/.runtime/tools';JDK=Path(os.environ.get('LINGYUAN_JAVA_HOME',str(runtime/'jdk-17')));SDK=Path(os.environ.get('LINGYUAN_ANDROID_HOME',str(runtime/'android-sdk')));BT=SDK/'build-tools/35.0.1';PLATFORM=SDK/'platforms/android-35/android.jar';ENV=dict(os.environ,JAVA_HOME=str(JDK),PATH=str(JDK/'bin')+os.pathsep+os.environ.get('PATH',''),JAVA_OPTS='-Xmx512m -XX:ActiveProcessorCount=2')
def run(name,cmd,timeout=100):
 r=subprocess.run([str(x) for x in cmd],cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=timeout);(OUT/(name+'.log')).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(name+': '+(r.stderr+r.stdout)[-1500:])
 return r.stdout+r.stderr
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report={'status':'FAIL','application_id':'com.yaojing.lingyuan','version_code':1,'version_name':'0.1.0','min_sdk':26,'target_sdk':35,'signature':'UNSIGNED','android_install_tested':False,'hardware_tested':False,'can_update_old_version':False,'runtime':'Bundled 3D viewer served on loopback to an installed browser','scope':'Character and three skill viewer, unfinished art, no full game match'}
try:
 for path in [JDK/'bin/javac',JDK/'bin/java',BT/'aapt2',BT/'d8',BT/'zipalign',PLATFORM]:
  if not path.is_file():raise FileNotFoundError(path)
 run('web-build',['npm','run','build','--prefix','skill-src'],180)
 WORK.mkdir(parents=True,exist_ok=True);generated=WORK/'generated';classes=WORK/'classes';dex=WORK/'dex'
 for path in [generated,classes,dex]:
  if path.exists():shutil.rmtree(path)
  path.mkdir()
 resources=WORK/'resources.ap_';compiled=WORK/'compiled.zip';raw=WORK/'unaligned.apk';aligned=WORK/'unsigned-aligned.apk'
 run('aapt-compile',[BT/'aapt2','compile','--dir',APP/'res','-o',compiled]);run('aapt-link',[BT/'aapt2','link','-o',resources,'--manifest',APP/'AndroidManifest.xml','-I',PLATFORM,'--java',generated,'--min-sdk-version','26','--target-sdk-version','35','--version-code','1','--version-name','0.1.0',compiled])
 sources=[*APP.joinpath('src').rglob('*.java'),*generated.rglob('*.java')];run('javac',[JDK/'bin/javac','-J-Xmx256m','-J-XX:ActiveProcessorCount=2','--release','8','-encoding','UTF-8','-classpath',PLATFORM,'-d',classes,*sources]);run('d8',[BT/'d8','--release','--min-api','26','--lib',PLATFORM,'--output',dex,*classes.rglob('*.class')])
 files={'lingyuan-lod1.glb':ROOT/'dist/lingyuan-lod1.glb'}
 for path in (ROOT/'dist/skill').iterdir():
  if path.is_file():files['skill/'+path.name]=path
 for required in ['skill/index.html','skill/app.js','skill/style.css','lingyuan-lod1.glb']:
  if required not in files or not files[required].is_file():raise RuntimeError('Missing bundled asset '+required)
 rows=[{'path':name,'bytes':p.stat().st_size,'sha256':digest(p)} for name,p in sorted(files.items())];shutil.copyfile(resources,raw)
 with zipfile.ZipFile(raw,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  z.write(dex/'classes.dex','classes.dex');z.writestr('assets/web-inventory.tsv',''.join(r['path']+'\t'+str(r['bytes'])+'\n' for r in rows));z.writestr('assets/content-manifest.json',json.dumps({'scope':report['scope'],'files':rows},ensure_ascii=False))
  for name,p in sorted(files.items()):z.write(p,'assets/web/'+name,compress_type=zipfile.ZIP_STORED if p.suffix in ('.glb','.png') else zipfile.ZIP_DEFLATED)
 run('zipalign',[BT/'zipalign','-f','-P','16','4',raw,aligned]);run('zipalign-check',[BT/'zipalign','-c','-P','16','4',aligned]);badging=run('manifest-badging',[BT/'aapt2','dump','badging',aligned]);run('manifest-tree',[BT/'aapt2','dump','xmltree','--file','AndroidManifest.xml',aligned])
 if "package: name='com.yaojing.lingyuan'" not in badging or "targetSdkVersion:'35'" not in badging or not re.search(r"^(?:minSdkVersion|sdkVersion):'26'$",badging,re.M) or 'launchable-activity:' not in badging:raise RuntimeError('Manifest identity or SDK mismatch')
 with zipfile.ZipFile(aligned) as z:
  if z.testzip() is not None or not z.read('classes.dex').startswith(b'dex\n'):raise RuntimeError('Invalid archive or DEX')
  for row in rows:
   if hashlib.sha256(z.read('assets/web/'+row['path'])).hexdigest()!=row['sha256']:raise RuntimeError('Asset hash mismatch '+row['path'])
 report.update(status='PASS_UNSIGNED_STRUCTURE_ONLY',unsigned_apk=str(aligned.relative_to(ROOT)),sha256=digest(aligned),bytes=aligned.stat().st_size,files=rows,zipalign='PASS',manifest='PASS',assets='PASS')
except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as e:report['error']=str(e)
(OUT/'unsigned.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report.get(k) for k in ['status','unsigned_apk','bytes','sha256','error']},ensure_ascii=False))
if report['status']=='FAIL':raise SystemExit(1)
