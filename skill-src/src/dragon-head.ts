import * as THREE from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// One sculptural head shared by the three skills. +X is forward. The components
// are solid meshes; merging per material keeps their draw-call cost bounded.
type Palette={shell:THREE.Material;light:THREE.Material;gold:THREE.Material;dark:THREE.Material;eye:THREE.Material};
const V=THREE.Vector3;
function tapered(points:THREE.Vector3[],start:number,end:number){
 const curve=new THREE.CatmullRomCurve3(points),steps=28,sides=7,vertices:number[]=[],indices:number[]=[];
 for(let i=0;i<=steps;i++){const t=i/steps,p=curve.getPoint(t),tan=curve.getTangent(t).normalize();let n=new V().crossVectors(tan,new V(0,0,1)).normalize();if(n.lengthSq()<.1)n.set(0,1,0);const b=new V().crossVectors(tan,n).normalize(),r=start*(1-t)+end*t;
  for(let j=0;j<=sides;j++){const a=j/sides*Math.PI*2,q=p.clone().addScaledVector(n,Math.cos(a)*r).addScaledVector(b,Math.sin(a)*r);vertices.push(q.x,q.y,q.z)}
 }
 for(let i=0;i<steps;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;indices.push(a,a+1,b,b,a+1,b+1)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));g.setIndex(indices);g.computeVertexNormals();return g;
}
function sections(rows:number[][]){
 const sides=12,pos:number[]=[],idx:number[]=[];
 for(const [x,y,ry,rz] of rows)for(let j=0;j<=sides;j++){const a=j/sides*Math.PI*2;pos.push(x,y+Math.cos(a)*ry,Math.sin(a)*rz)}
 for(let i=0;i<rows.length-1;i++)for(let j=0;j<sides;j++){const a=i*(sides+1)+j,b=a+sides+1;idx.push(a,b,a+1,b,b+1,a+1)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setIndex(idx);g.computeVertexNormals();return g;
}
function fin(points:THREE.Vector3[],thickness:number){
 const p:number[]=[],idx:number[]=[];for(const side of [-1,1])for(const v of points)p.push(v.x,v.y,v.z+side*thickness);
 const n=points.length;for(let i=1;i<n-1;i++){idx.push(0,i+1,i,n,n+i,n+i+1)}for(let i=0;i<n;i++){const j=(i+1)%n;idx.push(i,j,n+i,j,n+j,n+i)}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setIndex(idx);g.computeVertexNormals();return g;
}
export function makeDragonHead(p:Palette){
 const root=new THREE.Group();root.name='龙首 · 立体头骨角鬃牙须';
 const buckets=new Map<THREE.Material,THREE.BufferGeometry[]>();
 function add(g:THREE.BufferGeometry,m:THREE.Material,at=new V(),rot=new THREE.Euler(),scale=new V(1,1,1)){g.applyMatrix4(new THREE.Matrix4().compose(at,new THREE.Quaternion().setFromEuler(rot),scale));const list=buckets.get(m)||[];list.push(g);buckets.set(m,list)}
 function strand(pts:number[][],r:number,mat=p.light){add(tapered(pts.map(a=>new V(a[0],a[1],a[2])),r,.0015),mat)}
 // High cheekbones, long tapered snout and separate lower jaw form an open maw.
 add(sections([[-.40,.01,.07,.09],[-.29,.02,.19,.20],[-.08,.035,.23,.23],[.10,.015,.19,.20],[.29,-.04,.12,.15],[.50,-.075,.09,.12],[.62,-.08,.05,.075]]),p.shell);
 add(sections([[-.18,-.15,.035,.13],[.02,-.24,.055,.15],[.25,-.27,.045,.13],[.48,-.245,.04,.095],[.57,-.20,.025,.06]]),p.shell);
 add(sections([[-.13,-.135,.014,.13],[.08,-.17,.016,.15],[.37,-.17,.015,.11],[.55,-.16,.01,.06]]),p.dark);
 for(const s of [-1,1]){
  // Angular brows, eye sockets and nostrils give a readable face at game distance.
  add(new THREE.SphereGeometry(.043,12,8),p.eye,new V(.12,.085,s*.19),new THREE.Euler(),new V(1,.68,.5));
  add(new THREE.SphereGeometry(.022,10,7),p.dark,new V(.50,-.035,s*.105),new THREE.Euler(),new V(1,.65,.5));
  strand([[-.05,.16,s*.18],[.08,.17,s*.235],[.23,.11,s*.20],[.37,.045,s*.145]],.027,p.gold);
  // Antler-like swept horns and forks have thick roots and tapered tips.
  strand([[-.17,.16,s*.14],[-.29,.34,s*.22],[-.49,.43,s*.32],[-.68,.45,s*.37]],.047,p.gold);
  strand([[-.38,.38,s*.27],[-.40,.55,s*.32],[-.53,.62,s*.36]],.028,p.gold);
  strand([[-.22,.30,s*.20],[-.30,.45,s*.15],[-.33,.56,s*.16]],.022,p.gold);
  // Long whiskers, a pair of cheek fins and layered flowing mane silhouettes.
  strand([[.43,-.12,s*.10],[.52,-.13,s*.21],[.69,-.06,s*.32],[.81,.02,s*.37]],.013);
  strand([[.24,-.18,s*.14],[.30,-.30,s*.25],[.47,-.38,s*.33]],.011);
  for(let k=0;k<3;k++){const y=.11-k*.13,z=s*(.18+k*.015);add(fin([new V(-.18,y,z),new V(-.46,y+.16,z+s*.09),new V(-.77-k*.09,y+.19-k*.04,z+s*.13),new V(-.49,y-.06,z+s*.08)],.012),k===1?p.shell:p.light)}
  for(let k=0;k<4;k++){const y=.18-k*.105,z=s*(.13+k*.045);strand([[-.22,y,z],[-.47,y+.10,z+s*.08],[-.88-k*.08,y+.04-k*.06,z+s*.16]],.012,k===1?p.gold:p.light)}
  for(let i=0;i<5;i++){const x=.01+i*.105,z=s*(.145-i*.012);add(new THREE.ConeGeometry(.026,.115,6),p.light,new V(x,-.175,z),new THREE.Euler(0,0,Math.PI));if(i<4)add(new THREE.ConeGeometry(.021,.075,6),p.light,new V(x+.04,-.235,z*.92));}
 }
 for(let i=0;i<4;i++){const x=-.34-i*.115,y=.18-i*.018;add(fin([new V(x,y,0),new V(x-.13,y+.23,0),new V(x-.28,y+.20,0),new V(x-.18,y-.02,0)],.018),i%2?p.shell:p.light)}
 for(const [material,geometries] of buckets){const geometry=mergeGeometries(geometries);if(geometry){const mesh=new THREE.Mesh(geometry,material);mesh.frustumCulled=false;root.add(mesh)}geometries.forEach(g=>g.dispose())}
 return root;
}
// Maintain world-up for horns and jaw while following the direction of travel.
export function orientDragonHead(head:THREE.Object3D,direction:THREE.Vector3){
 const x=direction.clone().normalize();let z=new V().crossVectors(x,new V(0,1,0));if(z.lengthSq()<.0001)z.crossVectors(x,new V(0,0,1));z.normalize();const y=new V().crossVectors(z,x).normalize();head.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x,y,z));
}
