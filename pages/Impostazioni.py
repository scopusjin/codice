# pages/Impostazioni.py
import streamlit as st

st.set_page_config(page_title="Impostazioni", layout="centered")

st.markdown("## ⚙️ Impostazioni")

# Default se non c'è ancora
if "henssge_round_minutes" not in st.session_state:
    st.session_state["henssge_round_minutes"] = 30

scelta = st.radio(
    "Specifica con quale arrotondamento vuoi che sia fornito l'output per il raffreddamento cadaverico (metodo di Henssge)",
    ["6 minuti", "15 minuti", "30 minuti"],
    index={6: 0, 15: 1, 30: 2}[st.session_state["henssge_round_minutes"]],
)
st.session_state["henssge_round_minutes"] = {
    "6 minuti": 6,
    "15 minuti": 15,
    "30 minuti": 30,
}[scelta]

st.success(f"Impostato a {st.session_state['henssge_round_minutes']} minuti.")

if st.button("⬅️ Torna alla pagina principale", key="back_home"):
    st.switch_page("Stima epoca decesso.py")

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
