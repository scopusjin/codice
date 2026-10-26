const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {makeRecord, label, createStore} = require('../app/case_browser_frontend/store.js');

const caseData = {format:'mortem-case', schema_version:1, case_code:'x26-05', view:'full',
  app_version:'test', saved_at:'2026-10-12T18:00:00Z', inputs:{peso:70, rt_val:null},
  fc_draft:{manual:true, scenarios:[{lo:'1.25', hi:'1.30'}]}};
const raw = JSON.stringify(caseData);
const record = makeRecord(raw, 'unused', new Date('2026-10-12T20:00:00Z'));
assert.equal(record.id, 'code:x26-05');
assert.deepEqual(JSON.parse(record.data), {...caseData, saved_at:'2026-10-12T20:00:00.000Z'});
assert.equal(JSON.parse(raw).saved_at, caseData.saved_at);
assert.match(label(record), /x26-05.*Completa/);
assert.match(label({...record, code:'', view:'msil'}), /Senza sigla.*Sopralluogo/);
const unnamed = JSON.stringify({...caseData, case_code:''});
assert.notEqual(makeRecord(unnamed, 'one').id, makeRecord(unnamed, 'two').id);
assert.throws(() => makeRecord(JSON.stringify({...caseData, schema_version:999}), 'id'));
assert.throws(() => makeRecord('x'.repeat(1024 * 1024 + 1), 'id'));

// Exercise the UI against a storage boundary, including failed writes and concurrent updates.
const ids = ['save-controls','save','open','replace-note','status','saved','archive-title','empty',
  'saved-controls','version-note','archive'];
const nodes = Object.fromEntries(ids.map(id => [id, {textContent:'', value:'', hidden:false,
  disabled:false, events:{}, addEventListener(type, fn) { this.events[type] = fn; },
  replaceChildren(...children) { this.children = children; this.value = children[0]?.value || ''; }}]));
const records = new Map();
let failSave = false, conflict = false;
const storage = {
  async list() { return [...records.values()]; },
  async read(id) { return records.get(id); },
  async save(value, expected) {
    if (failSave) { const e = new Error(); e.name = 'QuotaExceededError'; throw e; }
    if (conflict || (records.has(value.id) && records.get(value.id).data !== expected)) return false;
    records.set(value.id, value); return true;
  }
};
const messages = [], events = {};
const parent = {postMessage:message => messages.push(message)};
const context = {MortemCaseStore:{makeRecord, label, createStore:() => storage},
  window:{parent, addEventListener:(type, fn) => events[type] = fn},
  document:{getElementById:id => nodes[id], body:{scrollHeight:100},
    createElement:() => ({}), documentElement:{style:{setProperty(){}}}},
  crypto:{randomUUID:() => require('node:crypto').randomUUID()},
  ResizeObserver:class { observe(){} }, console};
vm.runInNewContext(fs.readFileSync(require.resolve('../app/case_browser_frontend/main.js'), 'utf8'), context);
const render = data => events.message({source:parent, data:{type:'streamlit:render',
  args:{instance:'current', enabled:true, data, app_version:'test'}}});
const settle = () => new Promise(resolve => setImmediate(resolve));
(async () => {
  await assert.rejects(createStore(undefined).list(), /non disponibile/);
  render(raw); await settle();
  assert.equal(nodes.save.disabled, false);
  assert.equal(nodes.save.textContent, 'Salva nel browser');
  await nodes.save.events.click();
  assert.equal(records.size, 1);
  assert.equal(nodes.status.textContent, 'Caso salvato nel browser.');
  assert.equal(nodes.save.textContent, 'Aggiorna nel browser');
  assert.equal(messages.filter(m => m.type === 'streamlit:setComponentValue').length, 0);
  render(JSON.stringify({...caseData, inputs:{peso:85}})); await settle();
  await nodes.save.events.click();
  assert.equal(records.size, 1);
  assert.equal(JSON.parse(records.get(record.id).data).inputs.peso, 85);
  assert.equal(nodes.status.textContent, 'Caso aggiornato nel browser.');
  const existing = records.get(record.id).data;
  conflict = true;
  await nodes.save.events.click();
  assert.match(nodes.status.textContent, /un’altra scheda/);
  assert.equal(records.get(record.id).data, existing);
  conflict = false; failSave = true;
  await nodes.save.events.click();
  assert.match(nodes.status.textContent, /non è stato salvato/);
  assert.equal(records.get(record.id).data, existing);
  failSave = false;
  await nodes.open.events.click();
  const opened = messages.filter(m => m.type === 'streamlit:setComponentValue');
  assert.equal(opened.length, 1);
  assert.equal(opened[0].value.data, existing);
  assert.equal(opened[0].value.instance, 'current');
  render(unnamed); await settle();
  await nodes.save.events.click(); await nodes.save.events.click();
  assert.equal(records.size, 3);
  console.log('Browser cases: preserved inputs/drafts, named updates, unnamed saves, conflicts, failure and explicit open passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
