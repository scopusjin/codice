'use strict';
const openButton = document.getElementById('open');
const fileInput = document.getElementById('file');
const status = document.getElementById('status');
let args = {}, busy = false;
const send = (type, data) => window.parent.postMessage({isStreamlitMessage:true, type, ...data}, '*');
const resize = () => send('streamlit:setFrameHeight', {height:document.body.scrollHeight});
function message(text) {
  status.textContent = text;
  status.hidden = !text;
  resize();
}
openButton.addEventListener('click', () => {
  // Keep the native file chooser in the user's click, without a server rerun.
  fileInput.value = '';
  fileInput.click();
});
fileInput.addEventListener('change', async () => {
  const file = fileInput.files[0];
  if (!file || busy) return;
  if (file.size > args.max_bytes) { message('Dimensione massima: 1 MB.'); return; }
  const instance = args.instance;
  busy = true;
  openButton.disabled = true;
  message('');
  try {
    const data = new TextDecoder('utf-8', {fatal:true}).decode(await file.arrayBuffer());
    if (instance !== args.instance) return;
    send('streamlit:setComponentValue', {value:{action:'open', instance, event_id:crypto.randomUUID(), data}});
  } catch (_) {
    message('File non valido o non leggibile.');
  } finally {
    busy = false;
    openButton.disabled = false;
    fileInput.value = '';
  }
});
window.addEventListener('message', event => {
  if (event.source !== window.parent || event.data?.type !== 'streamlit:render') return;
  args = event.data.args || {};
  const theme = event.data.theme || {};
  for (const [name, value] of Object.entries({'--text':theme.textColor, '--background':theme.backgroundColor,
      '--primary':theme.primaryColor, '--font':theme.font})) {
    if (value) document.documentElement.style.setProperty(name, value);
  }
  openButton.disabled = busy || !!event.data.disabled;
  resize();
});
new ResizeObserver(resize).observe(document.body);
send('streamlit:componentReady', {apiVersion:1});
resize();
