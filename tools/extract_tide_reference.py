"""Extract the supplied Moon Tide archive without altering source pixels."""
from pathlib import Path,PurePosixPath
import zipfile,hashlib,json,io,stat
from PIL import Image
R=Path(__file__).resolve().parents[1];src=next(Path('/tmp/codex-remote-attachments/01a17201-4414-75d7-bf0a-2dde3b4310b0/5c1bf14c-9e6d-40f6-8acf-dc6e2c3ab7f1').glob('*.zip'));dest=R/'reference/moon-tide';dest.mkdir(parents=True,exist_ok=True);records=[]
with zipfile.ZipFile(src) as z:
 assert z.testzip() is None
 for info in z.infolist():
  name=PurePosixPath(info.filename)
  assert not name.is_absolute() and '..' not in name.parts and not stat.S_ISLNK(info.external_attr>>16)
  if info.is_dir():continue
  data=z.read(info);path=dest.joinpath(*name.parts);path.parent.mkdir(parents=True,exist_ok=True)
  if path.exists():assert path.read_bytes()==data
  else:path.write_bytes(data)
  entry={'path':str(name),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  if path.suffix.lower() in ('.webp','.png','.jpg','.jpeg'):
   with Image.open(io.BytesIO(data)) as im:entry['dimensions']=list(im.size);im.verify()
  records.append(entry)
(dest/'manifest.json').write_text(json.dumps({'archiveSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'files':records},ensure_ascii=False,indent=2))
print(json.dumps({'files':len(records),'images':sum('dimensions' in r for r in records),'largeImages':[r for r in records if 'dimensions' in r and min(r['dimensions'])>700]},ensure_ascii=False))
