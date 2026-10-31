"""Explicit Word launch parameters; no patient identity is accepted."""
from datetime import datetime
from math import isfinite
import re

PREFIX = 'mt_'


def launch_values(params):
    if params.get('mt_open') != '1':
        return None
    code = params.get('mt_case', '')
    if not re.fullmatch(r'X\d{2}\.\d{1,8}', code):
        raise ValueError('Numero X non valido.')
    request = params.get('mt_request', '')
    if request and not re.fullmatch(r'[a-f0-9]{32}', request):
        raise ValueError('Codice di collegamento Word non valido.')
    values = {'case_code': code}
    for source, target, low, high in [('mt_weight', 'peso', 0, 1000),
                                      ('mt_ta', 'ta_base_val', -100, 100),
                                      ('mt_tr', 'rt_val', 0, 60)]:
        raw = params.get(source, '').strip()
        if raw:
            value = float(raw.replace(',', '.'))
            if not isfinite(value) or not low <= value <= high or (target == 'peso' and value == 0):
                raise ValueError('Valore non valido: ' + source)
            values[target] = value
    day, hour = params.get('mt_date', ''), params.get('mt_time', '')
    if day:
        values['input_data_rilievo'] = datetime.strptime(day, '%d.%m.%Y').date()
    if hour:
        values['input_ora_rilievo'] = datetime.strptime(hour, '%H:%M').strftime('%H:%M')
    values['usa_orario_custom'] = bool(day and hour)
    return values


def apply_word_measurements(case, values):
    """Overlay current documented measurements while retaining saved case choices."""
    from app.case_file import restored_inputs, snapshot_case
    from app.fc_selection import refresh_fc_for_weight
    state = restored_inputs(case)
    old_ta = state.get('ta_base_val')
    for key in ('peso', 'rt_val', 'ta_base_val'):
        if key in values:
            state[key] = values[key]
    if 'ta_base_val' in values:
        ta = values['ta_base_val']
        state['__full_standard_ta_base_val'] = ta
        state['__full_interval_ta_base_val'] = ta
        # Keep a saved excursion bound; a single temperature follows the new measurement.
        if state.get('ta_other_val') == old_ta:
            state['ta_other_val'] = ta
            state['__full_interval_ta_other_val'] = ta
        other = state.get('ta_other_val')
        if other is not None:
            state['Ta_min_beta'], state['Ta_max_beta'] = sorted((ta, other))
    if 'peso' in values:
        refresh_fc_for_weight(state)
    updated = snapshot_case(state, case['view'], include_report=False)
    updated['editor_open'] = case['editor_open']
    return updated


def prepare_word_launch():
    import streamlit as st
    if st.query_params.get('mt_open') != '1':
        return
    params = dict(st.query_params)
    try:
        values = launch_values(params)
    except (ValueError, TypeError) as exc:
        st.error('Dati inviati da Word non validi: ' + str(exc))
        st.stop()
    from app.case_file import snapshot_case, CaseFileError
    if params.get('mt_resume') == '1':
        from app.word_resume import render_word_resume
        try:
            pending = render_word_resume(params)
        except CaseFileError as exc:
            st.error(str(exc))
            st.stop()
        if pending is None:
            st.stop()
        pending = apply_word_measurements(pending, values)
    else:
        pending = snapshot_case(values, 'full')
    st.session_state['__case_pending_import'] = pending
    if params.get('mt_request'):
        st.session_state['__word_launch_pending'] = {
            'request_id': params['mt_request'], 'case_code': values['case_code']}
    else:
        st.session_state.pop('__word_launch_pending', None)
        st.session_state.pop('__word_return', None)
    for key in list(st.query_params):
        if key.startswith(PREFIX):
            del st.query_params[key]


def word_result(state, view):
    """Return only a current result bound to the explicitly launched Word case."""
    context = state.get('__word_return')
    if not context or state.get('case_code') != context['case_code']:
        return None
    from app.case_file import snapshot_case, encode_case, case_filename
    case = snapshot_case(state, view)
    if not case.get('report') or not case['report'].get('word_blocks'):
        return None
    case['word_return'] = dict(context)
    filename = case_filename(case)
    return encode_case(case), filename


def render_word_download(view):
    """Compatibility hook: the ordinary Case menu owns the only download."""
    return None
