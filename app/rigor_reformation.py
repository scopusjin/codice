"""Ricomparsa della rigidità dopo mobilizzazione forzata.
Il reperto positivo restringe il limite massimo a 19 ore; quello negativo
non produce autonomamente un limite cronologico.
"""
from app.tanatology_states import RIGOR_DEVELOPING, RIGOR_FULL

REFORMATION_KEY = "rigor_reformation"
REFORMATION_VISIBILITY_KEY = "rigor_reformation_visible"
REFORMATION_NOT_ASSESSED = "not_assessed"
REFORMATION_YES = "yes"
REFORMATION_NO = "no"
REFORMATION_OPTIONS = (REFORMATION_NOT_ASSESSED, REFORMATION_YES, REFORMATION_NO)
REFORMATION_LABELS = {
    REFORMATION_NOT_ASSESSED: "Non valutata",
    REFORMATION_YES: "Sì",
    REFORMATION_NO: "No",
}


def reformation_can_change_range(rigor_id):
    """Il sì è utile solo con rigor presente e limite massimo superiore a 19 h."""
    return rigor_id in (RIGOR_DEVELOPING, RIGOR_FULL)


def effective_rigor_reformation(state):
    """Ignora sempre valori nascosti, disabilitati o non pertinenti."""
    if not state.get("mostra_parametri_aggiuntivi", False):
        return REFORMATION_NOT_ASSESSED
    if not state.get(REFORMATION_VISIBILITY_KEY, True):
        return REFORMATION_NOT_ASSESSED
    if not reformation_can_change_range(state.get("selettore_rigidita_id")):
        return REFORMATION_NOT_ASSESSED
    value = state.get(REFORMATION_KEY, REFORMATION_NOT_ASSESSED)
    return value if value in REFORMATION_OPTIONS else REFORMATION_NOT_ASSESSED


def intersect_rigor_reformation(rigor_range, choice):
    if rigor_range is None or choice != REFORMATION_YES:
        return rigor_range
    lo, hi = rigor_range
    return (lo, min(hi, 19)) if lo <= 19 else None


def render_rigor_reformation_input(rigor_id):
    """Sottodomanda parallela alla digitopressione, senza helper."""
    import streamlit as st
    if not st.session_state.get("mostra_parametri_aggiuntivi", False):
        return REFORMATION_NOT_ASSESSED
    if not st.session_state.get(REFORMATION_VISIBILITY_KEY, True):
        return REFORMATION_NOT_ASSESSED
    if not reformation_can_change_range(rigor_id):
        return REFORMATION_NOT_ASSESSED
    st.html("""
    <style>
    [class*="st-key-rigor_reformation_subquestion"] {padding-left: 0.75rem !important;}
    [class*="st-key-rigor_reformation_subquestion"] [data-testid="stSelectbox"] {
        gap: 0 !important;
    }
    [class*="st-key-rigor_reformation_subquestion"] [data-testid="stSelectbox"] > div {
        margin-top: 0 !important;
    }
    [class*="st-key-rigor_reformation_subquestion"] [data-testid="stSelectbox"] > label,
    [class*="st-key-rigor_reformation_subquestion"] [data-testid="stSelectbox"] > label p {
        font-size: 0.8rem !important; line-height: 1.1 !important;
        margin: 0 !important; padding: 0 !important; font-weight: 400 !important;
    }
    </style>
    """)
    with st.container(key="rigor_reformation_subquestion", gap=None):
        return st.selectbox(
            "La rigidità si riforma dopo essere stata vinta?",
            options=REFORMATION_OPTIONS,
            format_func=lambda value: REFORMATION_LABELS[value],
            key=REFORMATION_KEY,
            label_visibility="visible",
        )
