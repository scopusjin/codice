const assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),vm=require('vm');
const {api,base,panel,nodes}=require('./fc_panel_harness.cjs');
const plain=x=>JSON.parse(JSON.stringify(x));
const ids=c=>new Set(api.exampleMatches({...base,...c}).map(e=>e.id));
let checked=0;
for(const e of api.EXAMPLES){
  const r=e.contextualReview,p=r.criteria;
  assert(r&&r.reason,e.id+' missing review');
  if(!p)continue;
  const c={...base,state:p.state==='nonimmersed'?'Asciutto':p.state,
    air:p.air==='unspecified'||!p.air?'still':p.air,surf:p.surfaces?.[0]??0,
    s:p.garments?.[0]??0,p:0,m:p.covers?.[0]??0,h:0,
    leaf:p.leaf||'dry',leafCover:p.leafCover||'no',weight:p.maxWeight?14:70,
    water:p.water||'stagnante',waterNearZero:p.waterSeries==='cold',wetClothes:'full'};
  c.wind=c.air==='continuous';
  assert(ids(c).has(e.id),e.id+' has no reachable contextual condition');checked++;
}
assert(checked>=107);
for(const leaf of ['wet','humid','dry']){
 const found=ids({surf:8,leaf,leafCover:'no'});
 for(let i=1;i<=6;i++)assert(found.has('t6_11-riga-'+i));
 const covered=ids({surf:8,leaf,leafCover:'yes'});
 for(let i=1;i<=14;i++)assert(covered.has('t6_12-riga-'+i));
 assert(!found.has('t6_12-riga-2'));
}
for(const surf of [4,5]){
 const found=ids({surf,s:2});
 for(const id of ['t6_10-240','t6_10-250','t6_10-251','t6_10-252'])assert(found.has(id));
 assert(!found.has('t6_10-291'));
}
assert(ids({surf:4,s:2}).has('case-26'));
assert(ids({surf:5,s:2}).has('case-46'));
assert(!ids({state:'Immerso',water:'corrente'}).has('t6_7-20'));
assert(!ids({state:'Immerso',waterNearZero:true}).has('t6_7-20'));
assert(!ids({state:'Immerso',waterNearZero:false}).has('t6_7-06'));
assert(ids({surf:2,s:2,weight:14}).has('case-37'));
assert(!ids({surf:2,s:2,weight:70}).has('case-37'));
const similar=api.exampleMatches({...base,surf:8,leaf:'wet',leafCover:'no'}).find(e=>e.id==='t6_11-riga-4');
assert.match(similar.comparisonNote,/stato delle foglie differente/);
const archived=new Set(api.EXAMPLES.filter(e=>e.contextualReview.status==='archive').map(e=>e.id));
assert.deepEqual([...archived].sort(),['case-31','case-45','case-7','t6_6-senza-ID']);
for(const state of ['Asciutto','Bagnato','Immerso'])for(const surf of [0,2,3,4,5,8]){
 for(const e of api.exampleMatches({...base,state,surf,s:2,leaf:'dry',leafCover:'yes'}))assert(!archived.has(e.id));
}
// No catalogue source/FC fields are rewritten by the selector.
const before=JSON.stringify(api.EXAMPLES);
for(const leaf of ['wet','humid','dry'])api.exampleMatches({...base,surf:8,leaf,leafCover:'no'});
assert.equal(JSON.stringify(api.EXAMPLES),before);
// Keep six cards visible; every extra record remains in native expandable details.
panel.restore({state:'Asciutto',temperature:'20',fields:{thin:'0',thick:'0',medium:'0',heavy:'0',surface:'8',air:'still',leaf:'dry','leaf-cover':'yes'}},70,20);
assert.equal(nodes['example-list'].children.length,7);
const overflow=nodes['example-list'].children[6].children[0];
assert.match(overflow.children[0].textContent,/Altri esempi pertinenti \(8\)/);
assert.equal(overflow.children[1].children.length,8);
console.log('Reviewed examples: '+checked+' reachable profiles; all leaves, concrete/tiles, boundaries and exclusions OK.');
