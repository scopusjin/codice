// One description for the editor, the chosen FC and the final case summary.
(() => {
  function clothing(c) {
    const total = c.s + c.p;
    if (!total) return 'nudo';
    if (total === 1) return 'con uno strato di tessuto ' + (c.p ? 'pesante' : 'leggero');
    const quantity = total === 2 ? 'pochi' : total <= 4 ? 'alcuni' : 'molti';
    const kind = c.s && c.p ? 'di diverso spessore' : c.p ? 'pesanti' : 'leggeri';
    return 'con ' + quantity + ' strati di tessuti ' + kind;
  }
  function blankets(c) {
    const total = c.m + c.h;
    if (!total) return '';
    if (total === 1) return c.h ? 'sotto un piumone o una coperta molto pesante' : 'sotto una coperta spessa';
    const quantity = total === 2 ? 'poche' : total <= 4 ? 'alcune' : 'molte';
    const kind = c.m && c.h ? 'coperte di diverso spessore' : c.h ? 'coperte molto pesanti o piumoni' : 'coperte spesse';
    return 'sotto ' + quantity + ' ' + kind;
  }
  function conditions(c, fields) {
    if (c.state === 'Immerso') return 'corpo immerso in acqua ' + (c.water === 'corrente' ? 'corrente' : 'ferma');
    const parts = ['corpo ' + c.state.toLowerCase(), clothing(c), blankets(c)];
    const many = c.p >= 3 || (c.p >= 1 && c.s >= 3) || (!c.p && c.s >= 5);
    if (c.state === 'Asciutto') {
      if (!c.m && !c.h && many && c.isolation === 'one') parts.push('un capo particolarmente isolante');
      if (!c.m && !c.h && many && c.isolation === 'several') parts.push('più capi particolarmente isolanti');
      if (c.h && c.feather === 'yes') parts.push('piumone di piume voluminoso e avvolgente');
      if (c.m + c.h > 1 && (!c.h || c.feather === 'no') && c.volume === 'yes') parts.push('coperture molto voluminose');
    }
    const surfaces = {0:fields.surface === 'wood' ? 'piano di legno' : 'pavimento',
      1:'asfalto / terreno / prato', 2:'materasso / tappeto spesso', 3:'supporto molto imbottito e avvolgente',
      4:'cemento / pietra', 5:'pavimento molto freddo', 6:'piano metallico sottile o leggero',
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
