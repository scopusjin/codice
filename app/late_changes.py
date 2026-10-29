"""Descriptive late postmortem findings; no automatic chronological thresholds."""
from html import escape

CHANGES = {
    'colour': ('Alterazioni cromatiche', 'Discolouration'),
    'marbling': ('Evidenza della rete venosa superficiale', 'Marbling'),
    'gas': ('Enfisema putrefattivo', 'Putrefactive gas formation'),
    'skin': ('Epidermolisi', 'Skin slippage'),
    'liquefaction': ('Colliquazione', 'Liquefaction'),
    'mummification': ('Mummificazione', 'Mummification'),
    'adipocere': ('Adipocera', 'Adipocere'),
    'skeletonisation': ('Scheletrizzazione', 'Skeletonisation'),
}
INSECTS = {
    'eggs': ('Uova', 'Eggs'), 'larvae': ('Larve', 'Larvae'),
    'full_puparia': ('Pupari pieni', 'Full puparia'),
    'empty_puparia': ('Pupari vuoti', 'Empty puparia'),
}
CONCLUSIONS = {
    'unspecified': ('Epoca non ulteriormente precisabile', 'Time of death cannot be further specified'),
    'days': ('Almeno diversi giorni prima del rinvenimento', 'At least several days before discovery'),
    'weeks': ('Alcune settimane prima del rinvenimento', 'Several weeks before discovery'),
    'months': ('Alcuni mesi prima del rinvenimento', 'Several months before discovery'),
    'custom': ('Altra formulazione', 'Other wording'),
}
ENABLED = 'late_changes_enabled'
CHANGE_KEY = 'late_changes_observed'
INSECT_KEY = 'late_insects_observed'
CONCLUSION_KEY = 'late_conclusion'
CUSTOM_KEY = 'late_conclusion_custom'
KEYS = (ENABLED, CHANGE_KEY, INSECT_KEY, CONCLUSION_KEY, CUSTOM_KEY)


def _join(items, en=False):
    return (', '.join(items[:-1]) + (' and ' if en else ' e ') + items[-1]) if len(items) > 1 else ''.join(items)


def build_late_report(state, language='it'):
    """Use only explicit observations and the physician's selected conclusion."""
    if not state.get(ENABLED):
        return None
    en = language == 'en'
    index = int(en)
    changes = [k for k in CHANGES if k in state.get(CHANGE_KEY, [])]
    insects = [k for k in INSECTS if k in state.get(INSECT_KEY, [])]
    if not changes and not insects:
        return None
    unavailable = []
    if state.get('henssge_non_applicabile'):
        unavailable.append('body cooling' if en else 'il raffreddamento cadaverico')
    if state.get('selettore_macchie_id') == 'livor_unreliable':
        unavailable.append('postmortem lividity' if en else 'le caratteristiche delle macchie ipostatiche')
    if state.get('selettore_rigidita_id') == 'rigor_unreliable':
        unavailable.append('rigor mortis' if en else 'la rigidità cadaverica')
    if state.get('mostra_parametri_aggiuntivi'):
        from app.special_tanatology_states import SPECIAL_PARAM_LABEL_IT, SPECIAL_OPTION_LABEL_IT, OPTION_UNRELIABLE
        from app.i18n import special_parameter_label
        for param, label in SPECIAL_PARAM_LABEL_IT.items():
            selected = state.get(label + '_selector')
            unreliable = SPECIAL_OPTION_LABEL_IT[param].get(OPTION_UNRELIABLE)
            if unreliable is not None and selected == unreliable:
                unavailable.append(special_parameter_label(param, language).lower())
    paragraphs = []
    if unavailable:
        names = _join(unavailable, en)
        paragraphs.append((f'In this case, {names} cannot be used to estimate the time since death. '
                           'Subsequent postmortem changes may mask or profoundly alter these findings, preventing a chronological interpretation.') if en else
                          (f'Nel caso in esame, ai fini della stima dell’epoca del decesso non risultano utilizzabili {names}. '
                           'I successivi processi trasformativi possono mascherare o modificare profondamente tali fenomeni, che non conservano quindi caratteristiche utili per una valutazione cronologica.'))
    paragraphs.append('The following findings allow some considerations.' if en else
                      'Gli elementi su cui possono essere avanzate alcune considerazioni sono i seguenti.')
    items = []
    if changes:
        observations = _join([CHANGES[k][index].lower() for k in changes], en)
        putrefactive = any(k in changes for k in ('colour', 'marbling', 'gas', 'skin', 'liquefaction'))
        if en:
            text = f'Late postmortem changes, with {observations}. '
            if putrefactive:
                text += ('The onset and progression of putrefaction depend on numerous external factors (including ambient temperature and weather exposure) '
                         'and internal factors (including body temperature, premortem infections and wounds). ')
            else:
                text += 'Their development depends on environmental conditions and the characteristics of the body. '
            text += 'Their marked variability prevents a precise estimate of the time since death from these findings alone.'
        else:
            text = f'I processi post-mortali tardivi/trasformativi, con {observations}. '
            if putrefactive:
                text += ('La loro insorgenza e progressione sono influenzate da numerosi fattori esogeni (ad esempio temperatura ambientale ed esposizione ai fenomeni meteorologici) '
                         'ed endogeni (temperatura corporea, infezioni prima del decesso, presenza di ferite). ')
            else:
                text += 'Il loro sviluppo è influenzato dalle condizioni ambientali e dalle caratteristiche del cadavere. '
            text += 'L’ampia variabilità di tali processi non permette, sulla base di questi soli reperti, di formulare precisazioni sull’epoca della morte.'
        items.append(text)
    if insects:
        observations = _join([INSECTS[k][index].lower() for k in insects], en)
        if en:
            text = f'Insect colonisation of the body, with {observations}. '
            text += ('The development of colonising insects depends on species, environmental conditions and the exposure and accessibility of the body. ')
            if 'empty_puparia' in insects:
                text += ('Empty puparia attributable to this body indicate that at least some colonising insects completed their immature development and emerged as adults. ')
            text += ('Without making a specific entomological estimate, these findings are considered together with the other available evidence in the overall assessment of the time since death.')
        else:
            text = f'La colonizzazione del cadavere da parte dell’entomofauna, con presenza di {observations}. '
            text += ('Lo sviluppo degli insetti colonizzatori dipende dalla specie, dalle condizioni ambientali e dalle modalità di esposizione e accessibilità del cadavere. ')
            if 'empty_puparia' in insects:
                text += ('I pupari vuoti riferibili al cadavere in esame indicano che almeno una parte degli insetti colonizzatori ha completato il proprio sviluppo fino alla fuoriuscita dell’adulto. ')
            text += ('Pur senza avanzare specifiche valutazioni entomologiche, questi reperti vengono considerati congiuntamente agli altri elementi disponibili nella valutazione complessiva dell’epoca del decesso.')
        items.append(text)
    choice = state.get(CONCLUSION_KEY, 'unspecified')
    if choice == 'custom':
        conclusion = str(state.get(CUSTOM_KEY, '')).strip()
        if not conclusion:
            conclusion = CONCLUSIONS['unspecified'][index] + '.'
    elif choice in ('days', 'weeks', 'months'):
        timing = CONCLUSIONS[choice][index].lower()
        conclusion = ('In this case, the overall assessment of the findings supports the physician’s judgement that death occurred ' + timing + '.') if en else (
            'Nel caso in esame, la valutazione complessiva dei reperti permette di ritenere che il decesso si sia verificato ' + timing + '.')
    else:
        conclusion = ('The findings do not allow the time of death to be further specified.') if en else (
            'Sulla base dei reperti considerati, l’epoca del decesso non risulta ulteriormente precisabile.')
    html = ''.join('<p>' + escape(p) + '</p>' for p in paragraphs)
    html += '<ul>' + ''.join('<li>' + escape(p) + '</li>' for p in items) + '</ul>'
    html += '<p>' + escape(conclusion) + '</p>'
    return {'html': html, 'brief': conclusion, 'choice': choice}


def render_late_inputs():
    import streamlit as st
    from app.language import current_language
    en = current_language() == 'en'
    index = int(en)
    st.toggle('Add late postmortem changes / insect evidence' if en else 'Aggiungi fenomeni trasformativi / entomofauna', key=ENABLED)
    if not st.session_state.get(ENABLED):
        return
    with st.container(border=True, key='late_changes_card'):
        st.multiselect('Observed postmortem changes' if en else 'Modificazioni post-mortali osservate',
                       options=list(CHANGES), format_func=lambda k: CHANGES[k][index], key=CHANGE_KEY)
        st.multiselect('Observed insect evidence' if en else 'Reperti entomologici osservati',
                       options=list(INSECTS), format_func=lambda k: INSECTS[k][index], key=INSECT_KEY)
        st.selectbox('Overall assessment chosen by the physician' if en else 'Conclusione complessiva scelta dal medico',
                     options=list(CONCLUSIONS), format_func=lambda k: CONCLUSIONS[k][index], key=CONCLUSION_KEY)
        if st.session_state.get(CONCLUSION_KEY) == 'custom':
            st.text_area('Conclusion text' if en else 'Testo della conclusione', key=CUSTOM_KEY, max_chars=4000)
        st.caption('The selected findings do not generate an automatic time interval.' if en else
                   'I reperti selezionati non generano automaticamente un intervallo temporale.')


def late_hours_conflict(report, upper_bounds, language='it'):
    """Flag a clearly short upper limit, without turning the late choice into a range.

    Less than 24 hours is incompatible with a conclusion expressed in several
    days/weeks/months. Open limits and unparsed free text are not classified.
    """
    from math import isfinite
    from numbers import Real
    if not report or report.get('choice') not in {'days', 'weeks', 'months'}:
        return ''
    labels = list(dict.fromkeys(label for label, upper in upper_bounds
                               if isinstance(upper, Real) and isfinite(upper) and 0 <= upper < 24))
    if not labels:
        return ''
    if language == 'en':
        return ('Potential inconsistency: the physician selected a conclusion expressed in days, weeks or months, '
                'but the following parameters have an upper limit of less than 24 hours before the main examination: '
                + _join(labels, True) + '. Review the applicability of these parameters and the selected conclusion. '
                'The descriptive conclusion has not been included in the numerical combination.')
    return ('Possibile incoerenza: la conclusione scelta dal medico è espressa in giorni, settimane o mesi, '
            'mentre i seguenti parametri indicano un limite superiore inferiore a 24 ore prima dei rilievi principali: '
            + _join(labels) + '. Verificare l’utilizzabilità di questi parametri e la conclusione selezionata. '
            'La conclusione descrittiva non è stata inclusa nel calcolo della stima combinata.')
