# -*- coding: utf-8 -*-
"""Supporto UI per l'eccitabilità elettrica sopraciliare e peribuccale.

Mantiene le immagini di base, il layout affiancato dei due parametri elettrici,
posiziona meccanica e chimica pupillare sotto la peribuccale e sopprime i
vecchi popover. I renderer cliccabili correnti vengono installati dai moduli
``supra_single_grid`` e ``perioral_single_grid``.
"""

import base64
import inspect
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from app.special_tanatology_states import (
    PARAM_CHEMICAL_PUPILLARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_MECHANICAL_MUSCLE,
)


_SUPRA_LABEL = "Eccitabilità elettrica sopraciliare"
_PERIORAL_LABEL = "Eccitabilità elettrica peribuccale"
_DATA_DIR = Path(__file__).resolve().parent
_SUPRA_SELECTION_KEY = "_eccitabilita_sopraciliare_selected"
_RIGHT_STACK_PARAMS = {
    PARAM_MECHANICAL_MUSCLE,
    PARAM_CHEMICAL_PUPILLARY,
}
_ELECTRICAL_HELPER_TEXT = {
    PARAM_ELECTRICAL_SUPRACILIARY: (
        "Posizionare gli elettrodi distanziati di circa 2 cm nella parte nasale del sopracciglio, "
        "a una profondità di circa 0.5 - 0.7 cm, e applicare uno stimolo di 30 mA · 10 ms · 50 Hz."
    ),
    PARAM_ELECTRICAL_PERIORAL: (
        "Posizionare gli elettrodi a circa 1 cm dagli angoli della bocca, a una profondità di circa "
        "0.5 - 0.7 cm, e applicare uno stimolo di 30 mA · 10 ms · 50 Hz."
    ),
}


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

# Ordine della griglia sopraciliare 3 x 3.
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
        (
            cx - radius * 0.72,
            cy + radius * 0.72,
            cx + radius * 0.72,
            cy - radius * 0.72,
        ),
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
    """Contesto vuoto usato per sopprimere le vecchie immagini elettriche."""

    def __enter__(self):
        st._suppress_legacy_electrical_image = True
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        st._suppress_legacy_electrical_image = False
        return False


def _install_responsive_image_css():
    """Mantiene le griglie responsive e ancora stabilmente la Full desktop a sinistra."""
    st.markdown(
        """
        <style>
        .st-key-eccitabilita_sopraciliare_grid,
        .st-key-eccitabilita_peribuccale_grid {
            width: 100%;
            max-width: 100%;
            margin-left: auto;
            margin-right: auto;
        }

        /* Titoli elettrici: usa davvero una label di checkbox per ottenere
           l'identico help nativo dei checkbox/toggle della Full, ma nasconde
           esclusivamente il quadratino della checkbox. */
        [class*="st-key-electrical_native_label_"] [data-testid="stCheckbox"] label > div:first-child {
            display: none !important;
        }

        [class*="st-key-electrical_native_label_"] [data-testid="stCheckbox"] label {
            gap: 0 !important;
            padding: 0.4rem 0 0 0 !important;
            margin: 0 !important;
            align-items: center !important;
        }

        [class*="st-key-electrical_native_label_"] [data-testid="stMarkdownContainer"] {
            pointer-events: none !important;
        }

        [class*="st-key-electrical_native_label_"] [data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            line-height: 1.15 !important;
        }

        /* Allineamento desktop statico: non dipende da rerun, checkbox o
           dalla struttura interna dei dati tanatologici aggiuntivi. */
        @media (min-width: 769px) {
          [data-testid="stMainBlockContainer"] {
            box-sizing: border-box !important;
            width: min(100%, 46rem) !important;
            max-width: 46rem !important;
            margin-left: 0 !important;
            margin-right: auto !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _click_identity(click):
    """Identificatore stabile di un clic restituito dal componente locale."""
    if not isinstance(click, dict):
        return None
    click_id = click.get("unix_time")
    if click_id is not None:
        return click_id
    if "x" in click and "y" in click:
        return (click.get("x"), click.get("y"))
    return None


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
    """Installa layout elettrico, soppressione legacy e renderer correnti."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    _install_responsive_image_css()

    original_selectbox = st.selectbox
    original_popover = st.popover
    original_image = st.image
    original_columns = st.columns
    original_checkbox = st.checkbox
    original_markdown = st.markdown

    # La coppia viene ricreata a ogni esecuzione quando compare la riga
    # principale sopraciliare; non conserviamo DeltaGenerator di rerun precedenti.
    electrical_pair = {"columns": None}

    def columns_with_electrical_pair(spec, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None

        supported_params = {
            PARAM_ELECTRICAL_SUPRACILIARY,
            PARAM_ELECTRICAL_PERIORAL,
            *_RIGHT_STACK_PARAMS,
        }
        if parametro_id not in supported_params:
            return original_columns(spec, *args, **kwargs)

        is_main_row = _is_main_special_row(spec)

        if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY and is_main_row:
            with st.container(key="electrical_pair_layout"):
                electrical_pair["columns"] = original_columns(2, gap="small")

        # Meccanica e chimica pupillare devono seguire la peribuccale nella
        # colonna destra. Se per qualunque motivo la coppia elettrica non fosse
        # ancora stata creata, manteniamo il layout originale invece di
        # ricostruirla fuori ordine.
        if parametro_id in _RIGHT_STACK_PARAMS:
            if electrical_pair["columns"] is None:
                return original_columns(spec, *args, **kwargs)
            if not is_main_row:
                return original_columns(spec, *args, **kwargs)

            target_column = electrical_pair["columns"][1]
            with target_column:
                compact_stack = st.container(
                    gap="small",
                    key=f"special_right_stack_{parametro_id}",
                )
            return compact_stack, compact_stack

        if electrical_pair["columns"] is None:
            with st.container(key="electrical_pair_layout"):
                electrical_pair["columns"] = original_columns(2, gap="small")

        target_index = 0 if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY else 1
        target_column = electrical_pair["columns"][target_index]

        if is_main_row:
            return target_column, target_column

        with target_column:
            return original_columns(spec, *args, **kwargs)

    def markdown_with_electrical_help(body, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None
        nome_parametro = caller.f_locals.get("nome_parametro") if caller else None
        if (
            parametro_id in (PARAM_ELECTRICAL_SUPRACILIARY, PARAM_ELECTRICAL_PERIORAL)
            and isinstance(body, str)
            and nome_parametro
            and nome_parametro in body
        ):
            with st.container(key=f"electrical_native_label_{parametro_id}"):
                original_checkbox(
                    f"{nome_parametro}:",
                    value=False,
                    help=_ELECTRICAL_HELPER_TEXT[parametro_id],
                )
            return None
        return original_markdown(body, *args, **kwargs)

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
        if label == _SUPRA_LABEL:
            renderer = globals().get("_render_supra_tile_grid")
            if callable(renderer):
                return renderer(
                    widget_key=kwargs.get("key"),
                    options=list(options),
                )
        return original_selectbox(label, options, *args, **kwargs)

    st.columns = columns_with_electrical_pair
    st.markdown = markdown_with_electrical_help
    st.popover = popover_without_legacy_electrical_images
    st.image = image_without_legacy_electrical_images
    st.selectbox = selectbox_with_electrical_images
    st._sopraciliare_click_selector_installed = True
