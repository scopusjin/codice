# -*- coding: utf-8 -*-
"""Renderer responsive per l'eccitabilità elettrica sopraciliare.

Ogni riga usa un solo componente cliccabile contenente tre immagini senza testo.
Sotto ogni riga un unico controllo segmentato contiene le tre etichette
localizzabili, evitando l'impilamento dei singoli pulsanti su mobile.
"""

import importlib

import streamlit as st
from PIL import Image, ImageDraw, ImageOps

from app.clickable_image import responsive_image_coordinates
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


_IMAGE_SCAN_FRACTION = 0.69
_CONTENT_THRESHOLD = 246
_CONTENT_PAD_TOP = 3
_CONTENT_PAD_BOTTOM = 4
_PHASE_IDS = {
    SUPRA_PHASE_I,
    SUPRA_PHASE_II,
    SUPRA_PHASE_III,
    SUPRA_PHASE_IV,
    SUPRA_PHASE_V,
    SUPRA_PHASE_VI,
}


def _image_scan_tile(ui, option):
    """Esclude la vecchia didascalia raster mantenendo una fascia di scansione uniforme."""
    tile = ui._SUPRA_TILES[option]
    width, height = tile.size
    scan_height = max(1, round(height * _IMAGE_SCAN_FRACTION))
    scan = tile.crop((0, 0, width, scan_height)).convert("RGB")

    # La nona cella conteneva la vecchia scritta raster "Non valutata" più in alto:
    # conserviamo il simbolo e rendiamo bianco il resto prima del crop sul contenuto.
    if option == "Non valutata":
        visible_height = max(1, round(height * 0.60))
        cleaned = Image.new("RGB", (width, scan_height), (255, 255, 255))
        cleaned.paste(tile.crop((0, 0, width, visible_height)).convert("RGB"), (0, 0))
        return cleaned

    return scan


def _strip_original_edges(tile):
    """Elimina i bordi/cornici raster originari senza ridimensionare il disegno."""
    width, height = tile.size
    edge = 7
    if width <= edge * 2 or height <= edge * 2:
        return tile
    return tile.crop((edge, edge, width - edge, height - edge)).convert("RGB")


def _content_vertical_bounds(tile):
    """Trova l'estensione verticale reale del disegno, ignorando il fondo quasi bianco."""
    gray = ImageOps.grayscale(tile)
    mask = gray.point(lambda pixel: 255 if pixel < _CONTENT_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return None
    return bbox[1], bbox[3]


def _row_content_tiles(ui, row):
    """Ritaglia le tre celle della riga sugli stessi limiti reali del contenuto."""
    options = ui._SUPRA_TILE_OPTIONS[row * 3:(row + 1) * 3]
    tiles = [_strip_original_edges(_image_scan_tile(ui, option)) for option in options]
    bounds = [bound for tile in tiles if (bound := _content_vertical_bounds(tile)) is not None]
    if not bounds:
        return tiles

    top = max(0, min(bound[0] for bound in bounds) - _CONTENT_PAD_TOP)
    bottom = min(
        min(tile.height for tile in tiles),
        max(bound[1] for bound in bounds) + _CONTENT_PAD_BOTTOM,
    )
    if bottom <= top:
        return tiles

    return [tile.crop((0, top, tile.width, bottom)) for tile in tiles]


def _compose_row(ui, row):
    """Compone tre immagini pulite con la parte superiore della cornice unica."""
    tiles = _row_content_tiles(ui, row)
    sample = tiles[0]
    tile_width, tile_height = sample.size
    row_width = tile_width * 3
    row_image = Image.new("RGB", (row_width, tile_height), (255, 255, 255))

    for col, tile in enumerate(tiles):
        if tile.size != sample.size:
            tile = tile.resize(sample.size, Image.Resampling.LANCZOS)
        row_image.paste(tile, (col * tile_width, 0))

    # La cornice è unica con l'etichetta sottostante: qui disegniamo soltanto
    # bordo superiore e divisori verticali; il bordo inferiore appartiene
    # all'etichetta, senza linea di demarcazione tra immagine e testo.
    frame = (105, 105, 105)
    draw = ImageDraw.Draw(row_image)
    draw.line((0, 0, row_width - 1, 0), fill=frame, width=1)
    for x in (0, tile_width, tile_width * 2, row_width - 1):
        draw.line((x, 0, x, tile_height - 1), fill=frame, width=1)

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


def _segment_key(row):
    return f"eccitabilita_sopraciliare_segment_{row}"


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
    """Testo compatto; l'intervallo orario occupa sempre una seconda riga."""
    option_id = special_option_id(PARAM_ELECTRICAL_SUPRACILIARY, option)
    title = special_option_label(
        PARAM_ELECTRICAL_SUPRACILIARY,
        option_id,
        language=language,
    )
    detail, interval = _detail_for_option(option_id, language=language)

    if option_id in _PHASE_IDS:
        first_line = detail or ""
    else:
        first_line = " · ".join(part for part in (title, detail) if part)

    if interval:
        return f"{first_line}\n{interval}" if first_line else interval
    return first_line


def _on_segment_change(ui, widget_key, segment_key):
    """Sincronizza la selezione globale prima del rerun del controllo segmentato."""
    option = st.session_state.get(segment_key)
    if option is None:
        return
    st.session_state[ui._SUPRA_SELECTION_KEY] = option
    if widget_key:
        st.session_state[widget_key] = option


def _install_label_css():
    st.markdown(
        """
        <style>
        [class*="st-key-eccitabilita_sopraciliare_grid"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_grid"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
        }

        @media (max-width: 768px) {
            [class*="st-key-eccitabilita_sopraciliare_grid"] {
                position: relative !important;
                top: -0.80rem !important;
                margin-bottom: -0.80rem !important;
            }
        }

        [class*="st-key-eccitabilita_sopraciliare_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_row_click_"] iframe {
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_grid"]
        [data-testid="stElementContainer"]:has([class*="st-key-eccitabilita_sopraciliare_row_click_"]),
        [class*="st-key-eccitabilita_sopraciliare_grid"]
        [data-testid="stElementContainer"]:has([class*="st-key-eccitabilita_sopraciliare_segment_"]) {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
            width: 100% !important;
            margin-top: 0 !important;
            margin-bottom: 0.22rem !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] div[role="group"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            width: 100% !important;
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button {
            min-width: 0 !important;
            width: 100% !important;
            min-height: 0 !important;
            height: auto !important;
            padding: 1px 2px !important;
            margin: 0 !important;
            white-space: normal !important;
            border: 0 !important;
            border-left: 1px solid rgba(105, 105, 105, 0.72) !important;
            border-bottom: 1px solid rgba(105, 105, 105, 0.72) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            align-items: center !important;
            justify-content: center !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button:last-child {
            border-right: 1px solid rgba(105, 105, 105, 0.72) !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button > div,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] [data-testid="stMarkdownContainer"] {
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[kind="segmented_controlActive"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-pressed="true"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-checked="true"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[data-selected="true"] {
            background: #00A699 !important;
            box-shadow: none !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button p {
            margin: 0 !important;
            padding: 0 !important;
            white-space: pre-line !important;
            overflow-wrap: anywhere !important;
            text-align: center !important;
            line-height: 1.00 !important;
            font-size: clamp(0.53rem, 1.85vw, 0.66rem) !important;
            font-weight: 600 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[kind="segmented_controlActive"] *,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-pressed="true"] *,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-checked="true"] *,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[data-selected="true"] * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_segmented_labels(ui, *, row, selected, widget_key, options, language=None):
    row_options = [
        option
        for option in ui._SUPRA_TILE_OPTIONS[row * 3:(row + 1) * 3]
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
        args=(ui, widget_key, segment_key),
    )


def _make_renderer(ui):
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
                        ui,
                        candidates=[candidate],
                        widget_key=widget_key,
                        selected=selected,
                    )
                    if selected != previous:
                        st.rerun()

                _render_segmented_labels(
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
