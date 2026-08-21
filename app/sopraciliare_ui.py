# -*- coding: utf-8 -*-
"""UI cliccabile per l'eccitabilità elettrica sopraciliare.

La logica è volutamente isolata: intercetta soltanto il selectbox con l'etichetta
"Eccitabilità elettrica sopraciliare" e lascia invariati tutti gli altri widget.
"""

import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates


_LABEL = "Eccitabilità elettrica sopraciliare"
_IMAGE_PATH = "immagini/eccitabilità.PNG"
_IMAGE_WIDTH = 400
_IMAGE_HEIGHT = _IMAGE_WIDTH * 690 / 921
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

    if x < 0 or y < 0 or x > _IMAGE_WIDTH or y > _IMAGE_HEIGHT:
        return None

    col = min(2, int(x / (_IMAGE_WIDTH / 3)))
    row = min(1, int(y / (_IMAGE_HEIGHT / 2)))
    return _PHASES[row * 3 + col]


def install_sopraciliare_click_selector():
    """Aggiunge la selezione mediante clic senza alterare gli altri selectbox."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    original_selectbox = st.selectbox

    def selectbox_with_sopraciliare(label, options, *args, **kwargs):
        if label == _LABEL:
            click = streamlit_image_coordinates(
                _IMAGE_PATH,
                width=_IMAGE_WIDTH,
                cursor="pointer",
                key="eccitabilita_sopraciliare_click",
            )

            if click:
                # Il componente mantiene l'ultimo clic ai rerun: elaboriamo ogni evento una sola volta.
                click_id = click.get("unix_time")
                if click_id is None:
                    click_id = (click.get("x"), click.get("y"))

                last_click = st.session_state.get("_eccitabilita_sopraciliare_last_click")
                if click_id != last_click:
                    phase = _phase_from_click(click)
                    widget_key = kwargs.get("key")
                    if widget_key and phase in options:
                        st.session_state[widget_key] = phase
                    st.session_state["_eccitabilita_sopraciliare_last_click"] = click_id

        return original_selectbox(label, options, *args, **kwargs)

    st.selectbox = selectbox_with_sopraciliare
    st._sopraciliare_click_selector_installed = True
