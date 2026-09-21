// Local Streamlit component protocol. Scientific rules stay in index.html.
(() => {
  let instance = null, initialized = false, timer = null, navigating = false;
  const root = document.getElementById('fc-full');
  function post(type, data) {
    window.parent.postMessage({isStreamlitMessage:true, type, ...data}, '*');
  }
  function resize() {
    post('streamlit:setFrameHeight', {height:Math.ceil(root.getBoundingClientRect().height) + 20});
  }
  function send(action) {
    if (!initialized || navigating) return;
    clearTimeout(timer);
    const payload = window.FCPanel.payload();
    // A pending incomplete input is a draft, never a chosen FC.
    if (action === 'use' && document.getElementById('use').disabled) return;
    navigating = action !== 'draft';
    post('streamlit:setComponentValue', {value:{...payload, instance, action,
      event_id:crypto.randomUUID()}});
  }
  function schedule() {
    if (!initialized || navigating) return;
    clearTimeout(timer);
    timer = setTimeout(() => send('draft'), 250);
  }
  window.FCBridge = {send};
  window.addEventListener('message', event => {
    if (event.source !== window.parent || event.data?.type !== 'streamlit:render') return;
    const args = event.data.args || {};
    document.documentElement.style.colorScheme = args.theme_base === 'dark' ? 'dark' : 'light';
    if (!initialized || instance !== args.instance) {
      instance = args.instance;
      window.FCPanel.setExamples(args.examples);
      window.FCPanel.restore(args.draft, typeof args.weight === 'number' ? args.weight : NaN);
      initialized = true; navigating = false;
    }
    resize();
  });
  for (const name of ['input','change','click']) root.addEventListener(name, schedule);
  new ResizeObserver(resize).observe(root);
  post('streamlit:componentReady', {apiVersion:1});
  resize();
})();
