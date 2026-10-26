const assert=require('node:assert/strict');
const {panel,nodes,buttons,context,media}=require('./fc_panel_harness.cjs');
const plain=value=>JSON.parse(JSON.stringify(value));
const change=(id,value,event='change')=>{nodes[id].value=value;nodes[id].events[event]();};
const state=value=>buttons.find(b=>b.dataset.state===value).events.click();
const choose=i=>nodes['scenario-tabs'].children[i].click();
const toggle=value=>{nodes['multiple-scenarios'].checked=value;nodes['multiple-scenarios'].events.change();};
const manual=(lo,hi)=>{change('lo',String(lo),'input');change('hi',String(hi),'input');};
const weight=value=>change('weight',String(value),'input');
const summaryValues=()=>nodes['scenario-summary'].children.map(row=>row.children.at(-1).children[1].textContent);
const start={state:'Asciutto',temperature:'20',fields:{thin:'0',thick:'0',medium:'0',heavy:'0',surface:'0',
  'metal-type':'',leaf:'','leaf-cover':'',feather:'',air:'still',water:'stagnante',isolation:'',
  'blanket-volume':'','support-soaked':'unknown'}};
nodes.surface.selectedOptions=[{textContent:'Piano neutro'}];
panel.restore(start,70);toggle(true);
assert.equal(panel.snapshot().scenarios.length,2);
assert.equal(panel.snapshot().activeScenario,0);
assert.equal(nodes['fc-heading'].textContent,'FC dello scenario 1:');
assert.equal(nodes['conditions-title'].textContent,'Scenari considerati:');
assert.equal(nodes['scenario-temperature-output'].textContent,'20.0 °C');
assert.deepEqual(summaryValues(),['FC 1.00 · T. ambientale media 20.0 °C','FC 1.00 · T. ambientale media 20.0 °C']);
choose(1);
assert.equal(nodes.use.hidden,true);assert.equal(nodes['use-scenarios'].disabled,false);
state('Bagnato');
assert.deepEqual(plain(panel.payload().range),[.75,1]);
assert.match(panel.payload().description,/0.75 \(corpo bagnato.*1.00 \(corpo asciutto/s);
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
assert.deepEqual(summaryValues(),['FC 1.35 · T. ambientale media 20.0 °C','FC 1.75 · T. ambientale media 20.0 °C']);
assert.deepEqual(plain(panel.payload().scenarios.map(s=>s.base_range)),[[1.35,1.35],[2,2]]);
assert.equal(panel.payload().weight_adjusted,true);
const weighted=plain(panel.snapshot());panel.restore(weighted,100);
assert.equal(nodes.lo.value,'1.75');
weight(70);assert.deepEqual(plain(panel.payload().range),[1.35,2]);
weight(75);assert.equal(panel.payload().weight_adjusted,false);
panel.restore(weighted,70);assert.deepEqual(plain(panel.payload().range),[1.35,2]);
weight('');assert.equal(nodes['use-scenarios'].disabled,false);
assert(Number.isNaN(panel.payload().weight)); // FC may be chosen before entering weight in home.
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
assert.equal((panel.payload().description.match(/corpo bagnato/g)||[]).length,1);
console.log('FC scenarios: independent conditions, aggregate bounds, manual bases, weights, drafts, incomplete inputs and ties passed.');

// Temperatures are individual, accept negatives, and survive draft/weight changes.
choose(0);
const stableTab=nodes['scenario-tabs'].children[1];
change('scenario-temperature','-2,5','input');
nodes['scenario-temperature'].events.blur();
assert.equal(nodes['scenario-tabs'].children[1],stableTab,'Temperature blur must not replace the pending click target');
change('surface','wood');
assert.equal(panel.payload().scenarios[0].temperature,-2.5);
assert.equal(panel.payload().scenarios[0].conditions.surf,0);
assert.match(panel.payload().scenarios[0].description,/su piano di legno/);
choose(1);state('Immerso');change('scenario-temperature','8','input');
assert.equal(nodes['scenario-temperature-label'].textContent,'Temperatura dell’acqua');
assert.equal(nodes['scenario-temperature-output'].textContent,'-2.5 – 20.0 °C');
assert.match(summaryValues()[0],/T\. ambientale media -2\.5 °C/);
assert.match(summaryValues()[1],/T\. acqua 8\.0 °C/);
assert.doesNotMatch(panel.payload().description,/manuale/);
assert.doesNotMatch(panel.payload().description,/°C|aria ferma|pavimento interno|\[|\]/);
weight(90);panel.restore(plain(panel.snapshot()),90,30);
choose(0);assert.equal(nodes['scenario-temperature'].value,'-2.5');
change('scenario-temperature','','input');choose(1);
assert.equal(nodes['use-scenarios'].disabled,true);
assert.equal(nodes['scenario-temperature-output'].textContent,'—');
assert.match(summaryValues()[0],/T\. ambientale media —/);
assert.equal(nodes['scenario-error'].textContent,'Scenario 1: Specificare la temperatura.');
change('scenario-temperature','','input');
assert.equal(nodes['scenario-error'].textContent,'Scenario 1: Specificare la temperatura.\nScenario 2: Specificare la temperatura.');
change('scenario-temperature','8','input');
choose(0);change('scenario-temperature','0','input');
assert.equal(nodes['use-scenarios'].disabled,false);
assert.equal(nodes['scenario-error'].textContent,'');
assert.equal(nodes['scenario-temperature-output'].textContent,'0.0 – 20.0 °C');
change('scenario-temperature','1.01','input');
assert.equal(nodes['scenario-temperature-output'].textContent,'1.01 – 20.0 °C');
manual(1,1.2);assert.match(summaryValues()[0],/^FC 1.00 – 1.20 ·/);
// The current home temperature seeds new scenarios; unknown temperatures stay blank.
panel.restore({...start,temperature:undefined},70,19.5);toggle(true);
assert.deepEqual(plain(panel.payload().scenarios.map(s=>s.temperature)),[19.5,19.5]);
panel.restore({...start,temperature:undefined},70,null);toggle(true);
assert.equal(nodes['use-scenarios'].disabled,true);
assert.equal(nodes['scenario-temperature-output'].textContent,'—');
assert.equal(nodes['scenario-error'].textContent,'Scenario 1: Specificare la temperatura.\nScenario 2: Specificare la temperatura.');
console.log('FC temperatures: paired values, negative/zero/missing input, water label, restoration and neutral wood passed.');

// Home endpoints survive entering the single editor before enabling scenarios.
panel.restore({...start,temperature:null,initialScenarioTemperatures:[20,8]},70,null);
panel.restore(plain(panel.snapshot()),70,null);toggle(true);
assert.deepEqual(plain(panel.payload().scenarios.map(s=>s.temperature)),[20,8]);
choose(1);change('scenario-temperature','9','input');toggle(false);toggle(true);
assert.deepEqual(plain(panel.payload().scenarios.map(s=>s.temperature)),[20,9]);
panel.restore({...start,temperature:null,initialScenarioTemperatures:[0,0]},70,null);toggle(true);
assert.deepEqual(plain(panel.payload().scenarios.map(s=>s.temperature)),[0,0]);
// A temperature changed in the single editor takes precedence over old home endpoints.
panel.restore({...start,temperature:null,initialScenarioTemperatures:[20,8]},70,null);
change('scenario-temperature','17','input');toggle(true);
assert.deepEqual(plain(panel.payload().scenarios.map(s=>s.temperature)),[17,17]);

// Conditions must not describe defaults before an FC is available.
panel.restore({...start,lo:'',hi:'',manual:false},70);
assert.equal(nodes['conditions-summary'].hidden,true);
assert.equal(nodes['scenario-summary'].children.length,0);
state('Asciutto');
assert.equal(nodes['conditions-summary'].hidden,false);
assert.equal(nodes['scenario-summary'].children.length,1);
toggle(true);
choose(0);manual('','');
assert.equal(nodes['scenario-summary'].children.length,1);
assert.equal(nodes['scenario-summary'].children[0].children[0].textContent,'2');
choose(1);manual('','');
assert.equal(nodes['conditions-summary'].hidden,true);
assert.equal(nodes['scenario-summary'].children.length,0);
console.log('Conditions stay hidden without FC; available scenarios retain their original numbering.');


// Mobile: the multi-scenario warning is short and the missing fields remain identifiable.
panel.restore(null,70,null);
media.matches=true;media.events.change();
toggle(true);
assert.equal(nodes['scenario-error'].textContent,'Compila scenari 1 e 2');
nodes['add-scenario'].click();
assert.equal(nodes['scenario-error'].textContent,'Compila scenari 1, 2 e 3');
nodes['remove-scenario'].click();
choose(0);
assert.equal(nodes['scenario-error'].textContent,'Compila scenari 1 e 2');
assert.equal(nodes['scenario-temperature'].placeholder,'…');
assert.equal(nodes['scenario-temperature']['aria-invalid'],'true');
assert.equal(nodes.lo.placeholder,'…');
assert.equal(nodes['body-state-row']['data-needs-value'],'true');
state('Asciutto');change('scenario-temperature','20','input');
assert.equal(nodes['scenario-error'].textContent,'Compila scenario 2');
assert.equal(nodes['scenario-temperature']['aria-invalid'],'false');
assert.equal(nodes.lo.placeholder,'');
change('heavy','1','input');
assert.equal(nodes.feather['data-needs-value'],'true');
assert.equal(nodes.feather.options[0].textContent,'…');
change('feather','yes');
assert.equal(nodes.feather['data-needs-value'],'false');
assert.equal(nodes.feather.options[0].textContent,'Da precisare');
assert.equal(nodes['scenario-error'].textContent,'Compila scenario 2');
choose(1);
assert.equal(nodes['body-state-row']['data-needs-value'],'true');
change('lo','1.00','input');
assert.equal(nodes['body-state-row']['data-needs-value'],'false','Direct FC entry replaces body-state selection');
change('scenario-temperature','18','input');
assert.equal(nodes['scenario-error'].textContent,'');
assert.equal(nodes['use-scenarios'].disabled,false);

// Native popover trigger: second tap closes each help, including the air help.
choose(0);
for(const id of ['scenario','temperature','heavy','air']){
  const button=nodes[id+'-help-button'],hint=nodes[id+'-help'];
  assert.equal(button.popovertarget,id+'-help');
  button.click();assert.equal(button['aria-expanded'],'true');
  assert.equal(hint.matches(':popover-open'),true);
  button.click();assert.equal(button['aria-expanded'],'false');
  assert.equal(hint.matches(':popover-open'),false);
}
nodes['air-help-button'].click();state('Immerso');
assert.equal(nodes['air-help-button']['aria-expanded'],'false','Hiding air dismisses its open helper');
toggle(false);media.matches=false;media.events.change();panel.restore(null,70,null);
console.log('FC mobile: concise scenario messages, missing-field highlights and repeat-tap popovers passed.');
