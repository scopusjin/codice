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
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

from app.special_tanatology_states import (
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
)


_SUPRA_LABEL = "Eccitabilità elettrica sopraciliare"
_PERIORAL_LABEL = "Eccitabilità elettrica peribuccale"
_DATA_DIR = Path(__file__).resolve().parent


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

# Ordine visivo della tavola sopraciliare 2 colonne x 4 righe:
# VI-V / IV-III / II-I / Nessuna reazione-Non valutabile.
_SUPRA_GRID_OPTIONS = (
    "Fase VI", "Fase V",
    "Fase IV", "Fase III",
    "Fase II", "Fase I",
    "Nessuna reazione", "Non valutabile/non attendibile",
)

# Testo mostrato nel selectbox sopraciliare. I valori interni restano invariati
# per non alterare range, descrizioni, calcoli e compatibilità con il codice esistente.
_SUPRA_DISPLAY_LABELS = {
    "Non valutata": "Non valutata",
    "Fase VI": "Contrazione dei muscoli della fronte, delle palpebre e della guancia | 1–6 h",
    "Fase V": "Contrazione dei muscoli della fronte e delle palpebre | 2–7 h",
    "Fase IV": "Contrazione dei muscoli delle palpebre | 3–8 h",
    "Fase III": "Contrazione dell’intera palpebra superiore | 3 ½–13 h",
    "Fase II": "Contrazione di meno di 2/3 della palpebra superiore | 5–16 h",
    "Fase I": "Contrazione di meno di 1/3 della palpebra superiore | 5–22 h",
    "Nessuna reazione": "Nessuna reazione | > 5 h",
    "Non valutabile/non attendibile": "Non valutabile / non attendibile",
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


class _SuppressedElectricalPopover:
    """Contesto vuoto usato per eliminare i vecchi popover delle immagini."""

    def __enter__(self):
        st._suppress_legacy_electrical_image = True
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        st._suppress_legacy_electrical_image = False
        return False


def _install_responsive_image_css():
    """Adatta le due tavole alla larghezza dello schermo senza alterarne le proporzioni."""
    st.markdown(
        """
        <style>
        .st-key-eccitabilita_sopraciliare_image,
        .st-key-eccitabilita_peribuccale_image {
            width: 100%;
            margin-left: auto;
            margin-right: auto;
        }

        @media (max-width: 768px) {
            .st-key-eccitabilita_sopraciliare_image,
            .st-key-eccitabilita_peribuccale_image {
                max-width: 100%;
            }
        }

        @media (min-width: 769px) {
            .st-key-eccitabilita_sopraciliare_image {
                max-width: 450px;
            }

            .st-key-eccitabilita_peribuccale_image {
                max-width: 820px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _supra_option_from_click(click):
    """Converte il clic nel riquadro sopraciliare della griglia 2 x 4."""
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

    col = min(1, int(x / (width / 2)))
    row = min(3, int(y / (height / 4)))
    return _SUPRA_GRID_OPTIONS[row * 2 + col]


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
            # È sempre il primo dei due parametri: crea una nuova coppia 50/50
            # per il rerun corrente.
            with st.container(key="electrical_pair_layout"):
                electrical_pair["columns"] = original_columns(2, gap="small")

        if electrical_pair["columns"] is None:
            # Fallback difensivo nel caso l'ordine dei parametri venga cambiato.
            with st.container(key="electrical_pair_layout"):
                electrical_pair["columns"] = original_columns(2, gap="small")

        target_index = 0 if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY else 1
        target_column = electrical_pair["columns"][target_index]

        if is_main_row:
            # Il codice chiamante si aspetta due colonne, ma per questi due
            # parametri titolo e contenuto devono stare uno sotto l'altro e
            # sfruttare l'intero 50% disponibile.
            return target_column, target_column

        # Eventuali righe accessorie (orario personalizzato) restano dentro
        # la stessa metà assegnata al parametro.
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
            _render_clickable_selector(
                image=_SUPRA_IMAGE,
                container_key="eccitabilita_sopraciliare_image",
                component_key="eccitabilita_sopraciliare_click",
                last_click_key="_eccitabilita_sopraciliare_last_click",
                widget_key=widget_key,
                options=options,
                option_from_click=_supra_option_from_click,
                show_toast=False,
            )
            kwargs["format_func"] = lambda value: _SUPRA_DISPLAY_LABELS.get(value, value)

        elif label == _PERIORAL_LABEL:
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
