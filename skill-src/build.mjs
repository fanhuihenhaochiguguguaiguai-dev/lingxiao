import { build } from 'esbuild';
await build({entryPoints:['src/main.ts'],bundle:true,minify:true,format:'esm',target:['es2022'],outfile:'../dist/skill/app.js',sourcemap:false,legalComments:'external'});
