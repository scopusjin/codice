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
    from app.case_file import snapshot_case
    st.session_state['__case_pending_import'] = snapshot_case(values, 'full')
    for key in list(st.query_params):
        if key.startswith(PREFIX):
            del st.query_params[key]
