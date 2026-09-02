# -*- coding: utf-8 -*-
"""Supporto UI per l'eccitabilità elettrica sopraciliare e peribuccale.

Mantiene le immagini di base, il layout affiancato dei due parametri elettrici,
posiziona meccanica e chimica pupillare sotto la peribuccale e sostituisce i
vecchi popover illustrati con gli stessi helper testuali usati nella Full.
I renderer cliccabili correnti vengono installati dai moduli
``supra_single_grid`` e ``perioral_single_grid``.
"""

import base64
import inspect
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from app.full_mobile_layout import _render_click_help
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

# Posizione dei nove riquadri nella tavola corrente 3 x 3.
_SUPRA_SOURCE_POSITIONS = {
    "Fase VI": (0, 0),
    "Fase V": (0, 1),
    "Fase IV": (0, 2),
    "Fase III": (1, 0),
    "Fase II": (1, 1),
    "Fase I": (1, 2),
    "Nessuna reazione": (2, 0),
    "Non valutabile/non attendibile": (2, 1),
    "Non valutata": (2, 2),
}


def _build_supra_tiles(image):
    """Ricava i nove riquadri dalla tavola sopraciliare 3 x 3."""
    width, height = image.size
    cell_width = width / 3
    cell_height = height / 3
    tiles = {}

    for option, (row, col) in _SUPRA_SOURCE_POSITIONS.items():
        x0 = round(col * cell_width) + 3
        x1 = round((col + 1) * cell_width) - 3
        y0 = round(row * cell_height) + 3
        y1 = round((row + 1) * cell_height) - 3
        tiles[option] = image.crop((x0, y0, x1, y1)).convert("RGB")
    return tiles


_SUPRA_TILES = _build_supra_tiles(_SUPRA_IMAGE)


class _ElectricalHelperPopover:
    """Sostituisce il vecchio popover illustrato con l'helper comune della Full."""

    def __init__(self, helper_text, key):
        self._helper_text = helper_text
        self._key = key

    def __enter__(self):
        _render_click_help(self._helper_text, self._key)
        st._suppress_legacy_electrical_image = True
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        st._suppress_legacy_electrical_image = False
        return False


def _install_responsive_image_css():
    """Mantiene le griglie responsive e organizza la Full desktop larga a sinistra."""
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

        [class*="st-key-electrical_title_help_row_"] [data-testid="stHorizontalBlock"] {
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 0.28rem !important;
        }

        [class*="st-key-electrical_title_text_"] {
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-electrical_title_text_"] .mortem-section-title {
            margin: 0 !important;
        }

        [class*="st-key-mortem_help_prudent_electrical_"] {
            flex: 0 0 auto !important;
            width: 18px !important;
            min-width: 18px !important;
            max-width: 18px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-mortem_help_prudent_electrical_"] button {
            width: 18px !important;
            min-width: 18px !important;
            max-width: 18px !important;
            height: 18px !important;
            min-height: 18px !important;
            max-height: 18px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            line-height: 1 !important;
        }

        [class*="st-key-mortem_help_prudent_electrical_"] button p {
            margin: 0 !important;
            font-size: 0.72rem !important;
            line-height: 1 !important;
        }

        /* Full desktop: conserva la larghezza compatta quando i dati speciali
           sono chiusi, ma ancora la pagina al margine sinistro. */
        @media (min-width: 769px) {
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [data-testid="stMainBlockContainer"] {
            box-sizing: border-box !important;
            width: min(100%, 46rem) !important;
            max-width: 46rem !important;
            margin-left: 0 !important;
            margin-right: auto !important;
          }
        }

        /* Se i dati speciali sono aperti e c'è spazio reale, la Full usa due
           colonne: blocchi principali a sinistra, dati speciali a destra.
           Gli elementi successivi (stima/grafico) tornano a occupare entrambe. */
        @media (min-width: 1180px) {
          html body:has([class*="st-key-stima_cautelativa_beta"]):has([class*="st-key-electrical_pair_layout"])
          [data-testid="stMainBlockContainer"] {
            width: min(100%, 92rem) !important;
            max-width: 92rem !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"]):has([class*="st-key-electrical_pair_layout"])
          [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
            grid-auto-flow: row dense !important;
            column-gap: 1rem !important;
            row-gap: 0.65rem !important;
            align-items: start !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"]):has([class*="st-key-electrical_pair_layout"])
          [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {
            grid-column: 1 / -1;
            min-width: 0 !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"]):has([class*="st-key-electrical_pair_layout"])
          [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
          > [data-testid="stElementContainer"]:has([class*="st-key-selettore_macchie_ui"]),
          html body:has([class*="st-key-stima_cautelativa_beta"]):has([class*="st-key-electrical_pair_layout"])
          [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
          > [data-testid="stElementContainer"]:has([class*="st-key-henssge_non_applicabile"]) {
            grid-column: 1 !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"]):has([class*="st-key-electrical_pair_layout"])
          [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
          > [data-testid="stElementContainer"]:has([class*="st-key-mostra_parametri_aggiuntivi"]),
          html body:has([class*="st-key-stima_cautelativa_beta"]):has([class*="st-key-electrical_pair_layout"])
          [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
          > [data-testid="stElementContainer"]:has([class*="st-key-electrical_pair_layout"]) {
            grid-column: 2 !important;
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


def _columns_signature(spec):
    if isinstance(spec, int):
        return None
    try:
        return tuple(float(value) for value in spec)
    except (TypeError, ValueError):
        return None


def _is_main_special_row(spec):
    """Riconosce la riga principale [1, 2] usata dai parametri aggiuntivi."""
    return _columns_signature(spec) == (1.0, 2.0)


def _is_electrical_title_row(spec):
    """Riconosce la sottoriga [1, 0.5] di titolo e helper elettrico."""
    return _columns_signature(spec) == (1.0, 0.5)


def install_sopraciliare_click_selector():
    """Installa layout elettrico, helper testuali e renderer correnti."""
    if getattr(st, "_sopraciliare_click_selector_installed", False):
        return

    _install_responsive_image_css()

    original_selectbox = st.selectbox
    original_popover = st.popover
    original_image = st.image
    original_columns = st.columns
    original_container = st.container
    original_checkbox = st.checkbox

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
            if _is_electrical_title_row(spec):
                with original_container(
                    horizontal=True,
                    wrap=False,
                    vertical_alignment="center",
                    gap="small",
                    key=f"electrical_title_help_row_{parametro_id}",
                ):
                    title_cell = original_container(
                        width="content",
                        key=f"electrical_title_text_{parametro_id}",
                    )
                    help_cell = original_container(
                        width="content",
                        key=f"electrical_title_help_{parametro_id}",
                    )
                return title_cell, help_cell
            return original_columns(spec, *args, **kwargs)

    def popover_with_electrical_helper(*args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None
        if parametro_id in (PARAM_ELECTRICAL_SUPRACILIARY, PARAM_ELECTRICAL_PERIORAL):
            return _ElectricalHelperPopover(
                _ELECTRICAL_HELPER_TEXT[parametro_id],
                f"mortem_help_prudent_electrical_{parametro_id}",
            )
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

    def checkbox_with_putrefactive_right_stack(label, *args, **kwargs):
        if str(label).strip() == "Alterazioni putrefattive?" and electrical_pair["columns"] is not None:
            target_column = electrical_pair["columns"][1]
            with target_column:
                with st.container(gap="small", key="special_right_stack_putrefactive"):
                    return original_checkbox(label, *args, **kwargs)
        return original_checkbox(label, *args, **kwargs)

    st.columns = columns_with_electrical_pair
    st.popover = popover_with_electrical_helper
    st.image = image_without_legacy_electrical_images
    st.selectbox = selectbox_with_electrical_images
    st.checkbox = checkbox_with_putrefactive_right_stack
    st._sopraciliare_click_selector_installed = True
