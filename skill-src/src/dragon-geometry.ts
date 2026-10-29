import * as THREE from 'three/webgpu';
const V=THREE.Vector3,TAU=Math.PI*2;
function indexed(pos:number[],idx:number[]){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setIndex(idx);g.computeVertexNormals();return g}
/** Closed cross-section loft; rows are [x, centerY, verticalRadius, sideRadius]. */
export function loft(rows:number[][],sides=20){
 const p:number[]=[],idx:number[]=[];
 for(const [x,y,ry,rz] of rows)for(let j=0;j<=sides;j++){const a=j/sides*TAU;p.push(x,y+ry*Math.cos(a),rz*Math.sin(a))}
 for(let i=0;i<rows.length-1;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;idx.push(a,a+1,b,b,a+1,b+1)}
 for(const end of [0,rows.length-1]){const c=p.length/3,r=rows[end];p.push(r[0],r[1],0);for(let j=0;j<sides;j++){const a=end*(sides+1)+j;if(end===0)idx.push(c,a+1,a);else idx.push(c,a,a+1)}}
 return indexed(p,idx);
}
export function sweep(points:number[][],r0:number,r1:number,steps=18,sides=8){
 const c=new THREE.CatmullRomCurve3(points.map(p=>new V(...p as [number,number,number]))),p:number[]=[],idx:number[]=[];
 const frames=c.computeFrenetFrames(steps,false);
 for(let i=0;i<=steps;i++){const u=i/steps,v=c.getPoint(u),r=r0*Math.pow(1-u,.85)+r1*u;
  for(let j=0;j<=sides;j++){const a=j/sides*TAU,q=v.clone().addScaledVector(frames.normals[i],Math.cos(a)*r).addScaledVector(frames.binormals[i],Math.sin(a)*r);p.push(q.x,q.y,q.z)}
 }
 for(let i=0;i<steps;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;idx.push(a,a+1,b,b,a+1,b+1)}
 for(const end of [0,steps]){const cidx=p.length/3,q=c.getPoint(end/steps);p.push(q.x,q.y,q.z);for(let j=0;j<sides;j++){const a=end*(sides+1)+j;if(end===0)idx.push(cidx,a+1,a);else idx.push(cidx,a,a+1)}}
 return indexed(p,idx);
}
