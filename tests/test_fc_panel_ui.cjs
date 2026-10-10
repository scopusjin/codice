const assert=require('node:assert/strict');
const {panel,nodes,buttons,context}=require('./fc_panel_harness.cjs');
nodes.surface.selectedOptions=[{textContent:'Piano neutro'}];
let sent;
context.window.FCBridge={send:action=>{sent={action,...panel.payload()};}};
panel.restore(null,70);
assert.equal(nodes.lo.value,'1.00');
assert.equal(nodes['manual-state'].textContent,'');
nodes.weight.value='100';nodes.weight.events.input();
assert.equal(nodes.lo.value,'1.00');
assert.equal(nodes['manual-state'].textContent,'');
nodes.weight.value='70';nodes.weight.events.input();
nodes.thin.value='3';nodes.thin.events.input();
assert.equal(nodes.lo.value,'1.20');assert.equal(nodes.hi.value,'1.30');
nodes.lo.value='1.25';nodes.lo.events.input();
const draft=panel.snapshot();panel.restore(draft,70);
assert.equal(nodes.lo.value,'1.25');
nodes.use.events.click();
assert.equal(sent.action,'use');assert.deepEqual([...sent.range],[1.25,1.3]);
assert.equal(sent.manual,true);assert.deepEqual([...sent.base_range],[1.25,1.3]);
assert(sent.description.includes('alcuni strati di tessuti leggeri'));
panel.restore(draft,100);
assert.equal(nodes.lo.value,'1.25');assert.equal(nodes.hi.value,'1.30');
buttons.find(x=>x.dataset.state==='Immerso').events.click();nodes.use.events.click();
assert.equal(sent.conditions.s,undefined);assert.equal(sent.conditions.surf,undefined);
nodes['open-tables'].events.click({preventDefault(){}});assert.equal(sent.action,'tables');
panel.restore(null,NaN);assert.equal(nodes.use.disabled,true);
console.log('FC controls: manual bounds, weight, draft, immersion and tables handoff passed.');

// The new leaf-cover answer must survive a draft and reach the applied choice.
panel.restore({state:'Asciutto',fields:{thin:'0',thick:'0',medium:'0',heavy:'0',surface:'8',leaf:'dry','leaf-cover':'',air:'still'}},70);
nodes.surface.selectedOptions=[{textContent:'Foglie'}];
nodes.leaf.selectedOptions=[{textContent:'Secche'}];
assert.equal(nodes['leaf-cover-row'].hidden,false);
assert.equal(nodes.use.disabled,true);
assert.match(nodes.error.textContent,/Precisare se il corpo era anche coperto dalle foglie/);
nodes['leaf-cover'].value='no';nodes['leaf-cover'].events.change();
assert.equal(nodes.lo.value,'1.50');assert.equal(nodes.hi.value,'1.50');
assert.equal(nodes.use.disabled,false);
nodes['leaf-cover'].value='yes';nodes['leaf-cover'].events.change();
assert.equal(nodes.lo.value,'2.70');assert.equal(nodes.hi.value,'2.70');
const leafDraft=panel.snapshot();
nodes['leaf-cover'].value='';nodes['leaf-cover'].events.change();
assert.equal(nodes.use.disabled,true);
panel.restore(leafDraft,70);
assert.equal(nodes['leaf-cover'].value,'yes');
assert.equal(nodes.use.disabled,false);
nodes.use.events.click();
assert.deepEqual([...sent.range],[2.7,2.7]);
assert.equal(sent.manual,false);assert.deepEqual([...sent.base_range],[2.7,2.7]);
assert.equal(sent.conditions.leafCover,'yes');
assert.match(sent.description,/con copertura di foglie/);
console.log('FC leaves: required answer, support-only range, covering, draft and applied description passed.');

// The applied payload retains the unadapted range even at a different weight.
nodes.weight.value='100.0';nodes.weight.events.input();
assert.equal(nodes['manual-state'].textContent,'FC adattato per il peso.');
const adjustedSuggestion=panel.snapshot();panel.restore(adjustedSuggestion,100);
assert.equal(nodes['manual-state'].textContent,'FC adattato per il peso.');
nodes.use.events.click();
assert.notDeepEqual([...sent.range],[2.7,2.7]);
assert.deepEqual([...sent.base_range],[2.7,2.7]);
assert.equal(sent.manual,false);
nodes.restore.events.click();
assert.equal(nodes['manual-state'].textContent,'');

// Manual values are the anchor for every later weight, including restored drafts.
nodes.lo.value='2';nodes.lo.events.input();
nodes.hi.value='2';nodes.hi.events.input();
assert.equal(nodes['manual-state'].textContent.includes('adattato al nuovo peso'),false);
nodes.weight.events.input();
assert.equal(nodes.lo.value,'2');assert.equal(nodes.hi.value,'2');
for(const [weight,expected] of [[70,'2.00'],[100,'1.75'],[110,'1.70'],[70,'2.00']]){
  nodes.weight.value=String(weight);nodes.weight.events.input();
  assert.equal(nodes.lo.value,expected);assert.equal(nodes.hi.value,expected);
  nodes.use.events.click();
  assert.equal(sent.manual,true);assert.deepEqual([...sent.base_range],[2,2]);
}
assert.match(nodes['manual-state'].textContent,/reinseriscili manualmente/);
const manualDraft=panel.snapshot();panel.restore(manualDraft,100);
assert.equal(nodes.lo.value,'1.75');assert.equal(nodes.hi.value,'1.75');
assert.match(nodes['manual-state'].textContent,/adattato al nuovo peso/);
nodes.hi.value='2.5';nodes.hi.events.input();
nodes.lo.value='2.5';nodes.lo.events.input();
assert.equal(nodes['manual-state'].textContent.includes('adattato al nuovo peso'),false);
nodes.weight.value='110';nodes.weight.events.input();
assert.equal(nodes.lo.value,'2.00');assert.equal(nodes.hi.value,'2.00');
nodes.weight.value='';nodes.weight.events.input();
assert.equal(nodes.lo.value,'2.00');assert.equal(nodes.use.disabled,true);
nodes.weight.value='100';nodes.weight.events.input();
assert.equal(nodes.lo.value,'2.10');assert.equal(nodes.hi.value,'2.10');
nodes.lo.value='';nodes.lo.events.input();
nodes.weight.value='70';nodes.weight.events.input();
assert.equal(nodes.lo.value,'');assert.equal(nodes.use.disabled,true);
nodes.restore.events.click();
assert.equal(panel.payload().manual,false);
assert.equal(panel.payload().manual_weight_adjusted,false);
console.log('Manual FC: original bounds, repeated weights, drafts, new edits and invalid inputs passed.');

// Opening a main-page FC must preserve its current value and original base.
panel.restore({lo:'1.75',hi:'1.75',weight:100,manual:true,manualBase:[2,2],
  manualWeightAdjusted:true,weightAdjusted:true},100);
assert.equal(nodes.lo.value,'1.75');assert.deepEqual([...panel.payload().base_range],[2,2]);
nodes.weight.value='70';nodes.weight.events.input();
assert.equal(nodes.lo.value,'2.00');assert.equal(panel.payload().weight_adjusted,true);
nodes.weight.value='75';nodes.weight.events.input();
assert.equal(nodes.lo.value,'2.00');assert.equal(panel.payload().weight_adjusted,false);
assert.equal(panel.payload().manual_weight_adjusted,false);
assert.equal(nodes['manual-state'].textContent,'');
panel.restore({lo:'1.75',hi:'1.75',weight:100,manual:false,selectedBase:[2,2]},100);
assert.equal(panel.payload().manual,false);assert.deepEqual([...panel.payload().base_range],[2,2]);
nodes.weight.value='70';nodes.weight.events.input();
assert.equal(nodes.lo.value,'2.00');assert.equal(panel.payload().weight_adjusted,true);
assert.equal(nodes['manual-state'].textContent,'FC adattato per il peso.');
nodes.weight.value='75';nodes.weight.events.input();
assert.equal(panel.payload().weight_adjusted,false);
assert.equal(panel.payload().manual,false);
assert.equal(nodes['manual-state'].textContent,'');
console.log('FC editor: current manual/automatic selection and change-only notice survive reopening.');

require('./test_fc_field_controls.cjs');

// Exercise the actual component bridge: rerenders retain drafts, navigation is
// emitted once and cannot be overwritten by a delayed draft event.
const fs=require('fs'),vm=require('vm'),path=require('path');
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/fc_examples.json'),'utf8'));
const messages=[],events={},rootEvents={};let restored=0,callback=null;
const parent={postMessage:m=>messages.push(m)};
const win={parent,FCPanel:{setExamples(examples){assert.deepEqual(examples,catalog);},restore(){restored++;},payload(){return {weight:70,range:[1.2,1.3]};}},addEventListener:(name,cb)=>events[name]=cb};
const root={getBoundingClientRect:()=>({height:600}),addEventListener:(name,cb)=>rootEvents[name]=cb};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../app/fc_panel_frontend/bridge.js'),'utf8'),{
 window:win,document:{getElementById:id=>id==='fc-full'?root:{disabled:false},documentElement:{style:{}}},
 ResizeObserver:class{observe(){}},crypto:{randomUUID:()=>String(messages.length)},
 setTimeout:cb=>{callback=cb;return 1;},clearTimeout:()=>{callback=null;},
});
const render={source:parent,data:{type:'streamlit:render',args:{instance:'test',weight:70,draft:null,examples:catalog}}};
events.message(render);events.message(render);assert.equal(restored,1);
rootEvents.input();callback();assert.equal(messages.at(-1).value.action,'draft');
rootEvents.input();win.FCBridge.send('tables');rootEvents.click();
assert.equal(callback,null);assert.equal(messages.at(-1).value.action,'tables');
win.FCBridge.send('use');assert.equal(messages.at(-1).value.action,'tables');
console.log('Streamlit bridge: draft preservation and single navigation delivery passed.');
require('./test_fc_scenarios.cjs');

// The compact editor has one authoritative point value, or two independent bounds.
panel.restore({state:'Asciutto',temperature:'20',fields:{thin:'0',thick:'0',medium:'0',heavy:'0',surface:'0',air:'still',water:'stagnante'}},70,20);
assert.equal(nodes['hi-control'].hidden,true);
assert.equal(nodes['expand-range'].hidden,false);
buttons.find(b=>b.dataset.input==='lo'&&b.dataset.step==='0.05').click();
assert.deepEqual([...panel.payload().range],[1.05,1.05]);
nodes['expand-range'].click();
assert.equal(nodes['hi-control'].hidden,false);
buttons.find(b=>b.dataset.input==='hi'&&b.dataset.step==='0.05').click();
assert.deepEqual([...panel.payload().range],[1.05,1.1]);
panel.restore(panel.snapshot(),70,20);
assert.equal(nodes['hi-control'].hidden,false);
nodes.restore.click();
assert.deepEqual([...panel.payload().range],[1,1]);assert.equal(nodes['hi-control'].hidden,true);
nodes.medium.value='1';nodes.medium.events.input();
assert.equal(nodes['hi-control'].hidden,true,'An unambiguous bare-body blanket reference remains a point');
assert.match(panel.payload().description,/nudo, sotto una coperta spessa/);
nodes.thin.value='1';nodes.thin.events.input();
assert.equal(nodes['hi-control'].hidden,false,'Blanket conditions expose the automatic range');
assert.notEqual(panel.payload().range[0],panel.payload().range[1]);
assert.match(panel.payload().description,/uno strato di tessuto leggero, sotto una coperta spessa/);
assert.doesNotMatch(panel.payload().description,/\d+ strati|aria ferma|°C|manuale/);
// UI precision must not silently round a previously saved measured weight.
panel.restore(panel.snapshot(),82.5,20);
assert.equal(nodes.weight.value,'83');assert.equal(panel.payload().weight,82.5);
const legacyWeightBounds=[...panel.payload().range];
panel.restore(panel.snapshot(),82.5,20);
assert.deepEqual([...panel.payload().range],legacyWeightBounds);
assert.equal(panel.payload().weight,82.5);
// Editing the single scenario temperature is explicit and does not alter its FC.
const fcBefore=[...panel.payload().range];
assert.equal(panel.payload().temperature,undefined);
nodes['scenario-temperature'].value='8.5';nodes['scenario-temperature'].events.input();
assert.equal(panel.payload().temperature,8.5);assert.deepEqual([...panel.payload().range],fcBefore);
nodes['scenario-temperature'].value='';nodes['scenario-temperature'].events.input();
assert.equal(nodes.use.disabled,true);
nodes['scenario-temperature'].value='0';nodes['scenario-temperature'].events.input();
assert.equal(nodes.use.disabled,false);assert.equal(panel.payload().temperature,0);
console.log('Compact FC: point/range edits, automatic blanket range, exact saved weight and explicit temperature passed.');
