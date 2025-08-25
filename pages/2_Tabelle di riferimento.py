import streamlit as st

st.title("Tabelle di riferimento")

# --- Sezione 1: Mallach ---
st.markdown("## Ipostasi")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Ipostasi%20(Mallach).jpg",
    caption="Ipostasi (Mallach)",
    use_container_width=True
)

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
