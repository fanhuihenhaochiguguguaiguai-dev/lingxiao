import * as THREE from 'three/webgpu';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {sweep} from './dragon-geometry';
/** Local Y is longitudinal, local Z is surface normal. Separate ornamental forms. */
export function dragonScale(kind:'binding'|'sovereign'){
 const shape=new THREE.Shape();
 if(kind==='binding'){shape.moveTo(0,.12);shape.quadraticCurveTo(.065,.035,.045,-.055);shape.lineTo(0,-.12);shape.lineTo(-.045,-.055);shape.quadraticCurveTo(-.065,.035,0,.12)}
 else{shape.moveTo(0,.14);shape.lineTo(.08,.065);shape.lineTo(.075,-.055);shape.lineTo(0,-.13);shape.lineTo(-.075,-.055);shape.lineTo(-.08,.065);shape.closePath()}
 const g=new THREE.ExtrudeGeometry(shape,{depth:kind==='binding'?.008:.016,bevelEnabled:true,bevelSize:.003,bevelThickness:.003,bevelSegments:1,steps:1,curveSegments:5});g.deleteAttribute('uv');return g;
}
/** A mirrored pair is baked in the mesh, avoiding unsupported negative instance scale. */
export function dragonLimbPair(kind:'binding'|'sovereign'|'lunar'){
 const parts:THREE.BufferGeometry[]=[],mighty=kind==='sovereign',width=mighty?.085:kind==='lunar'?.038:.048;
 for(const side of [-1,1]){
  const z=mighty?.25:kind==='lunar'?.16:.14,y=mighty?-.10:-.03,reach=mighty?.52:kind==='lunar'?.43:.36;
  parts.push(sweep([[0,y,side*z],[kind==='lunar'?.06:-.09,y-.13,side*(z+.12)],[.12,y-.29,side*reach],[.23,y-.32,side*(reach+.03)]],width,.026,18,8));
  for(let i=0;i<(mighty?4:3);i++){const s=(i-(mighty?1.5:1))*.043;parts.push(sweep([[.20,y-.32,side*(reach+s)],[.34,y-.33,side*(reach+s+.025)],[.40,y-.39,side*(reach+s+.015)]],mighty?.018:.013,.0008,12,6))}
 }
 const g=mergeGeometries(parts)!;parts.forEach(p=>p.dispose());return g;
}
