"""Original periodic lunar albedo and tangent normal maps for the real 3D moon mesh.
Procedural surface interpretation, not recovered reference pixels.
"""
from pathlib import Path
import numpy as np
from scipy.ndimage import zoom,gaussian_filter
from PIL import Image
R=Path(__file__).resolve().parents[1];out=R/'dist/skill/assets';out.mkdir(exist_ok=True);rng=np.random.default_rng(3607);h,w=1024,2048
y,x=np.mgrid[0:h,0:w];height=np.zeros((h,w),dtype=np.float32)
for cells,weight in [(16,.12),(32,.07),(64,.035),(128,.018)]:
 base=rng.normal(size=(cells//2,cells));layer=zoom(base,(h/base.shape[0],w/base.shape[1]),order=3,mode='wrap');height+=layer[:h,:w]*weight
maria=gaussian_filter(height,18,mode='wrap');maria=(maria-np.percentile(maria,4))/(np.percentile(maria,96)-np.percentile(maria,4));rim=np.zeros_like(height)
for i in range(380):
 cx=rng.uniform(0,w);cy=rng.uniform(30,h-30);radius=rng.uniform(5,48) if i<350 else rng.uniform(40,95);dx=np.minimum(abs(x-cx),w-abs(x-cx));dy=y-cy;dist=np.sqrt(dx*dx+dy*dy);u=dist/radius;crater=-.20*np.exp(-u**4*3.0);lip=.12*np.exp(-((u-.94)/.13)**2);height+=crater+lip;rim+=lip
height=gaussian_filter(height,.65,mode='wrap');value=np.clip(.57+height*.58+(maria-.5)*.22+rim*.30,.17,.92)
color=np.stack([value*.82,value*.92,value*1.06],axis=-1);Image.fromarray(np.uint8(np.clip(color,0,1)*255)).save(out/'lunar-surface-color.webp',quality=94)
dy,dx=np.gradient(height);normal=np.stack([-dx*13,-dy*13,np.ones_like(height)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);Image.fromarray(np.uint8((normal*.5+.5)*255)).save(out/'lunar-surface-normal.webp',lossless=True)
print('LUNAR_SURFACE_READY',w,h,flush=True)
