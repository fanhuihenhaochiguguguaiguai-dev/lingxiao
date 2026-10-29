// Verify the existing second-skill profile rather than spreading a new art sample.
import {build} from '../skill-src/node_modules/esbuild/lib/main.js';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const old=execFileSync('git',['show','d1e5726:skill-src/src/dragon.ts'],{encoding:'utf8'});
await build({stdin:{contents:old,loader:'ts',resolveDir:process.cwd()+'/skill-src/src'},bundle:true,format:'esm',platform:'node',outfile:'/tmp/dragon32-legacy.mjs'});
const {DragonEffect:Legacy}=await import(pathToFileURL('/tmp/dragon32-legacy.mjs'));
const {DragonEffect:Current,THREE}=await import(pathToFileURL('/tmp/ling-dragon32-test.mjs'));
const a=new Legacy(new THREE.Group()),b=new Current(new THREE.Group(),'binding');
function sample(root){const rows=[];root.traverse(o=>{if(o.isMesh)rows.push({position:Array.from(o.geometry.getAttribute('position').array),normal:o.geometry.getAttribute('normal')?Array.from(o.geometry.getAttribute('normal').array):null,instances:o.isInstancedMesh?Array.from(o.instanceMatrix.array):null,opacity:o.material.opacity})});return rows}
const checked=[];
for(const t of [.3,1,2.7,3.8,5.8]){
 const orbit={phase:.85,sample:u=>new THREE.Vector3(Math.cos(t-u*2.7)*2.2,1.2+.1*Math.sin(u*3+t),Math.sin(t-u*2.7)*2.2)};
 a.update(t,true,orbit);b.update(t,true,orbit);assert.deepEqual(sample(a.group),sample(b.group));assert.deepEqual(a.head.quaternion.toArray(),b.head.quaternion.toArray());checked.push(t);
}
await writeFile('verification/dragon32/binding-regression.json',JSON.stringify({status:'PASS',baseline:'d1e5726',sampleTimes:checked,geometryNormalsInstancesOpacityAndHeadOrientationIdentical:true,artPromoted:false},null,2));console.log('PASS_BINDING_PROFILE_UNCHANGED');
