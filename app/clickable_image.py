# -*- coding: utf-8 -*-
"""Componente immagine cliccabile che segue i ridimensionamenti del contenitore."""

import base64
from io import BytesIO
from pathlib import Path

import streamlit.components.v1 as components


_FRONTEND_DIR = (Path(__file__).resolve().parent / "clickable_image_frontend").absolute()
_component = components.declare_component(
    "mortem_responsive_image_coordinates",
    path=str(_FRONTEND_DIR),
)


def responsive_image_coordinates(source, *, key=None, cursor="pointer"):
    """Mostra una PIL image a larghezza piena e restituisce le coordinate del clic."""
    if not hasattr(source, "save"):
        raise ValueError("source deve essere un'immagine PIL o compatibile con save()")

    buffer = BytesIO()
    source.save(buffer, format="PNG", compress_level=6)
    src = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")

    return _component(
        src=src,
        cursor=cursor,
        key=key,
        default=None,
    )
