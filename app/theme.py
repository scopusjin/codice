# app/theme.py
import streamlit as st

def _getopt(key, default=None):
    try:
        v = st.get_option(key)
    except Exception:
        return default
    return default if v is None else v

def theme_colors():
    base = (_getopt("theme.base", "light") or "light").lower()
    custom = _getopt(f"theme.custom.{base}", {}) or {}
    return {
        "Sfondo": _getopt("theme.backgroundColor", "#FFFFFF"),
        "Input": _getopt("theme.secondaryBackgroundColor", "#F3F4F6"),
        "Testo": _getopt("theme.textColor", "#1F2937"),
        "Btn": _getopt("theme.primaryColor", "#22D3EE"),
        "BtnHover": custom.get("buttonHover", "#06B6D4"),
        "OutBg": custom.get("outputBg", "#DDEBFF"),       # più leggibile
        "OutBorder": custom.get("outputBorder", "#5B9BFF"),
        "WarnBg": custom.get("warnBg", "#fff3cd"),
        "WarnText": custom.get("warnText", "#664d03"),
        "WarnBorder": custom.get("warnBorder", "#ffda6a"),
    }

def apply_theme():
    C = theme_colors()
    st.markdown(f"""
    <style>
      :root {{ --primary-color: {C["Btn"]}; }}

      html, body, [data-testid="stAppViewContainer"] {{
        background-color: {C["Sfondo"]} !important;
        color: {C["Testo"]} !important;
      }}

      /* Input base fuori dai pannelli speciali: lasciamo padding nativo */
      [data-baseweb="select"] > div {{
        background: {C["Input"]} !important;
        color: {C["Testo"]} !important;
        border-radius: 8px !important;
      }}
      input[type="text"], input[type="number"], textarea {{
        background: {C["Input"]} !important;
        color: {C["Testo"]} !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
        border-radius: 8px !important;
      }}

      /* Pulsanti */
      div.stButton > button {{
        background: {C["Btn"]} !important;
        color: #0b1220 !important;
        border: 0 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
      }}
      div.stButton > button:hover {{
        background: {C["BtnHover"]} !important;
        filter: brightness(0.98);
      }}

      /* Box output */
      .final-text, .fc-box {{
        background: {C["OutBg"]} !important;
        border: 1px solid {C["OutBorder"]} !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        color: {C["Testo"]} !important;
      }}

      /* Avvisi */
      .warn-box {{
        background: {C["WarnBg"]} !important;
        color: {C["WarnText"]} !important;
        border: 1px solid {C["WarnBorder"]} !important;
        border-radius: 8px !important;
        padding: 8px 10px !important;
        font-size: 0.92rem !important;
      }}

      /* PANNELLO FC: sfondo e INPUT coerenti all'interno */
      .fc-panel {{
        background: {C["OutBg"]} !important;
        border: 1px solid {C["OutBorder"]} !important;
        border-radius: 8px !important;
        padding: 8px !important;
        margin: 4px 0 !important;
      }}
      .fc-panel input[type="text"],
      .fc-panel input[type="number"],
      .fc-panel textarea,
      .fc-panel [data-baseweb="select"] > div {{
        background: {C["OutBg"]} !important;    /* stesso sfondo del pannello */
        color: {C["Testo"]} !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
      }}
    </style>
    """, unsafe_allow_html=True)

def fc_panel_start():
    st.markdown('<div class="fc-panel">', unsafe_allow_html=True)

def fc_panel_end():
    st.markdown('</div>', unsafe_allow_html=True)

def warn_box(msg: str):
    st.markdown(f'<div class="warn-box">⚠️ {msg}</div>', unsafe_allow_html=True)
