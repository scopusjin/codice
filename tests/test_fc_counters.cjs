const assert=require('node:assert/strict');
const {panel,nodes,api,base,buttons}=require('./fc_panel_harness.cjs');
const change=(id,value)=>{nodes[id].value=String(value);nodes[id].events.input();};
const fields={thin:'0',thick:'0',medium:'0',heavy:'0',surface:'0',air:'still',isolation:'none',feather:'no','blanket-volume':'no','support-soaked':'no'};
panel.restore({state:'Asciutto',fields},70,20);panel.setDesktop(true);
change('garment-thin',2);change('teli',1);change('light-cover',1);
let p=panel.payload();assert.equal(p.conditions.s,3);assert.equal(p.conditions.p,1);
assert.match(p.description,/con pochi indumenti leggeri, coperto con più teli di diverso spessore/);
assert.deepEqual([...p.base_range],[...api.evaluateFC({...base,s:3,p:1,isolation:'none'}).range]);
const saved=panel.snapshot();panel.restore({state:'Asciutto',fields},70,20);
assert.equal(nodes.teli.value,'0');assert.equal(panel.payload().conditions.garmentThin,undefined);
panel.restore(saved,70,20);assert.equal(panel.payload().description,p.description);
panel.setDesktop(false);assert.equal(nodes.thin.value,'3');assert.equal(nodes.thick.value,'1');
assert.equal(panel.payload().description,p.description,'Viewing on mobile must preserve detail');
change('thin',4);assert.equal(panel.payload().conditions.garmentThin,undefined);
assert.equal(nodes.teli.value,'0');assert.equal(nodes['light-cover'].value,'0');
panel.setDesktop(true);assert.equal(nodes['garment-thin'].value,'4');
change('garment-thin',1);change('teli','');assert.equal(nodes.use.disabled,true);
change('teli',0);change('light-cover',1);change('garment-thick',0);
assert(api.exampleMatches(panel.payload().conditions).some(e=>e.id==='blanket-B56'));
change('teli',1);assert(!api.EXAMPLE_MATCHERS['blanket-B56'](panel.payload().conditions));
assert(api.exampleMatches(panel.payload().conditions).some(e=>e.id==='blanket-B56')); // Broader comparisons deliberately include adjacent conditions.
const b33=api.EXAMPLE_MATCHERS['blanket-B33'];
assert(b33({...base,surf:2,m:2}));assert(b33({...base,surf:2,h:1}));
assert(!b33({...base,surf:2,m:1}));assert(!b33({...base,surf:0,m:2}));
assert(!b33({...base,surf:2,h:1,state:'Bagnato'}));assert(!b33({...base,surf:2,h:1,air:'continuous'}));
// The button path updates the same aggregate as direct entry.
const old=Number(nodes.thin.value);
buttons.find(b=>b.dataset.input==='teli'&&b.dataset.step==='1').click();
assert.equal(Number(nodes.thin.value),old+1);
console.log('Desktop detail: totals, descriptions, legacy drafts, mobile edits, validation and documentary matches passed.');

// Special covers contribute exactly once, through the existing categories.
const toggle=(id,value)=>{nodes[id].checked=value;nodes[id].events.change();};
for(const state of ['Asciutto','Bagnato'])for(const weight of [50,70,100])for(const surface of ['0','2','4']){
  const draft={state,fields:{...fields,thin:'2',thick:'1',surface}};
  panel.restore(draft,weight,20);toggle('thermal-foil',true);toggle('body-bag',true);
  const special=panel.payload();
  panel.restore({...draft,fields:{...draft.fields,thick:'2',medium:'1'}},weight,20);
  assert.deepEqual([...special.range],[...panel.payload().range]);
  assert.equal(JSON.stringify(special.base_range),JSON.stringify(panel.payload().base_range));
}
panel.restore({state:'Asciutto',fields},70,20);toggle('thermal-foil',true);
assert.deepEqual([...panel.payload().base_range],[1.8,1.8]);
assert.match(panel.payload().description,/nudo, coperto con una mantellina termica/);
assert.doesNotMatch(panel.payload().description,/sotto una coperta/);
assert.equal(nodes.medium.value,'0');
toggle('body-bag',true);const specialSaved=panel.snapshot(),specialText=panel.payload().description;
assert.match(specialText,/coperto con una mantellina termica, avvolto in un sacco mortuario/);
assert.equal(api.exampleMatches(panel.payload().conditions).length,0,'No documentary match treats the equivalents as actual clothes');
panel.restore({state:'Asciutto',fields},70,20);
assert.equal(nodes['thermal-foil'].checked,false);assert.equal(nodes['body-bag'].checked,false);
panel.restore(specialSaved,70,20);assert.equal(panel.payload().description,specialText);
panel.setDesktop(false);assert.equal(panel.payload().description,specialText);
toggle('thermal-foil',false);assert.equal(panel.payload().conditions.m,0);
assert.equal(panel.payload().conditions.p,1);assert.equal(nodes.thick.value,'0');
assert.match(panel.payload().description,/nudo, avvolto in un sacco mortuario/);
panel.restore({...specialSaved,state:'Immerso'},70,20);
assert.doesNotMatch(panel.payload().description,/sacco|mantellina/);
assert.equal(panel.payload().conditions.bodyBag,undefined);
const describe=require('./fc_panel_harness.cjs').context.window.FCDescriptions.conditions;
const descriptions=[
  [{thermalFoil:true,m:2},'coperto con una coperta spessa e una mantellina termica'],
  [{thermalFoil:true,m:2,h:1,feather:'yes'},'coperto con coperte di diverso spessore e una mantellina termica, tra cui un piumone molto voluminoso e avvolgente'],
  [{garmentThin:1},'con uno strato di indumenti leggeri'],
  [{garmentThin:2,teli:1},'con pochi indumenti leggeri, coperto con un telo sottile'],
  [{garmentThin:3,teli:2},'con vari strati di indumenti leggeri, coperto con due teli sottili'],
  [{garmentThin:2,garmentThick:3,m:2},'con molti strati di indumenti di diverso spessore, sotto due coperte spesse'],
  [{teli:1,lightCover:1},'coperto con più teli di diverso spessore'],
  [{m:1,h:1},'sotto più coperte di diverso spessore'],
  [{teli:1,m:1},'coperto con teli e coperte di diverso spessore'],
  [{h:1,feather:'yes'},'coperto con un piumone molto voluminoso e avvolgente'],
  [{teli:1,m:1,h:1,feather:'yes'},'coperto con coperte di diverso spessore, tra cui un piumone molto voluminoso e avvolgente']
];
for(const [counts,phrase] of descriptions)assert(describe({...base,garmentThin:0,garmentThick:0,...counts},{}).includes(phrase),phrase);
console.log('Special covers: numerical equivalence across states, weights and supports; no double counting; restore, mobile, immersion and wording passed.');
