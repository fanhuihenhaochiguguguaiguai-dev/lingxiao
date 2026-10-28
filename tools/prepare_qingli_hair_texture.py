"""Create a silver-blue CC0 long-hair color map while preserving its alpha.

The source is a generic MakeHuman asset, not the supplied design. This color
conversion does not create missing design detail.
"""
from pathlib import Path
from PIL import Image
import numpy as np

root=Path(__file__).resolve().parents[1]/'reference/makehuman'
im=Image.open(root/'long01_diffuse.png').convert('RGBA')
arr=np.asarray(im,dtype=np.uint8).copy()
rgb=arr[:,:,:3].astype(np.float32)
lum=rgb[:,:,0]*.2126+rgb[:,:,1]*.7152+rgb[:,:,2]*.0722
# Keep variations from real texture rather than increasing saturation or glow.
base=np.clip(135+lum*.72,0,238)
arr[:,:,0]=np.clip(base*.90,0,255).astype(np.uint8)
arr[:,:,1]=np.clip(base*.94,0,255).astype(np.uint8)
arr[:,:,2]=np.clip(base*1.04,0,255).astype(np.uint8)
Image.fromarray(arr,'RGBA').save(root/'long01_silver_study.png',optimize=True)
