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
from PIL import Image, ImageDraw, ImageFont
from streamlit_image_coordinates import streamlit_image_coordinates

from app.special_tanatology_states import (
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
)


_SUPRA_LABEL = "Eccitabilità elettrica sopraciliare"
_PERIORAL_LABEL = "Eccitabilità elettrica peribuccale"
_DATA_DIR = Path(__file__).resolve().parent
_SUPRA_SELECTION_KEY = "_eccitabilita_sopraciliare_selected"


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

# Ordine della nuova griglia sopraciliare 3 x 3.
_SUPRA_TILE_OPTIONS = (
    "Fase VI", "Fase V", "Fase IV",
    "Fase III", "Fase II", "Fase I",
    "Nessuna reazione", "Non valutabile/non attendibile", "Non valutata",
)

# Posizione degli otto riquadri nella tavola originale 2 x 4.
_SUPRA_SOURCE_POSITIONS = {
    "Fase VI": (0, 0),
    "Fase V": (0, 1),
    "Fase IV": (1, 0),
    "Fase III": (1, 1),
    "Fase II": (2, 0),
    "Fase I": (2, 1),
    "Nessuna reazione": (3, 0),
    "Non valutabile/non attendibile": (3, 1),
}

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


def _scaled_default_text(text, target_width):
    """Crea una piccola etichetta raster senza dipendere da font esterni."""
    font = ImageFont.load_default()
    probe = Image.new("L", (1, 1), 0)
    probe_draw = ImageDraw.Draw(probe)
    bbox = probe_draw.textbbox((0, 0), text, font=font)
    text_width = max(1, bbox[2] - bbox[0])
    text_height = max(1, bbox[3] - bbox[1])

    label = Image.new("L", (text_width + 4, text_height + 4), 255)
    label_draw = ImageDraw.Draw(label)
    label_draw.text((2 - bbox[0], 2 - bbox[1]), text, fill=45, font=font)

    scale = min(4.0, max(1.0, target_width / label.width))
    new_size = (round(label.width * scale), round(label.height * scale))
    return label.resize(new_size, Image.Resampling.LANCZOS)


def _build_supra_tiles(image):
    """Ricava gli otto riquadri completi di didascalia e crea 'Non valutata'."""
    width, height = image.size
    cell_width = width / 2
    cell_height = height / 4
    tiles = {}

    for option, (row, col) in _SUPRA_SOURCE_POSITIONS.items():
        x0 = round(col * cell_width) + 3
        x1 = round((col + 1) * cell_width) - 3
        y0 = round(row * cell_height) + 3
        y1 = round((row + 1) * cell_height) - 3
        tiles[option] = image.crop((x0, y0, x1, y1)).convert("RGB")

    # Nona cella grafica neutra, con didascalia integrata.
    sample = next(iter(tiles.values()))
    neutral = Image.new("RGB", sample.size, (255, 255, 255))
    draw = ImageDraw.Draw(neutral)
    w, h = neutral.size
    radius = min(w, h) * 0.20
    cx, cy = w / 2, h * 0.40
    box = (cx - radius, cy - radius, cx + radius, cy + radius)
    stroke = max(2, round(min(w, h) * 0.018))
    neutral_gray = (170, 170, 170)
    draw.ellipse(box, outline=neutral_gray, width=stroke)
    draw.line(
        (cx - radius * 0.72, cy + radius * 0.72,
         cx + radius * 0.72, cy - radius * 0.72),
        fill=neutral_gray,
        width=stroke,
    )

    label = _scaled_default_text("Non valutata", round(w * 0.72))
    label_x = round((w - label.width) / 2)
    label_y = round(h * 0.78 - label.height / 2)
    neutral.paste(Image.merge("RGB", (label, label, label)), (label_x, label_y))

    tiles["Non valutata"] = neutral
    return tiles


_SUPRA_TILES = _build_supra_tiles(_SUPRA_IMAGE)


class _SuppressedElectricalPopover:
    """Contesto vuoto usato per eliminare i vecchi popover delle immagini."""

    def __enter__(self):
        st._suppress_legacy_electrical_image = True
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        st._suppress_legacy_electrical_image = False
        return False


def _install_responsive_image_css():
    """Adatta le tavole alla larghezza disponibile senza alterarne le proporzioni."""
    st.markdown(
        """
        <style>
        .st-key-eccitabilita_sopraciliare_grid,
        .st-key-eccitabilita_peribuccale_image {
            width: 100%;
            margin-left: auto;
            margin-right: auto;
        }

        [class*="st-key-eccitabilita_sopraciliare_tile_"] {
            box-sizing: border-box;
            border: 2px solid transparent;
            border-radius: 7px;
            padding: 2px;
            transition: border-color 0.12s ease, background-color 0.12s ease;
            min-width: 0 !important;
        }

        /*
         * Streamlit tende a trasformare st.columns in colonne verticali sui
         * viewport stretti. Per questa sola griglia imponiamo sempre tre celle
         * per riga usando CSS Grid sul blocco orizzontale generato da st.columns.
         */
        .st-key-eccitabilita_sopraciliare_grid div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 0.25rem !important;
            align-items: stretch !important;
            width: 100% !important;
        }

        .st-key-eccitabilita_sopraciliare_grid div[data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            min-width: 0 !important;
            max-width: none !important;
            flex: none !important;
        }

        @media (max-width: 768px) {
            .st-key-eccitabilita_sopraciliare_grid,
            .st-key-eccitabilita_peribuccale_image {
                max-width: 100%;
            }
        }

        @media (min-width: 769px) {
            .st-key-eccitabilita_sopraciliare_grid {
                max-width: 100%;
            }

            .st-key-eccitabilita_peribuccale_image {
                max-width: 820px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_supra_tile_grid(*, widget_key, options):
    """Mostra nove componenti indipendenti e restituisce l'opzione selezionata."""
    if not options:
        return None

    # Stato dedicato alla griglia: non dipende più dall'esistenza del selectbox.
    selected = st.session_state.get(_SUPRA_SELECTION_KEY)
    if selected not in options and widget_key:
        selected = st.session_state.get(widget_key)
    if selected not in options:
        selected = options[0]

    st.session_state[_SUPRA_SELECTION_KEY] = selected
    if widget_key:
        st.session_state[widget_key] = selected

    clicked_option = None

    with st.container(key="eccitabilita_sopraciliare_grid"):
        for row in range(3):
            columns = st.columns(3, gap="small")
            for col in range(3):
                index = row * 3 + col
                option = _SUPRA_TILE_OPTIONS[index]
                tile = _SUPRA_TILES[option]
                component_key = f"eccitabilita_sopraciliare_tile_click_{index}"
                last_click_key = f"_eccitabilita_sopraciliare_tile_last_click_{index}"

                with columns[col]:
                    with st.container(key=f"eccitabilita_sopraciliare_tile_{index}"):
                        click = streamlit_image_coordinates(
                            tile,
                            use_column_width="always",
                            cursor="pointer",
                            key=component_key,
                        )

                if not click:
                    continue

                click_id = click.get("unix_time")
                if click_id is None:
                    click_id = (click.get("x"), click.get("y"))

                if click_id == st.session_state.get(last_click_key):
                    continue

                st.session_state[last_click_key] = click_id
                if option in options:
                    clicked_option = option

    if clicked_option is not None:
        selected = clicked_option
        st.session_state[_SUPRA_SELECTION_KEY] = selected
        if widget_key:
            st.session_state[widget_key] = selected

    if selected in _SUPRA_TILE_OPTIONS:
        selected_index = _SUPRA_TILE_OPTIONS.index(selected)
        st.markdown(
            f"""
            <style>
            .st-key-eccitabilita_sopraciliare_tile_{selected_index} {{
                border-color: #00A699 !important;
                background-color: rgba(0, 166, 153, 0.10) !important;
                box-shadow: inset 0 0 0 1px #00A699 !important;
                outline: 2px solid #00A699 !important;
                outline-offset: -2px !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    return selected if selected in options else options[0]


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
    container_key,
    component_key,
    last_click_key,
    widget_key,
    options,
    option_from_click,
    show_toast=True,
):
    with st.container(key=container_key):
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
        if show_toast:
            st.toast(f"✓ {selected}")


def _is_main_special_row(spec):
    """Riconosce la riga principale [1, 2] usata dai parametri aggiuntivi."""
    if isinstance(spec, int):
        return False
    try:
        values = tuple(float(value) for value in spec)
    except (TypeError, ValueError):
        return False
    return values == (1.0, 2.0)


def install_sopraciliare_click_selector():
    """Aggiunge immagini cliccabili e layout dedicato ai due parametri elettrici."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    _install_responsive_image_css()

    original_selectbox = st.selectbox
    original_popover = st.popover
    original_image = st.image
    original_columns = st.columns

    # La coppia viene ricreata a ogni esecuzione quando compare la riga
    # principale sopraciliare; in questo modo non conserviamo DeltaGenerator
    # appartenenti a un rerun precedente.
    electrical_pair = {"columns": None}

    def columns_with_electrical_pair(spec, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None

        if parametro_id not in (PARAM_ELECTRICAL_SUPRACILIARY, PARAM_ELECTRICAL_PERIORAL):
            return original_columns(spec, *args, **kwargs)

        is_main_row = _is_main_special_row(spec)

        if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY and is_main_row:
            with st.container(key="electrical_pair_layout"):
                electrical_pair["columns"] = original_columns(2, gap="small")

        if electrical_pair["columns"] is None:
            with st.container(key="electrical_pair_layout"):
                electrical_pair["columns"] = original_columns(2, gap="small")

        target_index = 0 if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY else 1
        target_column = electrical_pair["columns"][target_index]

        if is_main_row:
            return target_column, target_column

        with target_column:
            return original_columns(spec, *args, **kwargs)

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
            # La griglia 3x3 è il controllo: nessun selectbox aggiuntivo.
            return _render_supra_tile_grid(
                widget_key=widget_key,
                options=list(options),
            )

        if label == _PERIORAL_LABEL:
            _render_clickable_selector(
                image=_PERIORAL_IMAGE,
                container_key="eccitabilita_peribuccale_image",
                component_key="eccitabilita_peribuccale_click",
                last_click_key="_eccitabilita_peribuccale_last_click",
                widget_key=widget_key,
                options=options,
                option_from_click=_perioral_option_from_click,
            )

        return original_selectbox(label, options, *args, **kwargs)

    st.columns = columns_with_electrical_pair
    st.popover = popover_without_legacy_electrical_images
    st.image = image_without_legacy_electrical_images
    st.selectbox = selectbox_with_electrical_images
    st._sopraciliare_click_selector_installed = True