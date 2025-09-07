# main.py
import streamlit as st

# Riconoscimento automatico del dispositivo
try:
    from streamlit_user_agents import get_user_agent
    ua = get_user_agent()
    is_mobile = bool(ua and (ua.is_mobile or ua.is_tablet))
except Exception:
    # fallback: desktop
    is_mobile = False

# Permetti comunque override manuale via query param
qp = st.experimental_get_query_params()
if qp.get("mode") == ["mobile"]:
    is_mobile = True
if qp.get("mode") == ["desktop"]:
    is_mobile = False

# Carica l'app corretta
if is_mobile:
    exec(open("app_mobile.py", "r", encoding="utf-8").read(), {})
else:
    exec(open("app.py", "r", encoding="utf-8").read(), {})
