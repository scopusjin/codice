# pages/app_mobile.py
import streamlit as st
import datetime
from app.parameters import opzioni_macchie, opzioni_rigidita
from app.graphing import aggiorna_grafico

st.set_page_config(page_title="Mor-tem Mobile", layout="centered")

st.markdown("## Stima epoca decesso (mobile)")

# --- Data/Ora ispezione ---
with st.container(border=True):
    usa_orario_custom = st.toggle(
        "Aggiungi data/ora rilievi tanatologici",
        value=st.session_state.get("usa_orario_custom", False),
        key="usa_orario_custom",
    )
    if usa_orario_custom:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            input_data_rilievo = st.date_input(
                "Data ispezione legale:",
                value=st.session_state.get("input_data_rilievo") or datetime.date.today(),
                key="input_data_rilievo_widget",
                label_visibility="collapsed",
            )
            st.session_state["input_data_rilievo"] = input_data_rilievo
        with col2:
            input_ora_rilievo = st.text_input(
                "Ora ispezione legale (HH:MM):",
                value=st.session_state.get("input_ora_rilievo") or "00:00",
                key="input_ora_rilievo_widget",
                label_visibility="collapsed",
            )
            st.session_state["input_ora_rilievo"] = input_ora_rilievo
    else:
        st.session_state["input_data_rilievo"] = None
        st.session_state["input_ora_rilievo"] = None

# --- Ipostasi e rigidità ---
with st.container(border=True):
    col1, col2 = st.columns(2, gap="small")
    with col1:
        selettore_macchie = st.selectbox(
            "Macchie ipostatiche:",
            options=list(opzioni_macchie.keys()),
            key="selettore_macchie",
            label_visibility="collapsed",
        )
    with col2:
        selettore_rigidita = st.selectbox(
            "Rigidità cadaverica:",
            options=list(opzioni_rigidita.keys()),
            key="selettore_rigidita",
            label_visibility="collapsed",
        )

# --- Temperature e peso ---
with st.container(border=True):
    col1, col2, col3 = st.columns([1, 1, 1.3], gap="small")
    with col1:
        input_rt = st.number_input(
            "T. rettale (°C):",
            value=st.session_state.get("rt_val", 35.0),
            step=0.1, format="%.1f",
            key="rt_val",
            label_visibility="collapsed",
        )
    with col2:
        input_ta = st.number_input(
            "T. ambientale media (°C):",
            value=st.session_state.get("ta_base_val", 20.0),
            step=0.1, format="%.1f",
            key="ta_base_val",
            label_visibility="collapsed",
        )
    with col3:
        input_w = st.number_input(
            "Peso (kg):",
            value=st.session_state.get("peso", 70.0),
            step=1.0, format="%.1f",
            key="peso",
            label_visibility="collapsed",
        )

# --- Fattore di correzione (singolo) ---
with st.container(border=True):
    fattore_correzione = st.number_input(
        "Fattore di correzione (FC):",
        value=st.session_state.get("fattore_correzione", 1.0),
        step=0.01, format="%.2f",
        key="fattore_correzione",
        label_visibility="collapsed",
    )
    st.toggle(
        "Suggerisci FC",
        value=st.session_state.get("toggle_fattore_inline", False),
        key="toggle_fattore_inline",
    )
    st.session_state["toggle_fattore"] = st.session_state["toggle_fattore_inline"]

# --- Bottone e output ---
if st.button("STIMA EPOCA DECESSO", key="btn_stima_mobile"):
    aggiorna_grafico(
        selettore_macchie=selettore_macchie,
        selettore_rigidita=selettore_rigidita,
        input_rt=input_rt,
        input_ta=input_ta,
        input_tm=37.2,  # fisso default
        input_w=input_w,
        fattore_correzione=st.session_state["fattore_correzione"],
        widgets_parametri_aggiuntivi={},  # no extra
        usa_orario_custom=st.session_state["usa_orario_custom"],
        input_data_rilievo=st.session_state["input_data_rilievo"],
        input_ora_rilievo=st.session_state["input_ora_rilievo"],
        alterazioni_putrefattive=False,
    )
  
