"""Descriptive late postmortem findings; no automatic chronological thresholds."""
from html import escape

CHANGES = {
    'colour': ('Alterazioni cromatiche', 'Discolouration'),
    'marbling': ('Evidenza della rete venosa superficiale', 'Marbling'),
    'gas': ('Enfisema putrefattivo', 'Putrefactive gas formation'),
    'skin': ('Epidermolisi', 'Skin slippage'),
    'liquefaction': ('Colliquazione', 'Liquefaction'),
    'liquefaction_partial': ('Aree di parziale colliquazione', 'Areas of partial liquefaction'),
    'liquefaction_diffuse': ('Diffusa colliquazione di porzioni corporee', 'Extensive liquefaction of body regions'),
    'mummification': ('Mummificazione', 'Mummification'),
    'mummification_partial': ('Aree di parziale mummificazione', 'Areas of partial mummification'),
    'mummification_diffuse': ('Diffusa mummificazione di porzioni corporee', 'Extensive mummification of body regions'),
    'adipocere': ('Aree caratterizzate da presenza di adipocera', 'Areas showing adipocere'),
    'skeletonisation': ('Scheletrizzazione', 'Skeletonisation'),
    'skeletonisation_partial': ('Aree di parziale scheletrizzazione', 'Areas of partial skeletonisation'),
    'skeletonisation_diffuse': ('Diffusa scheletrizzazione di porzioni corporee', 'Extensive skeletonisation of body regions'),
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
    choice = state.get(CONCLUSION_KEY, 'unspecified')
    compatibility = []
    paragraphs = []
    if unavailable:
        names = _join(unavailable, en)
        paragraphs.append((f'In this case, some of the consecutive postmortem changes normally considered when estimating the time since death ({names}) cannot be used, '
                           'because the body was already in an advanced stage of postmortem change. These findings had completed their evolution or had been masked '
                           'or profoundly altered by subsequent processes and no longer retained features useful for a chronological assessment.') if en else
                          (f'Nel caso in esame, ai fini della stima dell’epoca del decesso non risultano utilizzabili alcuni dei fenomeni post-mortali consecutivi normalmente presi in considerazione (quali {names}), '
                           'in quanto il cadavere si trovava ormai in una fase avanzata delle modificazioni post-mortali, nella quale tali fenomeni hanno esaurito la loro evoluzione, '
                           'sono stati mascherati o profondamente modificati dai successivi processi trasformativi e non conservano quindi caratteristiche utili per una valutazione cronologica.'))
    from app.tanatology_data import LIVOR_RANGES_BY_ID, RIGOR_RANGES_BY_ID
    has_early = bool(LIVOR_RANGES_BY_ID.get(state.get('selettore_macchie_id')) or
                     RIGOR_RANGES_BY_ID.get(state.get('selettore_rigidita_id')) or
                     (state.get('rt_val') and not state.get('henssge_non_applicabile')))
    if state.get('mostra_parametri_aggiuntivi'):
        from app.special_tanatology_states import SPECIAL_PARAM_LABEL_IT, SPECIAL_OPTION_LABEL_IT, OPTION_NOT_ASSESSED, OPTION_UNRELIABLE
        has_early = has_early or any(state.get(label + '_selector') not in
            (None, SPECIAL_OPTION_LABEL_IT[param].get(OPTION_NOT_ASSESSED), SPECIAL_OPTION_LABEL_IT[param].get(OPTION_UNRELIABLE))
            for param, label in SPECIAL_PARAM_LABEL_IT.items())
    paragraphs.append('The following findings allow some considerations.' if en else
                      ('Gli elementi su cui possono esser avanzate alcune considerazioni sono i seguenti.' if has_early else
                       'Gli unici elementi su cui possono esser avanzate alcune considerazioni sono i seguenti.'))
    items = []
    if changes:
        observations = _join([CHANGES[k][index].lower() for k in changes], en)
        putrefactive = any(k in changes for k in ('colour', 'marbling', 'gas', 'skin', 'liquefaction', 'liquefaction_partial', 'liquefaction_diffuse'))
        if en:
            text = ('Late postmortem changes, particularly putrefaction. ' if putrefactive else 'Late postmortem changes. ')
            text += f'The following changes were observed: {observations}. '
            if putrefactive:
                text += ('The onset and progression of putrefaction depend on numerous external factors (including ambient temperature and weather exposure) '
                         'and internal factors (including body temperature, premortem infections and wounds). ')
            else:
                text += 'Their development depends on environmental conditions and the characteristics of the body. '
            text += ('Their onset may vary greatly, from hours to several weeks after death; their assessment does not permit a precise time of death.' if putrefactive else
                     'Their marked variability prevents a precise estimate of the time since death.')
            if choice in ('days', 'weeks', 'months'):
                text += ' In this case, their degree of development only supports a death occurring ' + CONCLUSIONS[choice][index].lower() + '.'
        else:
            text = ('I processi post-mortali tardivi/trasformativi, in particolare quelli putrefattivi. ' if putrefactive else
                    'I processi post-mortali tardivi/trasformativi. ')
            text += f'Nel caso in esame sono state rilevate le seguenti modificazioni: {observations}. '
            if putrefactive:
                text += ('La loro insorgenza è influenzata da numerosi fattori, esogeni (ad esempio temperatura ambientale, esposizione ai fenomeni meteorologici) '
                         'ed endogeni (temperatura corporea, infezioni prima del decesso, presenza di ferite). '
                         'Poiché tali processi possono manifestarsi in un intervallo temporale estremamente variabile, da poche ore a diverse settimane dopo il decesso, '
                         'la loro valutazione non permette di formulare precisazioni sull’epoca della morte.')
            else:
                text += ('La loro insorgenza e progressione sono influenzate dalle condizioni ambientali e dalle caratteristiche del cadavere. '
                         'La loro valutazione non permette di formulare precisazioni sull’epoca della morte.')
            if choice in ('days', 'weeks', 'months'):
                timing = {'days': 'quantomeno vari giorni', 'weeks': 'alcune settimane', 'months': 'alcuni mesi'}[choice]
                text += (' Nel caso in esame, il loro grado di sviluppo permette unicamente di ritenere che il decesso si sia verificato '
                         + timing + ' prima del rinvenimento.')
        items.append(text)
    if insects:
        observations = _join([INSECTS[k][index].lower() for k in insects], en)
        if en:
            stages = 'insects at different developmental stages (particularly ' + observations + ')' if len(insects) > 1 else observations
            text = f'Insect colonisation of the body, with {stages}. '
            text += 'Insect development is strongly influenced by environmental conditions, insect type and species, and the exposure of the body. '
            if 'empty_puparia' in insects:
                text += ('Without making a specific entomological estimate, empty puparia suggest that at least some colonising insects reached the advanced stages of development and emerged as adults. ')
                if choice in ('days', 'weeks', 'months'):
                    text += ('Despite the wide variation in developmental times with species and environmental conditions, this process requires an appreciable period, at least on the order of several days. ')
                    compatible = 'This finding is therefore also compatible with death occurring at least several days before discovery.'
                    compatibility.append(compatible)
                    text += compatible
            elif choice in ('days', 'weeks', 'months'):
                compatible = 'Without making a specific entomological estimate, these observations are compatible with death occurring ' + CONCLUSIONS[choice][index].lower() + '.'
                compatibility.append(compatible)
                text += compatible
        else:
            stages = 'insetti in differenti stadi di sviluppo (in particolare ' + observations + ')' if len(insects) > 1 else observations
            text = f'La colonizzazione del cadavere da parte dell’entomofauna, con presenza di {stages}. '
            text += ('Anche l’evoluzione dell’entomofauna è fortemente condizionata dalle condizioni ambientali, dalla tipologia e specie di insetto e dalle modalità di esposizione del cadavere. ')
            if 'empty_puparia' in insects:
                text += ('Pur senza avanzare specifiche valutazioni entomologiche, la presenza di pupari vuoti suggerisce che almeno una parte degli insetti colonizzatori '
                         'abbia raggiunto le fasi più avanzate del proprio ciclo di sviluppo, fino alla fuoriuscita dell’insetto adulto. ')
                if choice in ('days', 'weeks', 'months'):
                    text += ('Pur considerando l’ampia variabilità dei tempi di sviluppo in relazione alla specie coinvolta e alle condizioni ambientali, '
                             'tale processo richiede comunque un intervallo temporale non trascurabile, quantificabile almeno nell’ordine di diversi giorni. ')
                    compatible = 'Anche questo elemento risulta pertanto compatibile con un decesso avvenuto almeno diversi giorni prima del rinvenimento.'
                    compatibility.append(compatible)
                    text += compatible
            elif choice in ('days', 'weeks', 'months'):
                timing = CONCLUSIONS[choice][index].lower()
                compatible = ('Pur senza avanzare specifiche valutazioni entomologiche, quanto osservato non risulta in contrasto con le considerazioni sopra espresse '
                              'e appare compatibile con un decesso avvenuto ' + timing + '.') if changes else (
                              'Pur senza avanzare specifiche valutazioni entomologiche, quanto osservato appare compatibile con un decesso avvenuto ' + timing + '.')
                compatibility.append(compatible)
                text += compatible
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
    if not changes or choice not in ('days', 'weeks', 'months'):
        html += '<p>' + escape(conclusion) + '</p>'
    conflict_html = html
    for sentence in compatibility:
        conflict_html = conflict_html.replace(escape(sentence), '')
    footnotes = late_word_footnotes(changes, insects, en)
    return {'html': html, 'conflict_html': conflict_html, 'brief': conclusion, 'choice': choice, 'word_footnotes': footnotes}


def render_late_inputs():
    import streamlit as st
    from app.language import current_language
    en = current_language() == 'en'
    index = int(en)
    st.toggle('Add late postmortem changes / insect evidence' if en else 'Aggiungi fenomeni trasformativi / entomofauna', key=ENABLED)
    if not st.session_state.get(ENABLED):
        return
    with st.container(border=True, key='late_changes_card'):
        for title, options, state_key in (
            ('Observed postmortem changes' if en else 'Modificazioni post-mortali osservate', CHANGES, CHANGE_KEY),
            ('Observed insect evidence' if en else 'Reperti entomologici osservati', INSECTS, INSECT_KEY),
        ):
            selected = st.session_state.get(state_key, [])
            with st.popover(title, use_container_width=True):
                checked = []
                for option_id, labels in options.items():
                    # Preserve unqualified observations from older files without
                    # assigning them a new, unsupported extent.
                    legacy = state_key == CHANGE_KEY and option_id in {'liquefaction', 'mummification', 'skeletonisation'}
                    if legacy and option_id not in selected:
                        continue
                    label = labels[index] + ((' (previous selection)' if en else ' (selezione precedente)') if legacy else '')
                    if st.checkbox(label, value=option_id in selected,
                                   key=state_key + '__check_' + option_id):
                        checked.append(option_id)
            st.session_state[state_key] = checked
            if checked:
                st.caption('; '.join(options[k][index] for k in checked))
        st.selectbox('Overall assessment chosen by the physician' if en else 'Conclusione complessiva scelta dal medico',
                     options=list(CONCLUSIONS), format_func=lambda k: CONCLUSIONS[k][index], key=CONCLUSION_KEY)
        if st.session_state.get(CONCLUSION_KEY) == 'custom':
            st.text_area('Conclusion text' if en else 'Testo della conclusione', key=CUSTOM_KEY, max_chars=4000)


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
            + _join([label[:1].lower() + label[1:] for label in labels]) + '. Verificare l’utilizzabilità di questi parametri e la conclusione selezionata. '
            'La conclusione descrittiva non è stata inclusa nel calcolo della stima combinata.')


def late_word_footnotes(changes, insects, en=False):
    """Definitions supplied by the physician, exported only for native Word notes."""
    notes = []
    if any(k in changes for k in ('colour', 'marbling', 'gas', 'skin', 'liquefaction', 'liquefaction_partial', 'liquefaction_diffuse')):
        notes.append({
            'anchor': 'putrefaction' if en else 'putrefattivi',
            'text': ('Putrefaction is the postmortem degradation of tissues, mainly through bacterial activity. Its traditional phases may overlap: discolouration, sometimes with visible superficial veins (marbling); gas formation in tissues and body cavities; and liquefaction and progressive breakdown of soft tissues. Skin slippage, the separation of the epidermis from underlying layers, may also occur. Onset and progression vary widely with environmental conditions and the characteristics of the body.' if en else
                     'Per putrefazione si intende il complesso dei processi di degradazione post-mortale dei tessuti, principalmente legati all’azione della flora batterica. Classicamente se ne distinguono diverse fasi, che possono in parte sovrapporsi: una fase cromatica, caratterizzata dalla comparsa e progressiva diffusione di alterazioni cromatiche cutanee, nell’ambito della quale può rendersi evidente anche la rete venosa superficiale (cosiddetta fanerizzazione); una fase enfisematosa, dovuta alla produzione e all’accumulo di gas nei tessuti e nelle cavità corporee; e una fase colliquativa, caratterizzata dal progressivo disfacimento e dalla liquefazione dei tessuti molli. Nel corso di tali processi può inoltre verificarsi epidermolisi, ossia il distacco più o meno esteso dell’epidermide dagli strati cutanei sottostanti. La comparsa e la progressione di questi fenomeni presentano un’ampia variabilità in funzione delle condizioni ambientali e delle caratteristiche del cadavere.')})
    if insects:
        notes.append({
            'anchor': 'Insect colonisation' if en else 'entomofauna',
            'text': ('Insect colonisation is the settlement on the body of insects attracted to decomposing tissues, particularly flies, which may lay eggs that hatch into larvae. The larvae pass through successive stages before pupation within the puparium and eventual adult emergence. The sequence and duration of these stages depend on species and are strongly influenced by environmental conditions, particularly temperature, and the exposure and accessibility of the body.' if en else
                     'Per colonizzazione da parte dell’entomofauna si intende l’insediamento sul cadavere di insetti attratti dai tessuti in decomposizione, in particolare ditteri (mosche), che possono deporre uova da cui originano larve; queste attraversano successivi stadi di sviluppo, fino alla formazione della pupa all’interno del pupario e, infine, alla fuoriuscita dell’insetto adulto. La successione e la durata di tali fasi dipendono dalla specie coinvolta e sono fortemente influenzate dalle condizioni ambientali, in particolare dalla temperatura, nonché dalle modalità di esposizione e accessibilità del cadavere.')})
    return notes
