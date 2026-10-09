const assert=require('node:assert/strict');
const {panel,nodes,buttons,context}=require('./fc_panel_harness.cjs');
nodes.surface.selectedOptions=[{textContent:'Piano neutro'}];
let sent;
context.window.FCBridge={send:action=>{sent={action,...panel.payload()};}};
panel.restore(null,70);
assert.equal(nodes.lo.value,'1.00');
nodes.thin.value='3';nodes.thin.events.input();
assert.equal(nodes.lo.value,'1.20');assert.equal(nodes.hi.value,'1.30');
nodes.lo.value='1.25';nodes.lo.events.input();
const draft=panel.snapshot();panel.restore(draft,70);
assert.equal(nodes.lo.value,'1.25');
nodes.use.events.click();
assert.equal(sent.action,'use');assert.deepEqual([...sent.range],[1.25,1.3]);
assert.equal(sent.manual,true);assert.equal(sent.base_range,null);
assert(sent.description.includes('3 strati leggeri'));
panel.restore(draft,100);
assert.equal(nodes.lo.value,'1.20');assert.equal(nodes.hi.value,'1.30');
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
nodes.use.events.click();
assert.notDeepEqual([...sent.range],[2.7,2.7]);
assert.deepEqual([...sent.base_range],[2.7,2.7]);
assert.equal(sent.manual,false);

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
