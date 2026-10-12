'use strict';
const $ = id => document.getElementById(id);
let database;
try { database = window.indexedDB; } catch (_) { /* Storage can be blocked by browser settings. */ }
const archiveStore = MortemCaseStore.createStore(database);
let args = {}, entries = [], busy = false, available = false, refreshId = 0;
const send = (type, data) => window.parent.postMessage({isStreamlitMessage:true, type, ...data}, '*');
const resize = () => send('streamlit:setFrameHeight', {height:document.body.scrollHeight + 4});
function status(text) { $('status').textContent = text; resize(); }
function update() {
  let code = '';
  if (args.data) code = JSON.parse(args.data).case_code.trim();
  const existing = code && entries.some(record => record.code === code);
  $('save').textContent = existing ? 'Aggiorna nel browser' : 'Salva nel browser';
  $('replace-note').hidden = !existing;
  $('save').disabled = !available || !args.enabled || !args.data || busy;
  $('open').disabled = !available || !args.enabled || !entries.length || busy;
  const selected = entries.find(record => record.id === $('saved').value);
  $('version-note').hidden = !selected || selected.appVersion === args.app_version;
  resize();
}
function showEntries(records) {
  const selected = $('saved').value;
  entries = records;
  $('saved').replaceChildren(...records.map(record => {
    const option = document.createElement('option');
    option.value = record.id;
    option.textContent = MortemCaseStore.label(record);
    return option;
  }));
  if (records.some(record => record.id === selected)) $('saved').value = selected;
  $('archive-title').textContent = `Casi salvati${records.length ? ' (' + records.length + ')' : ''}`;
  $('empty').hidden = !!records.length;
  $('saved-controls').hidden = !records.length;
  update();
}
function storageError(error) {
  status(error && error.name === 'QuotaExceededError'
    ? 'Spazio del browser esaurito. Il caso non è stato salvato: usa Scarica file.'
    : 'Archivio del browser non disponibile. Nessun caso è stato modificato: usa Scarica file.');
}
async function refresh() {
  const requestId = ++refreshId;
  try {
    const records = await archiveStore.list();
    if (requestId !== refreshId) return;
    available = true;
    showEntries(records);
  } catch (error) {
    if (requestId !== refreshId) return;
    available = false; update(); storageError(error);
  }
}
$('save').addEventListener('click', async () => {
  if ($('save').disabled) return;
  busy = true; update();
  try {
    const record = MortemCaseStore.makeRecord(args.data, crypto.randomUUID());
    const previous = entries.find(item => item.id === record.id);
    const saved = await archiveStore.save(record, previous ? previous.data : null);
    await refresh();
    if (saved) {
      $('saved').value = record.id;
      status(previous ? 'Caso aggiornato nel browser.' : 'Caso salvato nel browser.');
    } else {
      status('Questo caso è stato aggiornato in un’altra scheda. Controlla l’elenco e premi nuovamente Aggiorna nel browser.');
    }
  } catch (error) { storageError(error); }
  finally { busy = false; update(); }
});
$('open').addEventListener('click', async () => {
  if ($('open').disabled) return;
  busy = true; update();
  try {
    const instance = args.instance;
    const record = await archiveStore.read($('saved').value);
    if (!record) { await refresh(); status('Questo caso non è più disponibile nel browser.'); return; }
    if (instance !== args.instance) return;
    send('streamlit:setComponentValue', {value:{instance, action:'open', event_id:crypto.randomUUID(), data:record.data}});
    status('Apertura del caso…');
  } catch (error) { storageError(error); }
  finally { busy = false; update(); }
});
$('archive').addEventListener('toggle', () => { resize(); if ($('archive').open) refresh(); });
$('saved').addEventListener('change', update);
window.addEventListener('message', event => {
  if (event.source !== window.parent || event.data?.type !== 'streamlit:render') return;
  args = event.data.args || {};
  const theme = event.data.theme || {};
  for (const [name, value] of Object.entries({'--text':theme.textColor, '--field':theme.secondaryBackgroundColor, '--primary':theme.primaryColor})) {
    if (value) document.documentElement.style.setProperty(name, value);
  }
  update();
  refresh();
});
new ResizeObserver(resize).observe(document.body);
send('streamlit:componentReady', {apiVersion:1});
resize();
