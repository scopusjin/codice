# -*- coding: utf-8 -*-
"""UI cliccabile per l'eccitabilità elettrica sopraciliare.

La logica è volutamente isolata: intercetta soltanto il selectbox della
sopraciliare e lascia invariati tutti gli altri widget.
"""

from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates


_LABEL = "Eccitabilità elettrica sopraciliare"
_IMAGE_PATH = Path("immagini/eccitabilità.PNG")
_DISPLAY_WIDTH = 400
_PHASES = (
    "Fase I", "Fase II", "Fase III",
    "Fase IV", "Fase V", "Fase VI",
)


def _phase_from_click(click, display_height: float):
    """Converte le coordinate del clic nella fase del pannello 3 x 2."""
    if not click:
        return None

    try:
        x = float(click["x"])
        y = float(click["y"])
    except (KeyError, TypeError, ValueError):
        return None

    if x < 0 or y < 0 or x > _DISPLAY_WIDTH or y > display_height:
        return None

    col = min(2, int(x / (_DISPLAY_WIDTH / 3)))
    row = min(1, int(y / (display_height / 2)))
    return _PHASES[row * 3 + col]


def _image_with_selection(selected_phase: str | None):
    """Restituisce l'immagine originale con una cornice sulla fase selezionata."""
    image = Image.open(_IMAGE_PATH).convert("RGBA")

    if selected_phase not in _PHASES:
        return image

    index = _PHASES.index(selected_phase)
    row, col = divmod(index, 3)
    width, height = image.size
    cell_w = width / 3
    cell_h = height / 2

    left = int(col * cell_w) + 4
    top = int(row * cell_h) + 4
    right = int((col + 1) * cell_w) - 4
    bottom = int((row + 1) * cell_h) - 4

    draw = ImageDraw.Draw(image, "RGBA")
    # Cornice marcata + velo leggero: feedback evidente senza coprire il disegno.
    draw.rectangle((left, top, right, bottom), fill=(33, 150, 243, 24))
    for inset in range(7):
        draw.rectangle(
            (left + inset, top + inset, right - inset, bottom - inset),
            outline=(33, 150, 243, 230),
        )

    return image


def install_sopraciliare_click_selector():
    """Aggiunge la selezione mediante clic senza alterare gli altri selectbox."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    original_selectbox = st.selectbox

    def selectbox_with_sopraciliare(label, options, *args, **kwargs):
        if label == _LABEL:
            widget_key = kwargs.get("key")
            selected_phase = st.session_state.get(widget_key) if widget_key else None
            image = _image_with_selection(selected_phase)
            display_height = _DISPLAY_WIDTH * image.height / image.width

            click = streamlit_image_coordinates(
                image,
                width=_DISPLAY_WIDTH,
                cursor="pointer",
                key="eccitabilita_sopraciliare_click",
            )

            if selected_phase in _PHASES:
                st.caption(f"✓ {selected_phase} selezionata")

            if click:
                # Il componente conserva l'ultimo clic ai rerun: ogni evento viene elaborato una sola volta.
                click_id = click.get("unix_time")
                if click_id is None:
                    click_id = (click.get("x"), click.get("y"))

                last_click = st.session_state.get("_eccitabilita_sopraciliare_last_click")
                if click_id != last_click:
                    phase = _phase_from_click(click, display_height)
                    st.session_state["_eccitabilita_sopraciliare_last_click"] = click_id
                    if widget_key and phase in options and st.session_state.get(widget_key) != phase:
                        st.session_state[widget_key] = phase
                        # Rerun immediato per mostrare subito cornice e conferma del clic.
                        st.rerun()

        return original_selectbox(label, options, *args, **kwargs)

    st.selectbox = selectbox_with_sopraciliare
    st._sopraciliare_click_selector_installed = True
