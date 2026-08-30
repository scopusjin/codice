import streamlit as st

from app import i18n
from app.parameters import INF_HOURS
from app.tanatology_data import LIVOR_RANGES_BY_ID, LIVOR_TYPICAL_RANGES_BY_ID
from app.tanatology_states import (
    LIVOR_ABSENT,
    LIVOR_CONFLUING,
    LIVOR_FULLY_MIGRATABLE,
    LIVOR_PARTIALLY_MIGRATABLE,
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE,
    LIVOR_FIXED,
)


_MALLACH_REFERENCE = (
    "Mallach HJ. Zur Frage der Todeszeitbestimmung. "
    "Berl Med. 1964;18:577–582."
)

_LIVOR_TABLE_IDS = (
    LIVOR_ABSENT,
    LIVOR_CONFLUING,
    LIVOR_FULLY_MIGRATABLE,
    LIVOR_PARTIALLY_MIGRATABLE,
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE,
    LIVOR_FIXED,
)


def _format_range(value):
    if value is None:
        return "—"
    lo, hi = value
    if hi >= INF_HOURS:
        return f"≥ {lo:g} h"
    return f"{lo:g}–{hi:g} h"


st.title("Tabelle di riferimento")

# --- Sezione 1: Mallach ---
st.markdown(f"## {i18n.ui_text('full.livor_heading')}")
livor_rows = [
    {
        "Reperto": i18n.livor_label(state_id),
        "Intervallo compatibile": _format_range(LIVOR_RANGES_BY_ID.get(state_id)),
        "Intervallo tipico": _format_range(LIVOR_TYPICAL_RANGES_BY_ID.get(state_id)),
    }
    for state_id in _LIVOR_TABLE_IDS
]
st.dataframe(livor_rows, hide_index=True, use_container_width=True)
st.caption(f"Adattato da: {_MALLACH_REFERENCE}")

st.markdown("## Rigidità cadaverica")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Rigor%20(Mallach).jpeg",
    caption="Rigor (Mallach)",
    use_container_width=True
)

st.markdown("## Metodi combinati")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Metodi%20combinati.jpeg",
    caption="Metodi combinati",
    use_container_width=True
)

# --- Sezione 2: Tabelle Henssge ---
st.markdown("## Fattori di correzione base")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Tabella%201%20henssge.png",
    caption="Tabella 1 henssge",
    use_container_width=True
)

st.markdown("Situazioni speciali")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Tabella%202%20Henssge.png",
    caption="Tabella 2 Henssge",
    use_container_width=True
)

st.markdown("Adattamento per peso corporeo")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Tabella%203%20Henssge.png",
    caption="Tabella 3 Henssge",
    use_container_width=True
)
if st.button("⬅️ Torna alla pagina principale", key="back_home"):
    st.switch_page("app.py")

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
