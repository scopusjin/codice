// Compare the actual FC engine before/after this presentation-only change.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('node:assert/strict');
const {execFileSync}=require('child_process');
const dirname=__dirname,harness=fs.readFileSync(path.join(dirname,'fc_panel_harness.cjs'),'utf8');
const original=execFileSync('git',['show','ea1d5a6e04cbd9f7844990451bbcf0c3a14dfdca:app/fc_panel_frontend/index.html'],{encoding:'utf8'});
const current=fs.readFileSync(path.join(dirname,'../app/fc_panel_frontend/index.html'),'utf8');
function load(html){
 const module={exports:{}};
 const shim={...fs,readFileSync:(p,...args)=>String(p).endsWith('/fc_panel_frontend/index.html')?html:fs.readFileSync(p,...args)};
 vm.runInNewContext(harness,{require:name=>name==='fs'?shim:require(name),module,__dirname:dirname,console});
 return module.exports;
}
const previous=load(original),updated=load(current);
const plain=x=>JSON.parse(JSON.stringify(x));
let count=0;
for(const state of ['Asciutto','Bagnato','Immerso'])for(const air of ['still','continuous','intermittent','unknown'])
for(const surf of [0,1,2,3,4,5,6,7,8,9,10])for(const [s,p,m,h] of [[0,0,0,0],[1,0,0,0],[2,0,0,0],[3,0,0,0],[0,2,0,0],[1,1,1,0],[0,0,1,0],[0,0,0,1]])
for(const water of ['stagnante','corrente'])for(const waterNearZero of [false,true]){
 const c={...updated.base,state,air,wind:air==='continuous',surf,s,p,m,h,water,waterNearZero,leaf:'dry',leafCover:'yes',wetClothes:'full',wetCovers:'full',weight:70};
 const expected=plain(previous.api.evaluateFC(c).range);
 updated.api.exampleMatches(c);
 assert.deepEqual(plain(updated.api.evaluateFC(c).range),expected,JSON.stringify(c));count++;
}
console.log('Numeric parity with '+count+' configurations: OK.');
