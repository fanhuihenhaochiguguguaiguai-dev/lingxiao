import * as THREE from 'three/webgpu';

/** Closed, consistently wound solids. Shape profiles remain skill-specific. */
function solid(positions:number[],indices:number[],faceted=false){
 let volume=0;
 for(let i=0;i<indices.length;i+=3){const a=indices[i]*3,b=indices[i+1]*3,c=indices[i+2]*3;
  volume+=(positions[a]*(positions[b+1]*positions[c+2]-positions[b+2]*positions[c+1])+positions[a+1]*(positions[b+2]*positions[c]-positions[b]*positions[c+2])+positions[a+2]*(positions[b]*positions[c+1]-positions[b+1]*positions[c]))/6;
 }
 if(volume<0)for(let i=0;i<indices.length;i+=3)[indices[i+1],indices[i+2]]=[indices[i+2],indices[i+1]];
 let geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setIndex(indices);
 if(faceted){const indexed=geometry;geometry=indexed.toNonIndexed();indexed.dispose()}
 geometry.computeVertexNormals();return geometry;
}

/** Lens section, two single-point ends: no collapsed quads or open thin sheets. */
function lens(center:(t:number)=>THREE.Vector3,side:THREE.Vector3,width:(t:number)=>number,thickness:(t:number)=>number,rows:number,sides=8){
 const v:number[]=[],f:number[]=[];const first=center(0);v.push(first.x,first.y,first.z);
 for(let i=1;i<rows;i++){
  const t=i/rows,p=center(t),tangent=center(Math.min(1,t+.001)).sub(center(Math.max(0,t-.001))).normalize(),normal=new THREE.Vector3().crossVectors(tangent,side).normalize();
  for(let j=0;j<sides;j++){const a=j/sides*Math.PI*2,q=p.clone().addScaledVector(side,Math.cos(a)*width(t)).addScaledVector(normal,Math.sin(a)*thickness(t));v.push(q.x,q.y,q.z)}
 }
 const end=v.length/3,last=center(1);v.push(last.x,last.y,last.z);
 for(let j=0;j<sides;j++){
  const k=(j+1)%sides;f.push(0,1+k,1+j,end,1+(rows-2)*sides+j,1+(rows-2)*sides+k);
  for(let i=0;i<rows-2;i++){const a=1+i*sides+j,b=1+i*sides+k;f.push(a,b,a+sides,b,b+sides,a+sides)}
 }
 return solid(v,f);
}
export function lotusPetal(profile:'frost'|'tide'){
 const frost=profile==='frost',height=frost?.62:.54,reach=frost?.54:.55,width=frost?.22:.20;
 return lens(t=>new THREE.Vector3(0,height*t,reach*t*t),new THREE.Vector3(1,0,0),t=>Math.pow(Math.sin(Math.PI*t),.7)*width,t=>Math.sin(Math.PI*t)*.014,14);
}
export function frostFeather(){
 return lens(t=>new THREE.Vector3(t*.68-.34,0,.035*Math.sin(t*Math.PI)),new THREE.Vector3(0,1,0),t=>Math.pow(Math.sin(Math.PI*t),.75)*.13*(1-.32*t),t=>.009*Math.sin(Math.PI*t),18,6);
}

/** Hexagonal prism with a real shoulder, pointed crown and sealed base. */
export function facetedCrystal(profile:'lunar'|'star'){
 const lunar=profile==='lunar',sides=6,levels=lunar?[[.08,0],[.21,.18],[.16,1]]:[[.045,0],[.18,.24],[.145,.84]],height=lunar?1.42:1.10;
 const v:number[]=[0,0,0],f:number[]=[];
 for(const [radius,y] of levels)for(let k=0;k<sides;k++){const a=k/sides*Math.PI*2;v.push(Math.cos(a)*radius,y,Math.sin(a)*radius*(lunar?1:.89))}
 const tip=v.length/3;v.push(0,height,0);
 for(let k=0;k<sides;k++){const j=(k+1)%sides;f.push(0,1+j,1+k,tip,1+2*sides+k,1+2*sides+j);
  for(let n=0;n<2;n++){const a=1+n*sides+k,b=1+n*sides+j;f.push(a,b,a+sides,b,b+sides,a+sides)}
 }
 return solid(v,f,true);
}
