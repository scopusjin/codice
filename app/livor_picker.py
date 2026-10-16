"""Scelta compatta degli stati delle ipostasi, condivisa dalle due interfacce.

Le opzioni restano tutte visibili all'interno dell'elenco aperto; il valore
selezionato usa le chiavi UI esistenti per i casi salvati e il motore.
"""

_STYLE = """
<style>
/* Come la tendina Appoggio dell'helper FC: testo compatto da 13 px.
   Il popover e la radio nativi gestiscono apertura e selezione. */
[class*="st-key-livor_picker_"] [data-testid="stPopoverButton"] p,
[class*="st-key-livor_picker_"] button p {
    font-size: 13px !important;
    line-height: 1.2 !important;
    font-weight: 400 !important;
    white-space: normal !important;
    text-align: left !important;
}
[class*="st-key-livor_options_"] [role="radiogroup"] {
    gap: 0.12rem !important;
}
[class*="st-key-livor_options_"] [role="radiogroup"] > label {
    min-height: 23px;
    margin: 0 !important;
    padding: 0.1rem 0.2rem !important;
}
[class*="st-key-livor_options_"] [role="radiogroup"] > label p {
    font-size: 13px !important;
    line-height: 1.2 !important;
}
</style>
"""


def render_livor_picker(options, *, state_key, picker_key, default_label=None):
    """Popover compatto con tutte le risposte e la chiave di selezione storica.

    La scelta si scrive soltanto nel widget originale; nessuna nuova copia
    indipendente dello stato tanatologico viene introdotta.
    """
    import streamlit as st

    choices = tuple(options)
    if not choices:
        raise ValueError("Nessuna opzione delle ipostasi.")

    selected = st.session_state.get(state_key)
    if selected not in choices:
        selected = default_label if default_label in choices else choices[0]
        st.session_state[state_key] = selected

    st.html(_STYLE)
    with st.popover(selected, key=picker_key, width="stretch"):
        with st.container(key="livor_options_" + picker_key, gap="xsmall"):
            selected = st.radio(
                "Macchie ipostatiche",
                options=choices,
                key=state_key,
                label_visibility="collapsed",
            )
    return selected
