// Several independent configurations share the existing, unchanged FC editor.
// Each keeps its own unadapted FC base; only their final bounds are combined.
(() => {
  const single = {...window.FCPanel}, q = id => document.getElementById(id);
  const copy = value => JSON.parse(JSON.stringify(value));
  let enabled = false, items = [], active = 0, paused = false, weightAdjusted = false;
  let defaultTemperature = '', temperatureEdited = false;

  function restoreTemperature(draft) {
    q('scenario-temperature').value = draft?.temperature ?? defaultTemperature;
    temperatureEdited = !!draft?.temperatureEdited;
  }
  function editorSnapshot() {
    return {...single.snapshot(), temperature:q('scenario-temperature').value, temperatureEdited};
  }
  function capture() {
    const item = single.payload.call(single);
    item.draft = editorSnapshot();
    const temperature = temperatureValue();
    item.temperature = Number.isFinite(temperature) ? temperature : null;
    item.error = q('error').textContent;
    if (item.temperature === null || !Number.isFinite(item.temperature)) item.error ||= 'Specificare la temperatura.';
    item.description = window.FCDescriptions.conditions(item.conditions,item.draft.fields);
    return item;
  }
  function combined() {
    if (!items.length || items.some(item => item.error || !item.range.every(Number.isFinite))) return null;
    const range = [Math.min(...items.map(item => item.range[0])), Math.max(...items.map(item => item.range[1]))];
    const conditions = bound => [...new Set(items.filter(item => item.range[bound] === range[bound]).map(item=>item.description))].join(' / ');
    if(range[0]===range[1])return {range,description:'FC degli scenari considerati: '+range[0].toFixed(2)+' ('+conditions(0)+')'};
    return {range, description:'FC degli scenari considerati: ' + range[0].toFixed(2) +
      ' (' + conditions(0) + ') — ' + range[1].toFixed(2) + ' (' + conditions(1) + ')'};
  }
  function renderConditions(selected, range) {
    const rows = range && range.every(Number.isFinite) && range[0]!==range[1] ? [0,1].map(index=>[
      index===0?'Minimo':'Massimo', [...new Set(selected.filter(item=>item.range[index]===range[index]).map(item=>item.description))].join(' / ')
    ]) : [['FC',[...new Set(selected.map(item=>item.description))].join(' / ')]];
    q('scenario-summary').replaceChildren(...rows.map(([label,description])=>{
      const row=document.createElement('div');row.className='condition-line';
      const name=document.createElement('span'),text=document.createElement('span');
      name.textContent=label;text.textContent='('+description+').';row.append(name,text);return row;
    }));
  }
  function updateTemperatureLabel() {
    const immersed=single.snapshot().state==='Immerso';
    q('environment-row').dataset.immersed=String(immersed);
    const label=q('scenario-temperature-label');
    label.textContent=immersed?'T.':'Temperatura ambientale';
    q('scenario-temperature').setAttribute('aria-label',immersed?'Temperatura dell’acqua in gradi Celsius':'Temperatura ambientale in gradi Celsius');
    if(immersed && q('water-fields').getBoundingClientRect &&
       q('scenario-temperature-row').getBoundingClientRect().top-q('water-fields').getBoundingClientRect().top>12)label.textContent='T. acqua';
  }
  function render() {
    q('multiple-scenarios').checked = enabled;
    q('scenario-controls').hidden = q('scenario-result').hidden = !enabled;
    q('scenario-duration-note').hidden = !enabled;
    q('scenario-temperature-row').hidden = false;
    updateTemperatureLabel();
    if(typeof requestAnimationFrame==='function')requestAnimationFrame(updateTemperatureLabel);
    q('use').hidden = enabled;
    q('fc-heading').textContent = 'FC';
    if (!enabled) {
      const item=single.payload.call(single);
      renderConditions([item],item.range);
      q('scenario-error').textContent=(temperatureEdited||item.conditions.state==='Immerso')&&!Number.isFinite(temperatureValue())?'Specificare la temperatura.':'';
      q('use').disabled=!!q('error').textContent||!!q('scenario-error').textContent;
      return;
    }
    // Keep button nodes stable during input/blur updates: replacing a focused
    // tab between pointerdown and click would discard the user's navigation.
    const tabs=q('scenario-tabs');
    if(tabs.children.length!==items.length)tabs.replaceChildren(...items.map((item,i)=>{
      const button=document.createElement('button');button.type='button';
      button.textContent=String(i+1);button.dataset.scenario=String(i);
      button.addEventListener('click',()=>{active=i;load(active,items[active].weight);render();tabs.children[i].focus();});
      return button;
    }));
    items.forEach((item,i)=>{
      tabs.children[i].setAttribute('aria-label','Scenario '+(i+1)+(item.error?' · da completare':''));
      tabs.children[i].setAttribute('aria-pressed',String(i===active));
    });
    q('remove-scenario').hidden = items.length <= 2;
    const group = combined(), missing = items.flatMap((item,i)=>item.error?[i+1]:[]);
    q('scenario-output').textContent=group?(group.range[0]===group.range[1]?group.range[0].toFixed(2):group.range.map(v=>v.toFixed(2)).join(' – ')):'—';
    if(group)renderConditions(items,group.range);
    else q('scenario-summary').textContent='Scenari da completare.';
    q('scenario-error').textContent = missing.length ? 'Completare gli scenari: ' + missing.join(', ') + '.' : '';
    q('use').disabled = q('use-scenarios').disabled = !group;
  }
  function temperatureValue() {
    return single.temperatureValue();
  }
  function refresh() {
    if (paused) return;
    if (!enabled) { render(); return; }
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
    normalizeAll(single.payload.call(single).weight);
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
      if (!enabled) return {...single.payload.call(single), draft:this.snapshot(),
        ...(temperatureEdited?{temperature:temperatureValue()}: {})};
      const group = combined();
      return {draft:this.snapshot(), range:group?.range || [null,null], weight:single.payload.call(single).weight,
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
  function temperatureChange() {temperatureEdited=true;single.temperatureChanged();refresh();}
  q('scenario-temperature').addEventListener('input',temperatureChange);
  q('scenario-temperature').addEventListener('blur',()=>{
    const value=temperatureValue();if(Number.isFinite(value))q('scenario-temperature').value=value.toFixed(Number.isInteger(value*10)?1:2);
    refresh();
  });
  document.getElementById('fc-full').querySelectorAll('[data-temperature]').forEach(button=>button.addEventListener('click',()=>{
    const value=temperatureValue();if(!Number.isFinite(value))return;
    q('scenario-temperature').value=(value+Number(button.dataset.temperature)).toFixed(1);temperatureChange();
  }));
  let previousWidth=-1;
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(entries=>{
    const width=entries[0].contentRect.width;
    if(Math.abs(width-previousWidth)<.5)return;
    previousWidth=width;requestAnimationFrame(updateTemperatureLabel);
  }).observe(q('environment-row'));
  render();
})();
