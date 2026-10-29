import * as THREE from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// Art profile for 破云·龙影斩 only. Curve transport is reusable; these anatomical
// proportions, scale arrangement and limb silhouettes are not a universal dragon.
const V=THREE.Vector3, TAU=Math.PI*2;
export const SLASH_LENGTH=3.8, NECK_OFFSET=.37;
type Role='skin'|'plate'|'gold'|'light'|'dark';
export type DragonPart={name:string;role:Role;body:boolean;geometry:THREE.BufferGeometry};
const roles:Role[]=['skin','plate','gold','light','dark'];
class Parts {
 private buckets=new Map<Role,THREE.BufferGeometry[]>();
 add(role:Role,g:THREE.BufferGeometry){g.deleteAttribute('uv');const list=this.buckets.get(role)||[];list.push(g);this.buckets.set(role,list)}
 finish(body:boolean){return roles.flatMap(role=>{const list=this.buckets.get(role);if(!list?.length)return [];const geometry=mergeGeometries(list)!;list.forEach(g=>g.dispose());return [{name:`slash ${body?'body':'head'} ${role}`,role,body,geometry}]})}
}
function indexed(pos:number[],idx:number[]){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setIndex(idx);g.computeVertexNormals();return g}
/** Closed cross-section loft; rows are [x, centerY, verticalRadius, sideRadius]. */
function loft(rows:number[][],sides=20){
 const p:number[]=[],idx:number[]=[];
 for(const [x,y,ry,rz] of rows)for(let j=0;j<=sides;j++){const a=j/sides*TAU;p.push(x,y+ry*Math.cos(a),rz*Math.sin(a))}
 for(let i=0;i<rows.length-1;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;idx.push(a,a+1,b,b,a+1,b+1)}
 for(const end of [0,rows.length-1]){const c=p.length/3,r=rows[end];p.push(r[0],r[1],0);for(let j=0;j<sides;j++){const a=end*(sides+1)+j;if(end===0)idx.push(c,a+1,a);else idx.push(c,a,a+1)}}
 return indexed(p,idx);
}
function sweep(points:number[][],r0:number,r1:number,steps=18,sides=8){
 const c=new THREE.CatmullRomCurve3(points.map(p=>new V(...p as [number,number,number]))),p:number[]=[],idx:number[]=[];
 const frames=c.computeFrenetFrames(steps,false);
 for(let i=0;i<=steps;i++){const u=i/steps,v=c.getPoint(u),r=r0*Math.pow(1-u,.85)+r1*u;
  for(let j=0;j<=sides;j++){const a=j/sides*TAU,q=v.clone().addScaledVector(frames.normals[i],Math.cos(a)*r).addScaledVector(frames.binormals[i],Math.sin(a)*r);p.push(q.x,q.y,q.z)}
 }
 for(let i=0;i<steps;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;idx.push(a,a+1,b,b,a+1,b+1)}
 for(const end of [0,steps]){const cidx=p.length/3,q=c.getPoint(end/steps);p.push(q.x,q.y,q.z);for(let j=0;j<sides;j++){const a=end*(sides+1)+j;if(end===0)idx.push(cidx,a+1,a);else idx.push(cidx,a,a+1)}}
 return indexed(p,idx);
}
function gem(at:THREE.Vector3,size:THREE.Vector3){const g=new THREE.SphereGeometry(1,12,8);g.scale(size.x,size.y,size.z);g.translate(at.x,at.y,at.z);return g}
const stations=[[0,.145,.14],[.12,.18,.17],[.22,.215,.195],[.38,.16,.145],[.52,.19,.17],[.65,.12,.10],[.82,.06,.05],[1,.004,.004]];
function radii(u:number){let k=0;while(k<stations.length-2&&u>stations[k+1][0])k++;const a=stations[k],b=stations[k+1],v=THREE.MathUtils.smoothstep(u,a[0],b[0]);return [THREE.MathUtils.lerp(a[1],b[1],v),THREE.MathUtils.lerp(a[2],b[2],v)]}
function surface(u:number,a:number,lift=0){const [ry,rz]=radii(THREE.MathUtils.clamp(u,0,1));return new V(-NECK_OFFSET-u*SLASH_LENGTH,(ry+lift)*Math.cos(a),(rz+lift)*Math.sin(a))}
/** Shield scale rests on the same shaped surface as the skin; no floating orbs. */
function scale(u:number,a:number,du:number,da:number){
 const outline=[[-.48,-.5],[.10,-.54],[.57,-.28],[.72,0],[.57,.28],[.10,.54],[-.48,.5],[-.58,0]],p:number[]=[],idx:number[]=[];
 const center=surface(u,a,.014*(1-u)+.0015);p.push(center.x,center.y,center.z);
 for(const [x,y] of outline){const q=surface(u+x*du,a+y*da,.0025);p.push(q.x,q.y,q.z)}
 const back=surface(u,a,.001);p.push(back.x,back.y,back.z);
 for(let i=0;i<8;i++){const j=1+i,k=1+(i+1)%8;idx.push(0,j,k,9,k,j)}
 return indexed(p,idx);
}
function crest(x:number,y:number,width:number,height:number){
 const p=[x+.06,y,0,x-.02,y+height,0,x-width,y+height*.42,0,x-width*.7,y-.015,0];
 // Give the crest a true thickness, rather than a camera-facing triangle.
 const pts:number[]=[],idx:number[]=[];for(const side of [-1,1])for(let i=0;i<4;i++)pts.push(p[i*3],p[i*3+1],side*.009);
 idx.push(0,2,1,0,3,2,4,5,6,4,6,7);for(let i=0;i<4;i++){const j=(i+1)%4;idx.push(i,j,i+4,j,j+4,i+4)}return indexed(pts,idx);
}
const skullRows=[[-.46,0,.065,.075],[-.34,.015,.13,.14],[-.20,.02,.195,.19],[-.02,.025,.20,.195],[.13,.005,.16,.18],[.26,-.025,.09,.125],[.40,-.025,.075,.11],[.51,-.005,.07,.09],[.57,.015,.025,.055]];
function headPlate(x:number,a:number,dx:number,da:number){
 const surfaceAt=(x:number,a:number,lift:number)=>{let i=0;while(i<skullRows.length-2&&x>skullRows[i+1][0])i++;const l=skullRows[i],r=skullRows[i+1],t=THREE.MathUtils.clamp((x-l[0])/(r[0]-l[0]),0,1);return new V(x,THREE.MathUtils.lerp(l[1],r[1],t)+(THREE.MathUtils.lerp(l[2],r[2],t)+lift)*Math.cos(a),(THREE.MathUtils.lerp(l[3],r[3],t)+lift)*Math.sin(a))};
 const outline=[[-.5,-.5],[.15,-.52],[.6,0],[.15,.52],[-.5,.5],[-.65,0]],p:number[]=[],idx:number[]=[];
 for(const q of [surfaceAt(x,a,.016),...outline.map(([u,v])=>surfaceAt(x+u*dx,a+v*da,.003)),surfaceAt(x,a,.001)])p.push(q.x,q.y,q.z);
 for(let i=0;i<6;i++){const j=1+i,k=1+(i+1)%6;idx.push(0,k,j,7,j,k)}return indexed(p,idx);
}
export function buildSlashDragonParts():DragonPart[]{
 const head=new Parts(),body=new Parts();
 head.add('skin',loft(skullRows,24));
 for(let row=0;row<5;row++)for(const a of [-.65,0,.65])head.add('plate',headPlate(-.29+row*.072,a,.082,.72));
 for(const side of [-1,1])for(let row=0;row<3;row++)head.add('plate',headPlate(-.32+row*.065,side*1.55,.076,.55));
 head.add('plate',sweep([[.40,.032,0],[.42,.12,0],[.48,.16,0]],.028,.001,12,8));
 head.add('skin',loft([[-.22,-.14,.035,.105],[-.05,-.22,.045,.15],[.18,-.30,.04,.125],[.39,-.295,.035,.09],[.56,-.20,.025,.05]],18));
 head.add('dark',loft([[-.12,-.16,.01,.11],[.12,-.205,.016,.115],[.38,-.195,.01,.08],[.55,-.16,.006,.04]],12));
 for(const s of [-1,1]){
  head.add('dark',gem(new V(.13,.07,s*.167),new V(.061,.029,.018)));
  head.add('light',gem(new V(.145,.075,s*.185),new V(.041,.016,.011)));
  head.add('dark',gem(new V(.16,.075,s*.196),new V(.004,.014,.004)));
  head.add('dark',gem(new V(.50,.022,s*.079),new V(.033,.015,.012)));
  head.add('gold',sweep([[-.07,.135,s*.175],[.08,.125,s*.203],[.25,.08,s*.16],[.35,.045,s*.12]],.024,.003));
  head.add('gold',sweep([[-.2,.15,s*.14],[-.30,.31,s*.2],[-.46,.50,s*.27],[-.66,.64,s*.34]],.043,.0015,24));
  head.add('gold',sweep([[-.39,.43,s*.25],[-.37,.57,s*.32],[-.43,.66,s*.38]],.025,.001,14));
  head.add('gold',sweep([[-.27,.28,s*.19],[-.43,.32,s*.34],[-.62,.40,s*.40]],.023,.001,14));
  head.add('light',sweep([[.53,-.085,s*.09],[.39,-.12,s*.26],[.04,-.05,s*.39],[-.46,.03,s*.47]],.009,.001,28,6));
  head.add('light',sweep([[.28,-.27,s*.11],[.14,-.38,s*.23],[-.15,-.35,s*.32],[-.48,-.31,s*.38]],.008,.001,22,6));
  for(let k=0;k<5;k++){
   const y=.14-k*.065,z=s*(.15+k*.012);
   head.add(k%3===0?'gold':'plate',sweep([[-.20,y,z],[-.42,y+.10,z+s*.07],[-.65-k*.06,y+.12-k*.035,z+s*.12],[-.9-k*.05,y+.06-k*.045,z+s*.15]],.026-k*.002,.0008,18,6));
  }
  for(let i=0;i<5;i++){
   const x=.04+i*.095,z=s*(.13-i*.013),length=i===1?.13:.050+i*.003;
   head.add('light',sweep([[x,-.13,z],[x+.012,-.16-length*.5,z],[x-.012,-.13-length,z*.94]],.012,.0004,10,7));
   if(i<4)head.add('light',sweep([[x+.035,-.275,z*.87],[x+.02,-.25,z*.86],[x+.018,-.225,z*.85]],.010,.0004,9,7));
  }
 }
 for(let i=0;i<5;i++)head.add('plate',crest(-.05-i*.12,.17-i*.014,.18,.12+i*.009));
 // Chest, waist, haunches and long taper are one connected skin surface.
 const p:number[]=[],idx:number[]=[],n=80,sides=20;
 for(let i=0;i<=n;i++)for(let j=0;j<=sides;j++){const q=surface(i/n,j/sides*TAU);p.push(q.x,q.y,q.z)}
 for(let i=0;i<n;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;idx.push(a,b,a+1,b,b+1,a+1)}
 // The neck cap is buried in the skull; the tapered tail has a closed endpoint.
 for(const end of [0,n]){const c=p.length/3;p.push(-NECK_OFFSET-end/n*SLASH_LENGTH,0,0);for(let j=0;j<sides;j++){const a=end*(sides+1)+j;if(end===0)idx.push(c,a,a+1);else idx.push(c,a+1,a)}}
 body.add('skin',indexed(p,idx));
 for(let row=0;row<38;row++)for(let col=0;col<10;col++){
  const u=.025+row*.024,a=(col+(row%2)*.5)/10*TAU;
  if(Math.cos(a)<-.77)continue; // ventral scutes use an independent broad structure
  body.add(row%9===2&&col%3===0?'gold':'plate',scale(u,a,.029,.72));
 }
 for(let row=0;row<31;row++)body.add('light',scale(.035+row*.028,Math.PI,.033,1.65));
 for(let row=0;row<22;row++){const u=.035+row*.041,[r]=radii(u);body.add(row%5===0?'gold':'plate',crest(-NECK_OFFSET-u*SLASH_LENGTH,r-.008,.20*(1-u)+.05,.17*(1-u)+.015))}
 // Four articulated-looking limbs, hooked digits and claws, rooted in shoulders/haunches.
 for(const rear of [false,true])for(const side of [-1,1]){
  const u=rear?.52:.20,x=-NECK_OFFSET-u*SLASH_LENGTH,z=side*(rear?.155:.18),wrist=x+(rear?.04:.25);
  body.add('skin',sweep([[x,-.01,z],[x-(rear?.19:.09),-.11,z+side*.13],[wrist-.10,-.30,z+side*.23],[wrist,-.36,z+side*.29]],rear?.083:.065,.033,20,10));
  body.add('plate',sweep([[x+.02,.015,z],[x-.05,-.03,z+side*.10],[wrist-.13,-.22,z+side*.22]],.035,.011,14,7));
  for(let finger=0;finger<4;finger++){
   const offset=(finger-1.5)*.037,tip=wrist+.20-Math.abs(finger-1.5)*.03,zz=z+side*(.28+offset);
   body.add('skin',sweep([[wrist-.02,-.35,zz],[wrist+.075,-.38,zz+side*.025],[tip,-.365,zz+side*.06]],.021,.009,10,7));
   body.add('light',sweep([[tip-.015,-.365,zz+side*.055],[tip+.06,-.35,zz+side*.065],[tip+.075,-.40,zz+side*.066]],.012,.0005,9,6));
  }
 }
 // Split tail vane continues the actual body taper instead of ending in a blunt tube.
 for(const side of [-1,1])body.add('plate',sweep([[-3.65,.015,side*.045],[-3.93,.10,side*.09],[-4.20,.10,side*.12],[-4.35,.035,side*.1]],.031,.001,18,7));
 return [...head.finish(false),...body.finish(true)];
}

type Frame={p:THREE.Vector3;x:THREE.Vector3;y:THREE.Vector3;z:THREE.Vector3};
const template=buildSlashDragonParts(); // immutable CPU templates; GPU copies belong to each cast
export class SlashDragon {
 readonly group=new THREE.Group();readonly head=new THREE.Group();
 private meshes:{mesh:THREE.Mesh;rest:Float32Array;normals:Float32Array}[]=[];
 private frames:Frame[]=Array.from({length:65},()=>({p:new V(),x:new V(1,0,0),y:new V(0,1,0),z:new V(0,0,1)}));
 private materials:Record<Role,THREE.MeshStandardMaterial>;
 constructor(){
  this.group.name='破云龙体 · 肩腰四肢叠鳞尾鳍';this.head.name='破云龙首 · 独立造型';
  this.materials={skin:new THREE.MeshStandardMaterial({color:0x174c8a,emissive:0x082653,emissiveIntensity:.30,metalness:.35,roughness:.32}),plate:new THREE.MeshStandardMaterial({color:0x428cc6,emissive:0x0b3d76,emissiveIntensity:.28,metalness:.48,roughness:.26}),gold:new THREE.MeshStandardMaterial({color:0xc6a15d,emissive:0x39230b,emissiveIntensity:.20,metalness:.8,roughness:.3}),light:new THREE.MeshStandardMaterial({color:0xa0d7e7,emissive:0x26658b,emissiveIntensity:.55,metalness:.3,roughness:.23}),dark:new THREE.MeshStandardMaterial({color:0x050f24,roughness:.52})};
  for(const material of Object.values(this.materials))material.transparent=true;
  for(const part of template){const geo=part.geometry.clone(),mesh=new THREE.Mesh(geo,this.materials[part.role]);mesh.name=part.name;mesh.frustumCulled=false;(part.body?this.group:this.head).add(mesh);
   if(part.body){const position=geo.getAttribute('position') as THREE.BufferAttribute,normal=geo.getAttribute('normal') as THREE.BufferAttribute;position.setUsage(THREE.DynamicDrawUsage);normal.setUsage(THREE.DynamicDrawUsage);this.meshes.push({mesh,rest:part.geometry.getAttribute('position').array as Float32Array,normals:part.geometry.getAttribute('normal').array as Float32Array})}
  }
 }
 /** Arc-length resampling avoids body collapse while the spear/head waits in windup. */
 update(t:number,phase:number,head:THREE.Vector3,forward:THREE.Vector3,path:(time:number)=>THREE.Vector3){
  const points=[head.clone()],lengths=[0];let total=0;
  for(let k=1;k<=256;k++){
   const age=t-k*.02,point=t<=.95?head.clone().add(new V(-k*.06,0,0)):age>=.95?path(age):path(.95).add(new V((age-.95)*3,0,0));
   total+=point.distanceTo(points[k-1]);points.push(point);lengths.push(total);
  }
  const endDir=points.at(-1)!.clone().sub(points.at(-2)!).normalize();if(endDir.lengthSq()<.5)endDir.copy(forward).negate();
  const at=(distance:number)=>{
   if(distance>=total)return points.at(-1)!.clone().addScaledVector(endDir,distance-total);
   let k=1;while(lengths[k]<distance)k++;return points[k-1].clone().lerp(points[k],(distance-lengths[k-1])/Math.max(1e-7,lengths[k]-lengths[k-1]));
  };
  for(let i=0;i<this.frames.length;i++){
   const f=this.frames[i],s=i/64,distance=NECK_OFFSET+s*SLASH_LENGTH;f.p.copy(at(distance));
   // Blend the neck into head-forward before the history tangent takes over.
   f.x.copy(at(Math.max(0,distance-.018))).sub(at(distance+.018)).normalize();if(f.x.lengthSq()<.5)f.x.copy(forward);
   if(i<4)f.x.lerp(forward,(1-i/4)*.8).normalize();
   if(i===0){f.z.crossVectors(f.x,new V(0,1,0));if(f.z.lengthSq()<1e-5)f.z.crossVectors(f.x,new V(0,0,1));f.z.normalize();f.y.crossVectors(f.z,f.x).normalize()}
   else{const prev=this.frames[i-1],q=new THREE.Quaternion().setFromUnitVectors(prev.x,f.x);f.y.copy(prev.y).applyQuaternion(q);f.z.crossVectors(f.x,f.y).normalize();f.y.crossVectors(f.z,f.x).normalize()}
   const upright=new V(0,1,0).addScaledVector(f.x,-f.x.y);if(upright.lengthSq()>.04){f.y.copy(upright).normalize();f.z.crossVectors(f.x,f.y).normalize();f.y.crossVectors(f.z,f.x).normalize()}
  }
  for(const {mesh,rest,normals} of this.meshes){
   const p=mesh.geometry.getAttribute('position') as THREE.BufferAttribute,n=mesh.geometry.getAttribute('normal') as THREE.BufferAttribute;
   for(let v=0;v<p.count;v++){
    const j=v*3,u=THREE.MathUtils.clamp((-rest[j]-NECK_OFFSET)/SLASH_LENGTH,0,1)*64,lo=Math.min(63,Math.floor(u)),a=this.frames[lo],b=this.frames[lo+1],w=u-lo;
    const y=rest[j+1],z=rest[j+2],px=THREE.MathUtils.lerp(a.p.x,b.p.x,w),py=THREE.MathUtils.lerp(a.p.y,b.p.y,w),pz=THREE.MathUtils.lerp(a.p.z,b.p.z,w);
    const xx=a.x.x+(b.x.x-a.x.x)*w,xy=a.x.y+(b.x.y-a.x.y)*w,xz=a.x.z+(b.x.z-a.x.z)*w;
    const yx=a.y.x+(b.y.x-a.y.x)*w,yy=a.y.y+(b.y.y-a.y.y)*w,yz=a.y.z+(b.y.z-a.y.z)*w;
    const zx=a.z.x+(b.z.x-a.z.x)*w,zy=a.z.y+(b.z.y-a.z.y)*w,zz=a.z.z+(b.z.z-a.z.z)*w;
    const residual=rest[j]-(-NECK_OFFSET-THREE.MathUtils.clamp((-rest[j]-NECK_OFFSET)/SLASH_LENGTH,0,1)*SLASH_LENGTH);
    p.setXYZ(v,px+yx*y+zx*z+xx*residual,py+yy*y+zy*z+xy*residual,pz+yz*y+zz*z+xz*residual);
    const nx=xx*normals[j]+yx*normals[j+1]+zx*normals[j+2],ny=xy*normals[j]+yy*normals[j+1]+zy*normals[j+2],nz=xz*normals[j]+yz*normals[j+1]+zz*normals[j+2],r=1/Math.max(1e-8,Math.hypot(nx,ny,nz));n.setXYZ(v,nx*r,ny*r,nz*r);
   }p.needsUpdate=true;n.needsUpdate=true;
  }
  for(const m of Object.values(this.materials))m.opacity=phase
 }
 center(u:number){const x=THREE.MathUtils.clamp(u,0,1)*64,i=Math.min(63,Math.floor(x));return this.frames[i].p.clone().lerp(this.frames[i+1].p,x-i)}
 sample(){return {bodyLength:SLASH_LENGTH,limbs:4,scalePlates:285,ventralScutes:31,frames:this.frames.map(f=>({p:f.p.toArray(),x:f.x.toArray(),y:f.y.toArray(),z:f.z.toArray()}))}}
}
