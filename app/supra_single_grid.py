# -*- coding: utf-8 -*-
"""Renderer 3x3 responsive per l'eccitabilità elettrica sopraciliare.

Usa un solo componente cliccabile: le nove celle vengono composte in una
singola tavola 3x3, evitando il wrapping degli iframe su schermi stretti.
"""

import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates


def _compose_grid(ui, selected):
    """Compone le nove celle in una tavola 3x3 di dimensioni uniformi."""
    sample = ui._SUPRA_TILES[ui._SUPRA_TILE_OPTIONS[0]]
    tile_width, tile_height = sample.size
    grid = Image.new("RGB", (tile_width * 3, tile_height * 3), (255, 255, 255))

    for index, option in enumerate(ui._SUPRA_TILE_OPTIONS):
        row, col = divmod(index, 3)
        tile = ui._SUPRA_TILES[option]
        if tile.size != sample.size:
            tile = tile.resize(sample.size, Image.Resampling.LANCZOS)
        if option == selected:
            tile = ui._highlight_supra_tile(tile)
        grid.paste(tile, (col * tile_width, row * tile_height))

    return grid


def _option_from_click(ui, click):
    """Converte il clic nella corrispondente cella della tavola 3x3."""
    if not isinstance(click, dict):
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
    row = min(2, int(y / (height / 3)))
    return ui._SUPRA_TILE_OPTIONS[row * 3 + col]


def _sync_click_before_render(ui, *, widget_key, options, selected):
    """Acquisisce il clic già presente nello stato prima di costruire l'immagine."""
    component_key = "eccitabilita_sopraciliare_grid_click"
    last_click_key = "_eccitabilita_sopraciliare_grid_last_click"
    click = st.session_state.get(component_key)
    click_id = ui._click_identity(click)

    if click_id is None or click_id == st.session_state.get(last_click_key):
        return selected

    option = _option_from_click(ui, click)
    st.session_state[last_click_key] = click_id

    if option in options:
        selected = option
        st.session_state[ui._SUPRA_SELECTION_KEY] = selected
        if widget_key:
            st.session_state[widget_key] = selected

    return selected


def _make_renderer(ui):
    def _render_supra_grid(*, widget_key, options):
        if not options:
            return None

        selected = st.session_state.get(ui._SUPRA_SELECTION_KEY)
        if selected not in options and widget_key:
            selected = st.session_state.get(widget_key)
        if selected not in options:
            selected = options[0]

        selected = _sync_click_before_render(
            ui,
            widget_key=widget_key,
            options=options,
            selected=selected,
        )

        st.session_state[ui._SUPRA_SELECTION_KEY] = selected
        if widget_key:
            st.session_state[widget_key] = selected

        grid = _compose_grid(ui, selected)
        component_key = "eccitabilita_sopraciliare_grid_click"
        last_click_key = "_eccitabilita_sopraciliare_grid_last_click"

        with st.container(key="eccitabilita_sopraciliare_grid"):
            click = streamlit_image_coordinates(
                grid,
                use_column_width="always",
                cursor="pointer",
                key=component_key,
            )

        # Fallback per versioni del componente che non espongono il nuovo valore
        # in session_state prima del rendering corrente.
        click_id = ui._click_identity(click)
        if click_id is not None and click_id != st.session_state.get(last_click_key):
            option = _option_from_click(ui, click)
            st.session_state[last_click_key] = click_id
            if option in options and option != selected:
                st.session_state[ui._SUPRA_SELECTION_KEY] = option
                if widget_key:
                    st.session_state[widget_key] = option

        return st.session_state.get(ui._SUPRA_SELECTION_KEY, selected)

    return _render_supra_grid


def install_supra_single_grid(ui):
    """Sostituisce soltanto il renderer sopraciliare 3x3."""
    ui._render_supra_tile_grid = _make_renderer(ui)
