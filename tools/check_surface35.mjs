import {build} from '../skill-src/node_modules/esbuild/lib/main.js';
import {writeFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const mode=process.argv[2];assert(['before','after'].includes(mode));
globalThis.location={search:''};
await build({stdin:{contents:"export {MoonFrost} from './skill-src/src/moon-frost';export {lunarGeometry} from './skill-src/src/moon-tide';export {BindStar} from './skill-src/src/bind-star';export * as THREE from './skill-src/node_modules/three/build/three.webgpu.js'",resolveDir:process.cwd()},bundle:true,platform:'node',format:'esm',outfile:'/tmp/surface35-runtime.mjs'});
const {MoonFrost,lunarGeometry,BindStar,THREE}=await import('file:///tmp/surface35-runtime.mjs?'+Date.now());
const frost=new MoonFrost(new THREE.Group()),bind=new BindStar(new THREE.Group());
const geos={frostPetal:frost.bloom.children[0].geometry,feather:frost.feathers.geometry,tidePetal:lunarGeometry.petal,lunarCrystal:lunarGeometry.crystal,starCrystal:bind.layers.crystals.children[0].children[0].geometry};
function audit(g){const p=g.attributes.position,ids=g.index?[...g.index.array]:Array.from({length:p.count},(_,i)=>i),weld=new Map(),keys=[],points=[];
 for(let i=0;i<p.count;i++){const a=[p.getX(i),p.getY(i),p.getZ(i)],key=a.map(x=>Math.round(x*1e7)).join(',');if(!weld.has(key)){weld.set(key,weld.size);points.push(a)}keys.push(weld.get(key))}
 const edges=new Map();let degenerate=0,volume=0,minNormal=1;
 for(let i=0;i<ids.length;i+=3){const a=new THREE.Vector3().fromBufferAttribute(p,ids[i]),b=new THREE.Vector3().fromBufferAttribute(p,ids[i+1]),c=new THREE.Vector3().fromBufferAttribute(p,ids[i+2]);const cross=b.clone().sub(a).cross(c.clone().sub(a));if(cross.length()<1e-10){degenerate++;continue}volume+=a.dot(b.clone().cross(c))/6;
 for(let k=0;k<3;k++){const u=keys[ids[i+k]],v=keys[ids[i+(k+1)%3]],key=[Math.min(u,v),Math.max(u,v)].join(':');const e=edges.get(key)||{count:0,direction:0};e.count++;e.direction+=u<v?1:-1;edges.set(key,e)}
 }
 for(const n of g.attributes.normal.array)assert(Number.isFinite(n));
 return {vertices:p.count,triangles:ids.length/3,degenerate,boundaryEdges:[...edges.values()].filter(e=>e.count===1).length,nonManifoldEdges:[...edges.values()].filter(e=>e.count>2).length,inconsistentEdges:[...edges.values()].filter(e=>e.count===2&&e.direction!==0).length,signedVolume:volume};
}
const report=Object.fromEntries(Object.entries(geos).map(([k,g])=>[k,audit(g)]));
if(mode==='after')for(const [name,r] of Object.entries(report)){assert.equal(r.boundaryEdges,0,name);assert.equal(r.nonManifoldEdges,0,name);assert.equal(r.inconsistentEdges,0,name);assert.equal(r.degenerate,0,name);assert(r.signedVolume>0,name)}
await mkdir('verification/v35/surfaces',{recursive:true});await writeFile('verification/v35/surfaces/'+mode+'.json',JSON.stringify(report,null,2));
await writeFile('/tmp/surface35-'+mode+'.json',JSON.stringify(Object.entries(geos).map(([role,g])=>({role,positions:[...g.attributes.position.array],normals:[...g.attributes.normal.array],indices:g.index?[...g.index.array]:Array.from({length:g.attributes.position.count},(_,i)=>i)}))));
console.log(mode,report);
