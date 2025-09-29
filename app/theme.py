def apply_theme():
    C = theme_colors()
    st.markdown(f"""
    <style>
      :root {{
        --primary-color: {C["Btn"]};
      }}

      html, body, [data-testid="stAppViewContainer"] {{
        background-color: {C["Sfondo"]} !important;
        color: {C["Testo"]} !important;
      }}

      /* Input base */
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

      /* Pannello FC con input coerenti */
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
        background: {C["OutBg"]} !important;
        color: {C["Testo"]} !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
      }}
    </style>
    """, unsafe_allow_html=True)
