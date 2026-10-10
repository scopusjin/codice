const assert=require('node:assert/strict');
const {panel,nodes,buttons,html}=require('./fc_panel_harness.cjs');
const change=(id,value,event='input')=>{nodes[id].value=value;nodes[id].events[event]();};
const temp=value=>change('scenario-temperature',value);
const state=value=>buttons.find(b=>b.dataset.state===value).click();
const range=()=>[...panel.payload().range];
const draft={state:'Immerso',temperature:'2',fields:{water:'stagnante',thin:'0',thick:'0',medium:'0',heavy:'0',surface:'0',air:'still'}};
panel.restore(draft,70,20);
assert.doesNotMatch(html,/id="water-near-zero(?:-row)?"/);
for(const [temperature,cold] of [['1.01',false],['1',true],['0.99',true],['0',true],['-0.5',true],['1,00',true],['1,01',false]]){
  temp(temperature);
  assert.equal(panel.payload().conditions.waterNearZero,cold,temperature);
  assert.deepEqual(range(),cold?[.5,1]:[.5,.5],temperature);
  assert.equal(nodes.use.disabled,false);
}
nodes['scenario-temperature'].events.blur();
assert.equal(nodes['scenario-temperature'].value,'1.01','Blur must not round a temperature across the threshold');
buttons.find(b=>b.dataset.temperature==='-0.1').click();
assert.deepEqual(range(),[.5,1]);
temp('1');buttons.find(b=>b.dataset.temperature==='0.1').click();
assert.deepEqual(range(),[.5,.5]);
// The existing running-water rule and dry/wet rules are independent of this threshold.
change('water','corrente','change');temp('0');
assert.deepEqual(range(),[.35,.35]);assert.equal(panel.payload().conditions.waterNearZero,false);
state('Asciutto');assert.deepEqual(range(),[1,1]);
temp('2');assert.deepEqual(range(),[1,1]);
state('Bagnato');const wet=range();temp('0');assert.deepEqual(range(),wet);
state('Immerso');change('water','stagnante','change');
// Invalid and empty inputs never become zero or allow the selection to be applied.
for(const temperature of ['', ' ', '-', 'abc', '1.001']){
  temp(temperature);assert.equal(nodes.use.disabled,true,temperature);
  assert.equal(panel.payload().conditions.waterNearZero,false);
}
temp('1');assert.equal(nodes.use.disabled,false);
// Same-category edits preserve manual choices; a category change restores its suggestion.
change('lo','0.6');change('hi','0.8');temp('0.5');
assert.deepEqual(range(),[.6,.8]);assert.equal(panel.payload().manual,true);
panel.restore(panel.snapshot(),70);assert.deepEqual(range(),[.6,.8]);
temp('2');assert.deepEqual(range(),[.5,.5]);assert.equal(panel.payload().manual,false);
temp('1');assert.deepEqual(range(),[.5,1]);
// The old saved checkbox cannot override the current water temperature, in either direction.
panel.restore({...draft,temperature:'1',waterNearZero:false,lo:'0.50',hi:'0.50',weight:70,selectedBase:[.5,.5]},70);
assert.deepEqual(range(),[.5,1]);
panel.restore({...panel.snapshot(),temperature:'2',manual:true,manualBase:[.6,.8],lo:'0.60',hi:'0.80'},70);
assert.deepEqual(range(),[.5,.5]);assert.equal(panel.payload().manual,false);
panel.restore({...draft,temperature:''},70);
assert.equal(nodes.use.disabled,true,'An unedited missing water temperature is required');
temp('1');temp('');panel.restore(panel.snapshot(),70);
assert.equal(nodes.use.disabled,true);temp('2');assert.deepEqual(range(),[.5,.5]);
// Each scenario keeps its own temperature and is recalculated on restore and weight edits.
temp('1');nodes['multiple-scenarios'].checked=true;nodes['multiple-scenarios'].events.change();
temp('2');
let scenarios=panel.payload().scenarios;
assert.deepEqual(Array.from(scenarios,s=>[...s.range]).flat(),[.5,1,.5,.5]);
nodes['scenario-tabs'].children[0].click();assert.deepEqual(range(),[.5,1]);
assert.equal(nodes['scenario-temperature'].value,'1');
change('weight','100');
panel.restore(panel.snapshot(),100);
scenarios=panel.payload().scenarios;
assert.deepEqual(Array.from(scenarios,s=>s.temperature),[1,2]);
assert.deepEqual(Array.from(scenarios,s=>[...s.range]).flat(),[.5,1,.5,.5]);
nodes['scenario-tabs'].children[1].click();
assert.equal(nodes.lo.value,'0.50');assert.equal(nodes.hi.value,'0.50');
temp('0');assert.equal(nodes.hi.value,'1.00');
console.log('Automatic cold water: inclusive threshold, decimals, buttons, invalid inputs, manual choices, legacy drafts and independent scenarios passed.');
