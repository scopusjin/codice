# pages/test_footer.py
import streamlit as st

st.set_page_config(page_title="Test Footer", layout="centered")

st.markdown("""
<style>
/* Header, footer, toolbar, menu */
header[data-testid="stHeader"]{display:none!important;}
footer{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
#MainMenu{display:none!important;}

/* Badge "Made with Streamlit" */
a[href^="https://streamlit.io"]{display:none!important;}
div[class*="viewerBadge_container"]{display:none!important;}

/* Pulsante "Manage app" - varianti */
[aria-label="Manage app"]{display:none!important;}
[title="Manage app"]{display:none!important;}
button:has(span:contains("Manage app")){display:none!important;}
div:has(> button[title="Manage app"]){display:none!important;}

/* Status widget / deploy */
div[data-testid="stStatusWidget"]{display:none!important;}
div[data-testid="stDeployButton"]{display:none!important;}
</style>
""", unsafe_allow_html=True)

st.title("Test campi numerici")

a = st.number_input("Valore A", step=1.0)
b = st.number_input("Valore B", step=1.0)

st.write("Somma:", a + b)
