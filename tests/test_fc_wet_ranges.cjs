const assert=require('node:assert/strict');
const {run,panel,nodes}=require('./fc_panel_harness.cjs');
const eq=(config,expected)=>assert.deepEqual(run({state:'Bagnato',wetClothes:'full',wetCovers:'full',...config}).range,expected,JSON.stringify(config));
// Agreed garment and covering examples, on neutral support, before weight adaptation.
for(const [s,p,still,moving] of [
 [1,0,[.9,1],[.7,.7]],[2,0,[1,1.1],[.7,.7]],[0,1,[1,1.1],[.7,.9]],
 [3,0,[1,1.1],[.7,.9]],[1,1,[1,1.1],[.7,.9]],[4,0,[1,1.1],[.7,.9]],
 [2,1,[1,1.1],[.7,.9]],[0,2,[1.1,1.1],[.9,.9]],
 [1,2,[1.1,1.2],[.9,.9]],[3,1,[1.1,1.2],[.7,.9]],[5,0,[1.1,1.2],[.7,.9]],
 [0,3,[1.2,1.2],[.9,.9]],[1,3,[1.2,1.2],[.9,.9]],[0,4,[1.2,1.2],[.9,.9]]]){
 eq({s,p},still);eq({s,p,air:'continuous'},moving);
}
for(const [m,h,s,p,still,moving] of [
 [1,0,0,0,[1,1.1],[.7,.9]],[1,0,1,0,[1,1.1],[.7,.9]],
 [1,0,2,0,[1.1,1.2],[.7,.9]],[1,0,0,1,[1.1,1.2],[.7,.9]],
 [1,0,0,2,[1.1,1.2],[.9,.9]],[2,0,0,0,[1.1,1.2],[.7,.9]],
 [2,0,0,1,[1.1,1.2],[.7,.9]],[3,0,0,0,[1.1,1.2],[.7,.9]],
 [0,1,0,0,[1.1,1.2],[.7,.9]],[0,1,1,0,[1.1,1.2],[.7,.9]],
 [0,1,0,1,[1.1,1.2],[.7,.9]],[0,1,0,2,[1.1,1.2],[.9,.9]]]){
 eq({m,h,s,p},still);eq({m,h,s,p,air:'continuous'},moving);
}
eq({m:1,wetCovers:'partial'},[1,1.8]);
eq({m:1,wetCovers:'unknown'},[1,1.8]);
eq({s:1,wetClothes:'partial'},[.9,1.1]);
eq({h:1,feather:'yes',wetCovers:'partial'},[1.1,3]);
eq({s:0,p:2,garmentThin:0,garmentThick:0,teli:0,lightCover:2,wetClothes:'unknown',wetCovers:'full'},[1.1,1.1]);
eq({s:0,p:2,garmentThin:0,garmentThick:0,teli:0,lightCover:2,wetCovers:'partial'},[1.1,1.2]);
// Independently capture the full envelope of existing dry rules.
let count=0;
for(const air of ['still','continuous','intermittent'])for(const surf of [0,2,4])for(const h of [0,1])for(const m of [0,1,2])for(const p of [0,1,3]){
 const c={state:'Bagnato',s:1,p,m,h,surf,air,feather:'no',volume:'no',isolation:'none',supportSoaked:'no'};
 const wet=run({...c,wetClothes:'full',wetCovers:'full'}),dry=run({...c,state:'Asciutto'});
 const mixed=run({...c,wetClothes:'partial',wetCovers:'partial'});
 assert.deepEqual(mixed.range,[Math.min(wet.range[0],dry.range[0]),Math.max(wet.range[1],dry.range[1])]);count++;
}
// Old automatic choices recompute, but an explicit manual choice is preserved.
const old={state:'Bagnato',fields:{thin:'0',thick:'0',medium:'1',heavy:'0',surface:'0',air:'still'},weight:70,lo:'1.00',hi:'1.10'};
panel.restore(old,70);assert.equal(nodes['wet-covers'].value,'unknown');assert.deepEqual([...panel.payload().range],[1,1.8]);
nodes['wet-covers'].value='full';nodes['wet-covers'].events.change();assert.deepEqual([...panel.payload().range],[1,1.1]);
const saved=panel.snapshot();panel.restore(null,70);panel.restore(saved,70);assert.equal(nodes['wet-covers'].value,'full');assert.deepEqual([...panel.payload().range],[1,1.1]);
panel.restore({...old,manual:true,lo:'1.45',hi:'1.55'},70);assert.deepEqual([...panel.payload().range],[1.45,1.55]);
// Separate groups and visibility; absent groups must not extend the range.
panel.restore({...old,fields:{...old.fields,medium:'0',thin:'1','wet-clothes':'full','wet-covers':'partial'}},70);
assert.equal(nodes['wet-covers-row'].hidden,true);assert.deepEqual([...panel.payload().range],[.9,1]);
console.log('Wet FC ranges, '+count+' envelopes and persistence: passed');
