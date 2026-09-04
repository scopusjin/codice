# -*- coding: utf-8 -*-

import inspect

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import app.perioral_single_grid as _perioral_single_grid
import app.sopraciliare_ui as _sopraciliare_ui
from app.decimal_number_input import decimal_number_input
from app.device_mode import full_device_is_mobile
from app.full_mobile_layout import _render_click_help, install_full_mobile_layout
from app.locales.it_ui import ui_text
from app.special_datetime_ui import install_special_datetime_ui
from app.special_heading_ui import install_special_heading_style
from app.supra_single_grid import install_supra_single_grid


# Campi decimali delle schermate completa e MSIL: il componente dedicato
# mantiene il punto decimale e i controlli −/+ nello stesso riquadro.
_decimal_keys = {
    "rt_val",
    "tm_val",
    "peso",
    "ta_base_val",
    "ta_other_val",
    "fattore_correzione",
    "fc_min_val",
    "fc_other_val",
    "rt_val_widget",
    "ta_base_val_widget",
    "peso_widget",
    "fcpanel_std_strati_sottili",
    "fcpanel_std_strati_spessi",
    "fcpanel_std_coperte_medie",
    "fcpanel_std_coperte_pesanti",
    "fcpanel_caut_strati_sottili",
    "fcpanel_caut_strati_spessi",
    "fcpanel_caut_coperte_medie",
    "fcpanel_caut_coperte_pesanti",
}
_msil_widget_state_keys = {
    "rt_val_widget": "rt_val",
    "ta_base_val_widget": "ta_base_val",
    "peso_widget": "peso",
}
_full_mobile_units = {
    "rt_val": "°C",
    "tm_val": "°C",
    "peso": "kg",
    "ta_base_val": "°C",
    "ta_other_val": "°C",
    "fattore_correzione": "",
    "fc_min_val": "",
    "fc_other_val": "",
    "fcpanel_std_strati_sottili": "",
    "fcpanel_std_strati_spessi": "",
    "fcpanel_std_coperte_medie": "",
    "fcpanel_std_coperte_pesanti": "",
    "fcpanel_caut_strati_sottili": "",
    "fcpanel_caut_strati_spessi": "",
    "fcpanel_caut_coperte_medie": "",
    "fcpanel_caut_coperte_pesanti": "",
}
_FULL_DESKTOP_COOLING_KEYS = {
    "rt_val",
    "tm_val",
    "peso",
    "ta_base_val",
    "ta_other_val",
    "fattore_correzione",
    "fc_min_val",
    "fc_other_val",
}
_TA_RANGE_DESKTOP_HELP = (
    "Inserisci il valore minimo e massimo plausibili della temperatura ambientale media "
    "nel periodo tra il decesso e l’ispezione."
)
_FC_RANGE_DESKTOP_HELP = (
    "Inserisci i due estremi plausibili del fattore di correzione. "
    "«Consiglia» aiuta a individuare i valori in base alle condizioni del corpo."
)
_main_delta_generator = getattr(st, "_main", None)


def _native_main_widget(method_name, fallback):
    """Restituisce il widget Streamlit nativo, senza wrapper di hot reload."""
    if _main_delta_generator is None:
        return fallback
    method = getattr(DeltaGenerator, method_name, None)
    if method is None:
        return fallback
    return method.__get__(_main_delta_generator, DeltaGenerator)


_number_input_original = _native_main_widget("number_input", st.number_input)
_dg_number_input_original = DeltaGenerator.number_input
_toggle_original = _native_main_widget("toggle", st.toggle)
_columns_original = st.columns


def _called_from_full_estimate_page(max_depth=8) -> bool:
    """Limita gli override desktop alla sola Stima_epoca_decesso.py."""
    frame = inspect.currentframe()
    depth = 0
    try:
        while frame is not None and depth < max_depth:
            filename = str(getattr(getattr(frame, "f_code", None), "co_filename", ""))
            if filename.replace("\\", "/").endswith("/Stima_epoca_decesso.py"):
                return True
            frame = frame.f_back
            depth += 1
    finally:
        del frame
    return False


def _columns_with_compact_full_cooling(spec, *args, **kwargs):
    """Rende omogenee solo le due sottocolonne desktop del raffreddamento Full."""
    is_target_pair = False
    if isinstance(spec, (list, tuple)) and len(spec) == 2:
        try:
            is_target_pair = abs(float(spec[0]) - 1.35) < 1e-9 and abs(float(spec[1]) - 1.0) < 1e-9
        except (TypeError, ValueError):
            is_target_pair = False

    if (
        not full_device_is_mobile()
        and _called_from_full_estimate_page()
        and is_target_pair
        and kwargs.get("vertical_alignment") == "bottom"
    ):
        spec = [1, 1]
        kwargs["gap"] = "xsmall"
    return _columns_original(spec, *args, **kwargs)


st.columns = _columns_with_compact_full_cooling


def _sync_full_interval_mode_state():
    """Conserva separatamente valori standard e intervalli al cambio modalità."""
    interval_mode = bool(st.session_state.get("stima_cautelativa_beta", False))

    if interval_mode:
        standard_ta = st.session_state.get("ta_base_val", 20.0)
        standard_fc = st.session_state.get("fattore_correzione", 1.0)
        st.session_state["__full_standard_ta_base_val"] = standard_ta
        st.session_state["__full_standard_fattore_correzione"] = standard_fc

        if "__full_interval_ta_base_val" in st.session_state:
            st.session_state["ta_base_val"] = st.session_state["__full_interval_ta_base_val"]
            st.session_state["ta_other_val"] = st.session_state["__full_interval_ta_other_val"]
            st.session_state["fc_min_val"] = st.session_state["__full_interval_fc_min_val"]
            st.session_state["fc_other_val"] = st.session_state["__full_interval_fc_other_val"]
        else:
            st.session_state["ta_base_val"] = standard_ta
            st.session_state["ta_other_val"] = standard_ta
            st.session_state["fc_min_val"] = standard_fc
            st.session_state["fc_other_val"] = standard_fc

        st.session_state["__prudent_explicit_ranges_initialized"] = True
        return

    # Il callback scatta prima del rerun: i widget della modalità con intervalli
    # sono ancora in session_state e possono essere salvati prima che spariscano.
    if st.session_state.get("__prudent_explicit_ranges_initialized", False):
        st.session_state["__full_interval_ta_base_val"] = st.session_state.get("ta_base_val", 20.0)
        st.session_state["__full_interval_ta_other_val"] = st.session_state.get("ta_other_val", 20.0)
        st.session_state["__full_interval_fc_min_val"] = st.session_state.get("fc_min_val", 1.0)
        st.session_state["__full_interval_fc_other_val"] = st.session_state.get("fc_other_val", 1.0)

    if "__full_standard_ta_base_val" in st.session_state:
        st.session_state["ta_base_val"] = st.session_state["__full_standard_ta_base_val"]
    if "__full_standard_fattore_correzione" in st.session_state:
        st.session_state["fattore_correzione"] = st.session_state["__full_standard_fattore_correzione"]


def _toggle_with_full_interval_state(label, *args, **kwargs):
    if kwargs.get("key") != "stima_cautelativa_beta":
        return _toggle_original(label, *args, **kwargs)

    user_on_change = kwargs.get("on_change")
    callback_args = kwargs.get("args") or ()
    callback_kwargs = kwargs.get("kwargs") or {}

    def _on_change():
        _sync_full_interval_mode_state()
        if callable(user_on_change):
            user_on_change(*callback_args, **callback_kwargs)

    kwargs["on_change"] = _on_change
    kwargs.pop("args", None)
    kwargs.pop("kwargs", None)
    return _toggle_original(label, *args, **kwargs)


st.toggle = _toggle_with_full_interval_state


def _same_decimal_value(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    try:
        return abs(float(a) - float(b)) < 1e-12
    except (TypeError, ValueError):
        return a == b


def _compact_mobile_label(label, key) -> str:
    prudent_mode = bool(st.session_state.get("stima_cautelativa_beta", False))
    range_mode = bool(st.session_state.get("range_unico_beta", False))

    if not full_device_is_mobile():
        if key == "fattore_correzione":
            return "Fattore di correzione (FC)"
        if key == "fc_min_val":
            return "Fattore minimo"
        if key == "fc_other_val":
            return "Fattore massimo"
        if key == "ta_base_val":
            return "T. ambientale media 1" if prudent_mode and range_mode else "T. ambientale media"
        if key == "ta_other_val":
            return "T. ambientale media 2"
        if key == "rt_val":
            return "T. rettale"
        if key == "tm_val":
            return "T. ante-mortem stimata"
        if key == "peso":
            return "Peso"

        text = str(label or key).strip().rstrip(":")
        for suffix in (" (°C)", " (kg)"):
            if text.endswith(suffix):
                text = text[:-len(suffix)]
                break
        return text

    if key == "fattore_correzione":
        return "FC"
    if key == "fc_min_val":
        return "FC min"
    if key == "fc_other_val":
        return "FC max"
    if key == "ta_base_val":
        return "T. amb. 1" if prudent_mode and range_mode else "T. amb. media"
    if key == "ta_other_val":
        return "T. amb. 2"

    text = str(label or key).strip().rstrip(":")
    if key == "tm_val":
        text = text.replace(" stimata", "")
    for suffix in (" (°C)", " (kg)"):
        if text.endswith(suffix):
            text = text[:-len(suffix)]
            break
    return text


def _desktop_cooling_label(key, prudent_mode):
    if key == "rt_val":
        return "T. rettale", None, None
    if key == "tm_val":
        return "T. ante-mortem", None, None
    if key == "peso":
        return "Peso", None, None
    if key == "ta_base_val":
        if prudent_mode:
            return "Range temperatura ambientale media", _TA_RANGE_DESKTOP_HELP, "mortem_help_prudent_ta_range"
        return "T. ambientale media", ui_text("full.ta_mean_help"), "mortem_help_prudent_ta_standard"
    if key == "ta_other_val":
        return "", None, None
    if key == "fattore_correzione":
        return "Fattore di correzione (FC)", None, None
    if key == "fc_min_val":
        if prudent_mode:
            return "Range fattore di correzione (FC)", _FC_RANGE_DESKTOP_HELP, "mortem_help_prudent_fc_range"
        return "Fattore minimo", None, None
    if key == "fc_other_val":
        return "", None, None
    return "", None, None


def _render_desktop_cooling_label(text, help_text=None, help_key=None):
    if not text:
        return

    label_html = (
        "<div style='margin:0;padding:0;overflow:visible;white-space:nowrap;"
        "font-size:0.86rem;font-weight:400;line-height:18px;opacity:0.82;width:max-content;'>"
        f"{text}</div>"
    )
    if help_text and help_key:
        row_key = help_key.replace("mortem_help_prudent_", "desktop_label_help_row_")
        with st.container(
            horizontal=True,
            wrap=False,
            vertical_alignment="center",
            gap="xsmall",
            key=row_key,
        ):
            with st.container(width="content"):
                st.markdown(label_html, unsafe_allow_html=True)
            _render_click_help(help_text, help_key)
        return
    st.markdown(label_html, unsafe_allow_html=True)


def _number_input_with_decimal_point(label, *args, **kwargs):
    key = kwargs.get("key")
    if key in _decimal_keys:
        compact_label_override = kwargs.pop("_mortem_compact_label", None)
        if args:
            # I campi interessati nell'app usano argomenti nominati; fallback
            # prudente al widget originale se in futuro la firma cambia.
            return _number_input_original(label, *args, **kwargs)

        prudent_mode = bool(st.session_state.get("stima_cautelativa_beta", False))
        range_mode = bool(st.session_state.get("range_unico_beta", False))
        state_key = _msil_widget_state_keys.get(key, key)
        logical_value = st.session_state.get(state_key, kwargs.get("value"))
        mirror_key = f"__decimal_component_mirror_{key}"
        sync_key = f"__decimal_component_sync_{key}"
        expected_sync_key = f"__decimal_component_expected_sync_{key}"
        component_key = f"mortem_decimal_{key}"

        if mirror_key not in st.session_state:
            st.session_state[mirror_key] = logical_value
        st.session_state.setdefault(sync_key, 0)

        external_change = not _same_decimal_value(
            logical_value,
            st.session_state.get(mirror_key),
        )
        if external_change:
            st.session_state[sync_key] += 1
            st.session_state[mirror_key] = logical_value
            st.session_state[expected_sync_key] = logical_value

            active_target = st.session_state.get("__full_fc_suggest_target")
            target_key = {
                "single": "fattore_correzione",
                "min": "fc_min_val",
                "max": "fc_other_val",
            }.get(active_target)
            range_from_single = (
                active_target == "single"
                and range_mode
                and key in {"fc_min_val", "fc_other_val"}
            )
            if key == target_key or range_from_single:
                toggle_key = "toggle_fattore_inline" if prudent_mode else "toggle_fattore_inline_std"
                st.session_state[toggle_key] = False
                st.session_state["toggle_fattore"] = False
                st.session_state.pop("__full_fc_suggest_target", None)

        user_on_change = kwargs.get("on_change")
        callback_args = kwargs.get("args") or ()
        callback_kwargs = kwargs.get("kwargs") or {}

        def _component_on_change():
            incoming = st.session_state.get(component_key)
            expected_present = expected_sync_key in st.session_state
            expected_value = (
                st.session_state.pop(expected_sync_key)
                if expected_present
                else None
            )

            st.session_state[state_key] = incoming
            if state_key != key:
                st.session_state[key] = incoming
            st.session_state[mirror_key] = incoming

            # Una sincronizzazione richiesta dal codice (es. “Suggerisci FC”)
            # non deve essere trattata come modifica manuale dell'utente.
            if expected_present and _same_decimal_value(incoming, expected_value):
                return

            if callable(user_on_change):
                user_on_change(*callback_args, **callback_kwargs)

        compact_mobile = (
            key in _full_mobile_units
            and (
                bool(str(label).strip())
                or compact_label_override is not None
            )
        )
        hide_group_heading = (
            compact_mobile
            and prudent_mode
            and key in {"peso", "ta_base_val", "fattore_correzione", "fc_min_val"}
        )
        inline_weight_toggle = (
            compact_mobile
            and prudent_mode
            and key == "peso"
        )

        suggest_target = None
        if compact_mobile:
            if key == "fattore_correzione" and (not prudent_mode or not range_mode):
                suggest_target = "single"
            elif prudent_mode and range_mode and key == "fc_other_val":
                suggest_target = "range"

        suggest_toggle_key = "toggle_fattore_inline" if prudent_mode else "toggle_fattore_inline_std"
        suggest_active = bool(
            suggest_target
            and st.session_state.get(suggest_toggle_key, False)
            and st.session_state.get("__full_fc_suggest_target") == suggest_target
        )

        def _component_suggest():
            if suggest_target is None:
                return

            same_open_target = bool(
                st.session_state.get(suggest_toggle_key, False)
                and st.session_state.get("__full_fc_suggest_target") == suggest_target
            )
            if same_open_target:
                st.session_state[suggest_toggle_key] = False
                st.session_state["toggle_fattore"] = False
                st.session_state.pop("__full_fc_suggest_target", None)
                return

            st.session_state[suggest_toggle_key] = True
            st.session_state["toggle_fattore"] = True
            st.session_state["__full_fc_suggest_target"] = suggest_target

        compact_label = ""
        if compact_mobile:
            compact_label = (
                str(compact_label_override)
                if compact_label_override is not None
                else _compact_mobile_label(label, key)
            )

        desktop_cooling = bool(
            not full_device_is_mobile()
            and _called_from_full_estimate_page()
            and key in _FULL_DESKTOP_COOLING_KEYS
        )
        desktop_label = ""
        desktop_help_text = None
        desktop_help_key = None
        if desktop_cooling:
            desktop_label, desktop_help_text, desktop_help_key = _desktop_cooling_label(key, prudent_mode)
            # Sul desktop l'etichetta vive nel documento Streamlit principale:
            # il V2 resta soltanto il controllo numerico, senza iframe più alto.
            compact_label = ""

        def _render_decimal_component():
            return decimal_number_input(
                value=logical_value,
                step=kwargs.get("step", 1.0),
                format=kwargs.get("format", "%g"),
                min_value=kwargs.get("min_value"),
                max_value=kwargs.get("max_value"),
                disabled=kwargs.get("disabled", False),
                sync_token=st.session_state[sync_key],
                aria_label=label or key,
                compact_mobile=compact_mobile,
                compact_label=compact_label,
                unit=_full_mobile_units.get(key, "") if compact_mobile else "",
                hide_group_heading=hide_group_heading,
                inline_weight_toggle=inline_weight_toggle,
                suggest_enabled=bool(suggest_target),
                suggest_label="Consiglia" if suggest_target else "",
                suggest_active=suggest_active,
                on_suggest=_component_suggest if suggest_target else None,
                on_change=_component_on_change if callable(user_on_change) else None,
                key=component_key,
            )

        if desktop_cooling:
            with st.container(gap="xsmall", key=f"full_desktop_decimal_field_{key}"):
                _render_desktop_cooling_label(
                    desktop_label,
                    desktop_help_text,
                    desktop_help_key,
                )
                result = _render_decimal_component()
        else:
            result = _render_decimal_component()

        # Durante una sincronizzazione esterna il valore restituito dal
        # componente può essere quello del render precedente: in quel solo
        # passaggio prevale il valore logico appena aggiornato.
        if external_change:
            return logical_value

        st.session_state[state_key] = result
        if state_key != key:
            st.session_state[key] = result
        st.session_state[mirror_key] = result
        return result

    return _number_input_original(label, *args, **kwargs)


st.number_input = _number_input_with_decimal_point


# Il campo FC della MSIL viene creato dentro uno st.empty(), quindi passa dal
# metodo del DeltaGenerator anziché da st.number_input: intercettiamo solo
# quel caso e renderizziamo lo stesso componente nello stesso placeholder.
def _dg_number_input_with_decimal_point(self, label, *args, **kwargs):
    if kwargs.get("key") == "fattore_correzione" and not str(label).strip():
        if args:
            return _dg_number_input_original(self, label, *args, **kwargs)
        with self.container():
            return _number_input_with_decimal_point(label, *args, **kwargs)
    return _dg_number_input_original(self, label, *args, **kwargs)


DeltaGenerator.number_input = _dg_number_input_with_decimal_point


# La tavola peribuccale corrente non contiene didascalie raster: la cella viene
# letta per intero e poi normalizzata dal renderer comune.
_perioral_single_grid._IMAGE_ONLY_FRACTION = 1.0

install_supra_single_grid(_sopraciliare_ui)
_perioral_single_grid.install_perioral_single_grid(_sopraciliare_ui)
_sopraciliare_ui.install_sopraciliare_click_selector()

_electrical_selectbox = st.selectbox


def _selectbox_with_perioral_grid(label, options, *args, **kwargs):
    if label == _sopraciliare_ui._PERIORAL_LABEL:
        return _sopraciliare_ui._render_perioral_tile_grid(
            widget_key=kwargs.get("key"),
            options=list(options),
        )
    return _electrical_selectbox(label, options, *args, **kwargs)


st.selectbox = _selectbox_with_perioral_grid
install_full_mobile_layout()
install_special_heading_style()
install_special_datetime_ui()
