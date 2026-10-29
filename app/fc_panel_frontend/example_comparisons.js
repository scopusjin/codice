// Documentary comparisons only. This module never reads or changes FC results.
(() => {
  function compare(example, c) {
    const review=example.contextualReview, p=review?.criteria;
    if(!['comparison','retained'].includes(review?.status)||!p)return null;
    const differences=[];
    let distanceAxes=0;
    const simulator=example.type==='Simulatore';
    if(p.state==='nonimmersed'){
      if(c.state==='Immerso')return null;
      if(c.state==='Bagnato'){distanceAxes++;differences.push('corpo bagnato selezionato; la prova non documenta il bagnato del corpo umano');}
    }else if(c.state!==p.state)return null;
    if(p.water){
      if(c.water!==p.water)return null;
      if((p.waterSeries==='cold')!==!!c.waterNearZero)return null;
    }
    const selectedAir=c.air||(c.wind?'continuous':'still');
    if(p.air&&p.air!=='unspecified'&&selectedAir!==p.air){
      // Intermittent/unknown air may be compared with documented fixed exposures,
      // but a known constant condition is not silently treated as another one.
      if(!['intermittent','unknown'].includes(selectedAir)&&p.air!=='intermittent')return null;
      distanceAxes++;differences.push('ventilazione diversa da quella documentata nella scheda');
    }else if(p.air==='unspecified')differences.push('ventilazione non precisata nella scheda');
    if(p.surfaces&&!p.surfaces.includes(c.surf)){
      // Neutral versus conductive is an adjacent support comparison, with an
      // explicit limitation. Insulating and metal supports stay separate.
      if(!p.surfaces.some(s=>[0,1,4,5].includes(s))||![0,1,4,5].includes(c.surf))return null;
      distanceAxes++;differences.push('superficie di appoggio differente');
    }else if(p.surfaces?.includes(4)&&c.surf===5){
      differences.push('prova su cemento o pietra, non sulle piastrelle selezionate');
    }
    if(p.maxWeight&&(!Number.isFinite(c.weight)||c.weight>p.maxWeight))return null;
    const garments=Number.isFinite(c.garmentThin)&&Number.isFinite(c.garmentThick)
      ? c.garmentThin+c.garmentThick : c.s+c.p;
    const covers=c.m+c.h+(c.lightCover||0);
    if((p.garments&&!Number.isFinite(garments))||(p.covers&&!Number.isFinite(covers)))return null;
    const distance=(value,[lo,hi])=>Math.max(lo-value,value-hi,0);
    if(p.covers&&distance(covers,p.covers)){
      if(!simulator&&(p.covers[1]===0||covers===0||distance(covers,p.covers)>1))return null;
      distanceAxes++;differences.push('coperture differenti');
    }
    if(p.garments&&distance(garments,p.garments)){
      if(!simulator&&distance(garments,p.garments)>1)return null;
      distanceAxes++;differences.push('indumenti differenti');
    }
    if(p.leafCover){
      if(!['yes','no'].includes(c.leafCover)||p.leafCover!==c.leafCover)return null;
      if(!['wet','humid','dry'].includes(c.leaf))return null;
      if(p.leaf&&c.leaf!==p.leaf){distanceAxes++;differences.push('stato delle foglie differente');}
    }
    if(p.soaked&&c.wetClothes==='partial')differences.push('nella prova i tessuti sono completamente bagnati');
    if(c.bodyBag||c.thermalFoil)differences.push('sacco mortuario o mantellina non presenti nella prova');
    if(distanceAxes>1)return null;
    // Profiles are deliberately comparisons, never new automatic FC rules.
    const note=['Situazione simile o contigua: '+p.note,...differences.map(t=>t+'.')];
    const trial=example.archive?.temperature;
    if(trial)note.push('Temperatura della prova: '+String(trial).replace(',','.')+' °C.');
    return {...example,comparisonNote:note.join(' '),comparisonDifferences:differences,comparisonDistance:distanceAxes};
  }
  window.FCExampleComparisons={compare,select:(examples,c)=>examples.map(e=>compare(e,c)).filter(Boolean).sort((a,b)=>a.comparisonDistance-b.comparisonDistance)};
})();
