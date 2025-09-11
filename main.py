# main.py
import streamlit as st

# Leggi/scrivi query params in modo compatibile
def get_mode():
    try:
        return st.query_params.get("mode")
    except Exception:
        # fallback per versioni vecchie
        return None

def set_mode(val: str):
    try:
        st.query_params["mode"] = val
    except Exception:
        st.experimental_set_query_params(mode=val)  # fallback

mode = get_mode()

st.title("Seleziona interfaccia")
col1, col2 = st.columns(2)

if mode not in {"mobile", "desktop"}:
    with col1:
        if st.button("Apri versione Mobile"):
            set_mode("mobile")
            st.rerun()
    with col2:
        if st.button("Apri versione Desktop"):
            set_mode("desktop")
            st.rerun()
    st.info("Oppure usa ?mode=mobile o ?mode=desktop nell’URL.")
    st.stop()

# Carica l’app selezionata
is_mobile = (mode == "mobile")
file_to_run = "App_MSIL.py" if is_mobile else "Stima_epoca_decesso.py"

# Mostra quale file stai aprendo, così vedi che funziona
st.caption(f"Caricamento: {file_to_run} (mode={mode})")

with open(file_to_run, "r", encoding="utf-8") as f:
    code = f.read()
exec(code, {})
