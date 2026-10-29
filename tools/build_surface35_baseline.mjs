import {build} from '../skill-src/node_modules/esbuild/lib/main.js';
import {execFileSync} from 'node:child_process';
// The same current QA camera helper, with only the effect geometries restored.
// No second website/checkout and no historical source edited.
await build({entryPoints:['skill-src/src/main.ts'],bundle:true,minify:true,format:'esm',target:['es2022'],outfile:'/tmp/surface35-before-app.js',legalComments:'external',plugins:[{name:'baseline-effects',setup(b){b.onLoad({filter:/\/(moon-frost|moon-tide|bind-star)\.ts$/},a=>({contents:execFileSync('git',['show','3528f0a:skill-src/src/'+a.path.split('/').pop()],{encoding:'utf8'}),loader:'ts'}))}}]});
