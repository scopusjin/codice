const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(require('path').join(__dirname,'../app/fc_panel_frontend/index.html'),'utf8'),nodes={},buttons=[],inputs=[];
class El{
  constructor(id){this.events={};this.dataset={};this.style={};this.children=[];this.value='';this.hidden=false;this.open=false;this.textContent='';if(id)this.id=id;}
  set id(v){this._id=v;nodes[v]=this;}get id(){return this._id;}
  set value(v){this._value=String(v);}get value(){return this._value;}
  set innerHTML(s){parseInputs(s);parseButtons(s);}
  append(...els){for(const e of els){e.parent=this;this.children.push(e);}}
  replaceChildren(...els){this.children=[];this.append(...els);}
  addEventListener(e,f){this.events[e]=f;}setAttribute(k,v){this[k]=v;}focus(){}
  querySelector(s){if(s.startsWith('label['))return new El();assert(nodes[s.slice(1)],'Missing DOM element '+s);return nodes[s.slice(1)];}
  querySelectorAll(s){if(s==='input')return inputs;const map={'[data-input]':'input','[data-state]':'state','[data-weight]':'weight'};assert(map[s],'Unexpected selector '+s);return buttons.filter(b=>b.dataset[map[s]]!==undefined);}
}
function parseInputs(s){for(const m of s.matchAll(/<input\b([^>]*)>/g)){const id=m[1].match(/id="([^"]+)"/);if(!id)continue;const e=nodes[id[1]]||new El(id[1]);const val=m[1].match(/value="([^"]*)"/);if(val)e.value=val[1];inputs.push(e);}}
function parseButtons(s){for(const m of s.matchAll(/<button\b([^>]*)>/g)){const id=m[1].match(/id="([^"]+)"/),e=id?nodes[id[1]]||new El(id[1]):new El();for(const d of m[1].matchAll(/data-(\w+)="([^"]+)"/g))e.dataset[d[1]]=d[2];buttons.push(e);}}
for(const m of html.matchAll(/id="([^"]+)"/g)){assert(!nodes[m[1]],'Duplicate ID '+m[1]);new El(m[1]);}
const markup=html.slice(0,html.indexOf('<script>'));parseInputs(markup);parseButtons(markup);
nodes['weight-data'].textContent=html.match(/id="weight-data">(.*?)<\/script>/s)[1];
nodes.surface.value='0';nodes.water.value='stagnante';nodes.air.value='still';
const code=html.match(/<script>(.*?)<\/script>/s)[1].replace('})();','globalThis.api={evaluateFC,exampleMatches,adjust,bounds,referenceLabel,wetSupportDecision,roundFC,roundRange,onFCGrid,airChangesSuggestion,RULES,EXAMPLES,SOURCES,table};})();');
const ctx={document:{getElementById:id=>nodes[id],createElement:()=>new El()},console,window:{}};vm.runInNewContext(code,ctx);
const api=ctx.api,base={state:'Asciutto',s:0,p:0,m:0,h:0,surf:0,air:'still',wind:false,strongWind:false,isolation:'',volume:'',water:'stagnante',feather:'no',leaf:'wet'};
const run=c=>JSON.parse(JSON.stringify(api.evaluateFC({...base,...c}))),eq=(c,expected)=>assert.deepEqual(run(c).range,expected,JSON.stringify(c));


module.exports={api,base,run,nodes,buttons,html,panel:ctx.window.FCPanel,context:ctx};
