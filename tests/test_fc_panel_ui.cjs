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
assert(sent.description.includes('3 strati leggeri'));
panel.restore(draft,100);
assert.equal(nodes.lo.value,'1.20');assert.equal(nodes.hi.value,'1.30');
buttons.find(x=>x.dataset.state==='Immerso').events.click();nodes.use.events.click();
assert.equal(sent.conditions.s,undefined);assert.equal(sent.conditions.surf,undefined);
nodes['open-tables'].events.click({preventDefault(){}});assert.equal(sent.action,'tables');
panel.restore(null,NaN);assert.equal(nodes.use.disabled,true);
console.log('FC controls: manual bounds, weight, draft, immersion and tables handoff passed.');

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
