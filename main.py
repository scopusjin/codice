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

# Override manuale via query param
mode = st.query_params.get("mode")  # "mobile" oppure "desktop"
if mode == "mobile":
    is_mobile = True
elif mode == "desktop":
    is_mobile = False

# Carica l'app corretta
if is_mobile:
    exec(open("App_MSIL.py", "r", encoding="utf-8").read(), {})
else:
    exec(open("Stima_epoca_decesso.py", "r", encoding="utf-8").read(), {})
    
