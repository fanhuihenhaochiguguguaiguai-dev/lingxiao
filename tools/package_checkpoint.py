"""Create and verify a clearly labelled work-in-progress checkpoint ZIP."""
import hashlib,json,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];target=Path(sys.argv[1]).resolve();temp=target.with_name(target.name+'.tmp')
if target.exists():raise SystemExit('Refusing to overwrite an existing ZIP: '+str(target))
files=[root/'README.md']
for name in ['dist','reference','docs']:
 files.extend(p for p in (root/name).rglob('*') if p.is_file())
for name in ['REPORT.md','lod-validation.json','blend-v4.json','controls-v4.json','loading-v4.json','webgpu-v4.json','sleeve-experiment.png']:
 p=root/'verification'/name
 if p.exists():files.append(p)
for name in ['export_refinement.py','refine_head_targets.py','refine_eyes.py','refine_sleeves.py','refine_hair.py','validate_blend.py','validate_refinement.py','render_details.py']:
 files.append(root/'tools'/name)
files=sorted(set(files));manifest={}
for p in files:
 if not p.is_file():raise FileNotFoundError(p)
 manifest[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
try:
 with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
  for p in files:z.write(p,str(p.relative_to(root)))
  z.writestr('CHECKPOINT-MANIFEST.json',json.dumps({'status':'WORK IN PROGRESS - NOT A FINAL CHARACTER','sha256':manifest},ensure_ascii=False,indent=2)+'\n')
 with zipfile.ZipFile(temp) as z:
  assert z.testzip() is None
  for name,sha in manifest.items():
   if hashlib.sha256(z.read(name)).hexdigest()!=sha:raise RuntimeError('ZIP verification mismatch: '+name)
 temp.replace(target)
except BaseException:
 temp.unlink(missing_ok=True);raise
print(json.dumps({'archive':str(target),'files':len(files),'bytes':target.stat().st_size,'status':'WIP','verified':True},ensure_ascii=False))
