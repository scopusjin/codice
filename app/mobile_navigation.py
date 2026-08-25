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
                display: block !important;
                width: max-content !important;
                max-width: 100% !important;
                margin: 0.55rem 0 0.10rem auto !important;
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
        }}
        </style>
        <span class="mortem-mobile-nav-style"></span>
        """,
        unsafe_allow_html=True,
    )

    with st.container(width="content", key=key):
        if st.button(label, key=f"{key}_button"):
            if key == "mobile_nav_footer_to_msil":
                _save_full_navigation_state()
            elif key == "mobile_nav_footer_to_full":
                _restore_full_navigation_state()
            st.switch_page(target)
