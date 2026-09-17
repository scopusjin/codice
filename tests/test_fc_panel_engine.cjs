const assert=require('node:assert/strict');
const {api,run,nodes,buttons,base,html}=require('./fc_panel_harness.cjs');
let checks=0;
function eq(actual,expected,label){checks++;assert.equal(actual.length,expected.length,label);actual.forEach((v,i)=>assert(Math.abs(v-expected[i])<1e-8,label+': '+actual+' vs '+expected));}
function point(actual,expected,label,tolerance=1e-5){checks++;assert(Math.abs(actual-expected)<tolerance,label+': '+actual+' vs '+expected);}
function c(config,expected){eq(run(config).range,expected,JSON.stringify(config));}
// Independent agreed scientific scenarios, not snapshots of the implementation.
c({s:3},[1.2,1.3]);c({s:3,air:'continuous'},[1.2,1.3]);
c({p:1},[1.2,1.2]);c({p:3,isolation:'none'},[1.4,1.4]);
c({state:'Bagnato',p:3},[1.2,1.3]);c({state:'Bagnato',p:4,s:2},[1.2,1.3]);
c({state:'Bagnato',p:3,air:'continuous'},[.9,.9]);
c({state:'Bagnato',m:1},[1,1.1]);c({state:'Bagnato',m:1,p:1},[1.1,1.2]);
c({state:'Bagnato',h:1},[1.2,1.3]);c({state:'Bagnato',h:1,air:'continuous'},[.9,.9]);
c({state:'Bagnato',surf:4},[.6,.75]);c({state:'Bagnato',surf:4,s:1,air:'continuous'},[.6,.6]);
c({state:'Bagnato',surf:4,p:2,air:'continuous'},[.8,.8]);
c({surf:3,s:2},[1.4,1.5]);c({surf:3,s:3},[1.3,1.4]);
c({h:1,feather:'yes'},[2.8,3]);c({h:1,feather:'yes',surf:2},[2.8,3.1]);
c({m:2,p:1,volume:'yes',surf:2},[2,2.8]); // bed counted once
c({surf:7},[.55,.55]);c({surf:7,p:1},[.55,1.2]);
c({state:'Bagnato',surf:7,p:3},[.55,1.3]);
for(const surf of [2,3]){c({state:'Bagnato',p:3,surf,supportSoaked:'yes'},[1.2,1.3]);c({state:'Bagnato',p:3,surf,supportSoaked:'no'},[1.3,1.4]);}
const leaves=[ [{},[1.3,1.3],[1.5,1.5]], [{s:1},[1.3,1.4],[1.5,1.6]], [{s:2},[1.3,1.5],[1.5,1.7]], [{s:3},[1.3,1.6],[1.5,1.8]], [{s:4},[1.3,1.6],[1.5,1.8]], [{p:1},[1.3,1.5],[1.5,1.7]], [{p:2,s:2},[1.3,1.7],[1.5,1.9]], [{p:3,isolation:'none'},[1.4,1.7],[1.5,1.9]] ];
for(const [config,humid,dry] of leaves){c({...config,surf:8,leaf:'humid'},humid);c({...config,surf:8,leaf:'dry'},dry);}
c({state:'Immerso',water:'stagnante'},[.5,.5]);c({state:'Immerso',water:'corrente',h:20,s:20},[.35,.35]);c({state:'Immerso',water:'stagnante',waterNearZero:true},[.5,1]);
// Formula checkpoints independently calculated from the published expression.
point(api.adjust(2,10),3.171869,'Formula 2 / 10 kg');
point(api.adjust(2,40),2.401129,'Formula 2 / 40 kg');
point(api.adjust(2,110),1.695384,'Formula 2 / 110 kg');
point(api.adjust(1.4,100),1.2917,'Formula 1.4 / 100 kg',.0001);
point(api.adjust(3.1,100),2.4620,'Formula >3 / 100 kg',.0001);
for(const w of [4,20,59.99,60,70,80,80.01,100,150])for(const v of [.35,.5,.75,1,1.3,1.35])point(api.adjust(v,w),v,'No adjustment below threshold');
for(const w of [60,65,70,75,80])for(const v of [1.4,1.8,2.8,3.1,5])point(api.adjust(v,w),v,'No adjustment in average weight band');
eq(api.roundRange(api.bounds(1.35,1.4,100)),[1.3,1.4],'Crossing threshold envelope');
eq(api.roundRange(api.bounds(2.8,3.1,100)),[2.3,2.45],'High range');
eq(api.roundRange(api.bounds(1.4,1.4,100)),[1.3,1.3],'Point at threshold');
for(const [v,e] of [[1.2917,1.3],[1.359,1.35],[2.884,2.9],[1.325,1.35],[.77,.75]])point(api.roundFC(v),e,'Nearest 0.05');
assert(Number.isNaN(api.adjust(1.8,151)));assert(Number.isNaN(api.adjust(1.8,NaN)));
// Continuous interval check, including values immediately below and at the threshold.
for(const w of [4,20,59.99,60,80,80.01,100,150])for(const [a,b] of [[1.3,1.4],[1.35,1.6],[1.4,3.1],[.75,1.8]]){
 const r=api.bounds(a,b,w);for(let i=0;i<=100;i++){const v=api.adjust(a+(b-a)*i/100,w);assert(v>=r[0]-1e-9&&v<=r[1]+1e-9);checks++;}
}
// Finite/ordered ranges and documented missing selections across all branches.
let combinations=0,pending=0;
for(const state of ['Asciutto','Bagnato'])for(const s of [0,1,2,3,4,5,20])for(const p of [0,1,2,3,20])for(const m of [0,1,2,3])for(const h of [0,1,2])for(const surf of [0,1,2,3,4,5,6,7,8,10])for(const air of ['still','continuous','intermittent','unknown']){
 const config={state,s,p,m,h,surf,air,isolation:'none',feather:'no',volume:'no',leaf:'dry',supportSoaked:'no'};
 const r=run(config);combinations++;
 if(!r.range){pending++;continue;}
 assert(r.range.every(Number.isFinite));assert(r.range[0]>0&&r.range[1]>=r.range[0]-1e-8);
 if(r.id.endsWith('-support')&&[4,5,10].includes(surf)&&s+p+m+h>0){const n=run({...config,s:0,p:0,m:0,h:0});assert(r.range[0]>=n.range[0]-1e-8,'Naked lower bound violated');}
}
assert.equal(pending,0,'Complete selections should not leave a missing rule');
console.log(JSON.stringify({checks,combinations,pending,result:'passed'}));
