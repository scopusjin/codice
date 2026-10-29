const assert=require('node:assert/strict');
const {api,base,nodes}=require('./fc_panel_harness.cjs');
const plain=x=>JSON.parse(JSON.stringify(x));
function check(c,range,kind){
 const r=api.evaluateFC(c);
 assert.deepEqual(plain(r.range),range);
 assert.equal(r.kind,kind);
 api.renderFCProvenance(r,[],c);
 const text=nodes['fc-provenance'].children.map(p=>p.textContent).join(' ');
 if(kind==='Tabella Henssge')assert.doesNotMatch(text,/analogia|condizioni differenti|deduzione/);
 return r;
}
for(const [s,range] of [[2,[1.1,1.2]],[3,[1.2,1.3]]])
 check({...base,s},range,'Tabella Henssge');
for(const [s,p,m,range] of [[1,0,0,[.9,.9]],[2,0,0,[.9,1]],[3,0,0,[1.1,1.2]],[0,1,0,[1.1,1.1]],[0,0,1,[1.7,1.7]]]){
 const r=check({...base,s,p,m,surf:4},range,'Tabella Henssge');
 assert.match(r.detail,/tabella di Henssge/);
 assert.doesNotMatch(r.detail,/ragionamento dell’app/);
}
check({...base,s:2,surf:2},[1.2,1.3],'Tabella Henssge');
check({...base,s:2,surf:3},[1.4,1.5],'Tabella Henssge');
for(const extra of [{surf:10},{surf:8,leaf:'dry',leafCover:'no'},{surf:4,bodyBag:true}]){
 const c={...base,s:2,...extra},r=api.evaluateFC(c);
 assert.equal(r.kind,'Ragionamento dell’app');
}
const mixed=api.evaluateFC({...base,s:1,p:1,surf:4});
assert.equal(mixed.kind,'Ragionamento dell’app');
console.log('Tabulated provenance and retained app assumptions: OK.');

const windy=api.evaluateFC({...base,s:3,wind:true,air:'continuous'});
assert.equal(windy.kind,'Ragionamento dell’app');
assert.match(windy.detail,/estensione/);
