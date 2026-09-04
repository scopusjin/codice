# -*- coding: utf-8 -*-
"""Navigazione mobile tra versione completa e modalità sopralluogo."""

import streamlit as st


_FULL_NAV_STATE_KEYS = (
    "stima_cautelativa_beta",
    "range_unico_beta",
    "peso_stimato_beta",
    "ta_range_toggle_beta",
    "fc_manual_range_beta",
    "ta_other_val",
    "fc_min_val",
    "fc_other_val",
    "__prudent_explicit_ranges_initialized",
    "__full_standard_ta_base_val",
    "__full_standard_fattore_correzione",
    "__full_interval_ta_base_val",
    "__full_interval_ta_other_val",
    "__full_interval_fc_min_val",
    "__full_interval_fc_other_val",
    "toggle_fattore_inline",
    "toggle_fattore_inline_std",
    "toggle_fattore",
    "__full_fc_suggest_target",
)
_FULL_NAV_SNAPSHOT_KEY = "__mobile_full_state_snapshot"


def _save_full_navigation_state() -> None:
    snapshot = {
        state_key: st.session_state[state_key]
        for state_key in _FULL_NAV_STATE_KEYS
        if state_key in st.session_state
    }
    if bool(st.session_state.get("stima_cautelativa_beta", False)):
        ta_base = st.session_state.get("ta_base_val")
        if ta_base is None:
            ta_base = st.session_state.get("__full_interval_ta_base_val")
        if ta_base is None:
            ta_base = st.session_state.get("ta_other_val")
        if ta_base is not None:
            snapshot["ta_base_val"] = ta_base
    st.session_state[_FULL_NAV_SNAPSHOT_KEY] = snapshot


def _restore_full_navigation_state() -> None:
    snapshot = st.session_state.pop(_FULL_NAV_SNAPSHOT_KEY, None)
    shared_ta = st.session_state.get("ta_base_val")

    for state_key in _FULL_NAV_STATE_KEYS:
        st.session_state.pop(state_key, None)

    if not isinstance(snapshot, dict):
        return

    snapshot_interval_mode = bool(snapshot.get("stima_cautelativa_beta", False))
    if snapshot_interval_mode:
        st.session_state.pop("ta_base_val", None)

    st.session_state.update(snapshot)

    if not snapshot_interval_mode:
        st.session_state["ta_base_val"] = shared_ta


def _ensure_desktop_sidebar_collapsed() -> None:
    """Chiude la sidebar Full sul desktop lasciando il controllo nativo di apertura."""
    st.iframe(
        """
        <style>
          html, body {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            background: transparent !important;
          }
        </style>
        <script>
          (() => {
            const frame = window.frameElement;
            if (frame) {
              Object.assign(frame.style, {
                display: "none",
                width: "0",
                minWidth: "0",
                height: "0",
                minHeight: "0",
                border: "0",
                margin: "0",
                padding: "0"
              });
            }

            if (window.parent.innerWidth < 769) return;

            const doc = window.parent.document;
            const collapseTarget = () =>
              doc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
              doc.querySelector('button[data-testid="stSidebarCollapseButton"]') ||
              doc.querySelector('[data-testid="stCollapseSidebarButton"] button') ||
              doc.querySelector('button[data-testid="stCollapseSidebarButton"]') ||
              doc.querySelector('section[data-testid="stSidebar"] button[aria-label*="Collapse"]') ||
              doc.querySelector('section[data-testid="stSidebar"] button[aria-label*="Close sidebar"]');

            const target = collapseTarget();
            if (target) target.click();
          })();
        </script>
        """,
        height=0,
        width=0,
    )


def render_mobile_page_switch(label: str, target: str, key: str) -> None:
    """Renderizza il cambio modalità nel punto reale in cui viene chiamato."""
    if key == "mobile_nav_footer_to_msil":
        _ensure_desktop_sidebar_collapsed()

    st.markdown(
        f"""
        <style>
        [data-testid="stElementContainer"]:has(.mortem-mobile-nav-style) {{
            display: none !important;
        }}
        [class*="st-key-{key}"] {{
            display: none !important;
        }}

        @media (min-width: 769px) {{
            body:has([class*="st-key-stima_cautelativa_beta"])
            header[data-testid="stHeader"] {{
                min-height: 2.35rem !important;
                height: 2.35rem !important;
                background: transparent !important;
            }}

            /* Mantiene disponibile il controllo nativo della sidebar anche
               nelle versioni Streamlit che lo collocano dentro la toolbar. */
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stToolbar"] {{
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stExpandSidebarButton"],
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stSidebarCollapsedControl"],
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="collapsedControl"] {{
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                pointer-events: auto !important;
            }}

            /* Desktop: sidebar più stretta quando viene aperta. */
            body:has([class*="st-key-stima_cautelativa_beta"])
            section[data-testid="stSidebar"] {{
                width: 13rem !important;
                min-width: 13rem !important;
                max-width: 13rem !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
                width: 13rem !important;
                min-width: 13rem !important;
                max-width: 13rem !important;
            }}

            /* La Full non resta centrata nel viewport: parte dal margine sinistro. */
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] {{
                box-sizing: border-box !important;
                margin-left: 0 !important;
                margin-right: auto !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }}
        }}

        /* Tablet, laptop stretti e finestre ridotte: tutto il flusso principale
           torna verticale. Questo override prevale sul vecchio grid >=1024 px. */
        @media (min-width: 769px) and (max-width: 1199px) {{
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] {{
                width: min(100%, 52rem) !important;
                max-width: 52rem !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{
                display: flex !important;
                flex-direction: column !important;
                width: 100% !important;
                max-width: none !important;
                gap: 0.30rem !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {{
                grid-column: auto !important;
                grid-row: auto !important;
                position: static !important;
                top: auto !important;
                width: 100% !important;
                max-width: none !important;
                min-width: 0 !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
            }}
        }}

        /* Desktop largo: colonna input compatta a sinistra e risultati sticky
           nello spazio residuo a destra. */
        @media (min-width: 1200px) {{
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] {{
                width: 100% !important;
                max-width: none !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{
                display: grid !important;
                position: relative !important;
                grid-template-columns: minmax(0, 52rem) minmax(18rem, 1fr) !important;
                grid-auto-flow: row !important;
                justify-content: stretch !important;
                column-gap: clamp(0.75rem, 1.4vw, 1.35rem) !important;
                row-gap: 0.30rem !important;
                align-items: start !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {{
                grid-column: 1 !important;
                grid-row: auto !important;
                min-width: 0 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has(.mortem-full-title) {{
                grid-column: 1 / -1 !important;
                grid-row: 1 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > [class*="st-key-inspection_datetime_row"],
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has([class*="st-key-inspection_datetime_row"]) {{
                grid-column: 1 !important;
                grid-row: 2 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > [class*="st-key-selettore_macchie_ui"],
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has([class*="st-key-selettore_macchie_ui"]) {{
                grid-column: 1 !important;
                grid-row: 3 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > [class*="st-key-henssge_non_applicabile"],
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has([class*="st-key-henssge_non_applicabile"]) {{
                grid-column: 1 !important;
                grid-row: 4 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has([class*="st-key-btn_stima"]) {{
                grid-column: 2 !important;
                grid-row: 3 !important;
                position: sticky !important;
                top: 1rem !important;
                width: min(100%, 18rem) !important;
                max-width: 18rem !important;
                justify-self: center !important;
                align-self: start !important;
                margin: 0 !important;
                z-index: 4 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > [class*="st-key-mortem_result_box"],
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has([class*="st-key-mortem_result_box"]) {{
                grid-column: 2 !important;
                grid-row: 3 / span 12 !important;
                position: sticky !important;
                top: 5.2rem !important;
                width: 100% !important;
                max-width: none !important;
                min-height: 0 !important;
                padding: 0.85rem 0.85rem 1.10rem !important;
                align-self: start !important;
                justify-self: stretch !important;
                margin: 4.4rem 0 0 0 !important;
                z-index: 3 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > [class*="st-key-mortem_no_data_box"],
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has([class*="st-key-mortem_no_data_box"]) {{
                grid-column: 2 !important;
                grid-row: 3 / span 12 !important;
                position: sticky !important;
                top: 5.2rem !important;
                width: 100% !important;
                max-width: none !important;
                align-self: start !important;
                justify-self: stretch !important;
                margin: 4.4rem 0 0 0 !important;
                z-index: 3 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-mortem_result_box"] > [data-testid="stVerticalBlock"] {{
                gap: 0.55rem !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-mortem_result_box"]
            [data-testid="stMarkdownContainer"] > div[style*="background:#E6F1EF"] {{
                margin: 0.70rem 0 1.05rem !important;
                padding: 1rem 1.25rem !important;
            }}

            /* I comandi della colonna risultati possono andare a capo senza
               restringere artificialmente la colonna. */
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-btn_stima"] button,
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-mortem_result_box"] button,
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-mortem_no_data_box"] button {{
                height: auto !important;
                min-height: 2.5rem !important;
                white-space: normal !important;
                overflow-wrap: anywhere !important;
                line-height: 1.2 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-btn_stima"] button p,
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-mortem_result_box"] button p,
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [class*="st-key-mortem_no_data_box"] button p {{
                white-space: normal !important;
                overflow-wrap: anywhere !important;
                line-height: 1.2 !important;
                text-align: center !important;
            }}
        }}

        @media (max-width: 768px) {{
            [class*="st-key-{key}"] {{
                display: flex !important;
                justify-content: flex-end !important;
                width: 100% !important;
                max-width: 100% !important;
                margin: 0.55rem 0 0.10rem 0 !important;
                padding: 0 !important;
            }}
            [class*="st-key-{key}"] [data-testid="stButton"] button {{
                min-height: 1.75rem !important;
                height: auto !important;
                padding: 0.08rem 0.50rem !important;
                background: transparent !important;
                color: var(--primary-color, #2196F3) !important;
                border: 1px solid var(--primary-color, #2196F3) !important;
                border-radius: 7px !important;
                box-shadow: none !important;
                font-size: 0.76rem !important;
                font-weight: 600 !important;
                white-space: nowrap !important;
            }}
            [class*="st-key-{key}"] [data-testid="stButton"] button:hover,
            [class*="st-key-{key}"] [data-testid="stButton"] button:active,
            [class*="st-key-{key}"] [data-testid="stButton"] button:focus {{
                background: transparent !important;
                color: var(--primary-color, #2196F3) !important;
                border-color: var(--primary-color, #2196F3) !important;
                box-shadow: none !important;
                outline: 0 !important;
            }}

            body:has([class*="st-key-stima_cautelativa_beta"])
            header[data-testid="stHeader"] {{
                min-height: 2.35rem !important;
                height: 2.35rem !important;
                background: transparent !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            div.block-container {{
                padding-top: 0.40rem !important;
            }}

            /* Full mobile: lascia un minimo respiro sotto il titolo e compatta
               solo il riquadro data/ora, senza cambiare il contenuto. */
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stElementContainer"]:has(.mortem-full-title) {{
                margin: 0 0 0.18rem 0 !important;
                padding: 0 !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-usa_orario_custom"]) {{
                padding: 0.42rem 0.75rem !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-usa_orario_custom"])
            [data-testid="stVerticalBlock"] {{
                gap: 0.20rem !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            [class*="st-key-usa_orario_custom"] {{
                margin: 0 !important;
                padding: 0 !important;
            }}
        }}
        </style>
        <span class="mortem-mobile-nav-style"></span>
        """,
        unsafe_allow_html=True,
    )

    with st.container(
        horizontal=True,
        horizontal_alignment="right",
        key=key,
    ):
        if st.button(label, key=f"{key}_button"):
            if key == "mobile_nav_footer_to_msil":
                _save_full_navigation_state()
            elif key == "mobile_nav_footer_to_full":
                _restore_full_navigation_state()
            st.switch_page(target)