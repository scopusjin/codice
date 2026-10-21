const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const elements = Object.fromEntries(['open','file','status'].map(id => [id, {
  events:{}, files:[], value:'', disabled:true,
  addEventListener(name, handler){this.events[name]=handler;},
  click(){this.clicks=(this.clicks||0)+1;}
}]));
const messages = [], events = {};
const parent = {postMessage:message=>messages.push(message)};
const context = {document:{getElementById:id=>elements[id], body:{scrollHeight:44},
    documentElement:{style:{setProperty(){}}}},
  window:{parent,addEventListener:(name,handler)=>events[name]=handler},
  ResizeObserver:class{observe(){}}, TextDecoder, crypto:{randomUUID:()=>String(messages.length)}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../app/case_file_picker_frontend/main.js'),'utf8'),context);
const render = instance => events.message({source:parent,data:{type:'streamlit:render',args:{instance,max_bytes:1024}}});
const sentFiles = () => messages.filter(message=>message.type==='streamlit:setComponentValue');
const bytes = text => new TextEncoder().encode(text).buffer;

(async () => {
  render('current');
  assert.equal(elements.open.disabled,false);
  // Selecting a file is triggered synchronously by the single button click.
  elements.open.events.click();
  assert.equal(elements.file.clicks,1);
  assert.equal(sentFiles().length,0);
  await elements.file.events.change(); // Cancelled chooser.
  assert.equal(sentFiles().length,0);
  elements.file.files=[{size:20,arrayBuffer:async()=>bytes('{"case":"prova"}')}];
  await elements.file.events.change();
  assert.equal(sentFiles().length,1);
  assert.equal(sentFiles()[0].value.data,'{"case":"prova"}');
  assert.equal(sentFiles()[0].value.instance,'current');
  assert.equal(elements.open.disabled,false);
  elements.file.files=[{size:1025,arrayBuffer:()=>{throw Error('Oversized file read');}}];
  await elements.file.events.change();
  assert.equal(sentFiles().length,1);
  assert.match(elements.status.textContent,/1 MB/);
  elements.file.files=[{size:1,arrayBuffer:async()=>new Uint8Array([255]).buffer}];
  await elements.file.events.change();
  assert.equal(sentFiles().length,1);
  assert.match(elements.status.textContent,/non valido/);
  let finish;
  elements.file.files=[{size:2,arrayBuffer:()=>new Promise(resolve=>finish=resolve)}];
  const pending=elements.file.events.change();
  render('another');
  finish(bytes('{}'));
  await pending;
  assert.equal(sentFiles().length,1);
  console.log('Direct file chooser, cancellation, size/encoding checks and stale events: passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
