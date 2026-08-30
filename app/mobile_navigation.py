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

            /* Full mobile: mantiene il controllo nativo della sidebar ma
               nasconde gli altri elementi della toolbar Streamlit. */
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stToolbar"] {{
                display: block !important;
                position: static !important;
                width: 0 !important;
                min-width: 0 !important;
                max-width: 0 !important;
                height: 0 !important;
                min-height: 0 !important;
                max-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: visible !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            [data-testid="stToolbar"] > *:not([data-testid="stSidebarCollapsedControl"]):not([data-testid="collapsedControl"]):not(:has([data-testid="stSidebarCollapsedControl"])):not(:has([data-testid="collapsedControl"])) {{
                display: none !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            :is([data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"]) {{
                display: flex !important;
                position: fixed !important;
                top: auto !important;
                right: auto !important;
                bottom: 0.70rem !important;
                left: 0.70rem !important;
                z-index: 1000000 !important;
                visibility: visible !important;
                opacity: 1 !important;
                width: 2.15rem !important;
                min-width: 2.15rem !important;
                height: 2.15rem !important;
                min-height: 2.15rem !important;
                align-items: center !important;
                justify-content: center !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            :is([data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"]) button {{
                display: flex !important;
                width: 2.15rem !important;
                min-width: 2.15rem !important;
                height: 2.15rem !important;
                min-height: 2.15rem !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 0 !important;
                border: 1px solid var(--primary-color, #2196F3) !important;
                border-radius: 8px !important;
                background: var(--background-color, #FFFFFF) !important;
                color: var(--primary-color, #2196F3) !important;
                box-shadow: 0 1px 4px rgba(0,0,0,.12) !important;
            }}
            body:has([class*="st-key-stima_cautelativa_beta"])
            header[data-testid="stHeader"] {{
                min-height: 2.35rem !important;
                height: 2.35rem !important;
                background: transparent !important;
                overflow: visible !important;
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
