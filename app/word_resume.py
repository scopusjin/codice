"""Event-based transfer from the local Word launcher; reuse case validation."""
from base64 import b64decode
from binascii import Error
from pathlib import Path
import re

from app.case_file import CaseFileError, MAX_BYTES, decode_case


def resume_case(event, params):
    token = params.get('mt_request', '')
    if not re.fullmatch(r'[a-f0-9]{32}', token):
        raise CaseFileError('Collegamento Word non valido.')
    if event is None:
        return None
    if not isinstance(event, dict) or event.get('token') != token:
        raise CaseFileError('Il file ricevuto non appartiene a questa apertura Word.')
    data = event.get('data')
    if not isinstance(data, str) or len(data) > 4 * ((MAX_BYTES + 2) // 3):
        raise CaseFileError('Dimensione massima del caso: 1 MB.')
    try:
        case = decode_case(b64decode(data, validate=True))
    except (Error, ValueError) as exc:
        raise CaseFileError('File Mortem non valido.') from exc
    if case['case_code'].upper() != params.get('mt_case', '').upper():
        raise CaseFileError('Il numero X del file non corrisponde al documento Word.')
    if case['view'] != 'full':
        raise CaseFileError('Il file non appartiene alla stima completa.')
    return case


def render_word_resume(params):
    import streamlit as st
    import streamlit.components.v1 as components
    component = components.declare_component('mortem_word_resume',
        path=str(Path(__file__).with_name('word_resume_frontend')))
    event = component(token=params.get('mt_request', ''),
                      key='word_resume_' + params.get('mt_request', ''), default=None)
    case = resume_case(event, params)
    if case is None:
        st.info('Caricamento del caso salvato da Word. Se il browser impedisce il passaggio automatico, seleziona qui lo stesso JSON.')
        upload = st.file_uploader('Caso Mortem da riprendere', type=['json'], key='word_resume_fallback')
        if upload is not None:
            from base64 import b64encode
            case = resume_case({'token': params['mt_request'],
                                'data': b64encode(upload.getvalue()).decode('ascii')}, params)
    return case
