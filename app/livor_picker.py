"""Menu nativo compatto per le ipostasi, condiviso da Full e sopralluogo.

La selezione usa sempre le chiavi logiche preesistenti; il componente HTML
visualizza un <select> nativo, come quello per la superficie di appoggio FC.
"""

from pathlib import Path

import streamlit.components.v1 as components


_FRONTEND = (Path(__file__).resolve().parent / "livor_picker_frontend").absolute()
_native_select = components.declare_component(
    "mortem_livor_native_select",
    path=str(_FRONTEND),
)


def render_livor_picker(options, *, state_key, picker_key, default_label=None, aria_label="Macchie ipostatiche"):
    """Menu browser sovrapposto alla pagina senza espandere il contenitore.

    La sorgente di verità resta st.session_state[state_key], così i casi
    salvati, il motore e gli ID delle ipostasi restano compatibili.
    """
    import streamlit as st

    choices = tuple(options)
    if not choices:
        raise ValueError("Nessuna opzione delle ipostasi.")

    selected = st.session_state.get(state_key)
    if selected not in choices:
        selected = default_label if default_label in choices else choices[0]

    # Un caso JSON appena importato deve avere un nuovo stato del componente,
    # senza riproporre la scelta del caso precedente durante il primo render.
    case_instance = st.session_state.get("__case_ui_id", "")
    component_key = f"{picker_key}_{case_instance}" if case_instance else picker_key
    dark = str(st.get_option("theme.base") or "light").lower() == "dark"
    from app.presentation_translation import translate
    from_browser = _native_select(
        options=list(choices),
        labels={value: translate(value) for value in choices},
        value=selected,
        dark=dark,
        aria_label=translate(aria_label),
        key=component_key,
        default=selected,
    )
    if from_browser in choices:
        selected = from_browser
    st.session_state[state_key] = selected
    return selected
