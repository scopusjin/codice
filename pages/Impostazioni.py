# pages/Impostazioni.py
import streamlit as st

from app.livor_digitopressione import PRESSURE_VISIBILITY_KEY
from app.rigor_reformation import REFORMATION_VISIBILITY_KEY
from app.mobile_shell import install_minimal_mobile_shell
from app.language import render_language_selector
from app.page_heading import render_page_heading
from app.page_navigation import SETTINGS_PAGE, record_page_visit, render_back_button

from app.language import current_language
st.set_page_config(page_title="Settings" if current_language() == "en" else "Impostazioni", layout="centered")
install_minimal_mobile_shell()
record_page_visit(st.session_state, SETTINGS_PAGE)

render_page_heading("⚙️ Impostazioni")

# Default se non c'è ancora
if "henssge_round_minutes" not in st.session_state:
    st.session_state["henssge_round_minutes"] = 15

scelta = st.radio(
    ("Final rounding interval for estimated postmortem intervals and times of death" if current_language() == "en" else
     "Ampiezza dell’arrotondamento finale degli intervalli temporali e degli orari stimati del decesso"),
    ["6 minuti", "15 minuti", "30 minuti"],
    index={6: 0, 15: 1, 30: 2}[st.session_state["henssge_round_minutes"]],
)
st.session_state["henssge_round_minutes"] = {
    "6 minuti": 6,
    "15 minuti": 15,
    "30 minuti": 30,
}[scelta]

st.caption(
    "Rounding is applied only when displaying results: lower bounds downwards and upper bounds upwards. "
    "Durations and calendar times are derived separately from unrounded values, without successive rounding. "
    "The examination time remains unchanged." if current_language() == "en" else
    "L’arrotondamento viene applicato solo alla presentazione dei risultati, per difetto al limite inferiore "
    "e per eccesso al limite superiore. Intervalli temporali e orari sono ricavati separatamente dai valori "
    "non arrotondati, senza arrotondamenti in successione. L’orario dei rilievi resta invariato."
)
st.success(f"Final rounding interval: {st.session_state['henssge_round_minutes']} minutes." if current_language() == "en"
           else f"Arrotondamento finale: {st.session_state['henssge_round_minutes']} minuti.")

# Preferenza distinta dal widget: rimane valida anche dopo il cambio pagina.
st.session_state.setdefault(PRESSURE_VISIBILITY_KEY, True)
mostra_digitopressione = st.toggle(
    "Mostra digitopressione nelle ipostasi",
    value=bool(st.session_state[PRESSURE_VISIBILITY_KEY]),
    key="__setting_digitopressione_toggle",
    help=(
        "Se disattivata, la sottodomanda non comparirà nei pannelli delle ipostasi "
        "e non verrà considerata nel calcolo."
    ),
)
st.session_state[PRESSURE_VISIBILITY_KEY] = mostra_digitopressione

st.session_state.setdefault(REFORMATION_VISIBILITY_KEY, True)
mostra_ricomparsa = st.toggle(
    "Mostra ricomparsa della rigidità dopo mobilizzazione",
    value=bool(st.session_state[REFORMATION_VISIBILITY_KEY]),
    key="__setting_rigor_reformation_toggle",
)
st.session_state[REFORMATION_VISIBILITY_KEY] = mostra_ricomparsa

st.markdown(
    "[Archivio completo dei casi FC — Google Drive]"
    "(https://docs.google.com/spreadsheets/d/134cUMee2Uot64lJQ2ocIsqvNkTCKkdM-kJHAaLY6je0/edit)"
)

render_back_button(SETTINGS_PAGE, key="back_home")

st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: transparent !important;
        color: #1e90ff !important;
        font-size: 10px !important;  /* più piccolo del normale */
        border: none !important;
        padding: 0 !important;
        text-align: left !important;
    }
    div.stButton > button:first-child:hover {
        text-decoration: underline !important;
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

render_language_selector()
