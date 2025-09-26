# pages/test_footer.py
import streamlit as st

st.set_page_config(page_title="Test Footer", layout="centered")

# CSS: nascondi header, footer, toolbar, menu, badge e "Manage app"
st.markdown("""
<style>
/* Header, footer, toolbar e menu */
header[data-testid="stHeader"]{display:none!important;}
footer{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
#MainMenu{display:none!important;}

/* Badge "Made with Streamlit" e varianti */
a[href^="https://streamlit.io"]{display:none!important;}
div[class*="viewerBadge_container"]{display:none!important;}

/* Pulsante "Manage app" su Streamlit Cloud */
[aria-label="Manage app"]{display:none!important;}
button[title="Manage app"]{display:none!important;}
div[data-testid="stStatusWidget"]{display:none!important;}

/* Pulsante Deploy e menu base */
div[data-testid="stDeployButton"]{display:none!important;}
button[data-testid="baseButton-header"]{display:none!important;}
[data-testid="stBaseMenuButton"]{display:none!important;}
</style>
""", unsafe_allow_html=True)

st.title("Test campi numerici")

a = st.number_input("Valore A", step=1.0)
b = st.number_input("Valore B", step=1.0)

st.write("Somma:", a + b)
