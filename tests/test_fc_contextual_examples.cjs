const assert=require('node:assert/strict');
const {api,base,panel,nodes}=require('./fc_panel_harness.cjs');
const ids=c=>Array.from(api.exampleMatches({...base,...c}),e=>e.id);
for(const [conditions,expected] of [
  [{state:'Immerso',water:'stagnante',waterNearZero:false,air:'unknown'},['t6_7-01','t6_7-10']],
  [{state:'Immerso',water:'stagnante',waterNearZero:true},['t6_7-15','t6_7-16']],
  [{state:'Immerso',water:'corrente',waterNearZero:false},[]],
  [{air:'continuous',wind:true},['t6_3-28']],
  [{surf:3},['t6_10-200']],
  [{surf:10},['t6_10-230']],
  [{surf:4},['t6_10-260']],
  [{surf:7},['t6_10-290']],
  [{surf:8,leaf:'wet',leafCover:'no'},['t6_11-riga-1']],
  [{surf:8,leaf:'humid',leafCover:'no'},['t6_11-riga-2']],
  [{surf:8,leaf:'dry',leafCover:'no'},['t6_11-riga-5']],
  [{surf:8,leaf:'dry',leafCover:'yes'},['t6_12-riga-1','t6_12-riga-13']],
  [{surf:8,leaf:'dry',leafCover:''},[]],
  [{air:'intermittent',wind:false},[]],
  [{state:'Bagnato',air:'continuous',wind:true,p:2},['t6_8-55']],
  [{state:'Bagnato',air:'continuous',wind:true,s:3},['t6_8-47']],
])assert.deepEqual(ids(conditions),expected,JSON.stringify(conditions));

// Exercise the visible source section: immersion must work despite stale,
// hidden land controls; each selected card carries its own source and weight.
const text=node=>[node.textContent,...node.children.map(text)].join('\n');
const links=node=>[...(node.href?[node.href]:[]),...node.children.flatMap(links)];
const fields={thin:'0',thick:'0',medium:'0',heavy:'0',surface:'0',air:'still',water:'stagnante'};
function show(state,extra){
  panel.restore({state,temperature:extra['scenario-temperature']??'20',fields:{...fields,...extra}},70,20);
  return text(nodes['example-list']);
}
let rendered=show('Immerso',{'scenario-temperature':'10',air:'unknown',surface:'metal','metal-type':'',thin:'invalid'});
assert.equal(nodes['source-examples'].hidden,false);
assert.match(rendered,/Caso 01/);assert.match(rendered,/Caso 10/);
assert.match(rendered,/Peso: 65 kg/);assert.match(rendered,/19,3 °C/);
assert.match(rendered,/tab\. 6\.7/);
assert(links(nodes['example-list']).includes('https://pubmed.ncbi.nlm.nih.gov/6485584/'));
rendered=show('Immerso',{'scenario-temperature':'0'});
assert.match(rendered,/Caso 15/);assert.match(rendered,/FC: 1\.040/);
assert.doesNotMatch(rendered,/Caso 01/);
show('Immerso',{water:'corrente','scenario-temperature':'0'});
assert.equal(nodes['source-examples'].hidden,true);
assert.match(text(nodes['source-full-citations']),/Brown e Marshall/);
rendered=show('Asciutto',{surface:'8',leaf:'dry','leaf-cover':'no'});
assert.match(rendered,/Prova su simulatore/);
assert.match(rendered,/Peso virtuale standard: 60,4 kg/);
assert.match(rendered,/Althaus/);assert.match(rendered,/tab\. 6\.11/);
assert.doesNotMatch(rendered,/Esperimento su cadavere|undefined/);
rendered=show('Asciutto',{surface:'8',leaf:'dry','leaf-cover':'yes',air:'intermittent'});
assert.match(rendered,/FC: 1\.77/);assert.match(rendered,/FC: 2\.72/);
assert.match(rendered,/asterisco/);
console.log('Contextual examples: condition matching, immersion, source links and simulator labels passed.');
