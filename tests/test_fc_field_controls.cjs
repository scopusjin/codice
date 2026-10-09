const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function harness(version) {
  const nodes = {}, values = [], edits = [];
  function node(id) {
    return nodes[id] ||= {
      value: '', dataset: {}, style: {setProperty() {}}, events: {},
      classList: {toggle() {}, remove() {}},
      setAttribute(name, value) { this[name] = value; },
      addEventListener(name, callback) { this.events[name] = callback; },
      fire(name, event = {}) { (this.events[name] || this['on' + name])?.(event); },
      blur() { this.fire('blur'); },
    };
  }
  const document = {getElementById: node, querySelectorAll: () => [], documentElement: node('html')};
  const window = {addEventListener() {}, clearTimeout() {}, setTimeout(callback) { callback(); return 1; }};
  let render;
  if (version === 1) {
    const Streamlit = {
      RENDER_EVENT: 'render', events: {addEventListener(name, callback) { render = callback; }},
      setComponentReady() {}, setFrameHeight() {},
      setComponentValue(value) { value?.edit_token ? edits.push(value) : values.push(value); },
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../app/decimal_number_input_frontend/main.js'), 'utf8'), {document, window, Streamlit});
    return {input: node('number-input'), minus: node('number-minus'), plus: node('number-plus'),
      values, edits, render: data => render({detail: {args: data}})};
  }
  const source = fs.readFileSync(path.join(__dirname, '../app/decimal_number_input_v2.py'), 'utf8');
  const js = source.match(/_JS = r"""([\s\S]*?)"""/)[1];
  const context = {document, window};
  vm.runInNewContext(js.replace('export default function', 'globalThis.render = function'), context);
  return {input: node('.number-input'), minus: node('.number-minus'), plus: node('.number-plus'),
    values, edits, render: data => context.render({parentElement: {querySelector: node}, data,
      setStateValue: (key, value) => values.push(value), setTriggerValue: key => edits.push(key)})};
}

for (const version of [1, 2]) {
  const h = harness(version);
  const data = {value: 2, decimals: 2, step: .05, min_value: .35, sync_token: 0, edit_on_click: true};
  h.render(data);
  assert.equal(h.input.readOnly, true);
  assert.equal(h.input.inputmode, 'none');
  h.input.fire('click');
  h.minus.fire('click');
  h.plus.fire('click');
  for (const key of ['Enter', ' ', 'ArrowUp', 'ArrowDown', '2', 'Backspace', 'Delete']) {
    h.input.fire('keydown', {key, preventDefault() {}});
  }
  assert.equal(h.edits.length, 10);
  assert.equal(h.input.value, '2.00');
  assert.equal(h.values.length, 0);
  h.input.value = '3'; h.input.fire('input'); h.input.fire('blur');
  assert.equal(h.input.value, '2.00');
  assert.equal(h.values.length, 0);
  // A weight-driven refresh changes the displayed FC without opening its panel.
  h.render({...data, value: 1.75, sync_token: 1});
  assert.equal(h.input.value, '1.75');
  assert.equal(h.edits.length, 10);
  h.render({...data, disabled: true, sync_token: 1}); h.input.fire('click');
  assert.equal(h.edits.length, 10);

  // Weight and temperature inputs retain ordinary editing, with no navigation.
  const ordinary = harness(version);
  ordinary.render({...data, edit_on_click: false});
  ordinary.input.fire('click');
  ordinary.input.value = '3'; ordinary.input.fire('input'); ordinary.input.fire('blur');
  assert.equal(ordinary.input.readOnly, false);
  assert.equal(ordinary.values.at(-1), 3);
  assert.equal(ordinary.edits.length, 0);
}
console.log('FC field V1/V2: click/keyboard opens editor; inline edits blocked; weight refresh never navigates.');
