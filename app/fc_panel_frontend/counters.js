// Desktop detail is presentation data; thin/thick remain the engine totals.
window.FCCounters = ({root,q,num,step,recalc}) => {
  let detailed=false;
  const pairs=[['thin','garment-thin','teli'],['thick','garment-thick','light-cover']];
  const specs=[['garment-thin','Indumenti leggeri'],['teli','Teli'],
    ['garment-thick','Indumenti pesanti'],['light-cover','Copriletti / coperte leggere']];
  for(const [id,label] of specs){
    step(id,label,0,1,'#desktop-counts');
    q('#'+id).setAttribute('inputmode','numeric');
    q('#'+id).addEventListener('input',()=>{changed(id);recalc();});
  }
  const helpItems=[
    ['scenario','#scenario-help-anchor','Quando usare più scenari','Da usare se il corpo si è trovato, o potrebbe ragionevolmente essersi trovato, in condizioni diverse. L’app considera le condizioni più favorevoli e più sfavorevoli al raffreddamento e fornisce un intervallo di stima che comprende entrambe. Variazioni di breve durata delle condizioni del corpo possono ragionevolmente essere trascurate.'],
    ['teli','#teli-control','Esempi di teli','Lenzuola, asciugamani sottili.'],
    ['heavy','#heavy-control','Esempi di piumoni e coperte molto pesanti','Piumoni o coperte molto pesanti, spesse o imbottite.'],
    ['air','#air-row','Quando considerare le correnti d’aria','Considerare le correnti d’aria se interessano effettivamente il corpo per un periodo rilevante. Una finestra aperta o una corrente occasionale nell’ambiente non bastano.'],
    ['temperature','#temperature-help-anchor','Temperatura ambientale media','Indicare la temperatura ambientale media dello scenario considerato, riferita al periodo in cui il corpo si è trovato, o si ipotizza possa essersi trovato, nelle condizioni descritte.']
  ];
  for(const [id,parent,label,text] of helpItems){
    const button=document.createElement('button');
    button.id=id+'-help-button';button.type='button';button.className='counter-help';
    button.setAttribute('aria-label',label);
    button.setAttribute('aria-expanded','false');button.setAttribute('aria-controls',id+'-help');
    button.setAttribute('popovertarget',id+'-help');
    const symbol=document.createElement('span');symbol.textContent='?';symbol.setAttribute('aria-hidden','true');
    button.append(symbol);
    const hint=document.createElement('div');
    hint.id=id+'-help';hint.className='fc-help-popover';hint.textContent=text;
    hint.setAttribute('popover','auto');hint.setAttribute('role','note');
    // Native popover buttons toggle on repeated taps and retain outside-click/Escape dismissal.
    hint.addEventListener('toggle',event=>{
      const isOpen=event.newState==='open';
      button.setAttribute('aria-expanded',String(isOpen));
      if(!isOpen)return;
      const anchor=button.getBoundingClientRect(),box=hint.getBoundingClientRect();
      hint.style.left=Math.max(8,Math.min(anchor.left,window.innerWidth-box.width-8))+'px';
      hint.style.top=Math.max(8,Math.min(anchor.bottom+4,window.innerHeight-box.height-8))+'px';
    });
    q(parent).append(button);root.append(hint);
  }
  function changed(id){
    if(specs.some(([key])=>key===id)){
      detailed=true;
      for(const [total,garment,cover] of pairs)q('#'+total).value=String(num(q('#'+garment))+num(q('#'+cover)));
    }else if(id==='thin'||id==='thick'){
      // A mobile edit no longer specifies the original garment/cover split.
      detailed=false;
      for(const [total,garment,cover] of pairs){q('#'+cover).value='0';q('#'+garment).value=q('#'+total).value;}
    }
  }
  function restore(draft){
    detailed=draft?.clothingDetailed===true;
    for(const [total,garment,cover] of pairs){
      q('#'+cover).value=detailed?(draft?.fields?.[cover]??'0'):'0';
      q('#'+garment).value=String(num(q('#'+total))-num(q('#'+cover)));
    }
  }
  function details(){
    return detailed?{garmentThin:num(q('#garment-thin')),garmentThick:num(q('#garment-thick')),
      teli:num(q('#teli')),lightCover:num(q('#light-cover'))}:{};
  }
  function setDesktop(value){
    root.dataset.desktop=String(!!value);
    q('label[for="medium"]').textContent=value?'Coperte spesse':'Spesse';
    q('label[for="heavy"]').textContent=value?'Piumoni':'Molto pesanti / piumoni';
  }
  setDesktop(false);
  return {changed,restore,details,setDesktop,known:()=>detailed};
};
