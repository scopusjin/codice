"""Digitopressione delle ipostasi: opzioni, limiti e controllo condiviso.

La digitopressione è indipendente dalla migrabilità dopo cambiamento di posizione.
I suoi limiti sono intersecati con il solo intervallo delle ipostasi, senza
aggiungere una seconda famiglia di dati nel metodo combinato.
"""

from app.tanatology_states import LIVOR_ABSENT, LIVOR_NOT_ASSESSED, LIVOR_UNRELIABLE

PRESSURE_KEY = "livor_digitopressione"
PRESSURE_VISIBILITY_KEY = "livor_digitopressione_visible"
PRESSURE_NOT_ASSESSED = "not_assessed"
PRESSURE_COMPLETE_FADING = "complete_fading"
PRESSURE_INCOMPLETE_FADING = "incomplete_fading"

PRESSURE_OPTIONS = (
    PRESSURE_NOT_ASSESSED,
    PRESSURE_COMPLETE_FADING,
    PRESSURE_INCOMPLETE_FADING,
)

PRESSURE_LABEL_IT = {
    PRESSURE_NOT_ASSESSED: "Non valutata",
    PRESSURE_COMPLETE_FADING: "Sì",
    PRESSURE_INCOMPLETE_FADING: "No",
}


def pressure_is_enabled(state):
    """La preferenza è di sessione; il default mantiene la domanda visibile."""
    return bool(state.get(PRESSURE_VISIBILITY_KEY, True))


def effective_livor_pressure(state):
    """Ignora una risposta quando il controllo è disabilitato o non informativo."""
    if not pressure_is_enabled(state):
        return PRESSURE_NOT_ASSESSED
    livor_id = state.get("selettore_macchie_id")
    if livor_id is not None and not pressure_can_change_range(livor_id):
        return PRESSURE_NOT_ASSESSED
    chosen = state.get(PRESSURE_KEY, PRESSURE_NOT_ASSESSED)
    return chosen if chosen in PRESSURE_OPTIONS else PRESSURE_NOT_ASSESSED


def pressure_is_applicable(livor_id):
    """La domanda ha senso solo quando le ipostasi sono presenti e attendibili."""
    return livor_id not in (None, LIVOR_NOT_ASSESSED, LIVOR_ABSENT, LIVOR_UNRELIABLE)


def pressure_can_change_range(livor_id):
    """Mostra il controllo solo se almeno una risposta restringe i limiti."""
    if not pressure_is_applicable(livor_id):
        return False
    # Import locale: evita dipendenze circolari durante l'inizializzazione.
    from app.tanatology_data import LIVOR_RANGES_BY_ID
    interval = LIVOR_RANGES_BY_ID.get(livor_id)
    if interval is None:
        return False
    lo, hi = interval
    return lo < 1 or hi > 20


def intersect_livor_pressure(livor_range, pressure_option):
    """Interseca i limiti bibliografici senza inventare limiti mancanti.

    Scomparsa completa: non oltre 20 h. Mancata scomparsa completa: almeno 1 h.
    Il valore superiore aperto dell'intervallo delle ipostasi viene preservato.
    """
    if livor_range is None:
        return None
    lo, hi = livor_range
    if pressure_option == PRESSURE_COMPLETE_FADING:
        hi = min(hi, 20)
    elif pressure_option == PRESSURE_INCOMPLETE_FADING:
        lo = max(lo, 1)
    # Le combinazioni attualmente ammesse non hanno intersezioni vuote.
    return (lo, hi) if lo <= hi else None


def render_livor_pressure_input(livor_id, label):
    """Stessa sottodomanda nella pagina completa e nel sopralluogo."""
    import streamlit as st

    if not pressure_is_enabled(st.session_state):
        return PRESSURE_NOT_ASSESSED
    if not pressure_can_change_range(livor_id):
        # Quando nessuna risposta può restringere il range, non usare un vecchio
        # risultato di digitopressione eventualmente rimasto nella sessione.
        st.session_state[PRESSURE_KEY] = PRESSURE_NOT_ASSESSED
        return PRESSURE_NOT_ASSESSED
    # Un solo widget elimina lo spazio fra caption e risposta.
    # L'etichetta conserva il formato ridotto e il rientro da sottodomanda.
    st.html("""
    <style>
    [class*="st-key-livor_pressure_subquestion"] {
        padding-left: 0.75rem !important;
    }
    [class*="st-key-livor_pressure_subquestion"] [data-testid="stSelectbox"] > label,
    [class*="st-key-livor_pressure_subquestion"] [data-testid="stSelectbox"] > label p {
        font-size: 0.8rem !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        padding: 0 !important;
        font-weight: 400 !important;
    }
    </style>
    """)
    with st.container(key="livor_pressure_subquestion", gap=None):
        return st.selectbox(
            label,
            options=PRESSURE_OPTIONS,
            format_func=lambda value: PRESSURE_LABEL_IT[value],
            key=PRESSURE_KEY,
            label_visibility="visible",
        )
