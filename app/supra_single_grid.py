# -*- coding: utf-8 -*-
"""Renderer responsive per l'eccitabilità elettrica sopraciliare.

Ogni riga usa un solo componente cliccabile contenente tre immagini senza testo.
Le etichette sottostanti sono pulsanti nativi localizzabili: anche il clic sul
testo seleziona l'opzione, mentre le immagini restano statiche al cambio di stato.
"""

import importlib

import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

from app.i18n import normalize_language, special_option_label
from app.special_tanatology_states import (
    PARAM_ELECTRICAL_SUPRACILIARY,
    SUPRA_PHASE_I,
    SUPRA_PHASE_II,
    SUPRA_PHASE_III,
    SUPRA_PHASE_IV,
    SUPRA_PHASE_V,
    SUPRA_PHASE_VI,
    special_option_id,
)


_IMAGE_ONLY_FRACTION = 0.76
_PHASE_IDS = {
    SUPRA_PHASE_I,
    SUPRA_PHASE_II,
    SUPRA_PHASE_III,
    SUPRA_PHASE_IV,
    SUPRA_PHASE_V,
    SUPRA_PHASE_VI,
}


def _image_only_tile(ui, option):
    """Rimuove la didascalia raster dalla cella originale."""
    tile = ui._SUPRA_TILES[option]
    width, height = tile.size
    image_height = max(1, round(height * _IMAGE_ONLY_FRACTION))
    return tile.crop((0, 0, width, image_height)).convert("RGB")


def _compose_row(ui, row):
    """Compone tre immagini mute in una singola riga cliccabile."""
    options = ui._SUPRA_TILE_OPTIONS[row * 3:(row + 1) * 3]
    tiles = [_image_only_tile(ui, option) for option in options]
    sample = tiles[0]
    tile_width, tile_height = sample.size
    row_image = Image.new("RGB", (tile_width * 3, tile_height), (255, 255, 255))

    for col, tile in enumerate(tiles):
        if tile.size != sample.size:
            tile = tile.resize(sample.size, Image.Resampling.LANCZOS)
        row_image.paste(tile, (col * tile_width, 0))

    return row_image


def _option_from_row_click(ui, row, click):
    """Converte il clic nella corrispondente cella della riga."""
    if not isinstance(click, dict):
        return None

    try:
        x = float(click["x"])
        width = float(click["width"])
    except (KeyError, TypeError, ValueError):
        return None

    if width <= 0 or x < 0 or x > width:
        return None

    col = min(2, int(x / (width / 3)))
    return ui._SUPRA_TILE_OPTIONS[row * 3 + col]


def _component_key(row):
    return f"eccitabilita_sopraciliare_row_click_{row}"


def _last_click_key(row):
    return f"_eccitabilita_sopraciliare_row_last_click_{row}"


def _click_candidate(ui, *, row, click, options):
    """Restituisce un nuovo clic valido e lo marca come acquisito."""
    click_id = ui._click_identity(click)
    if click_id is None or click_id == st.session_state.get(_last_click_key(row)):
        return None

    st.session_state[_last_click_key(row)] = click_id
    option = _option_from_row_click(ui, row, click)
    if option not in options:
        return None

    order_value = click.get("unix_time") if isinstance(click, dict) else None
    if order_value is None:
        order_value = row
    return order_value, option


def _apply_newest_click(ui, *, candidates, widget_key, selected):
    if not candidates:
        return selected

    _, selected = max(candidates, key=lambda item: item[0])
    st.session_state[ui._SUPRA_SELECTION_KEY] = selected
    if widget_key:
        st.session_state[widget_key] = selected
    return selected


def _sync_clicks_before_render(ui, *, widget_key, options, selected):
    """Acquisisce eventuali clic già presenti nello stato del componente."""
    candidates = []
    for row in range(3):
        candidate = _click_candidate(
            ui,
            row=row,
            click=st.session_state.get(_component_key(row)),
            options=options,
        )
        if candidate is not None:
            candidates.append(candidate)

    return _apply_newest_click(
        ui,
        candidates=candidates,
        widget_key=widget_key,
        selected=selected,
    )


def _detail_for_option(option_id, language=None):
    """Carica il testo sintetico dal modulo locale dedicato alla griglia."""
    language = normalize_language(language)
    locale = importlib.import_module(f"app.locales.{language}_supra")
    return locale.SUPRA_GRID_DETAIL_BY_ID[option_id]


def _label_for_option(option, language=None):
    """Testo compatto del pulsante; per le fasi omette volutamente 'Fase I–VI'."""
    option_id = special_option_id(PARAM_ELECTRICAL_SUPRACILIARY, option)
    title = special_option_label(
        PARAM_ELECTRICAL_SUPRACILIARY,
        option_id,
        language=language,
    )
    detail, interval = _detail_for_option(option_id, language=language)

    if option_id in _PHASE_IDS:
        parts = [detail, interval]
    else:
        parts = [title, detail, interval]

    return " · ".join(part for part in parts if part)


def _set_label_selection(ui, widget_key, option):
    """Callback eseguita prima del rerun quando viene premuta una didascalia."""
    st.session_state[ui._SUPRA_SELECTION_KEY] = option
    if widget_key:
        st.session_state[widget_key] = option


def _install_label_css():
    st.markdown(
        """
        <style>
        [class*="st-key-eccitabilita_sopraciliare_label_row_"] {
            width: 100% !important;
            margin-top: -0.42rem !important;
            margin-bottom: 0.20rem !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_label_row_"] div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 2px !important;
            width: 100% !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_label_row_"] div[data-testid="stHorizontalBlock"] > div {
            flex: 1 1 0 !important;
            width: 0 !important;
            min-width: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_label_button_"] {
            width: 100% !important;
            min-width: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_label_button_"] button {
            width: 100% !important;
            min-width: 0 !important;
            min-height: 2.65rem !important;
            padding: 3px 3px !important;
            border-radius: 6px !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_label_button_"] button p {
            margin: 0 !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            text-align: center !important;
            line-height: 1.08 !important;
            font-size: clamp(0.58rem, 2.2vw, 0.74rem) !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_label_buttons(ui, *, row, selected, widget_key, options, language=None):
    with st.container(
        horizontal=True,
        horizontal_alignment="left",
        gap=2,
        key=f"eccitabilita_sopraciliare_label_row_{row}",
    ):
        for col in range(3):
            index = row * 3 + col
            option = ui._SUPRA_TILE_OPTIONS[index]
            if option not in options:
                continue

            st.button(
                _label_for_option(option, language=language),
                key=f"eccitabilita_sopraciliare_label_button_{index}",
                type="primary" if option == selected else "secondary",
                width="stretch",
                on_click=_set_label_selection,
                args=(ui, widget_key, option),
            )


def _make_renderer(ui):
    # Le immagini delle tre righe sono statiche: non vengono ricostruite al clic.
    row_images = tuple(_compose_row(ui, row) for row in range(3))

    def _render_supra_grid(*, widget_key, options):
        if not options:
            return None

        selected = st.session_state.get(ui._SUPRA_SELECTION_KEY)
        if selected not in options and widget_key:
            selected = st.session_state.get(widget_key)
        if selected not in options:
            selected = options[0]

        selected = _sync_clicks_before_render(
            ui,
            widget_key=widget_key,
            options=options,
            selected=selected,
        )

        st.session_state[ui._SUPRA_SELECTION_KEY] = selected
        if widget_key:
            st.session_state[widget_key] = selected

        _install_label_css()

        with st.container(key="eccitabilita_sopraciliare_grid"):
            for row, row_image in enumerate(row_images):
                click = streamlit_image_coordinates(
                    row_image,
                    use_column_width="always",
                    cursor="pointer",
                    key=_component_key(row),
                )

                candidate = _click_candidate(
                    ui,
                    row=row,
                    click=click,
                    options=options,
                )
                if candidate is not None:
                    selected = _apply_newest_click(
                        ui,
                        candidates=[candidate],
                        widget_key=widget_key,
                        selected=selected,
                    )

                _render_label_buttons(
                    ui,
                    row=row,
                    selected=selected,
                    widget_key=widget_key,
                    options=options,
                )

        return selected if selected in options else options[0]

    return _render_supra_grid


def install_supra_single_grid(ui):
    """Sostituisce soltanto il renderer sopraciliare."""
    ui._render_supra_tile_grid = _make_renderer(ui)
