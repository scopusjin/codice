"""Independent ambient-temperature input mode; calculation bounds stay explicit."""

from app.cooling_inputs import finite_number
from app.fc_scenarios import scenario_temperature_bounds

MODE_KEY = "ambient_temperature_range"


def set_temperature_mode(state):
    from app.fc_input_mode import initialize_fc_mode
    initialize_fc_mode(state)
    if state[MODE_KEY]:
        if not state.get("stima_cautelativa_beta", False):
            fc = state.get("fattore_correzione")
            for key in ("fc_min_val", "fc_other_val", "FC_min_beta", "FC_max_beta"):
                state[key] = fc
        if not finite_number(state.get("ta_other_val")):
            state["ta_other_val"] = state.get("ta_base_val")
        state["stima_cautelativa_beta"] = True
        state["__prudent_explicit_ranges_initialized"] = True
    state["show_results"] = False


def sync_temperature_bounds(state):
    first = state.get("ta_base_val")
    if not state[MODE_KEY]:
        state["ta_other_val"] = first
    second = state.get("ta_other_val")
    if all(finite_number(v) for v in (first, second)):
        state["Ta_min_beta"], state["Ta_max_beta"] = sorted((float(first), float(second)))
    else:
        state.pop("Ta_min_beta", None)
        state.pop("Ta_max_beta", None)


def apply_scenario_temperatures(state):
    choice = state.get("__fc_applied_choice") or {}
    bounds = scenario_temperature_bounds(choice) if choice.get("scenarios") else None
    if bounds is None:
        return False
    state[MODE_KEY] = bounds[0] != bounds[1]
    state["ta_base_val"], state["ta_other_val"] = bounds
    return True


def toggle_temperature_mode(state):
    state[MODE_KEY] = not state[MODE_KEY]
    set_temperature_mode(state)


def render_temperature_inputs(*, mobile, render_label):
    import streamlit as st
    from app import i18n

    from_scenarios = apply_scenario_temperatures(st.session_state)
    if not mobile:
        render_label("T. ambientale media", i18n.ui_text("full.ta_mean_help"), "ta_mode")
    interval = st.session_state[MODE_KEY]
    fields = [("ta_base_val", "full.ta_base_input" if interval else "full.ta_input_label")]
    if interval:
        fields.append(("ta_other_val", "full.ta_other_input"))
    # Native columns preserve the same field width as rectal/ante-mortem inputs.
    slots = [st.container() for _ in fields] if mobile else st.columns(3, gap="xsmall")
    for slot, (key, label) in zip(slots, fields):
        with slot:
            # When scenarios supplied these values, the shared numeric control
            # already opens the FC editor on click instead of accepting inline edits.
            # Do not disable that click target.
            st.number_input(i18n.ui_text(label), value=st.session_state.get(key),
                            step=0.1, format="%.1f", key=key, label_visibility="collapsed",
                            **({} if mobile else {"_mortem_compact_label": ""}))
    if not mobile and not (from_scenarios and interval):
        with slots[len(fields)]:
            with st.container(key="ambient_temperature_action", horizontal=True, vertical_alignment="center", height=40, border=False):
                st.button("Valore singolo?" if interval else "Range?",
                          key="ambient_temperature_range_toggle", type="tertiary", disabled=from_scenarios,
                          help="Temperature ricavate dai singoli scenari; modificale nel pannello FC." if from_scenarios else None,
                          on_click=toggle_temperature_mode, args=(st.session_state,))
    sync_temperature_bounds(st.session_state)
