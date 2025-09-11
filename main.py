# main.py
import streamlit as st
import streamlit.components.v1 as components

# 1) Leggi override manuale
mode = st.query_params.get("mode")  # "mobile" | "desktop" | None

# 2) Se assente, rileva via JS e reindirizza aggiungendo ?mode=...
if mode is None:
    components.html(
        """
        <script>
        (function () {
          const ua = navigator.userAgent || "";
          const mobileUA = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
          const small = Math.min(screen.width, screen.height) <= 820 || window.innerWidth <= 820;
          const isMobile = mobileUA || small;
          const url = new URL(window.location.href);
          if (!url.searchParams.get('mode')) {
            url.searchParams.set('mode', isMobile ? 'mobile' : 'desktop');
            window.location.replace(url.toString());
          }
        })();
        </script>
        """,
        height=0,
    )
    st.stop()

# 3) Carica l’app corretta
is_mobile = (mode == "mobile")
if is_mobile:
    exec(open("App_MSIL.py", "r", encoding="utf-8").read(), {})
else:
    exec(open("Stima_epoca_decesso.py", "r", encoding="utf-8").read(), {})
    
