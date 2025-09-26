# pages/test_footer.py
import streamlit as st

st.set_page_config(page_title="Test Footer", layout="centered")

# CSS per nascondere header e footer
st.markdown("""
<style>
header[data-testid="stHeader"] {display: none !important;}
footer {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

st.title("Test campi numerici")

a = st.number_input("Valore A", step=1.0)
b = st.number_input("Valore B", step=1.0)

st.write("Somma:", a + b)
