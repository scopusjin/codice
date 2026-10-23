const assert=require('node:assert/strict');
const {panel,nodes}=require('./fc_panel_harness.cjs');
const fields={thin:'0',thick:'0',medium:'0',heavy:'0',surface:'0',air:'still',isolation:'none',feather:'no','blanket-volume':'no','support-soaked':'no'};
const toggle=(id,value)=>{nodes[id].checked=value;nodes[id].events.change();};
// Assumed equivalences must never be presented as published device-specific CFs.
for(const device of ['body-bag','thermal-foil']){
  panel.restore({state:'Asciutto',fields},70,20);toggle(device,true);
  const provenance=nodes['fc-provenance'].children;
  assert.equal(provenance[0].className,'fc-provenance-red');
  assert.match(provenance[0].textContent,/Assunzione degli autori dell’app/);
  assert(provenance.every(line=>line.className!=='fc-provenance-green'));
  assert.match(provenance[1].textContent,device==='body-bag'?/FC 1.2 per 1–2 strati pesanti asciutti/:/FC 1.8 per una coperta spessa/);
  assert.equal(nodes['rule-source'].textContent,'');
  assert(!nodes['rule-source'].classList.contains('fc-provenance-green'));
  assert.equal(nodes['h08-notice'].hidden,true);
  assert.match(panel.payload().explanation,/Assunzione degli autori/);
  assert.doesNotMatch(panel.payload().explanation,/Fattore di correzione indicato nella tabella/);
  toggle(device,false);
  assert(nodes['rule-source'].classList.contains('fc-provenance-green'));
  assert(!nodes['rule-source'].classList.contains('fc-provenance-red'));
}
panel.restore({state:'Asciutto',fields},70,20);toggle('body-bag',true);toggle('thermal-foil',true);
assert.equal(nodes['fc-provenance'].children.length,3);
assert.match(nodes['fc-provenance'].children[0].textContent,/sacco mortuario.*mantellina/);
panel.restore({state:'Asciutto',fields:{...fields,medium:'1'}},70,20);
assert(nodes['fc-provenance'].children.some(line=>line.className==='fc-provenance-green'));
assert.equal(nodes['h08-notice'].hidden,false,'Ordinary blankets retain their contextual evidence');
console.log('Cover provenance: author assumptions in red, concise references and ordinary-cover evidence preserved.');

for(const state of ['Asciutto','Bagnato'])for(const weight of [50,70,100])for(const surface of ['0','2','4']){
  const draft={state,fields:{...fields,thin:'2',thick:'1',surface}};
  panel.restore(draft,weight,20);toggle('thermal-foil',true);toggle('body-bag',true);
  const special=panel.payload();
  assert(nodes['fc-provenance'].children.every(line=>line.className!=='fc-provenance-green'));
  panel.restore({...draft,fields:{...draft.fields,thick:'2',medium:'1'}},weight,20);
  assert.deepEqual([...special.range],[...panel.payload().range]);
  assert.equal(JSON.stringify(special.base_range),JSON.stringify(panel.payload().base_range));
}
console.log('Special covers: numerical equivalence preserved across wet/dry conditions, weights and supports.');
