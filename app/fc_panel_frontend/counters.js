// Desktop detail is presentation data; thin/thick remain the engine totals.
window.FCCounters = ({root,q,num,step,recalc}) => {
  let detailed=false;
  const pairs=[['thin','garment-thin','teli'],['thick','garment-thick','light-cover']];
  const specs=[['garment-thin','Indumenti leggeri'],['teli','Teli ⓘ'],
    ['garment-thick','Indumenti pesanti'],['light-cover','Copriletti / coperte leggere']];
  for(const [id,label] of specs){
    step(id,label,0,1,'#desktop-counts');
    q('#'+id).setAttribute('inputmode','numeric');
    q('#'+id).addEventListener('input',()=>{changed(id);recalc();});
  }
  q('#teli-control').setAttribute('title','Lenzuola, asciugamani sottili');
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
    q('label[for="heavy"]').textContent=value?'Piumoni ⓘ':'Molto pesanti / piumoni';
    q('#heavy-control').setAttribute('title','Piumoni o coperte molto pesanti');
  }
  setDesktop(false);
  return {changed,restore,details,setDesktop,known:()=>detailed};
};
