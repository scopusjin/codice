# -*- coding: utf-8 -*-
"""Input numerico decimale con punto e controlli integrati per Mor-tem."""

import html
import math
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from app.decimal_number_input_v2 import (
    is_full_mobile_v2_key,
    mobile_decimal_v2_available,
    render_mobile_decimal_v2,
)
from app.locales.it_ui import ui_text


_FRONTEND_DIR = (Path(__file__).resolve().parent / "decimal_number_input_frontend").absolute()
_component = components.declare_component(
    "mortem_decimal_number_input",
    path=str(_FRONTEND_DIR),
)
_FORMAT_RE = re.compile(r"^%\.(\d+)f$")
_TA_BASE_COMPONENT_KEY = "mortem_decimal_ta_base_val"
_TA_OTHER_COMPONENT_KEY = "mortem_decimal_ta_other_val"
_TA_STANDARD_HELP_OPEN_KEY = "__decimal_ta_standard_help_open"
_TA_RANGE_HELP_OPEN_KEY = "__decimal_ta_range_help_open"
_FC_STANDARD_HELP_OPEN_KEY = "__decimal_fc_standard_help_open"
_FC_RANGE_HELP_OPEN_KEY = "__decimal_fc_range_help_open"
_TA_RANGE_MOBILE_NOTE = (
    "Inserisci il valore minimo e massimo plausibili della temperatura ambientale media "
    "nel periodo tra il decesso e l’ispezione."
)
_FC_RANGE_NOTE = (
    "Inserisci i due estremi plausibili del fattore di correzione. "
    "«Consiglia» aiuta a individuare i valori in base alle condizioni del corpo."
)
_FC_STANDARD_NOTE = (
    "«Consiglia» aiuta a individuare il fattore di correzione in base alle condizioni del corpo, "
    "agli indumenti o alle coperture, alla superficie di appoggio e alle condizioni ambientali."
)
_COMPACT_LABEL_ALIASES = {
    "Piumone / coperta molto spessa": "Piumone / coperta pesante",
}

_TA_NATIVE_POPOVER_CSS = r"""
<style data-mortem-ta-popover-style>
[data-testid="stElementContainer"]:has(style[data-mortem-ta-popover-style]) {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

@media (max-width: 768px) {
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stVerticalBlock"]:has(> [data-testid="stLayoutWrapper"] > [class~="st-key-ta_native_help_standard"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stVerticalBlock"]:has(> [data-testid="stLayoutWrapper"] > [class~="st-key-ta_native_help_range"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stVerticalBlock"]:has(> [data-testid="stLayoutWrapper"] > [class~="st-key-ta_native_help_fc_standard"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stVerticalBlock"]:has(> [data-testid="stLayoutWrapper"] > [class~="st-key-ta_native_help_fc_range"]) {
  position: relative !important;
  overflow: visible !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stLayoutWrapper"]:has(> [class~="st-key-ta_native_help_standard"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stLayoutWrapper"]:has(> [class~="st-key-ta_native_help_range"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stLayoutWrapper"]:has(> [class~="st-key-ta_native_help_fc_standard"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stLayoutWrapper"]:has(> [class~="st-key-ta_native_help_fc_range"]) {
  box-sizing: border-box !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: max-content !important;
  min-width: 0 !important;
  height: 40px !important;
  min-height: 40px !important;
  max-height: 40px !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
  z-index: 30 !important;
  pointer-events: none !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class~="st-key-ta_native_help_standard"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class~="st-key-ta_native_help_range"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class~="st-key-ta_native_help_fc_standard"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class~="st-key-ta_native_help_fc_range"] {
  box-sizing: border-box !important;
  position: static !important;
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 2px !important;
  width: max-content !important;
  min-width: 0 !important;
  height: 40px !important;
  min-height: 40px !important;
  max-height: 40px !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
  pointer-events: none !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-ta_native_help_label_"] {
  flex: 0 0 auto !important;
  width: max-content !important;
  min-width: max-content !important;
  margin: 0 !important;
  padding: 0 !important;
  pointer-events: none !important;
}

.mortem-ta-help-label-spacer {
  box-sizing: border-box;
  display: inline-block;
  visibility: hidden;
  padding: 0 0 0 8px;
  margin: 0;
  white-space: nowrap;
  font-family: var(--st-font, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
  font-size: 0.82rem;
  font-weight: 400;
  line-height: 1.1;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-ta_native_help_button_"] {
  flex: 0 0 18px !important;
  width: 18px !important;
  min-width: 18px !important;
  max-width: 18px !important;
  height: 18px !important;
  min-height: 18px !important;
  max-height: 18px !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
  pointer-events: auto !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-ta_native_help_button_"] [data-testid="stPopover"] {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 18px !important;
  min-width: 18px !important;
  max-width: 18px !important;
  height: 18px !important;
  min-height: 18px !important;
  max-height: 18px !important;
  margin: 0 !important;
  padding: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-ta_native_help_button_"] button {
  box-sizing: border-box !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 18px !important;
  min-width: 18px !important;
  max-width: 18px !important;
  height: 18px !important;
  min-height: 18px !important;
  max-height: 18px !important;
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 50% !important;
  line-height: 1 !important;
  pointer-events: auto !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-ta_native_help_button_"] button [data-testid="stIconMaterial"] {
  display: none !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-ta_native_help_button_"] button p {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  font-size: 0.72rem !important;
  line-height: 1 !important;
}
}
</style>
"""


def _theme_value(option, fallback):
    try:
        value = st.get_option(option)
    except Exception:
        value = None
    return value or fallback


def _decimal_places(fmt: str, step) -> int:
    match = _FORMAT_RE.fullmatch(str(fmt or ""))
    if match:
        return max(0, min(8, int(match.group(1))))
    try:
        text = f"{abs(float(step)):.8f}".rstrip("0").rstrip(".")
        return len(text.split(".", 1)[1]) if "." in text else 0
    except Exception:
        return 2


def _finite_float(value):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _render_ta_native_popover(label_text: str, help_text: str, key: str) -> None:
    st.markdown(_TA_NATIVE_POPOVER_CSS, unsafe_allow_html=True)
    with st.container(
        horizontal=True,
        wrap=False,
        vertical_alignment="center",
        gap="xsmall",
        key=f"ta_native_help_{key}",
    ):
        with st.container(width="content", key=f"ta_native_help_label_{key}"):
            st.markdown(
                f"<span class='mortem-ta-help-label-spacer'>{html.escape(str(label_text or ''))}</span>",
                unsafe_allow_html=True,
            )
        with st.container(width="content", key=f"ta_native_help_button_{key}"):
            with st.popover(
                "?",
                key=f"ta_native_help_popover_{key}",
                on_change="ignore",
                width="content",
            ):
                st.caption(help_text)


def decimal_number_input(
    value=None,
    *,
    step=1.0,
    format="%g",
    min_value=None,
    max_value=None,
    disabled=False,
    sync_token=0,
    aria_label="Valore numerico",
    compact_mobile=False,
    compact_label="",
    unit="",
    hide_group_heading=False,
    inline_weight_toggle=False,
    suggest_enabled=False,
    suggest_label="",
    suggest_active=False,
    on_suggest=None,
    on_change=None,
    key=None,
):
    """Restituisce float/None usando un controllo decimale non localizzato."""
    decimals = _decimal_places(format, step)
    current = _finite_float(value)
    minimum = _finite_float(min_value)
    maximum = _finite_float(max_value)

    compact_mobile = bool(compact_mobile)
    compact_label = _COMPACT_LABEL_ALIASES.get(str(compact_label or ""), str(compact_label or ""))

    prudent_mode = bool(st.session_state.get("stima_cautelativa_beta", False))
    interval_mode = bool(
        prudent_mode
        and st.session_state.get("range_unico_beta", False)
    )
    is_ta_base = key == _TA_BASE_COMPONENT_KEY
    is_ta_other = key == _TA_OTHER_COMPONENT_KEY

    help_state_key = None
    help_text = ""
    inline_range_help = False
    if prudent_mode and compact_label == "T. ambientale":
        help_state_key = _TA_RANGE_HELP_OPEN_KEY
        help_text = _TA_RANGE_MOBILE_NOTE
        inline_range_help = True
    elif prudent_mode and compact_label == "Range FC":
        help_state_key = _FC_RANGE_HELP_OPEN_KEY
        help_text = _FC_RANGE_NOTE
        inline_range_help = True
    elif is_ta_base and not interval_mode:
        help_state_key = _TA_STANDARD_HELP_OPEN_KEY
        help_text = ui_text("full.ta_mean_help")
    elif is_ta_other and interval_mode:
        help_state_key = _TA_RANGE_HELP_OPEN_KEY
        help_text = _TA_RANGE_MOBILE_NOTE
    elif key == "mortem_decimal_fattore_correzione" and not prudent_mode:
        help_state_key = _FC_STANDARD_HELP_OPEN_KEY
        help_text = _FC_STANDARD_NOTE
    elif key == "mortem_decimal_fc_other_val" and prudent_mode:
        help_state_key = _FC_RANGE_HELP_OPEN_KEY
        help_text = _FC_RANGE_NOTE
    help_enabled = help_state_key is not None

    use_v2_mobile = bool(
        compact_mobile
        and is_full_mobile_v2_key(key)
        and mobile_decimal_v2_available()
    )
    full_mobile = bool(st.session_state.get("__full_device_mobile", False))
    native_ta_popover = bool(
        use_v2_mobile
        and full_mobile
        and help_enabled
    )
    if native_ta_popover and help_state_key:
        st.session_state[help_state_key] = False

    if use_v2_mobile:
        result = render_mobile_decimal_v2(
            value=current,
            step=float(step),
            decimals=decimals,
            min_value=minimum,
            max_value=maximum,
            disabled=bool(disabled),
            sync_token=int(sync_token),
            aria_label=str(aria_label or "Valore numerico"),
            compact_label=str(compact_label or ""),
            unit=str(unit or ""),
            help_enabled=bool(help_enabled and not native_ta_popover),
            help_state_key=help_state_key,
            suggest_enabled=bool(suggest_enabled),
            suggest_label=str(suggest_label or ""),
            suggest_active=bool(suggest_active),
            on_suggest=on_suggest,
            on_change=on_change,
            key=key,
        )
        if native_ta_popover:
            if help_state_key == _FC_STANDARD_HELP_OPEN_KEY:
                native_key = "fc_standard"
            elif help_state_key == _FC_RANGE_HELP_OPEN_KEY:
                native_key = "fc_range"
            elif help_state_key == _TA_RANGE_HELP_OPEN_KEY:
                native_key = "range"
            else:
                native_key = "standard"
            _render_ta_native_popover(compact_label, help_text, native_key)
    else:
        result = _component(
            value=current,
            step=float(step),
            decimals=decimals,
            min_value=minimum,
            max_value=maximum,
            disabled=bool(disabled),
            sync_token=int(sync_token),
            aria_label=str(aria_label or "Valore numerico"),
            compact_mobile=compact_mobile,
            compact_label=str(compact_label or ""),
            unit=str(unit or ""),
            help_enabled=help_enabled,
            hide_group_heading=bool(hide_group_heading),
            inline_weight_toggle=bool(inline_weight_toggle),
            suggest_enabled=bool(suggest_enabled),
            suggest_label=str(suggest_label or ""),
            suggest_active=bool(suggest_active),
            primary_color=_theme_value("theme.primaryColor", "#168AC1"),
            background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),
            text_color=_theme_value("theme.textColor", "#31333F"),
            key=key,
            on_change=on_change,
            default=current,
        )

    if isinstance(result, dict):
        suggest_token = result.get("suggest_token")
        if suggest_token is not None and callable(on_suggest):
            event_key = f"__decimal_suggest_event_{key or aria_label}"
            if st.session_state.get(event_key) != suggest_token:
                st.session_state[event_key] = suggest_token
                on_suggest()

        help_token = result.get("help_token")
        if help_token is not None and help_enabled and not native_ta_popover:
            event_key = f"__decimal_help_event_{key or aria_label}"
            if st.session_state.get(event_key) != help_token:
                st.session_state[event_key] = help_token
                st.session_state[help_state_key] = not bool(
                    st.session_state.get(help_state_key, False)
                )

        result = result.get("value", current)

    if result is None:
        parsed_result = None
    else:
        parsed_result = _finite_float(result)
        if parsed_result is None:
            parsed_result = current
        if parsed_result is not None and minimum is not None:
            parsed_result = max(minimum, parsed_result)
        if parsed_result is not None and maximum is not None:
            parsed_result = min(maximum, parsed_result)
        if parsed_result is not None:
            parsed_result = round(parsed_result, decimals)

    if help_enabled and not native_ta_popover and st.session_state.get(help_state_key, False):
        if help_state_key in {_FC_STANDARD_HELP_OPEN_KEY, _FC_RANGE_HELP_OPEN_KEY}:
            note_key = "fc_range_help_note"
        elif inline_range_help or interval_mode:
            note_key = "ta_range_help_note"
        else:
            note_key = "ta_standard_help_note"
        with st.container(key=note_key):
            st.caption(help_text)

    return parsed_result
