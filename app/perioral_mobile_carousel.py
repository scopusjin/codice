# -*- coding: utf-8 -*-
"""Carousel touch compatto per l'eccitabilità elettrica peribuccale nella Full mobile."""

import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import ImageEnhance, ImageOps

from app.electrical_grid_geometry import neutral_electrical_tile, normalize_electrical_tile


_FRONTEND_DIR = (Path(__file__).resolve().parent / "supra_mobile_carousel_frontend").absolute()
_component = components.declare_component(
    "mortem_perioral_mobile_carousel",
    path=str(_FRONTEND_DIR),
)
_IMAGE_URI_CACHE = {}
_CONTENT_THRESHOLD = 246
_HORIZONTAL_CONTENT_PAD = 10
_VERTICAL_CONTENT_PAD = 4
_COLOR_INTENSITY = 2.8
_MOBILE_REACTION_LABELS = {
    "Muscoli facciali (+++)": "Contrazione generalizzata dei muscoli facciali",
    "Muscoli peribuccali (++)": "Contrazione dei muscoli peribuccali",
    "Reazione focale (+)": "Reazione focale vicino agli elettrodi",
    "Nessuna reazione": "Nessuna contrazione muscolare",
    "Non valutabile/non attendibile": "Non valutabile / non attendibile",
    "Non valutata": "Non valutata",
}


def _content_bbox(tile):
    image = tile.convert("RGB")
    gray = ImageOps.grayscale(image)
    mask = gray.point(lambda pixel: 255 if pixel < _CONTENT_THRESHOLD else 0)
    return image, mask.getbbox()


def _crop_horizontal_content(tile):
    image, bbox = _content_bbox(tile)
    if bbox is None:
        return image

    left = max(0, bbox[0] - _HORIZONTAL_CONTENT_PAD)
    right = min(image.width, bbox[2] + _HORIZONTAL_CONTENT_PAD)
    if right <= left:
        return image
    return image.crop((left, 0, right, image.height))


def _crop_vertical_content(tile):
    image, bbox = _content_bbox(tile)
    if bbox is None:
        return image

    top = max(0, bbox[1] - _VERTICAL_CONTENT_PAD)
    bottom = min(image.height, bbox[3] + _VERTICAL_CONTENT_PAD)
    if bottom <= top:
        return image
    return image.crop((0, top, image.width, bottom))


def _enhance_existing_color(tile):
    return ImageEnhance.Color(tile.convert("RGB")).enhance(_COLOR_INTENSITY)


def _image_data_uri(option, tile):
    cached = _IMAGE_URI_CACHE.get(option)
    if cached is not None:
        return cached

    if option == "Non valutata":
        image = neutral_electrical_tile()
        image = _crop_horizontal_content(image)
    else:
        image = normalize_electrical_tile(tile)
        image = _enhance_existing_color(image)
        image = _crop_horizontal_content(image)
        image = _crop_vertical_content(image)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    uri = f"data:image/png;base64,{encoded}"
    _IMAGE_URI_CACHE[option] = uri
    return uri


def _single_line_label(option, label):
    """Usa una descrizione clinica breve, senza +, con l'intervallo tra parentesi."""
    parts = [part.strip() for part in str(label or "").splitlines() if part.strip()]
    interval = parts[-1] if len(parts) > 1 else ""
    reaction = _MOBILE_REACTION_LABELS.get(option)

    if reaction:
        return f"{reaction} ({interval})" if interval else reaction
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return f"{' '.join(parts[:-1])} ({interval})"


def _theme_value(option, fallback):
    try:
        value = st.get_option(option)
    except Exception:
        value = None
    return value or fallback


def render_perioral_mobile_carousel(
    *,
    tiles,
    ordered_options,
    options,
    selected,
    widget_key,
    label_for_option,
):
    """Renderizza una fascia circolare con swipe e selezione centrale."""
    carousel_options = [option for option in ordered_options if option in options]
    if not carousel_options:
        return None

    if selected not in carousel_options:
        selected = carousel_options[0]

    items = [
        {
            "value": option,
            "label": _single_line_label(option, label_for_option(option)),
            "image": _image_data_uri(option, tiles[option]),
        }
        for option in carousel_options
    ]

    result = _component(
        items=items,
        value=selected,
        primary_color=_theme_value("theme.primaryColor", "#168AC1"),
        background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),
        text_color=_theme_value("theme.textColor", "#31333F"),
        key=f"{widget_key or 'eccitabilita_peribuccale'}_mobile_carousel",
        default=selected,
    )

    if result not in carousel_options:
        result = selected

    st.session_state["_eccitabilita_peribuccale_selected"] = result
    if widget_key:
        st.session_state[widget_key] = result
    return result
