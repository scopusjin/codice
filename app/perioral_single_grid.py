# -*- coding: utf-8 -*-
"""Renderer responsive per l'eccitabilità elettrica peribuccale.

Ogni riga usa un solo componente cliccabile contenente tre immagini senza testo.
Sotto ogni riga un unico controllo segmentato contiene le tre etichette
localizzabili, con intervallo orario su una seconda riga e selezione evidente.
"""

import importlib

import streamlit as st
from PIL import Image, ImageDraw

from app.clickable_image import responsive_image_coordinates
from app.i18n import normalize_language, special_option_label
from app.special_tanatology_states import (
    OPTION_NOT_ASSESSED,
    PARAM_ELECTRICAL_PERIORAL,
    special_option_id,
)


_PERIORAL_SELECTION_KEY = "_eccitabilita_peribuccale_selected"
_PERIORAL_TILE_OPTIONS = (
    "Marcata ed estesa (+++)",
    "Discreta (++)",
    "Accennata (+)",
    "Nessuna reazione",
    "Non valutabile/non attendibile",
    "Non valutata",
)
_IMAGE_ONLY_FRACTION = 0.76


def _source_tile(ui, index):
    """Ricava una cella dalla tavola peribuccale originale 3 x 2."""
    image = ui._PERIORAL_IMAGE
    width, height = image.size
    row, col = divmod(index, 3)
    cell_width = width / 3
    cell_height = height / 2

    x0 = round(col * cell_width) + 3
    x1 = round((col + 1) * cell_width) - 3
    y0 = round(row * cell_height) + 3
    y1 = round((row + 1) * cell_height) - 3
    return image.crop((x0, y0, x1, y1)).convert("RGB")


def _image_only_tile(tile):
    """Rimuove la didascalia raster dalla cella originale."""
    width, height = tile.size
    image_height = max(1, round(height * _IMAGE_ONLY_FRACTION))
    return tile.crop((0, 0, width, image_height)).convert("RGB")


def _build_tiles(ui):
    """Costruisce le cinque immagini originali e la cella neutra 'Non valutata'."""
    tiles = {
        option: _image_only_tile(_source_tile(ui, index))
        for index, option in enumerate(_PERIORAL_TILE_OPTIONS[:5])
    }

    sample = next(iter(tiles.values()))
    neutral = Image.new("RGB", sample.size, (255, 255, 255))
    draw = ImageDraw.Draw(neutral)
    width, height = neutral.size
    radius = min(width, height) * 0.20
    cx, cy = width / 2, height / 2
    stroke = max(2, round(min(width, height) * 0.018))
    gray = (170, 170, 170)

    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        outline=gray,
        width=stroke,
    )
    draw.line(
        (
            cx - radius * 0.72,
            cy + radius * 0.72,
            cx + radius * 0.72,
            cy - radius * 0.72,
        ),
        fill=gray,
        width=stroke,
    )

    tiles["Non valutata"] = neutral
    return tiles


def _compose_row(tiles, row):
    """Compone tre immagini mute in una singola riga cliccabile."""
    options = _PERIORAL_TILE_OPTIONS[row * 3:(row + 1) * 3]
    row_tiles = [tiles[option] for option in options]
    sample = row_tiles[0]
    tile_width, tile_height = sample.size
    row_image = Image.new("RGB", (tile_width * 3, tile_height), (255, 255, 255))

    for col, tile in enumerate(row_tiles):
        if tile.size != sample.size:
            tile = tile.resize(sample.size, Image.Resampling.LANCZOS)
        row_image.paste(tile, (col * tile_width, 0))

    return row_image


def _option_from_row_click(row, click):
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
    return _PERIORAL_TILE_OPTIONS[row * 3 + col]


def _component_key(row):
    return f"eccitabilita_peribuccale_row_click_{row}"


def _last_click_key(row):
    return f"_eccitabilita_peribuccale_row_last_click_{row}"


def _segment_key(row):
    return f"eccitabilita_peribuccale_segment_{row}"


def _click_candidate(ui, *, row, click, options):
    click_id = ui._click_identity(click)
    if click_id is None or click_id == st.session_state.get(_last_click_key(row)):
        return None

    st.session_state[_last_click_key(row)] = click_id
    option = _option_from_row_click(row, click)
    if option not in options:
        return None

    order_value = click.get("unix_time") if isinstance(click, dict) else None
    if order_value is None:
        order_value = row
    return order_value, option


def _apply_newest_click(*, candidates, widget_key, selected):
    if not candidates:
        return selected

    _, selected = max(candidates, key=lambda item: item[0])
    st.session_state[_PERIORAL_SELECTION_KEY] = selected
    if widget_key:
        st.session_state[widget_key] = selected
    return selected


def _sync_clicks_before_render(ui, *, widget_key, options, selected):
    candidates = []
    for row in range(2):
        candidate = _click_candidate(
            ui,
            row=row,
            click=st.session_state.get(_component_key(row)),
            options=options,
        )
        if candidate is not None:
            candidates.append(candidate)

    return _apply_newest_click(
        candidates=candidates,
        widget_key=widget_key,
        selected=selected,
    )


def _interval_for_option(option_id, language=None):
    language = normalize_language(language)
    locale = importlib.import_module(f"app.locales.{language}_perioral")
    return locale.PERIORAL_GRID_INTERVAL_BY_ID[option_id]


def _label_for_option(option, language=None):
    option_id = special_option_id(PARAM_ELECTRICAL_PERIORAL, option)
    title = special_option_label(
        PARAM_ELECTRICAL_PERIORAL,
        option_id,
        language=language,
    )
    interval = _interval_for_option(option_id, language=language)

    if interval:
        return f"{title}\n{interval}"
    return title


def _on_segment_change(widget_key, segment_key):
    option = st.session_state.get(segment_key)
    if option is None:
        return
    st.session_state[_PERIORAL_SELECTION_KEY] = option
    if widget_key:
        st.session_state[widget_key] = option


def _install_label_css():
    st.markdown(
        """
        <style>
        [class*="st-key-eccitabilita_peribuccale_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0.04rem !important;
        }

        [class*="st-key-eccitabilita_peribuccale_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] {
            width: 100% !important;
            margin-top: -0.98rem !important;
            margin-bottom: -0.24rem !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] div[role="group"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            width: 100% !important;
            gap: 2px !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button {
            min-width: 0 !important;
            width: 100% !important;
            min-height: 2.65rem !important;
            padding: 3px 3px !important;
            white-space: normal !important;
            border-color: rgba(128, 128, 128, 0.35) !important;
            background: transparent !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button[kind="segmented_controlActive"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-pressed="true"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-checked="true"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[data-selected="true"] {
            border-color: #008F84 !important;
            background: #00A699 !important;
            box-shadow: inset 0 0 0 1px #008F84 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button p {
            margin: 0 !important;
            white-space: pre-line !important;
            overflow-wrap: anywhere !important;
            text-align: center !important;
            line-height: 1.10 !important;
            font-size: clamp(0.57rem, 2.15vw, 0.72rem) !important;
            font-weight: 600 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button[kind="segmented_controlActive"] *,
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-pressed="true"] *,
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-checked="true"] *,
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[data-selected="true"] * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_segmented_labels(*, row, selected, widget_key, options, language=None):
    row_options = [
        option
        for option in _PERIORAL_TILE_OPTIONS[row * 3:(row + 1) * 3]
        if option in options
    ]
    segment_key = _segment_key(row)
    desired = selected if selected in row_options else None

    if st.session_state.get(segment_key) != desired:
        st.session_state[segment_key] = desired

    return st.segmented_control(
        "Selezione",
        options=row_options,
        key=segment_key,
        format_func=lambda option: _label_for_option(option, language=language),
        selection_mode="single",
        label_visibility="collapsed",
        width="stretch",
        on_change=_on_segment_change,
        args=(widget_key, segment_key),
    )


def _make_renderer(ui):
    tiles = _build_tiles(ui)
    row_images = tuple(_compose_row(tiles, row) for row in range(2))

    def _render_perioral_grid(*, widget_key, options):
        if not options:
            return None

        selected = st.session_state.get(_PERIORAL_SELECTION_KEY)
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

        st.session_state[_PERIORAL_SELECTION_KEY] = selected
        if widget_key:
            st.session_state[widget_key] = selected

        _install_label_css()

        with st.container(key="eccitabilita_peribuccale_grid"):
            for row, row_image in enumerate(row_images):
                click = responsive_image_coordinates(
                    row_image,
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
                    previous = selected
                    selected = _apply_newest_click(
                        candidates=[candidate],
                        widget_key=widget_key,
                        selected=selected,
                    )
                    if selected != previous:
                        st.rerun()

                _render_segmented_labels(
                    row=row,
                    selected=selected,
                    widget_key=widget_key,
                    options=options,
                )

        return selected if selected in options else options[0]

    return _render_perioral_grid


def install_perioral_single_grid(ui):
    """Sostituisce soltanto il renderer peribuccale."""
    ui._render_perioral_tile_grid = _make_renderer(ui)
