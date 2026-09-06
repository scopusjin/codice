# -*- coding: utf-8 -*-
"""Carousel touch compatto per l'eccitabilità sopraciliare nella Full mobile."""

import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import ImageEnhance, ImageOps

from app.electrical_grid_geometry import neutral_electrical_tile, normalize_electrical_tile


_FRONTEND_DIR = (Path(__file__).resolve().parent / "supra_mobile_carousel_frontend").absolute()
_component = components.declare_component(
    "mortem_supra_mobile_carousel",
    path=str(_FRONTEND_DIR),
)
_IMAGE_URI_CACHE = {}
_CONTENT_THRESHOLD = 246
_HORIZONTAL_CONTENT_PAD = 10
_COLOR_INTENSITY = 2.3


def _strip_original_edges(tile):
    width, height = tile.size
    edge = 7
    if width <= edge * 2 or height <= edge * 2:
        return tile.convert("RGB")
    return tile.crop((edge, edge, width - edge, height - edge)).convert("RGB")


def _crop_horizontal_content(tile):
    """Elimina il bianco laterale superfluo lasciando un piccolo margine al disegno."""
    image = tile.convert("RGB")
    gray = ImageOps.grayscale(image)
    mask = gray.point(lambda pixel: 255 if pixel < _CONTENT_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return image

    left = max(0, bbox[0] - _HORIZONTAL_CONTENT_PAD)
    right = min(image.width, bbox[2] + _HORIZONTAL_CONTENT_PAD)
    if right <= left:
        return image
    return image.crop((left, 0, right, image.height))


def _enhance_existing_color(tile):
    """Rende più leggibili i colori già presenti senza modificare forme o tratti neri."""
    return ImageEnhance.Color(tile.convert("RGB")).enhance(_COLOR_INTENSITY)


def _image_data_uri(ui, option):
    cached = _IMAGE_URI_CACHE.get(option)
    if cached is not None:
        return cached

    if option == "Non valutata":
        tile = neutral_electrical_tile()
    else:
        tile = normalize_electrical_tile(_strip_original_edges(ui._SUPRA_TILES[option]))
        tile = _enhance_existing_color(tile)

    tile = _crop_horizontal_content(tile)

    buffer = BytesIO()
    tile.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    uri = f"data:image/png;base64,{encoded}"
    _IMAGE_URI_CACHE[option] = uri
    return uri


def _single_line_label(label):
    """Compatta l'etichetta mobile mettendo l'intervallo temporale tra parentesi."""
    parts = [part.strip() for part in str(label or "").splitlines() if part.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return f"{' '.join(parts[:-1])} ({parts[-1]})"


def _theme_value(option, fallback):
    try:
        value = st.get_option(option)
    except Exception:
        value = None
    return value or fallback


def render_supra_mobile_carousel(*, ui, options, selected, widget_key, label_for_option):
    """Renderizza una sola immagine centrale con swipe orizzontale e scroll-snap."""
    ordered_options = [option for option in ui._SUPRA_TILE_OPTIONS if option in options]
    if not ordered_options:
        return None

    if selected not in ordered_options:
        selected = ordered_options[0]

    items = [
        {
            "value": option,
            "label": _single_line_label(label_for_option(option)),
            "image": _image_data_uri(ui, option),
        }
        for option in ordered_options
    ]

    result = _component(
        items=items,
        value=selected,
        primary_color=_theme_value("theme.primaryColor", "#168AC1"),
        background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),
        text_color=_theme_value("theme.textColor", "#31333F"),
        key=f"{widget_key or 'eccitabilita_sopraciliare'}_mobile_carousel",
        default=selected,
    )

    if result not in ordered_options:
        result = selected

    st.session_state[ui._SUPRA_SELECTION_KEY] = result
    if widget_key:
        st.session_state[widget_key] = result
    return result
