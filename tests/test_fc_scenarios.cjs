const assert=require('node:assert/strict');
const {panel,nodes,buttons,context}=require('./fc_panel_harness.cjs');
const plain=value=>JSON.parse(JSON.stringify(value));
const change=(id,value,event='change')=>{nodes[id].value=value;nodes[id].events[event]();};
const state=value=>buttons.find(b=>b.dataset.state===value).events.click();
const choose=i=>change('scenario-select',String(i));
const toggle=value=>{nodes['multiple-scenarios'].checked=value;nodes['multiple-scenarios'].events.change();};
const manual=(lo,hi)=>{change('lo',String(lo),'input');change('hi',String(hi),'input');};
const weight=value=>change('weight',String(value),'input');
const start={state:'Asciutto',fields:{thin:'0',thick:'0',medium:'0',heavy:'0',surface:'0',
  'metal-type':'',leaf:'','leaf-cover':'',feather:'',air:'still',water:'stagnante',isolation:'',
  'blanket-volume':'','support-soaked':'unknown'}};
nodes.surface.selectedOptions=[{textContent:'Piano neutro'}];
panel.restore(start,70);toggle(true);
assert.equal(panel.snapshot().scenarios.length,2);
assert.equal(nodes.use.hidden,true);assert.equal(nodes['use-scenarios'].disabled,false);
state('Bagnato');
assert.deepEqual(plain(panel.payload().range),[.75,1]);
assert.match(panel.payload().description,/0.75 \[corpo bagnato.*aria ferma.*1.00 \[corpo asciutto/s);
choose(0);assert.equal(nodes.lo.value,'1.00');choose(1);assert.equal(nodes.lo.value,'0.75');
nodes['add-scenario'].click();state('Immerso');change('water','corrente');
assert.equal(panel.snapshot().scenarios.length,3);
assert.equal(panel.payload().scenarios[2].conditions.s,undefined);
assert.match(panel.payload().description,/corpo immerso in acqua corrente/);
nodes['remove-scenario'].click();assert.equal(panel.snapshot().scenarios.length,2);
const draft=plain(panel.snapshot());panel.restore(draft,70);
assert.deepEqual(plain(panel.payload().range),[.75,1]);
assert.equal(panel.snapshot().activeScenario,1);

// A hidden incomplete scenario must block application, including after reopening.
choose(0);change('thin','invalid','input');choose(1);
assert.equal(nodes['use-scenarios'].disabled,true);assert.match(nodes['scenario-error'].textContent,/1/);
panel.restore(plain(panel.snapshot()),70);assert.equal(nodes['use-scenarios'].disabled,true);
choose(0);change('thin','0','input');assert.equal(nodes['use-scenarios'].disabled,false);

// Adapt separate bases, not the continuous envelope across the 1.40 threshold.
manual(1.35,1.35);choose(1);manual(2,2);
weight(100);assert.deepEqual(plain(panel.payload().range),[1.35,1.75]);
assert.deepEqual(plain(panel.payload().scenarios.map(s=>s.base_range)),[[1.35,1.35],[2,2]]);
assert.equal(panel.payload().weight_adjusted,true);
const weighted=plain(panel.snapshot());panel.restore(weighted,100);
assert.equal(nodes.lo.value,'1.75');
weight(70);assert.deepEqual(plain(panel.payload().range),[1.35,2]);
weight(75);assert.equal(panel.payload().weight_adjusted,false);
panel.restore(weighted,70);assert.deepEqual(plain(panel.payload().range),[1.35,2]);
weight('');assert.equal(nodes['use-scenarios'].disabled,true);
weight(100);assert.deepEqual(plain(panel.payload().range),[1.35,1.75]);
choose(0);assert.equal(nodes.lo.value,'1.35');choose(1);assert.equal(nodes.lo.value,'1.75');

// The single-scenario editor and previous multi-scenario draft remain usable.
toggle(false);assert.equal(nodes.use.hidden,false);assert.equal(panel.payload().scenarios,undefined);
assert.deepEqual(plain(panel.payload().range),[1.75,1.75]);
toggle(true);assert.equal(panel.snapshot().scenarios.length,2);
let sent;context.window.FCBridge={send:action=>sent={action,...panel.payload()}};
nodes['use-scenarios'].click();assert.equal(sent.action,'use');assert.equal(sent.scenarios.length,2);
assert.deepEqual(plain(sent.range),[1.35,1.75]);

// Equal extremes retain all distinct conditions, while duplicates stay compact.
choose(0);manual(1,1);choose(1);manual(1,1);
assert.match(panel.payload().description,/corpo asciutto.* \/ corpo bagnato/);
nodes['add-scenario'].click();
assert.equal((panel.payload().description.match(/corpo bagnato/g)||[]).length,2);
console.log('FC scenarios: independent conditions, aggregate bounds, manual bases, weights, drafts, incomplete inputs and ties passed.');
