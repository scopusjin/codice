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
_VERTICAL_CONTENT_PAD = 4
_COLOR_INTENSITY = 2.3
_MOBILE_REACTION_LABELS = {
    "Fase VI": "Reagiscono fronte, orbita e guancia",
    "Fase V": "Reagiscono fronte e orbita",
    "Fase IV": "Reagiscono gli orbicolari superiore e inferiore",
    "Fase III": "Reagisce: palpebra superiore intera",
    "Fase II": "Reagisce: < 2/3 palpebra superiore",
    "Fase I": "Reagisce: < 1/3 palpebra superiore",
}


def _strip_original_edges(tile):
    width, height = tile.size
    edge = 7
    if width <= edge * 2 or height <= edge * 2:
        return tile.convert("RGB")
    return tile.crop((edge, edge, width - edge, height - edge)).convert("RGB")


def _content_bbox(tile):
    image = tile.convert("RGB")
    gray = ImageOps.grayscale(image)
    mask = gray.point(lambda pixel: 255 if pixel < _CONTENT_THRESHOLD else 0)
    return image, mask.getbbox()


def _crop_horizontal_content(tile):
    """Elimina il bianco laterale superfluo lasciando un piccolo margine al disegno."""
    image, bbox = _content_bbox(tile)
    if bbox is None:
        return image

    left = max(0, bbox[0] - _HORIZONTAL_CONTENT_PAD)
    right = min(image.width, bbox[2] + _HORIZONTAL_CONTENT_PAD)
    if right <= left:
        return image
    return image.crop((left, 0, right, image.height))


def _crop_vertical_content(tile):
    """Riduce solo il bianco verticale esterno per rendere il disegno appena più grande."""
    image, bbox = _content_bbox(tile)
    if bbox is None:
        return image

    top = max(0, bbox[1] - _VERTICAL_CONTENT_PAD)
    bottom = min(image.height, bbox[3] + _VERTICAL_CONTENT_PAD)
    if bottom <= top:
        return image
    return image.crop((0, top, image.width, bottom))


def _enhance_existing_color(tile):
    """Rende più leggibili i colori già presenti senza modificare forme o tratti neri."""
    return ImageEnhance.Color(tile.convert("RGB")).enhance(_COLOR_INTENSITY)


def _image_data_uri(ui, option):
    cached = _IMAGE_URI_CACHE.get(option)
    if cached is not None:
        return cached

    if option == "Non valutata":
        tile = neutral_electrical_tile()
        tile = _crop_horizontal_content(tile)
    else:
        tile = normalize_electrical_tile(_strip_original_edges(ui._SUPRA_TILES[option]))
        tile = _enhance_existing_color(tile)
        tile = _crop_horizontal_content(tile)
        tile = _crop_vertical_content(tile)

    buffer = BytesIO()
    tile.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    uri = f"data:image/png;base64,{encoded}"
    _IMAGE_URI_CACHE[option] = uri
    return uri


def _single_line_label(option, label):
    """Compatta l'etichetta mobile e mantiene l'intervallo temporale tra parentesi."""
    parts = [part.strip() for part in str(label or "").splitlines() if part.strip()]
    if not parts:
        return ""

    interval = parts[-1] if len(parts) > 1 else ""
    reaction = _MOBILE_REACTION_LABELS.get(option)
    if reaction:
        return f"{reaction} ({interval})" if interval else reaction

    if len(parts) == 1:
        return parts[0]
    return f"{' '.join(parts[:-1])} ({interval})"


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
            "label": _single_line_label(option, label_for_option(option)),
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
