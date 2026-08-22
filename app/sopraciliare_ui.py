# -*- coding: utf-8 -*-
"""UI cliccabile per l'eccitabilità elettrica sopraciliare.

La logica è volutamente isolata: intercetta soltanto il selectbox della
sopraciliare e lascia invariati tutti gli altri widget.
"""

import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates


_LABEL = "Eccitabilità elettrica sopraciliare"
_IMAGE_PATH = "immagini/eccitabilità.PNG"
_DISPLAY_WIDTH = 400
_DISPLAY_HEIGHT = _DISPLAY_WIDTH * 690 / 921
_PHASES = (
    "Fase I", "Fase II", "Fase III",
    "Fase IV", "Fase V", "Fase VI",
)


def _phase_from_click(click):
    """Converte le coordinate del clic nella fase del pannello 3 x 2."""
    if not click:
        return None

    try:
        x = float(click["x"])
        y = float(click["y"])
    except (KeyError, TypeError, ValueError):
        return None

    if x < 0 or y < 0 or x > _DISPLAY_WIDTH or y > _DISPLAY_HEIGHT:
        return None

    col = min(2, int(x / (_DISPLAY_WIDTH / 3)))
    row = min(1, int(y / (_DISPLAY_HEIGHT / 2)))
    return _PHASES[row * 3 + col]


def install_sopraciliare_click_selector():
    """Aggiunge la selezione mediante clic senza alterare gli altri selectbox."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    original_selectbox = st.selectbox

    def selectbox_with_sopraciliare(label, options, *args, **kwargs):
        if label == _LABEL:
            widget_key = kwargs.get("key")

            click = streamlit_image_coordinates(
                _IMAGE_PATH,
                width=_DISPLAY_WIDTH,
                cursor="pointer",
                key="eccitabilita_sopraciliare_click",
            )

            if click:
                # Il componente conserva l'ultimo clic ai rerun: ogni evento viene elaborato una sola volta.
                click_id = click.get("unix_time")
                if click_id is None:
                    click_id = (click.get("x"), click.get("y"))

                last_click = st.session_state.get("_eccitabilita_sopraciliare_last_click")
                if click_id != last_click:
                    phase = _phase_from_click(click)
                    st.session_state["_eccitabilita_sopraciliare_last_click"] = click_id
                    if widget_key and phase in options:
                        st.session_state[widget_key] = phase
                        # Feedback immediato nello stesso rerun naturale generato dal clic.
                        st.toast(f"✓ {phase} selezionata")

            selected_phase = st.session_state.get(widget_key) if widget_key else None
            if selected_phase in _PHASES:
                st.caption(f"✓ {selected_phase} selezionata")

        return original_selectbox(label, options, *args, **kwargs)

    st.selectbox = selectbox_with_sopraciliare
    st._sopraciliare_click_selector_installed = True
