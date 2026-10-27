"""Crop the supplied 1280×853 reference boards into individually indexed PNGs.
Coordinates are hand-mapped from the original boards, not generated art.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import csv,hashlib,json
R=Path(__file__).resolve().parents[1];root=R/'reference/skillboards';out=root/'crops';out.mkdir(parents=True,exist_ok=True)
images={i:Image.open(root/'originals'/f'board-{i:02}.jpg').convert('RGB') for i in (1,2,3)};rows=[]
def crop(board,group,label,rect):
 im=images[board];x1,y1,x2,y2=rect;assert 0<=x1<x2<=im.width and 0<=y1<y2<=im.height,(board,group,label,rect)
 n=1+sum(r['board']==board and r['group']==group for r in rows);folder=out/f'{board:02}'/group;folder.mkdir(parents=True,exist_ok=True);file=folder/f'{n:02}_{label}.png'
 src=im.crop(rect);scale=3 if max(src.size)<500 else 2;up=src.resize((src.width*scale,src.height*scale),Image.Resampling.LANCZOS);up.save(file,optimize=True)
 rows.append({'board':board,'group':group,'label':label,'source':f'originals/board-{board:02}.jpg','rectangle':','.join(map(str,rect)),'source_pixels':f'{src.width}x{src.height}','png_pixels':f'{up.width}x{up.height}','path':str(file.relative_to(root)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
def grid_edges(board,group,labels,edges,y1,y2):
 assert len(edges)==len(labels)+1
 for label,x1,x2 in zip(labels,edges,edges[1:]):crop(board,group,label,(x1,y1,x2,y2))
def grid(board,group,labels,x1,x2,y1,y2):
 n=len(labels)
 for i,label in enumerate(labels):crop(board,group,label,(round(x1+(x2-x1)*i/n),y1,round(x1+(x2-x1)*(i+1)/n),y2))
# Board 1: portrait, hair, outfit, weapon, anatomy and skills.
grid_edges(1,'01_character',['front','side','back'],[4,177,281,421],29,279)
crop(1,'02_face','portrait',(425,30,535,265));grid(1,'02_face',['front','angle45','side'],537,777,30,159);grid(1,'02_face',['eyes','eyebrows'],537,699,161,222);crop(1,'02_face','nose',(700,161,777,263));grid(1,'02_face',['lips','ear'],537,699,223,264)
grid(1,'03_hair',['front','side','back'],784,1033,30,266);grid(1,'03_hair',['crown_front','crown_side','crown_back'],1034,1275,30,122);crop(1,'03_hair','hair_strands',(1034,124,1110,264));crop(1,'03_hair','hair_part',(1110,124,1191,202));crop(1,'03_hair','hairline',(1110,202,1191,264));crop(1,'03_hair','scalp_upper',(1192,124,1275,198));crop(1,'03_hair','scalp_back',(1192,198,1275,264))
grid(1,'04_clothing',['shoulder','collar','chest','waist','sleeve','hem'],4,455,313,403);grid(1,'04_clothing',['back','fabric','metal_a','metal_b','gem'],4,455,408,493)
grid(1,'05_weapon',['front','side','back'],464,619,311,492);grid(1,'05_weapon',['tip','shaft_pattern','dragon'],621,820,311,402);grid(1,'05_weapon',['middle','butt','crystal'],621,820,406,491)
grid(1,'06_anatomy',['front','side','back'],827,1000,310,491);crop(1,'06_anatomy','proportions',(1001,310,1069,491));grid(1,'06_anatomy',['spine','skeleton','rig'],1070,1276,310,421);grid(1,'06_anatomy',['skull','hand','foot','joints'],1070,1276,421,491)
grid(1,'07_expressions',['neutral','cold','anger','smile','shout','hurt'],4,529,523,618);grid(1,'08_poses',['idle','walk','run','jump','combat','cast_a','cast_b'],533,1276,523,618)
for group,x1,x2 in [('09_skill1',4,437),('10_skill2',442,836),('11_ultimate',840,1276)]:
 grid(1,group,['front','side','back','top','angle45','wide'],x1,x2,651,748)
 grid(1,group,['detail_01','detail_02','detail_03','detail_04','detail_05','detail_06'],x1,x2,751,847)
# Board 2.
grid(2,'01_character',['front','side','back','angle45'],4,441,30,286)
crop(2,'02_face','portrait',(446,30,548,278));grid(2,'02_face',['front','angle45','side'],550,730,30,157);grid(2,'02_face',['eye','eyelash','nose'],550,730,160,225);grid(2,'02_face',['lips','ear','ornament'],550,730,225,278)
grid(2,'03_hair',['front','side','back','angle45'],734,1008,30,158);grid(2,'03_hair',['strands','ornament','scalp','hair_root'],734,1008,160,278)
grid(2,'04_clothing',['cloth','shoulder','waist','sleeve'],1013,1276,30,138);grid(2,'04_clothing',['fabric','metal','gem','embroidery'],1013,1276,140,278)
for group,x1,x2 in [('05_skill1',4,442),('06_skill2',448,835),('07_ultimate',839,1276)]:
 grid(2,group,['front','left','right','back','angle45','top','up'],x1,x2,327,443 if group=='05_skill1' else 462)
 labels=['windup','dash','sweep','dragon','recover'] if group=='05_skill1' else ['phase_01','phase_02','phase_03','phase_04','phase_05','phase_06']
 if group=='05_skill1':
  grid_edges(2,group,labels,[4,90,180,267,357,442],456,533);grid_edges(2,group,['detail_01','detail_02','detail_03','detail_04','detail_05','detail_06'],[4,80,150,223,294,368,442],548,645)
 elif group=='06_skill2':
  grid_edges(2,group,labels,[451,528,594,654,710,772,835],473,543);grid_edges(2,group,['detail_01','detail_02','detail_03','detail_04','detail_05','detail_06'],[450,523,577,643,702,759,835],564,645)
 else:
  grid_edges(2,group,labels,[840,916,975,1058,1128,1206,1276],475,543);grid_edges(2,group,['detail_01','detail_02','detail_03','detail_04','detail_05','detail_06'],[840,918,983,1051,1118,1196,1276],565,645)
# Long spear views are separate horizontal drawings.
crop(2,'08_weapon','front',(4,683,379,723));crop(2,'08_weapon','side_back',(4,725,379,755));grid(2,'08_weapon',['tip','shaft','dragon','gem','grip','tassel'],4,380,758,846)
grid(2,'09_body',['front','side','back'],386,508,680,848);crop(2,'09_body','proportions',(509,678,576,848));grid(2,'09_body',['skeleton_front','skeleton_side','skeleton_back','rig'],578,735,678,848);grid(2,'09_body',['hand_upper','foot_upper'],736,894,679,762);grid(2,'09_body',['hand_lower','foot_lower'],736,894,763,848)
grid(2,'10_topology',['head','face','body','clothes','hair'],898,1276,678,763);grid(2,'10_topology',['face_wire','hair_wire','clothes_wire','weapon_wire','vfx_wire'],898,1276,763,848)
# Board 3.
grid(3,'01_character',['front','side','back','angle45'],4,464,28,226)
crop(3,'02_face','portrait',(468,29,585,224));grid(3,'02_face',['front','side'],588,827,29,81);grid(3,'02_face',['eyes','brows','nose'],588,827,82,143);grid(3,'02_face',['lips','ear'],588,827,145,224)
grid(3,'03_hair',['front','side','back'],831,1036,29,224);grid(3,'03_hair',['crown_front','crown_side','crown_back'],1038,1275,29,106);grid(3,'03_hair',['strands','hairline','scalp'],1038,1275,108,224)
grid(3,'04_clothing',['collar','shoulder','chest','waist','sleeve','hem'],4,464,279,345);grid(3,'04_clothing',['fabric','metal','embroidery','gem','tassel','cape'],4,464,347,417)
grid(3,'05_weapon',['front','side','back'],469,593,263,416);crop(3,'05_weapon','tip',(595,260,678,416));grid(3,'05_weapon',['shaft','dragon'],679,828,260,336);grid(3,'05_weapon',['middle','gem','butt'],679,828,338,416)
grid(3,'06_anatomy',['front','side','back'],832,998,260,416);crop(3,'06_anatomy','proportion',(999,260,1068,416));grid(3,'06_anatomy',['spine','skeleton','rig_a','rig_b'],1070,1276,260,345);grid(3,'06_anatomy',['skull','hand','foot','joints'],1070,1276,348,416)
for group,top in [('07_skill1',423),('08_skill2',591)]:
 crop(3,group,'hero_visual',(4,top+24,228,top+164));grid(3,group,['windup','motion_02','motion_03','motion_04','motion_05','recover'],231,721,top+24,top+87)
 grid(3,group,['front','side','back','angle45_left','angle45_right','top','up','wide'],231,721,top+89,top+164)
 grid(3,group,['vfx_01','vfx_02','vfx_03','vfx_04','vfx_05','vfx_06','vfx_07','vfx_08','vfx_09'],725,1275,top+24,top+87)
 grid(3,group,['vfx_10','vfx_11','vfx_12','vfx_13','vfx_14','vfx_15','vfx_16','vfx_17','vfx_18'],725,1275,top+89,top+164)
with (root/'crop-index.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rows)
(root/'crop-index.json').write_text(json.dumps({'source_dimensions':[1280,853],'crop_count':len(rows),'files':rows},ensure_ascii=False,indent=2),encoding='utf8')
(root/'README.md').write_text('# 人物与三技能参考裁切\n\n三张 1280×853 用户原图逐格裁切，采用 Lanczos 2–3 倍插值保存为 PNG；这是放大原始像素，不会恢复原图不存在的细节。分组及原始坐标见 `crop-index.csv`，原始 JPEG 保留在 originals。图片为设计参考，不是模型渲染结果。\n',encoding='utf8')
print(json.dumps({'count':len(rows),'by_board':{i:sum(x['board']==i for x in rows) for i in images},'status':'PASS_RECTS_AND_PNG_WRITE'},ensure_ascii=False))
