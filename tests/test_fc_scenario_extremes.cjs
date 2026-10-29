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
// A range sharing the minimum belongs only to the maximum parenthesis.
panel.restore(start,70);toggle(true);choose(0);manual(.90,.90);
choose(1);state('Bagnato');manual(.90,1.00);
const tiedEndpoint=panel.payload();
assert.deepEqual(plain(tiedEndpoint.range),[.90,1.00]);
assert.match(tiedEndpoint.description,/0.90 \(corpo asciutto[^)]*\) — 1.00 \(corpo bagnato[^)]*\)$/);
assert.equal((tiedEndpoint.description.match(/corpo bagnato/g)||[]).length,1);

console.log("FC endpoint descriptions: OK");
