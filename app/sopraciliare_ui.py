# -*- coding: utf-8 -*-
"""UI cliccabile per l'eccitabilità elettrica sopraciliare e peribuccale.

La logica è volutamente isolata: intercetta soltanto i due selectbox
dell'eccitabilità elettrica e lascia invariati tutti gli altri widget.
"""

import base64
import inspect
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

from app.special_tanatology_states import (
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
)


_SUPRA_LABEL = "Eccitabilità elettrica sopraciliare"
_PERIORAL_LABEL = "Eccitabilità elettrica peribuccale"
_DATA_DIR = Path(__file__).resolve().parent


def _load_embedded_image(filenames):
    image_b64 = "".join(
        (_DATA_DIR / filename).read_text(encoding="ascii").strip()
        for filename in filenames
    )
    return Image.open(BytesIO(base64.b64decode(image_b64))).convert("RGB")


_SUPRA_IMAGE = _load_embedded_image(
    (
        "_sopraciliare_img_1.b64",
        "_sopraciliare_img_2.b64",
        "_sopraciliare_img_3.b64",
        "_sopraciliare_img_4.b64",
    )
)

_PERIORAL_IMAGE = _load_embedded_image(
    (
        "_peribuccale_img_1.b64",
        "_peribuccale_img_2.b64",
        "_peribuccale_img_3.b64",
        "_peribuccale_img_4.b64",
    )
)

# Ordine visivo della tavola sopraciliare 2 colonne x 4 righe:
# VI-V / IV-III / II-I / Nessuna reazione-Non valutabile.
_SUPRA_GRID_OPTIONS = (
    "Fase VI", "Fase V",
    "Fase IV", "Fase III",
    "Fase II", "Fase I",
    "Nessuna reazione", "Non valutabile/non attendibile",
)

# Ordine visivo della tavola peribuccale 3 colonne x 2 righe:
# +++ / ++ / + / Nessuna reazione / Non valutabile / vuoto.
_PERIORAL_GRID_OPTIONS = (
    "Marcata ed estesa (+++)",
    "Discreta (++)",
    "Accennata (+)",
    "Nessuna reazione",
    "Non valutabile/non attendibile",
    None,
)


class _SuppressedElectricalPopover:
    """Contesto vuoto usato per eliminare i vecchi popover delle immagini."""

    def __enter__(self):
        st._suppress_legacy_electrical_image = True
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        st._suppress_legacy_electrical_image = False
        return False


def _supra_option_from_click(click):
    """Converte il clic nel riquadro sopraciliare della griglia 2 x 4."""
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
    return _SUPRA_GRID_OPTIONS[row * 2 + col]


def _perioral_option_from_click(click):
    """Converte il clic nel riquadro peribuccale della griglia 3 x 2."""
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

    col = min(2, int(x / (width / 3)))
    row = min(1, int(y / (height / 2)))
    return _PERIORAL_GRID_OPTIONS[row * 3 + col]


def _render_clickable_selector(
    *,
    image,
    component_key,
    last_click_key,
    widget_key,
    options,
    option_from_click,
):
    click = streamlit_image_coordinates(
        image,
        use_column_width="always",
        cursor="pointer",
        key=component_key,
    )

    if not click:
        return

    click_id = click.get("unix_time")
    if click_id is None:
        click_id = (click.get("x"), click.get("y"))

    last_click = st.session_state.get(last_click_key)
    if click_id == last_click:
        return

    selected = option_from_click(click)
    st.session_state[last_click_key] = click_id

    # Il riquadro volutamente vuoto della tavola peribuccale restituisce None.
    if widget_key and selected in options:
        st.session_state[widget_key] = selected
        st.toast(f"✓ {selected}")


def install_sopraciliare_click_selector():
    """Aggiunge la selezione mediante clic senza alterare gli altri selectbox."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    original_selectbox = st.selectbox
    original_popover = st.popover
    original_image = st.image

    def popover_without_legacy_electrical_images(*args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None
        if parametro_id in (PARAM_ELECTRICAL_SUPRACILIARY, PARAM_ELECTRICAL_PERIORAL):
            return _SuppressedElectricalPopover()
        return original_popover(*args, **kwargs)

    def image_without_legacy_electrical_images(image, *args, **kwargs):
        if getattr(st, "_suppress_legacy_electrical_image", False):
            return None
        return original_image(image, *args, **kwargs)

    def selectbox_with_electrical_images(label, options, *args, **kwargs):
        widget_key = kwargs.get("key")

        if label == _SUPRA_LABEL:
            _render_clickable_selector(
                image=_SUPRA_IMAGE,
                component_key="eccitabilita_sopraciliare_click",
                last_click_key="_eccitabilita_sopraciliare_last_click",
                widget_key=widget_key,
                options=options,
                option_from_click=_supra_option_from_click,
            )

        elif label == _PERIORAL_LABEL:
            _render_clickable_selector(
                image=_PERIORAL_IMAGE,
                component_key="eccitabilita_peribuccale_click",
                last_click_key="_eccitabilita_peribuccale_last_click",
                widget_key=widget_key,
                options=options,
                option_from_click=_perioral_option_from_click,
            )

        return original_selectbox(label, options, *args, **kwargs)

    st.popover = popover_without_legacy_electrical_images
    st.image = image_without_legacy_electrical_images
    st.selectbox = selectbox_with_electrical_images
    st._sopraciliare_click_selector_installed = True
