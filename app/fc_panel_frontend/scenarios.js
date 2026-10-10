// Several independent configurations share the existing, unchanged FC editor.
// Each keeps its own unadapted FC base; only their final bounds are combined.
(() => {
  const single = {...window.FCPanel}, q = id => document.getElementById(id);
  const copy = value => JSON.parse(JSON.stringify(value));
  let enabled = false, items = [], active = 0, paused = false, weightAdjusted = false;
  let defaultTemperature = '';

  function restoreTemperature(draft) {
    q('scenario-temperature').value = draft?.temperature ?? defaultTemperature;
  }
  function editorSnapshot() {
    return {...single.snapshot(), temperature:q('scenario-temperature').value};
  }
  function withTemperature(item) {
    const medium = item.conditions.state === 'Immerso' ? 'acqua' : 'ambiente';
    return item.description + ', ' + medium + ' ' + item.temperature + ' °C';
  }

  function describe(item) {
    const c = item.conditions, fields = item.draft.fields;
    if (c.state === 'Immerso') return 'corpo immerso in acqua ' + c.water +
      (c.water === 'stagnante' && c.waterNearZero ? ', prossima a 0 °C' : '');
    const parts = ['corpo ' + c.state.toLowerCase()], clothes = [];
    for (const [key, one, many] of [['s','strato leggero','strati leggeri'],
      ['p','strato pesante','strati pesanti'], ['m','coperta spessa','coperte spesse'],
      ['h','piumone/coperta molto pesante','piumoni/coperte molto pesanti']]) {
      if (c[key] > 0) clothes.push(c[key] + ' ' + (c[key] === 1 ? one : many));
    }
    parts.push(clothes.length ? clothes.join(', ') : 'senza indumenti o coperture');
    if (c.state === 'Asciutto') {
      if (!q('isolation-row').hidden && c.isolation === 'one') parts.push('un capo particolarmente isolante');
      if (!q('isolation-row').hidden && c.isolation === 'several') parts.push('più capi particolarmente isolanti');
      if (c.h && c.feather === 'yes') parts.push('piumone di piume voluminoso e avvolgente');
      if (c.m + c.h > 1 && (!c.h || c.feather === 'no') && c.volume === 'yes') parts.push('coperture molto voluminose');
    }
    parts.push(({still:'aria ferma',continuous:'aria in movimento continuo',
      intermittent:'aria in movimento intermittente',unknown:'movimento dell’aria non ricostruibile'})[fields.air] || '');
    const surfaces = {0:fields.surface === 'wood' ? 'piano di legno' : 'pavimento interno',1:'asfalto / terreno / prato',
      2:'materasso / tappeto spesso',3:'supporto molto imbottito e avvolgente',4:'cemento / pietra',
      5:'pavimento molto freddo',6:'piano metallico sottile o leggero',7:'piano metallico molto spesso',
      8:'foglie ' + ({dry:'secche',humid:'umide',wet:'bagnate'}[c.leaf] || ''),10:'pavimento in PVC'};
    if (surfaces[c.surf]) parts.push('su ' + surfaces[c.surf]);
    if (c.surf === 8 && c.leafCover === 'yes') parts.push('con copertura di foglie');
    if (c.state === 'Bagnato' && [2,3].includes(c.surf) && c.supportSoaked === 'yes') parts.push('appoggio impregnato di liquidi');
    if (c.state === 'Bagnato' && c.surf === 1 && c.air === 'continuous' && c.wetCase && c.s+c.p === 2 && !c.m && !c.h) parts.push('pantaloni e slip fradici, pioggia');
    return parts.filter(Boolean).join(', ');
  }
  function capture() {
    const item = single.payload.call(single);
    item.draft = editorSnapshot();
    const raw = q('scenario-temperature').value.trim().replace(',','.');
    item.temperature = /^-?\d+(\.\d{1,2})?$/.test(raw) ? Number(raw) : null;
    item.error = q('error').textContent;
    if (item.temperature === null || !Number.isFinite(item.temperature)) item.error ||= 'Specificare la temperatura.';
    item.description = describe(item);
    return item;
  }
  function combined() {
    if (!items.length || items.some(item => item.error || !item.range.every(Number.isFinite))) return null;
    const range = [Math.min(...items.map(item => item.range[0])), Math.max(...items.map(item => item.range[1]))];
    const conditions = bound => [...new Set(items.filter(item => item.range[bound] === range[bound]).map(withTemperature))].join(' / ');
    return {range, description:'FC degli scenari considerati: ' + range[0].toFixed(2) +
      ' [' + conditions(0) + '] — ' + range[1].toFixed(2) + ' [' + conditions(1) + ']'};
  }
  function render() {
    q('multiple-scenarios').checked = enabled;
    q('scenario-controls').hidden = q('scenario-result').hidden = !enabled;
    q('scenario-temperature-row').hidden = !enabled;
    q('scenario-temperature-label').textContent = single.snapshot().state === 'Immerso' ? 'Temperatura dell’acqua' : 'Temperatura ambientale';
    q('use').hidden = enabled;
    q('fc-heading').textContent = enabled ? 'FC scenario ' + (active+1) : 'FC';
    if (!enabled) return;
    q('scenario-select').replaceChildren(...items.map((item, i) => {
      const option = document.createElement('option'); option.value = String(i);
      option.textContent = 'Scenario ' + (i+1) + ' · ' + (item.error ? 'da completare' :
        item.range[0] === item.range[1] ? item.range[0].toFixed(2) : item.range.map(v=>v.toFixed(2)).join('–'));
      return option;
    }));
    q('scenario-select').value = String(active);
    q('remove-scenario').disabled = items.length <= 2;
    const group = combined(), missing = items.flatMap((item,i)=>item.error?[i+1]:[]);
    q('scenario-summary').textContent = group ? group.description + '.' : 'FC degli scenari considerati: da completare.';
    q('scenario-error').textContent = missing.length ? 'Completare gli scenari: ' + missing.join(', ') + '.' : '';
    q('use').disabled = q('use-scenarios').disabled = !group;
  }
  function refresh() {
    if (paused || !enabled) return;
    const current = capture(), previous = items[active];
    if (previous && (JSON.stringify(current.range) !== JSON.stringify(previous.range) ||
        JSON.stringify(current.conditions) !== JSON.stringify(previous.conditions) || current.manual !== previous.manual)) weightAdjusted = false;
    items[active] = current;
    render();
  }
  function load(index, weight) {
    paused = true;
    try { restoreTemperature(items[index].draft); single.restore(items[index].draft, weight); items[index] = capture(); }
    finally { paused = false; }
  }
  function normalizeAll(weight) {
    for (let i=0; i<items.length; i++) load(i,weight);
    load(active,weight); render();
  }
  window.FCScenarios = {refresh, weightChanged() {
    if (!enabled) return false;
    const previous = combined()?.range;
    normalizeAll(Number(q('weight').value.replace(',','.')) || NaN);
    const current = combined()?.range;
    weightAdjusted = !!(previous && current && current.some((v,i)=>v!==previous[i]));
    return true;
  }};
  window.FCPanel = {...single,
    snapshot() {
      return {...editorSnapshot(), multiple:enabled, activeScenario:active,
        scenarios:items.map(item=>copy(item.draft)), scenarioWeightAdjusted:weightAdjusted};
    },
    restore(draft, weight, temperature) {
      if (temperature !== undefined) defaultTemperature = Number.isFinite(temperature) ? String(temperature) : '';
      restoreTemperature(draft);
      paused = true; enabled = !!draft?.multiple;
      try { single.restore(draft,weight); } finally { paused = false; }
      items = Array.isArray(draft?.scenarios) ? draft.scenarios.map(d=>({draft:copy(d)})) : [];
      active = Math.max(0,Math.min(Number(draft?.activeScenario)||0,items.length-1));
      weightAdjusted = !!draft?.scenarioWeightAdjusted;
      if (enabled && items.length >= 2) normalizeAll(weight);
      else { enabled = false; items = []; active = 0; render(); }
    },
    payload() {
      if (!enabled) return {...single.payload.call(single), draft:this.snapshot()};
      const group = combined();
      return {draft:this.snapshot(), range:group?.range || [null,null], weight:Number(q('weight').value.replace(',','.')),
        base_range:null, manual:false, weight_adjusted:weightAdjusted, rule:'multiple-scenarios',
        description:group?.description || '', scenarios:items.map(({error,...item})=>copy(item))};
    }
  };
  q('multiple-scenarios').addEventListener('change',()=>{
    if (q('multiple-scenarios').checked) {
      const current = capture();
      if (items.length < 2) { items = [current,copy(current)]; active = 1; }
      else items[active] = current;
      enabled = true; normalizeAll(current.weight);
    } else {
      enabled = false; weightAdjusted = false; load(active,items[active].weight); render();
    }
  });
  q('scenario-select').addEventListener('change',()=>{
    active = Number(q('scenario-select').value); load(active,items[active].weight); render();
  });
  q('add-scenario').addEventListener('click',()=>{
    weightAdjusted = false;
    items.push(copy(items[active])); active = items.length-1; load(active,items[active].weight); render();
  });
  q('remove-scenario').addEventListener('click',()=>{
    if (items.length <= 2) return;
    weightAdjusted = false;
    items.splice(active,1); active = Math.min(active,items.length-1); load(active,items[active].weight); render();
  });
  q('use-scenarios').addEventListener('click',()=>q('use').click());
  q('scenario-temperature').addEventListener('input',refresh);
  render();
})();
