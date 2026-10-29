import assert from 'node:assert/strict';
import {build} from '../skill-src/node_modules/esbuild/lib/main.js';
import {pathToFileURL} from 'node:url';
import {mkdir,writeFile} from 'node:fs/promises';
const label=process.argv[2];if(!['before','after'].includes(label))throw Error('before/after required');
await build({stdin:{contents:"export {BindStar} from './skill-src/src/bind-star';export {StarVortex} from './skill-src/src/star-vortex';export {IceDragon} from './skill-src/src/ice-dragon';export * as THREE from './skill-src/node_modules/three/build/three.webgpu.js';",resolveDir:process.cwd()},bundle:true,platform:'node',format:'esm',outfile:'/tmp/dragon-promotion-probe.mjs'});
const {BindStar,StarVortex,IceDragon,THREE}=await import(pathToFileURL('/tmp/dragon-promotion-probe.mjs'));
const bind=new BindStar(new THREE.Group()),star=new StarVortex(new THREE.Group()),ice=new IceDragon(new THREE.Group()),rows={};
const layers={dragon:true,circle:true,crystals:true,beams:true,chains:true,particles:true};
function inspect(mesh,sides){const p=mesh.geometry.getAttribute('position'),n=mesh.geometry.getAttribute('normal'),centers=[];let length=0,minDot=1;const stride=sides+1;for(let i=0;i<p.count/stride;i++){const c=new THREE.Vector3();for(let j=0;j<sides;j++)c.add(new THREE.Vector3().fromBufferAttribute(p,i*stride+j));c.multiplyScalar(1/sides);if(i)length+=c.distanceTo(centers.at(-1));centers.push(c);if(i>2&&i<p.count/stride-3){const radial=new THREE.Vector3().fromBufferAttribute(p,i*stride).sub(c).normalize();minDot=Math.min(minDot,radial.dot(new THREE.Vector3().fromBufferAttribute(n,i*stride)))}}return {length,minOutwardNormalDot:minDot}}
bind.update(3.3,true,layers);rows.binding=inspect(bind.dragon.body,10);
star.update(3.2,true);rows.sovereign=inspect(star.body,10);
for(const t of [2.4,3.7,4.15,4.4,5.2]){ice.update(t,true,1,0);rows['ice-'+t]=inspect(ice.body,14)}
if(label==='after'){assert(rows.sovereign.minOutwardNormalDot>.5);assert(rows.binding.minOutwardNormalDot>.5);for(const [key,row] of Object.entries(rows))if(key.startsWith('ice-'))assert(row.length>12&&row.length<13&&row.minOutwardNormalDot>.5)}
await mkdir('verification/promotion',{recursive:true});await writeFile(`verification/promotion/${label}-geometry.json`,JSON.stringify(rows,null,2));console.log(JSON.stringify(rows));
