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
  function coverings(c){
    const thin=c.teli||0,thick=c.lightCover||0;
    const medium=c.m-Number(!!c.thermalFoil),heavy=c.h;
    if(!Number.isFinite(medium+heavy))return 'coperture da precisare';
    const sheets=thin+thick,blankets=medium+heavy;
    if(sheets&&blankets)return 'coperto con teli e coperte di diverso spessore';
    if(sheets){
      if(thin&&thick)return 'coperto con più teli di diverso spessore';
      return 'coperto con '+(thin?counted(thin,'un telo sottile','teli sottili'):counted(thick,'un telo spesso','teli spessi'));
    }
    if(blankets){
      if(medium&&heavy)return 'sotto più coperte di diverso spessore';
      return 'sotto '+(medium?counted(medium,'una coperta spessa','coperte spesse'):counted(heavy,'una coperta molto pesante','coperte molto pesanti'));
    }
    return '';
  }
  function specialCoverings(c){
    const items=[];
    if(c.thermalFoil)items.push('una mantellina termica');
    if(c.bodyBag)items.push('un sacco mortuario');
    return items.length?'avvolto in '+items.join(' e in '):'';
  }
  function conditions(c, fields) {
    if (c.state === 'Immerso') return 'corpo immerso in acqua ' + (c.water === 'corrente' ? 'corrente' : 'ferma');
    const parts = ['corpo ' + c.state.toLowerCase(), clothing(c), coverings(c), specialCoverings(c)];
    const many = c.p >= 3 || (c.p >= 1 && c.s >= 3) || (!c.p && c.s >= 5);
    if (c.state === 'Asciutto') {
      if (!c.m && !c.h && many && c.isolation === 'one') parts.push('un capo particolarmente isolante');
      if (!c.m && !c.h && many && c.isolation === 'several') parts.push('più capi particolarmente isolanti');
      if (c.h && c.feather === 'yes') parts.push('piumone di piume voluminoso e avvolgente');
      if (c.m + c.h > 1 && (!c.h || c.feather === 'no') && c.volume === 'yes') parts.push('coperture molto voluminose');
    }
    const surfaces = {0:fields.surface === 'wood' ? 'piano di legno' : 'pavimento',
      1:'asfalto / terreno / prato', 2:'materasso / tappeto spesso', 3:'supporto molto imbottito e avvolgente',
      4:'cemento / pietra', 5:'piastrelle molto fredde', 6:'piano metallico sottile o leggero',
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
