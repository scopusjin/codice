# app/theme.py
# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_extras.stylable_container import stylable_container  # <- aggiungi

# ------------------------------------------------------------
# Utility per ottenere valori dal config di Streamlit
# ------------------------------------------------------------
def _getopt(key, default=None):
    try:
        v = st.get_option(key)
    except Exception:
        return default
    return default if v is None else v

# ------------------------------------------------------------
# Palette temi
# ------------------------------------------------------------
def theme_colors():
    base = (_getopt("theme.base", "light") or "light").lower()
    custom = _getopt(f"theme.custom.{base}", {}) or {}

    # Default per Opzione 3 (Acquamarina soft)
    default_out_bg     = "#153A33" if base == "dark" else "#E6F1EF"
    default_out_border = "#72C2B3" if base == "dark" else "#7FA8A0"
    default_out_text   = "#FFFFFF" if base == "dark" else "#123C34"

    return {
        "Sfondo":   _getopt("theme.backgroundColor",           "#111827" if base == "dark" else "#FFFFFF"),
        "Input":    _getopt("theme.secondaryBackgroundColor",  "#374151" if base == "dark" else "#F3F4F6"),
        "Testo":    _getopt("theme.textColor",                 "#F9FAFB" if base == "dark" else "#1F2937"),

        # Pulsanti blu unificati
        "Btn":        _getopt("theme.primaryColor", "#0284C7"),
        "BtnHover":   custom.get("buttonHover",   "#0369A1"),
        "BtnActive":  custom.get("buttonActive",  "#0C4A6E"),
        "BtnText":    custom.get("buttonText",    "#FFFFFF"),
        "FocusRing":  custom.get("focusRing",     "rgba(34,211,238,0.45)"),

        # Output verdi soft (Opzione 3)
        "OutBg":      custom.get("outputBg",      default_out_bg),
        "OutBorder":  custom.get("outputBorder",  default_out_border),
        "OutText":    custom.get("outputText",    default_out_text),

        # Avvisi
        "WarnBg":     custom.get("warnBg",        "#fff3cd"),
        "WarnText":   custom.get("warnText",      "#664d03"),
        "WarnBorder": custom.get("warnBorder",    "#ffda6a"),
    }

# ------------------------------------------------------------
# Applica CSS del tema
# ------------------------------------------------------------
def apply_theme():
    C = theme_colors()

    # 1) Tema generale
    st.markdown(f"""
    <style>
      :root {{
        --primary-color: {C["Btn"]};
      }}

      html, body, [data-testid="stAppViewContainer"] {{
        background-color: {C["Sfondo"]} !important;
        color: {C["Testo"]} !important;
      }}

      /* Input */
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
      .stButton > button {{
        background: {C["Btn"]} !important;
        color: {C["BtnText"]} !important;
        border: 0 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
      }}
      .stButton > button:hover  {{ background: {C["BtnHover"]} !important; }}
      .stButton > button:active {{ background: {C["BtnActive"]} !important; }}
      .stButton > button:focus  {{
        outline: 0 !important;
        box-shadow: 0 0 0 3px {C["FocusRing"]} !important;
      }}

      /* Box output (final-text, fc-box) */
      .final-text, .fc-box {{
        background: {C["OutBg"]} !important;
        border: 1px solid {C["OutBorder"]} !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        color: {C["OutText"]} !important;
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

      /* Pannello FC */
      .fc-panel {{
        background: {C["OutBg"]} !important;
        border: 1px solid {C["OutBorder"]} !important;
        border-radius: 8px !important;
        padding: 8px !important;
        margin: 4px 0 !important;
        color: {C["OutText"]} !important;
      }}
      .fc-panel input[type="text"],
      .fc-panel input[type="number"],
      .fc-panel textarea,
      .fc-panel [data-baseweb="select"] > div {{
        background: {C["OutBg"]} !important;
        color: {C["OutText"]} !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
      }}
    </style>
    """, unsafe_allow_html=True)

    # 2) Override: final-text bianco SOLO nel popover
    st.markdown("""
    <style>
      div[data-testid="stPopoverContent"] .final-text{
        background:#ffffff !important;
        border:1px solid #e5e7eb !important;
        color:#1f1f1f !important;
      }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Helper per pannello FC
# ------------------------------------------------------------
def fc_panel_start(key: str = "fcwrap_mobile"):
    C = theme_colors()
    bg_light = "#f0f6ff"
    bg_dark  = "#0f2036"
    border_light = "#34D39920"
    border_dark  = "#34D39940"

    return stylable_container(
        key=key,
        css_styles=f"""
        {{
          background:{bg_light};
          border:1px solid {border_light};
          border-radius:8px;
          padding:8px;
          margin:4px 0;
          color:{C['OutText']};
        }}

        [data-stylable-key="{key}"] input[type="text"],
        [data-stylable-key="{key}"] input[type="number"],
        [data-stylable-key="{key}"] textarea,
        [data-stylable-key="{key}"] [data-baseweb="select"] > div {{
          background:{bg_light} !important;
          border:1px solid rgba(0,0,0,0.12) !important;
          color:{C['OutText']} !important;
        }}

        [data-stylable-key="{key}"] [data-testid="stDataEditor"],
        [data-stylable-key="{key}"] [data-testid="stDataEditor"] .cell,
        [data-stylable-key="{key}"] [data-testid="stDataEditor"] input,
        [data-stylable-key="{key}"] [data-testid="stDataEditor"] textarea{{
          background:{bg_light} !important;
          color:{C['OutText']} !important;
        }}

        [data-stylable-key="{key}"] div[data-testid="stVerticalBlock"]{{margin:0!important}}
        [data-stylable-key="{key}"] div[data-testid="stVerticalBlock"]>div{{margin:2px 0!important}}

        @media (prefers-color-scheme: dark){{
          [data-stylable-key="{key}"]{{
            background:{bg_dark};
            border-color:{border_dark};
          }}
          [data-stylable-key="{key}"] input[type="text"],
          [data-stylable-key="{key}"] input[type="number"],
          [data-stylable-key="{key}"] textarea,
          [data-stylable-key="{key}"] [data-baseweb="select"] > div,
          [data-stylable-key="{key}"] [data-testid="stDataEditor"],
          [data-stylable-key="{key}"] [data-testid="stDataEditor"] .cell,
          [data-stylable-key="{key}"] [data-testid="stDataEditor"] input,
          [data-stylable-key="{key}"] [data-testid="stDataEditor"] textarea{{
            background:{bg_dark} !important;
          }}
        }}
        """
    )



# ------------------------------------------------------------
# Box avvisi
# ------------------------------------------------------------
def warn_box(msg: str):
    st.markdown(f'<div class="warn-box">⚠️ {msg}</div>', unsafe_allow_html=True)
