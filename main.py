# main.py
import streamlit as st
import streamlit.components.v1 as components

MOBILE_FILE = "App_MSIL.py"
DESKTOP_FILE = "Stima_epoca_decesso.py"

def get_mode():
    try:
        return st.query_params.get("mode")  # Streamlit ≥1.33
    except Exception:
        qp = st.experimental_get_query_params()
        return (qp.get("mode") or [None])[0]

def set_mode(val: str):
    try:
        st.query_params["mode"] = val
    except Exception:
        st.experimental_set_query_params(mode=val)
    st.rerun()

mode = get_mode()

# 1) Se già presente -> carica subito
if mode in ("mobile", "desktop"):
    file_to_run = MOBILE_FILE if mode == "mobile" else DESKTOP_FILE
    with open(file_to_run, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, {})
    st.stop()

# 2) Tentativo server-side con streamlit_user_agents (se installato)
is_mobile_ss = None
try:
    from streamlit_user_agents import get_user_agent
    ua = get_user_agent()
    is_mobile_ss = bool(ua and (ua.is_mobile or ua.is_tablet))
except Exception:
    is_mobile_ss = None

if is_mobile_ss is True:
    set_mode("mobile")
elif is_mobile_ss is False:
    set_mode("desktop")

# 3) Fallback client-side: rileva via JS e reindirizza con ?mode=...
components.html(
    """
    <script>
    (function () {
      try {
        const ua = navigator.userAgent || "";
        const isTouch = ( 'ontouchstart' in window ) || ( navigator.maxTouchPoints > 0 );
        const mobileUA = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
        const small = Math.min(screen.width, screen.height) <= 820 || window.innerWidth <= 820;
        const isMobile = mobileUA || (isTouch && small);
        const url = new URL(window.location.href);
        if (!url.searchParams.get('mode')) {
          url.searchParams.set('mode', isMobile ? 'mobile' : 'desktop');
          window.location.replace(url.toString());
        }
      } catch (e) {
        // default desktop se JS fallisce
        const url = new URL(window.location.href);
        if (!url.searchParams.get('mode')) {
          url.searchParams.set('mode', 'desktop');
          window.location.replace(url.toString());
        }
      }
    })();
    </script>
    """,
    height=0,
)
st.stop()
