"""Independent FC input presentation; explicit bounds feed the existing solver."""
from app.cooling_inputs import finite_number

FC_MODE_KEY = "fc_input_range"


def initialize_fc_mode(state):
    if FC_MODE_KEY not in state:
        state[FC_MODE_KEY] = bool(state.get("stima_cautelativa_beta") and
                                 state.get("fc_min_val") != state.get("fc_other_val"))
    choice = state.get("__fc_applied_choice") or {}
    if choice.get("scenarios"):
        lo, hi = choice["range"]
        state[FC_MODE_KEY] = lo != hi
    return bool(choice.get("scenarios"))


def render_fc_inputs(*, mobile, render_label, normalize, help_text):
    import streamlit as st
    from app import i18n
    state = st.session_state
    initialize_fc_mode(state)
    interval = state[FC_MODE_KEY]
    if not mobile:
        render_label("Fattore di correzione (FC)", help_text, "fc_independent")
    fields = ([("fc_min_val", "full.fc_min_input"), ("fc_other_val", "full.fc_max_input")]
              if interval else [("fattore_correzione", "full.fc_input_label")])
    slots = [st.container() for _ in fields] if mobile else st.columns(3, gap="xsmall")
    for slot, (key, label) in zip(slots, fields):
        with slot:
            st.number_input(i18n.ui_text(label), value=state.get(key), step=0.05, format="%.2f",
                            key=key, on_change=normalize, args=(key,), label_visibility="collapsed",
                            **({} if mobile else {"_mortem_compact_label": ""}))
    if not interval:
        state["fc_min_val"] = state["fc_other_val"] = state.get("fattore_correzione")
    values = [state.get("fc_min_val"), state.get("fc_other_val")]
    if all(finite_number(value) for value in values):
        state["FC_min_beta"], state["FC_max_beta"] = sorted(map(float, values))
    else:
        state.pop("FC_min_beta", None)
        state.pop("FC_max_beta", None)
