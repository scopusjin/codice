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


def _render_mobile_sidebar_button() -> None:
    """Su mobile mostra Menu; su desktop mantiene la sidebar realmente aperta."""
    st.iframe(
        """
        <button id="mortem-sidebar-button" type="button" aria-label="Apri menu">☰ Menu</button>
        <style>
          html, body {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            background: transparent !important;
          }
          #mortem-sidebar-button {
            height: 2.1rem;
            margin: 0;
            padding: 0.08rem 0.58rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.28rem;
            border: 1px solid #2196F3;
            border-radius: 8px;
            background: white;
            color: #2196F3;
            box-shadow: none;
            font: 600 0.78rem/1 Arial, sans-serif;
            cursor: pointer;
            white-space: nowrap;
          }
        </style>
        <script>
          (() => {
            const frame = window.frameElement;
            if (!frame) return;

            const doc = window.parent.document;
            const isDesktop = window.parent.innerWidth >= 769;
            const expandTarget = () =>
              doc.querySelector('[data-testid="stExpandSidebarButton"] button') ||
              doc.querySelector('button[data-testid="stExpandSidebarButton"]') ||
              doc.querySelector('[data-testid="stExpandSidebarButton"]') ||
              doc.querySelector('[data-testid="stSidebarCollapsedControl"] button') ||
              doc.querySelector('[data-testid="collapsedControl"] button');

            if (isDesktop) {
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

              const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
              if (!sidebar || sidebar.getAttribute("aria-expanded") === "false") {
                const target = expandTarget();
                if (target) target.click();
              }
              return;
            }

            Object.assign(frame.style, {
              position: "static",
              width: "6.2rem",
              minWidth: "6.2rem",
              height: "2.2rem",
              minHeight: "2.2rem",
              border: "0",
              margin: "0.35rem 0 0.10rem 0",
              padding: "0",
              background: "transparent",
              overflow: "hidden"
            });

            const button = document.getElementById("mortem-sidebar-button");
            if (!button) return;

            button.addEventListener("click", () => {
              const target = expandTarget();
              if (target) target.click();
            });
          })();
        </script>
        """,
        height=38,
        width=105,
    )


def render_mobile_page_switch(label: str, target: str, key: str) -> None:
    """Renderizza il cambio modalità nel punto reale in cui viene chiamato."""
    st.markdown(
        f"""
        <style>
        [data-testid="stElementContainer"]:has(.mortem-mobile-nav-style) {{
            display: none !important;
        }}
        [class*="st-key-{key}"] {{
            display: none !important;
        }}
        [class*="st-key-mobile_sidebar_menu_footer"] {{
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}

        /* La toolbar Streamlit non viene usata nella Full. */
        body:has([class*="st-key-stima_cautelativa_beta"])
        [data-testid="stToolbar"],
        body:has([class*="st-key-stima_cautelativa_beta"])
        [data-testid="stExpandSidebarButton"] {{
            display: none !important;
        }}

        @media (min-width: 769px) {{
            body:has([class*="st-key-stima_cautelativa_beta"])
            header[data-testid="stHeader"] {{
                min-height: 0 !important;
                height: 0 !important;
                background: transparent !important;
            }}

            /* Desktop: sidebar sempre aperta e più stretta. */
            body:has([class*="st-key-stima_cautelativa_beta"])
            section[data-testid="stSidebar"] {{
                visibility: visible !important;
                transform: none !important;
                left: 0 !important;
                width: 13rem !important;
                min-width: 13rem !important;
                max-width: 13rem !important;
                flex: 0 0 13rem !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
                width: 13rem !important;
                min-width: 13rem !important;
                max-width: 13rem !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stSidebarCollapseButton"],
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stSidebarCollapsedControl"],
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="collapsedControl"] {{
                display: none !important;
            }}
        }}

        /* Desktop largo: il pulsante parte alla stessa quota dell'ipostasi.
           Il risultato resta sotto, più alto e con più respiro attorno alla frase. */
        @media (min-width: 1280px) {{
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
                width: 100% !important;
                max-width: 34rem !important;
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
                grid-row: 4 / span 12 !important;
                position: sticky !important;
                top: 5.2rem !important;
                width: 100% !important;
                max-width: 34rem !important;
                min-height: 31rem !important;
                padding: 0.85rem 0.85rem 1.10rem !important;
                align-self: start !important;
                margin: 0 !important;
                z-index: 3 !important;
            }}

            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > [class*="st-key-mortem_no_data_box"],
            html body:has([class*="st-key-stima_cautelativa_beta"]):has(.mortem-full-title)
            [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
            > *:has([class*="st-key-mortem_no_data_box"]) {{
                grid-column: 2 !important;
                grid-row: 4 !important;
                position: sticky !important;
                top: 5.2rem !important;
                width: 100% !important;
                max-width: 34rem !important;
                align-self: start !important;
                margin: 0 !important;
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

            [class*="st-key-mobile_sidebar_menu_footer"] {{
                height: auto !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: visible !important;
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

    if key == "mobile_nav_footer_to_msil":
        with st.container(key="mobile_sidebar_menu_footer"):
            _render_mobile_sidebar_button()
