import {build} from '../skill-src/node_modules/esbuild/lib/main.js';
import {pathToFileURL} from 'node:url';
import {writeFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const dest='/tmp/ling-dragon32-test.mjs';
await build({stdin:{contents:"export {DragonEffect} from './skill-src/src/dragon'; export {buildSlashDragonParts,SLASH_LENGTH} from './skill-src/src/slash-dragon'; export * as THREE from './skill-src/node_modules/three/build/three.webgpu.js';",resolveDir:process.cwd()},bundle:true,platform:'node',format:'esm',outfile:dest});
const {DragonEffect,buildSlashDragonParts,SLASH_LENGTH,THREE}=await import(pathToFileURL(dest));
const out='verification/dragon32';await mkdir(out,{recursive:true});
const parts=buildSlashDragonParts();
for(const part of parts){const p=part.geometry.getAttribute('position'),n=part.geometry.getAttribute('normal');assert([...p.array,...n.array].every(Number.isFinite));for(let i=0;i<n.count;i++)assert(Math.abs(Math.hypot(n.getX(i),n.getY(i),n.getZ(i))-1)<.002);}
const root=new THREE.Group(),a=new DragonEffect(root),b=new DragonEffect(root),binding=new DragonEffect(root,'binding');assert.equal(binding.sample(),null);
const rows=[];
for(const t of [.08,.35,.8,1.1,1.45,1.8,2.2,2.6,3.15,3.8,4.3]){
 a.update(t,true);const sample=a.sample();assert.equal(sample.limbs,4);assert.equal(sample.scalePlates,285);
 let length=0,maxFrameError=0,minUp=1;
 for(let i=0;i<sample.frames.length;i++){
  const f=sample.frames[i],x=new THREE.Vector3(...f.x),y=new THREE.Vector3(...f.y),z=new THREE.Vector3(...f.z);
  minUp=Math.min(minUp,y.y);
  maxFrameError=Math.max(maxFrameError,Math.abs(x.dot(y)),Math.abs(x.dot(z)),Math.abs(y.dot(z)),Math.abs(x.length()-1),Math.abs(y.length()-1),Math.abs(z.length()-1));
  if(i)length+=new THREE.Vector3(...f.p).distanceTo(new THREE.Vector3(...sample.frames[i-1].p));
 }
 assert(minUp>=-1e-6,`inverted claws at ${t}`);assert(maxFrameError<1e-5);assert(length>SLASH_LENGTH*.85&&length<SLASH_LENGTH*1.02,`collapsed or stretched at ${t}: ${length}`);
 a.group.traverse(o=>{if(o.isMesh){const p=o.geometry.getAttribute('position');assert([...p.array].every(Number.isFinite));}});
 rows.push({time:t,centerlineLength:length,maxFrameError,minUp});
}
a.update(1.4,true);b.update(.4,true);const before=[];a.group.traverse(o=>{if(o.isMesh)before.push([...o.geometry.getAttribute('position').array]);});b.update(2.6,true);let index=0;a.group.traverse(o=>{if(o.isMesh)assert.deepEqual([...o.geometry.getAttribute('position').array],before[index++]);});
// Check a dense time sample for frame/shape discontinuities, including the dash turn.
let maxStep=0,previous=null;
for(let t=.1;t<4.3;t+=1/120){a.update(t,true);const current=a.sample().frames;if(previous)for(let i=0;i<current.length;i++)maxStep=Math.max(maxStep,new THREE.Vector3(...current[i].p).distanceTo(new THREE.Vector3(...previous[i].p)));previous=current;}
assert(maxStep<.25,`discontinuous curve transport ${maxStep}`);
const summary={status:'PASS_GEOMETRY_AND_CURVE_ONLY',parts:parts.map(p=>({name:p.name,vertices:p.geometry.getAttribute('position').count,triangles:p.geometry.index.count/3})),frameChecks:rows,maxCenterlineStepAt120Hz:maxStep,independentDynamicBuffers:true,bindingProfileUnchanged:true,artAccepted:false,phoneTested:false};
await writeFile(out+'/geometry.json',JSON.stringify(summary,null,2));
// Portable Blender input, including true closed mesh geometry, not a render card.
await writeFile('/tmp/dragon32-master.json',JSON.stringify(parts.map(p=>({name:p.name,role:p.role,body:p.body,positions:Array.from(p.geometry.getAttribute('position').array),indices:Array.from(p.geometry.index.array)}))));
for(const p of parts)p.geometry.dispose();console.log(JSON.stringify(summary));
