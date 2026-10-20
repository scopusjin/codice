// One description for the editor, the chosen FC and the final case summary.
(() => {
  function clothing(c) {
    const detailed=Number.isFinite(c.garmentThin)&&Number.isFinite(c.garmentThick);
    const light=detailed?c.garmentThin:c.s,heavy=detailed?c.garmentThick:c.p-Number(!!c.bodyBag);
    const total=light+heavy;
    if(!Number.isFinite(total))return 'vestizione da precisare';
    if(!total)return 'nudo';
    const noun=detailed?'indumenti':'indumenti o teli';
    const kind=light&&heavy?'di diverso spessore':heavy?'pesanti':'leggeri';
    if(total===1)return detailed?'con uno strato di '+noun+' '+kind:'con un indumento o telo '+(heavy?'pesante':'leggero');
    if(total===2)return 'con pochi '+noun+' '+kind;
    return 'con '+(total<=4?'vari':'molti')+' strati di '+noun+' '+kind;
  }
  function counted(n,one,many){return n===1?one:n===2?'due '+many:'più '+many;}
  function ordinaryCoverings(c){
    const thin=c.teli||0,thick=c.lightCover||0;
    const medium=c.m-Number(!!c.thermalFoil),heavy=c.h;
    if(!Number.isFinite(medium+heavy))return 'coperture da precisare';
    const sheets=thin+thick,blankets=medium+heavy;
    if(c.state==='Asciutto'&&heavy&&c.feather==='yes'){
      return sheets+blankets>1
        ? 'coperto con coperte di diverso spessore, tra cui un piumone molto voluminoso e avvolgente'
        : 'coperto con un piumone molto voluminoso e avvolgente';
    }
    if(sheets&&blankets)return 'coperto con teli e coperte di diverso spessore';
    if(sheets){
      if(thin&&thick)return 'coperto con più teli di diverso spessore';
      return 'coperto con '+(thin?counted(thin,'un telo sottile','teli sottili'):counted(thick,'un telo spesso','teli spessi'));
    }
    if(blankets){
      const wet=c.state==='Bagnato'?({
        full:blankets===1?' impregnata d’acqua':' impregnate d’acqua',
        partial:blankets===1?' umida o parzialmente bagnata':' umide o parzialmente bagnate',
        unknown:' (condizioni di umidità non determinabili)'
      }[c.wetCovers]||''):'';
      if(medium&&heavy)return 'sotto più coperte di diverso spessore'+wet;
      return 'sotto '+(medium?counted(medium,'una coperta spessa','coperte spesse'):counted(heavy,'una coperta molto pesante','coperte molto pesanti'))+wet;
    }
    return '';
  }
  function coverings(c){
    const ordinary=ordinaryCoverings(c);
    if(!c.thermalFoil)return ordinary;
    if(!ordinary)return 'coperto con una mantellina termica';
    if(ordinary==='coperture da precisare')return 'coperto con una mantellina termica e altre coperture da precisare';
    const description=ordinary.replace(/^sotto /,'coperto con ');
    const detail=description.indexOf(', tra cui ');
    return detail<0 ? description+' e una mantellina termica'
      : description.slice(0,detail)+' e una mantellina termica'+description.slice(detail);
  }
  function specialCoverings(c){
    return c.bodyBag?'avvolto in un sacco mortuario':'';
  }
  function conditions(c, fields) {
    if (c.state === 'Immerso') return 'corpo immerso in acqua ' + (c.water === 'corrente' ? 'corrente' : 'ferma');
    const parts = ['corpo ' + c.state.toLowerCase(), clothing(c), coverings(c), specialCoverings(c)];
    if(c.state==='Bagnato'){
      const details=Number.isFinite(c.garmentThin)&&Number.isFinite(c.garmentThick);
      const hasClothes=details?c.garmentThin+c.garmentThick+(c.teli||0)>0:c.s+c.p-Number(!!c.bodyBag)>0;
      const hasCovers=c.m-Number(!!c.thermalFoil)+c.h+(c.lightCover||0)>0;
      const garmentText={full:'indumenti e teli completamente impregnati d’acqua',partial:'indumenti e teli umidi o parzialmente bagnati',unknown:'condizioni di umidità di indumenti e teli non determinabili'};
      const coverText={full:'coperte completamente impregnate d’acqua',partial:'coperte umide o parzialmente bagnate',unknown:'condizioni di umidità delle coperte non determinabili'};
      if(hasClothes)parts.push(garmentText[c.wetClothes]||'');
      const coverConditionIncluded=c.m-Number(!!c.thermalFoil)+c.h>0&&!(c.teli||c.lightCover);
      if(hasCovers&&!coverConditionIncluded)parts.push(coverText[c.wetCovers]||'');
    }
    const many = c.p >= 3 || (c.p >= 1 && c.s >= 3) || (!c.p && c.s >= 5);
    if (c.state === 'Asciutto') {
      if (!c.m && !c.h && many && c.isolation === 'one') parts.push('un capo particolarmente isolante');
      if (!c.m && !c.h && many && c.isolation === 'several') parts.push('più capi particolarmente isolanti');
      if (c.m + c.h > 1 && (!c.h || c.feather === 'no') && c.volume === 'yes') parts.push('coperture molto voluminose');
    }
    const surfaces = {0:fields.surface === 'wood' ? 'piano di legno' : 'pavimento',
      1:'superficie termicamente indifferente', 2:'superficie termicamente isolante', 3:'superficie termicamente isolante',
      4:'superficie termicamente conduttiva', 5:'superficie termicamente conduttiva', 6:'piano metallico sottile',
      7:'piano metallico molto spesso', 8:'foglie ' + ({dry:'secche',humid:'umide',wet:'bagnate'}[c.leaf] || ''),
      10:'pavimento in PVC'};
    if (surfaces[c.surf]) parts.push('adagiato su ' + surfaces[c.surf]);
    if (c.surf === 8 && c.leafCover === 'yes') parts.push('con copertura di foglie');
    if (c.state === 'Bagnato' && [2,3].includes(c.surf) && c.supportSoaked === 'yes') parts.push('appoggio impregnato di liquidi');
    if (c.state === 'Bagnato' && c.surf === 1 && c.air === 'continuous' && c.wetCase && c.s+c.p === 2 && !c.m && !c.h) parts.push('pantaloni e slip fradici, pioggia');
    parts.push(({continuous:'con correnti d’aria continue',intermittent:'con correnti d’aria intermittenti'})[c.air] || '');
    return parts.filter(Boolean).join(', ');
  }
  window.FCDescriptions = {conditions};
})();
