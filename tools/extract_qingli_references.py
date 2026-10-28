"""Extract named visual panels from four supplied sheets. Source boxes stay explicit and auditable."""
from pathlib import Path
from PIL import Image,ImageDraw
import csv,json,hashlib
root=Path(__file__).resolve().parents[1]/'reference/qingli';raw=root/'crops';up=root/'upscaled';spec=[]
def add(b,category,label,box,notes=''):
 x0,y0,x1,y1=box;assert 0<=x0<x1<=1280 and 0<=y0<y1<=853,(b,label,box)
 if b==3:
  category=('full_body' if label.startswith(('full_','body_pose')) else 'expressions' if label.startswith('expression') else 'hair' if label.startswith(('hair','profile')) else 'face' if label=='portrait' else 'features' if label=='eye_close' else 'accessories' if label=='flower_close' else 'accessories' if label in ('flower_hair','hand','boots') else 'clothing')
  notes=(notes+'; ' if notes else '')+'black-haired alternate design; excluded from primary styling'
 spec.append((b,category,label,box,notes))
def row(b,category,y0,y1,xs,labels,notes=''):
 assert len(xs)==len(labels)+1,(b,category,len(xs),len(labels))
 for i,name in enumerate(labels):add(b,category,name,(xs[i],y0,xs[i+1],y1),notes)
# The views in the full-body panoramas overlap in the source. Retain each frame with a review flag.
row(1,'full_body',0,337,[0,155,286,414,558,791],['front','side','back','angle45','motion'],'source figures or ornaments may overlap; full silhouette not isolated')
add(1,'full_body','panorama_context',(0,0,791,337),'context only, multiple overlapping views; not an isolated figure')
row(1,'face',4,197,[796,985,1111],['portrait_front','portrait_angle'])
row(1,'features',8,73,[1114,1203,1275],['eye','eye_angle'])
row(1,'features',77,144,[1114,1203,1275],['lips','profile'])
row(1,'features',148,197,[1114,1203,1275],['eyelid','cheek'])
row(1,'expressions',225,324,[796,875,955,1035,1113,1193,1275],['calm','smile','sad','surprised','angry','shy'])
row(1,'hair',382,494,[7,120,234,344,454,515,573,629,687],['front','side','back','crown','hair_layers','hair_strands','hair_ends','hair_ornament'])
row(1,'scalp',382,493,[700,798,886,982,1071,1145,1205,1275],['scalp_regions','topology','hairline','fringe','side_scalp','back_scalp_a','back_scalp_b'])
row(1,'body',530,656,[7,100,165,236,337,404,478,550],['skeleton_front','skeleton_side','skeleton_back','skull','head_skeleton','shoulder_skeleton','body_skeleton'])
add(1,'body','arm_skeleton',(550,530,650,600));row(1,'body',601,656,[550,597,650],['hand_skeleton','foot_skeleton'])
row(1,'body',530,668,[665,720,773,824,873,945],['proportions_front','proportions_45','proportions_side','proportions_back','proportions_variant'])
row(1,'body',530,639,[949,1010,1072,1131,1189,1231,1275],['neck','back','shoulder','waist','hand','foot'])
row(1,'clothing',702,827,[8,103,171,236,305,387],['complete','outer_layer','inner_layer','side_structure','back_structure'])
# The first three cells span BOTH rows. The old two-row grid cut them in half;
# keep each original tall detail intact and crop the smaller cells separately.
row(1,'clothing',702,828,[399,473,548,622],['waist_ornament','skirt_embroidery','cloak_ornament'])
row(1,'materials',702,765,[625,695,767,846],['sheer_fabric','flower','metal_ornament'])
row(1,'clothing',768,828,[625,695],['gold_embroidery'])
row(1,'accessories',702,765,[858,930,1000,1063,1110,1162,1210,1275],['crown_front','crown_side','crown_back','earring','necklace','hand','foot'])
row(1,'accessories',768,828,[858,917,974,1030,1069,1118,1169,1207,1275],['waist','hairpin','flower','tassel','metal_setting','gem_setting','blue_gem','material'])
row(1,'accessories',768,828,[695,735,790,846],['gem_tassel','blue_gem_setting','embroidered_panel'])
# Board 02 is retained as a supporting silver-haired reference.
row(2,'full_body',0,366,[116,300,441,560,724,949],['front','angle45','side','back','motion'],'source silhouettes and ribbons overlap adjacent views')
add(2,'full_body','panorama_context',(0,0,949,366),'context only, multiple overlapping views; retains the left-hand train omitted by the per-view crop')
add(2,'face','main_portrait',(950,0,1280,221));row(2,'features',232,287,[958,1037,1117,1196,1275],['eye_1','eye_2','eye_3','eye_4']);row(2,'features',310,379,[958,1037,1117,1196,1275],['mouth','closed_eye','iris','face_side'])
row(2,'expressions',405,491,[10,106,203,301,400,498,595,692,790,887,986,1083,1180,1274],['calm','smile','happy','surprised','angry','sad','cool','focused_a','focused_b','shy','gentle','thoughtful','look_back'])
row(2,'hair',537,647,[10,91,169,253,334,424,505],['front','side','back','angle45','look_down','look_up'])
row(2,'accessories',538,658,[514,602,689,797],['hairpin_metal','hairpin_flower','earrings'])
row(2,'body',538,658,[802,942,1117,1274],['neck','shoulder','bodice'])
row(2,'clothing',695,817,[10,104,201,299,395,488,580,675,774,903],['bodice','waist','skirt_layers','side_skirt','ribbon','cuff','hem_ornament','heel','back'])
row(2,'materials',695,817,[912,982,1054,1127,1200,1275],['metal','cloth','flower','gem','translucent'])
# Board 03 is the explicitly different black-haired variant: preserve for comparison, do not merge its design.
add(3,'variant','portrait',(0,0,318,484),'black-haired alternate design; not the selected main')
row(3,'variant',0,384,[319,506,628,746,865,987],['full_front','full_angle','full_side','full_back_a','full_back_b'],'black-haired alternate; some views overlap')
row(3,'variant',0,126,[997,1090,1182,1276],['hair_front','hair_side','hair_back'])
row(3,'variant',130,255,[997,1090,1182,1276],['hair_side_detail','hair_rear_detail','hair_profile'])
row(3,'variant',260,387,[997,1090,1182,1276],['hair_ornament_front','hair_ornament_back','hair_ornament_back_close'])
row(3,'variant',393,483,[530,629,726,819,913,1004,1099,1198,1276],['sleeve','chest','waist','skirt','ribbon','back_fabric','waist_gem','skirt_tail'])
row(3,'variant',486,624,[0,121,239,359,471,587,704,802,900],['expression_1','expression_2','expression_3','expression_4','expression_5','expression_6','flower_hair','side_face'],'some figures extend across original row boundaries');add(3,'variant','eye_close',(900,486,998,543));add(3,'variant','flower_close',(900,544,998,624));row(3,'variant',486,624,[1000,1110,1185,1277],['skirt_detail','legs','shoes'],'some figures extend across original row boundaries')
row(3,'variant',625,712,[0,124,239,359,474,590,702,816,925,1040,1120,1183,1277],['hair_detail_1','hair_detail_2','hair_back','hair_side','bodice','profile','hairpin','shoulder','hand','leg','skirt','boots'])
row(3,'variant',714,851,[0,115,219,322,423,526,628,733,839,941,1045,1152,1277],['body_pose_01','body_pose_02','body_pose_03','body_pose_04','body_pose_05','body_pose_06','body_pose_07','body_pose_08','body_pose_09','body_pose_10','body_pose_11','body_pose_12'],'source overlaps neighboring silhouettes')
# Board 04 and board 01 are the user's newly confirmed principal references.
row(4,'full_body',0,365,[138,300,427,531,671,909],['front','angle45','side','back','motion'],'primary silver-haired reference; silhouette overlaps')
add(4,'full_body','panorama_context',(0,0,909,365),'primary reference; context only, contains multiple overlapping views')
row(4,'face',25,159,[916,1044,1171,1276],['front','angle45','profile'])
row(4,'features',198,250,[918,996,1076,1155,1215,1276],['iris','lashes','eye_makeup','nose','lips'])
row(4,'face',271,367,[916,1152,1276],['eye_close','face_lighting'])
row(4,'expressions',402,484,[7,77,147,217,285,356,427,497,565],['calm','smile','sad','surprised','angry','cool','gentle','focused'])
row(4,'scalp',403,483,[578,669,750,825,899,965],['parting','scalp','roots','layers','section'])
row(4,'hair',403,483,[980,1054,1129,1200,1275],['front','side','back','angle45'])
row(4,'body',533,728,[7,75,127,171,238,300],['skeleton_front','skeleton_side','skeleton_back','body_front','body_back'])
row(4,'body',534,609,[303,369,424,478,540],['joints','back','arm','waist'])
row(4,'body',650,723,[303,369,424,478,540],['shoulder','pelvis','knee','knee_side'])
row(4,'body',750,823,[7,77,149,220,300,360,422,480,540],['hand','hand_bones','foot','foot_detail','knee','shoulder_joint','spine','torso'])
add(4,'clothing','overall',(551,533,658,687));row(4,'clothing',533,687,[658,718,780,849,909,969],['inner_layer','skirt_structure','ribbon','metal_details','back_layers'])
row(4,'accessories',720,823,[552,626,682,744,800,856,913,969],['hairpin','earring','necklace','waist','arm_ornament','ribbon','shoe_ornament'])
row(4,'materials',534,657,[979,1040,1100,1158,1217,1275],['sheer_cloth','metal','gem','fabric_pattern','embroidery'])
row(4,'accessories',709,823,[979,1039,1103,1167,1225,1275],['shoe_front','shoe_side','shoe_detail','leg_ornament','ankle_chain'])
source={1:'board-01.jpg',2:'board-02-main.jpg',3:'board-03-blackhair-variant.jpg',4:'board-04.jpg'};images={i:Image.open(root/'originals'/v).convert('RGB') for i,v in source.items()};rows=[];counter={}
for b,category,label,box,notes in spec:
 key=(b,category);counter[key]=counter.get(key,0)+1;name=f'{counter[key]:02}_{label}.png';rel=Path(f'board-{b:02}')/category/name;im=images[b].crop(box);scale=4 if max(im.size)<160 else 2
 (raw/rel).parent.mkdir(parents=True,exist_ok=True);(up/rel).parent.mkdir(parents=True,exist_ok=True);im.save(raw/rel,optimize=True);large=im.resize((im.width*scale,im.height*scale),Image.Resampling.LANCZOS);large.save(up/rel,optimize=True)
 rows.append({'board':b,'reference_role':('primary' if b in (1,4) else 'supporting' if b==2 else 'alternate_excluded'),'category':category,'label':label,'source':'originals/'+source[b],'box':list(box),'source_size':list(im.size),'scale':scale,'raw':'crops/'+str(rel),'upscaled':'upscaled/'+str(rel),'raw_sha256':hashlib.sha256((raw/rel).read_bytes()).hexdigest(),'status':'needs_review' if notes else 'cropped','notes':notes})
(root/'index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
with (root/'index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows)
(root/'README.md').write_text('''# 清璃参考图拆解\n\n用户最新确定角色显示名为「月璃」。`originals/board-05-yueli.jpg` 是新补充的原始设定图，保留原始像素，尚未拆图；其余路径沿用历史名称。\n\n用户最新指定第 1、4 张银白发设定为主要参考，第 2 张「清璃」保留为辅助；第 3 张黑发造型为独立变体，仅作对比，不混入主设计。新上传的两张与这两份原图的 SHA-256 完全一致，无需重制。`originals/` 保留全部原始 JPEG，`crops/` 保存原始像素 PNG，`upscaled/` 是 Lanczos 2 或 4 倍插值，未使用生成式修复，不会还原原图缺失细节。\n\n`index.csv`、`index.json` 记录每张的参考优先级、类别、原图、坐标、比例和校验值。全身、飘带等在原图中跨视图重叠，裁切标记 `needs_review`；请参阅 `overlap-audit.md`。未进行前景分离，不能声称这些区域已完全独立，也不能保证所有细节边界均自动验证。模糊纹样需人工确认。\n''',encoding='utf8')
print(json.dumps({'files':len(rows),'boards':{str(i):sum(r['board']==i for r in rows) for i in source},'review':sum(r['status']=='needs_review' for r in rows)},ensure_ascii=False))
