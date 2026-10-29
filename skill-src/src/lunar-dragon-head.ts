import * as THREE from 'three/webgpu';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {loft,sweep} from './dragon-geometry';
type Role='shell'|'light'|'gold'|'dark'|'eye';
export type LunarPalette=Record<Role,THREE.Material>;
let topology:{geometry:THREE.BufferGeometry;role:Role}[]|undefined;
function build(){
 const buckets=new Map<Role,THREE.BufferGeometry[]>();
 const add=(role:Role,g:THREE.BufferGeometry)=>{g.deleteAttribute('uv');if(!g.index)g.setIndex(Array.from({length:g.getAttribute('position').count},(_,i)=>i));const a=buckets.get(role)||[];a.push(g);buckets.set(role,a)};
 const line=(role:Role,p:number[][],r:number)=>add(role,sweep(p,r,.001,20,7));
 // Slender icy muzzle and swept crescent horns are specific to 月璃's lunar setting.
 add('shell',loft([[-.43,.01,.065,.075],[-.25,.015,.15,.15],[-.04,.025,.17,.16],[.12,.015,.13,.145],[.29,-.015,.07,.10],[.50,.005,.055,.065],[.59,.025,.018,.035]],20));
 add('shell',loft([[-.20,-.12,.025,.085],[0,-.21,.032,.105],[.24,-.25,.027,.078],[.48,-.19,.016,.04]],16));
 add('dark',loft([[-.08,-.135,.01,.085],[.18,-.17,.009,.08],[.45,-.15,.006,.033]],12));
 for(const s of [-1,1]){
  const eye=new THREE.SphereGeometry(1,12,8);eye.scale(.047,.017,.012);eye.translate(.13,.065,s*.147);add('eye',eye);
  line('gold',[[-.06,.13,s*.125],[.13,.12,s*.17],[.27,.07,s*.12]],.016);
  // A crescent swept backwards; no gold branching antler copied from Lingyuan.
  line('gold',[[-.18,.13,s*.11],[-.31,.36,s*.18],[-.58,.53,s*.25],[-.84,.48,s*.28]],.030);
  line('light',[[-.34,.19,s*.135],[-.59,.26,s*.24],[-.83,.20,s*.30]],.018);
  for(let i=0;i<4;i++){
   const x=-.16-i*.075,y=.09-i*.045,z=s*(.12+i*.012),tip=new THREE.Vector3(x-.32-i*.02,y+.20-i*.018,z+s*.17);
   const g=new THREE.OctahedronGeometry(1,0);g.scale(.033,.20,.018);const direction=tip.clone().sub(new THREE.Vector3(x,y,z));g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),direction.normalize()));const center=tip.clone().lerp(new THREE.Vector3(x,y,z),.5);g.translate(center.x,center.y,center.z);add('light',g);
  }
  line('light',[[.43,-.07,s*.07],[.24,-.10,s*.22],[-.13,-.02,s*.32],[-.58,.04,s*.38]],.006);
  for(let i=0;i<4;i++){const x=.05+i*.11,z=s*(.105-i*.013);line('light',[[x,-.12,z],[x+.012,-.17,z],[x-.018,-.22+(i%2)*.03,z*.95]],.010)}
 }
 const crest=new THREE.OctahedronGeometry(1,0);crest.scale(.045,.14,.035);crest.translate(-.09,.19,0);add('light',crest);
 return [...buckets].map(([role,list])=>{const geometry=mergeGeometries(list)!;list.forEach(g=>g.dispose());return {role,geometry}});
}
export function makeLunarDragonHead(palette:LunarPalette){
 topology??=build();const root=new THREE.Group();root.name='月霜冰龙 · 月弧角/冰羽鳃冠';for(const p of topology){const mesh=new THREE.Mesh(p.geometry,palette[p.role]);mesh.frustumCulled=false;root.add(mesh)}return root;
}
