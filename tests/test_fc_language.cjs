// Exercise the presentation layer with the real, unchanged FC engine.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const {panel,context,run,base,nodes}=require('./fc_panel_harness.cjs');
const dictionary=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const textNodes=['Consiglia FC','Rigor mortis','Più scenari','Data'].map(data=>({data,parentElement:{closest:()=>false}}));
const attributeNode={attributes:{'aria-label':'FC minimo'},hasAttribute(k){return k in this.attributes;},getAttribute(k){return this.attributes[k];},setAttribute(k,v){this.attributes[k]=v;}};
context.NodeFilter={SHOW_TEXT:4};
context.MutationObserver=class{observe(){}disconnect(){}};
context.document.documentElement={lang:'it'};
context.document.body={};
context.document.createTreeWalker=()=>{let index=-1;return {nextNode(){return ++index<textNodes.length;},get currentNode(){return textNodes[index];}};};
context.document.querySelectorAll=()=>[attributeNode];
vm.runInNewContext(fs.readFileSync(require.resolve('../app/fc_panel_frontend/i18n.js'),'utf8'),context);
const scenarios=[{}, {s:3}, {s:1,p:2}, {state:'Bagnato',s:1,wetClothes:'full'}, {state:'Bagnato',p:2,wind:true}, {state:'Immerso',water:'corrente'}, {state:'Asciutto',h:1,feather:'yes'}, {surf:8,leaf:'dry',leafCover:'no'}];
const before=scenarios.map(run),snapshot=JSON.stringify(panel.snapshot());
const translate=context.window.FCTranslation;
translate.set('en',dictionary);
assert.equal(textNodes[0].data,'Suggest CF');assert.equal(textNodes[1].data,'Rigor mortis');assert.equal(textNodes[2].data,'Multiple scenarios');assert.equal(textNodes[3].data,'Date');
assert.equal(attributeNode.attributes['aria-label'],'Minimum CF');
assert.deepEqual(scenarios.map(run),before);
assert.equal(JSON.stringify(panel.snapshot()),snapshot);
assert.equal(nodes.surface.value,'0');assert.equal(nodes.water.value,'stagnante');
assert.equal(translate.text('Fisse'),'Fixed');
assert.equal(translate.text('FC 1.10 – 1.30'),'CF 1.10 – 1.30');
assert.equal(translate.text('Rigor mortis'),'Rigor mortis');
for(const [source,expected] of [
 ['Assunzione degli autori dell’app: sacco mortuario assimilato a un telo pesante.','Assumption by the app authors: a body bag is treated as one heavy sheet.'],
 ['Assunzione degli autori dell’app: mantellina termica assimilata a una coperta spessa.','Assumption by the app authors: a thermal foil blanket is treated as one thick blanket.'],
 ['Riferimento Henssge: FC 1.2 per 1–2 strati pesanti asciutti.','Henssge reference: CF 1.2 for 1–2 thick, dry layers.'],
 ['Riferimento Henssge: FC 1.8 per una coperta spessa.','Henssge reference: CF 1.8 for one thick blanket.']
])assert.equal(translate.text(source),expected);

textNodes[0].data='Gestisci scenari';translate.set('en',dictionary);assert.equal(textNodes[0].data,'Manage scenarios');
translate.set('it',dictionary);assert.equal(textNodes[0].data,'Gestisci scenari');assert.equal(textNodes[2].data,'Più scenari');assert.equal(attributeNode.attributes['aria-label'],'FC minimo');
assert.deepEqual(scenarios.map(run),before);
console.log('FC language: reversible labels, stable values, drafts and scientific decisions passed.');
