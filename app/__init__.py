# -*- coding: utf-8 -*-

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import app.perioral_single_grid as _perioral_single_grid
import app.sopraciliare_ui as _sopraciliare_ui
from app.decimal_number_input import decimal_number_input
from app.device_mode import full_device_is_mobile
from app.full_mobile_layout import install_full_mobile_layout
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
_number_input_original = st.number_input
_dg_number_input_original = DeltaGenerator.number_input
_toggle_original = st.toggle


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
            return "Fattore di correzione minimo"
        if key == "fc_other_val":
            return "Fattore di correzione massimo"
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


def _number_input_with_decimal_point(label, *args, **kwargs):
    key = kwargs.get("key")
    if key in _decimal_keys:
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
            and bool(str(label).strip())
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

        result = decimal_number_input(
            value=logical_value,
            step=kwargs.get("step", 1.0),
            format=kwargs.get("format", "%g"),
            min_value=kwargs.get("min_value"),
            max_value=kwargs.get("max_value"),
            disabled=kwargs.get("disabled", False),
            sync_token=st.session_state[sync_key],
            aria_label=label or key,
            compact_mobile=compact_mobile,
            compact_label=_compact_mobile_label(label, key) if compact_mobile else "",
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


# La tavola peribuccale originale lascia più bianco sotto i disegni rispetto
# alla sopraciliare. Manteniamo però bocca e mento integralmente visibili.
_perioral_single_grid._IMAGE_ONLY_FRACTION = 0.82

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
