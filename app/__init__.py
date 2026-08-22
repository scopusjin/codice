# -*- coding: utf-8 -*-

import streamlit as st

import app.perioral_single_grid as _perioral_single_grid
import app.sopraciliare_ui as _sopraciliare_ui
from app.special_heading_ui import install_special_heading_style
from app.supra_single_grid import install_supra_single_grid

# La tavola peribuccale originale lascia più bianco sotto i disegni rispetto
# alla sopraciliare: riduciamo soltanto qui la quota di immagine conservata.
_perioral_single_grid._IMAGE_ONLY_FRACTION = 0.56

install_supra_single_grid(_sopraciliare_ui)
_perioral_single_grid.install_perioral_single_grid(_sopraciliare_ui)
_sopraciliare_ui.install_sopraciliare_click_selector()

_electrical_selectbox = st.selectbox


def _selectbox_with_perioral_grid(label, options, *args, **kwargs):
    if label == _sopraciliare_ui._PERIORAL_LABEL:
        return _sopraciliare_ui._render_perioral_tile_grid(
            widget_key=kwargs.get("key"),
            options=list(options),
        )
    return _electrical_selectbox(label, options, *args, **kwargs)


st.selectbox = _selectbox_with_perioral_grid
install_special_heading_style()
