# -*- coding: utf-8 -*-
"""UI cliccabile per l'eccitabilità elettrica sopraciliare.

La logica è volutamente isolata: intercetta soltanto il selectbox della
sopraciliare e lascia invariati tutti gli altri widget.
"""

import base64
import inspect
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

from app.special_tanatology_states import PARAM_ELECTRICAL_SUPRACILIARY


_LABEL = "Eccitabilità elettrica sopraciliare"
_DATA_DIR = Path(__file__).resolve().parent
_IMAGE_B64 = "".join(
    (_DATA_DIR / filename).read_text(encoding="ascii").strip()
    for filename in ("_sopraciliare_img_1.b64", "_sopraciliare_img_2.b64")
)
_IMAGE = Image.open(BytesIO(base64.b64decode(_IMAGE_B64))).convert("RGB")

# Ordine visivo della tavola 2 colonne x 4 righe:
# VI-V / IV-III / II-I / Nessuna reazione-Non valutabile.
_GRID_OPTIONS = (
    "Fase VI", "Fase V",
    "Fase IV", "Fase III",
    "Fase II", "Fase I",
    "Nessuna reazione", "Non valutabile/non attendibile",
)


class _SuppressedSopraciliaryPopover:
    """Contesto vuoto usato per eliminare il vecchio popover sopraciliare."""

    def __enter__(self):
        st._suppress_legacy_sopraciliary_image = True
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        st._suppress_legacy_sopraciliary_image = False
        return False


def _option_from_click(click):
    """Converte il clic nel riquadro corrispondente della griglia 2 x 4."""
    if not click:
        return None

    try:
        x = float(click["x"])
        y = float(click["y"])
        width = float(click["width"])
        height = float(click["height"])
    except (KeyError, TypeError, ValueError):
        return None

    if width <= 0 or height <= 0 or x < 0 or y < 0 or x > width or y > height:
        return None

    col = min(1, int(x / (width / 2)))
    row = min(3, int(y / (height / 4)))
    return _GRID_OPTIONS[row * 2 + col]


def install_sopraciliare_click_selector():
    """Aggiunge la selezione mediante clic senza alterare gli altri selectbox."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    original_selectbox = st.selectbox
    original_popover = st.popover
    original_image = st.image

    def popover_without_legacy_sopraciliare(*args, **kwargs):
        caller = inspect.currentframe().f_back
        if caller and caller.f_locals.get("parametro_id") == PARAM_ELECTRICAL_SUPRACILIARY:
            return _SuppressedSopraciliaryPopover()
        return original_popover(*args, **kwargs)

    def image_without_legacy_sopraciliare(image, *args, **kwargs):
        if getattr(st, "_suppress_legacy_sopraciliary_image", False):
            return None
        return original_image(image, *args, **kwargs)

    def selectbox_with_sopraciliare(label, options, *args, **kwargs):
        if label == _LABEL:
            widget_key = kwargs.get("key")

            click = streamlit_image_coordinates(
                _IMAGE,
                use_column_width="always",
                cursor="pointer",
                key="eccitabilita_sopraciliare_click",
            )

            if click:
                click_id = click.get("unix_time")
                if click_id is None:
                    click_id = (click.get("x"), click.get("y"))

                last_click = st.session_state.get("_eccitabilita_sopraciliare_last_click")
                if click_id != last_click:
                    selected = _option_from_click(click)
                    st.session_state["_eccitabilita_sopraciliare_last_click"] = click_id
                    if widget_key and selected in options:
                        st.session_state[widget_key] = selected
                        st.toast(f"✓ {selected}")

            selected = st.session_state.get(widget_key) if widget_key else None
            if selected in _GRID_OPTIONS:
                st.caption(f"✓ Selezione: {selected}")

        return original_selectbox(label, options, *args, **kwargs)

    st.popover = popover_without_legacy_sopraciliare
    st.image = image_without_legacy_sopraciliare
    st.selectbox = selectbox_with_sopraciliare
    st._sopraciliare_click_selector_installed = True
