from pathlib import Path
import json,struct,subprocess,hashlib,os
import numpy as np
from PIL import Image,ImageDraw,ImageOps
R=Path(__file__).resolve().parents[1];out=R/'verification/moonfall/character'
def positions(data):
 size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size]);binary=data[28+size:];mesh=next(m for m in doc['meshes'] if 'female base' in m.get('name',''))
 a=doc['accessors'][mesh['primitives'][0]['attributes']['POSITION']];view=doc['bufferViews'][a['bufferView']];offset=view.get('byteOffset',0)+a.get('byteOffset',0);return np.ndarray((a['count'],3),dtype='<f4',buffer=binary,offset=offset,strides=(view.get('byteStride',12),4)).copy()
before_data=subprocess.check_output(['git','show',os.environ.get('YUELI_BASELINE_COMMIT','c4bee71638f92cabbbff55cf5bda10e4fee597db')+':dist/yueli-study.glb'],cwd=R);after_data=(R/'dist/yueli-study.glb').read_bytes();a=positions(before_data);b=positions(after_data);assert a.shape==b.shape;delta=np.linalg.norm(a-b,axis=1);assert (delta>1e-6).sum()>1000
master=(R/'characters/qingli/Yueli_working.glb').read_bytes();assert master==after_data
report={'meshVertexPositionsChanged':int((delta>1e-6).sum()),'maximumMeshDisplacementMeters':float(delta.max()),'bodyTopologyVertexCountPreserved':len(a),'runtimeAndMasterGLBIdentical':True,'runtimeGLBSha256':hashlib.sha256(after_data).hexdigest(),'scope':'exported 3D geometry difference only; likeness and artistic quality not automatically accepted'}
(out/'export-geometry.json').write_text(json.dumps(report,indent=2))
canvas=Image.new('RGB',(1536,552),'#17202c');d=ImageDraw.Draw(canvas)
source=Image.open(R/'reference/qingli/originals/board-04.jpg');ref=source.crop((916,26,1040,158));ref=ImageOps.contain(ref,(512,512));canvas.paste(ref,((512-ref.width)//2,40))
for i,name in [(1,'before-face.png'),(2,'candidate-face.png')]:canvas.paste(Image.open(out/name).resize((512,512)),(i*512,40))
for i,label in enumerate(['DESIGN CROP (124 x 132 source; perspective)','BEFORE (fixed orthographic render)','CURRENT STUDY (same light/camera)']):d.text((i*512+12,14),label,fill='white')
canvas.save(out/'reference-before-after.png');print(json.dumps(report),flush=True)
