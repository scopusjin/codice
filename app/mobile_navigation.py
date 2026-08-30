# -*- coding: utf-8 -*-
"""Navigazione mobile tra versione completa e modalità sopralluogo."""

import streamlit as st
import streamlit.components.v1 as components


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
    """Mostra in fondo alla pagina un pulsante mobile che apre la sidebar."""
    components.html(
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

            const isMobile = window.parent.matchMedia("(max-width: 768px)").matches;
            if (!isMobile) {
              frame.style.display = "none";
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
              const doc = window.parent.document;
              const target =
                doc.querySelector('[data-testid="stExpandSidebarButton"] button') ||
                doc.querySelector('button[data-testid="stExpandSidebarButton"]') ||
                doc.querySelector('[data-testid="stExpandSidebarButton"]');

              if (target) target.click();
            });
          })();
        </script>
        """,
        height=38,
        width=105,
        scrolling=False,
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

            /* Full mobile: nasconde la toolbar Streamlit; l'apertura della
               sidebar è affidata al pulsante mobile in fondo alla pagina. */
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stToolbar"] {{
                display: none !important;
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
        _render_mobile_sidebar_button()
