# app/theme.py
# -*- coding: utf-8 -*-
import streamlit as st

def _getopt(key: str, default=None):
    try:
        val = st.get_option(key)
    except Exception:
        return default
    return default if val is None else val

def theme_colors():
    base = (_getopt("theme.base", "light") or "light").lower()
    custom = _getopt(f"theme.custom.{base}", {}) or {}

    return {
        "Sfondo": _getopt("theme.backgroundColor", "#FFFFFF"),
        "Input": _getopt("theme.secondaryBackgroundColor", "#F3F4F6"),
        "Testo": _getopt("theme.textColor", "#1F2937"),
        "Btn": _getopt("theme.primaryColor", "#22D3EE"),
        "BtnHover": custom.get("buttonHover", "#06B6D4"),
        "OutBg": custom.get("outputBg", "#D1FAE5"),
        "OutBorder": custom.get("outputBorder", "#10B981"),
        "WarnBg": custom.get("warnBg", "#fff3cd"),
        "WarnText": custom.get("warnText", "#664d03"),
        "WarnBorder": custom.get("warnBorder", "#ffda6a"),
    }

def apply_theme():
    C = theme_colors()
    st.markdown(f"""
    <style>
      :root {{
        --primary-color: {C["Btn"]};
      }}

      /* Sfondo e testo base */
      html, body, [data-testid="stAppViewContainer"] {{
        background-color: {C["Sfondo"]} !important;
        color: {C["Testo"]} !important;
      }}

      /* Input base */
      input[type="text"], input[type="number"], textarea {{
        background: {C["Input"]} !important;
        color: {C["Testo"]} !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
        border-radius: 8px !important;
      }}

      /* Select (baseweb) */
      [data-baseweb="select"] > div {{
        background: {C["Input"]} !important;
        color: {C["Testo"]} !important;
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

      /* Box output coerenti */
      .final-text, .fc-box {{
        background: {C["OutBg"]} !important;
        border: 1px solid {C["OutBorder"]} !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        color: {C["Testo"]} !important;
      }}

      /* Box avviso coerenti */
      .warn-box {{
        background: {C["WarnBg"]} !important;
        color: {C["WarnText"]} !important;
        border: 1px solid {C["WarnBorder"]} !important;
        border-radius: 8px !important;
        padding: 8px 10px !important;
        font-size: 0.92rem !important;
      }}
    </style>
    """, unsafe_allow_html=True)

def fc_box_html(content: str):
    st.markdown(f'<div class="fc-box">{content}</div>', unsafe_allow_html=True)

def warn_box(msg: str):
    st.markdown(f'<div class="warn-box">⚠️ {msg}</div>', unsafe_allow_html=True)
