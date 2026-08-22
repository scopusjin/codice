# -*- coding: utf-8 -*-

import streamlit as st

from app import i18n as _i18n
import app.perioral_single_grid as _perioral_single_grid
import app.sopraciliare_ui as _sopraciliare_ui
from app.inspection_datetime_ui import install_inspection_datetime_ui
from app.special_datetime_ui import install_special_datetime_ui
from app.special_heading_ui import install_special_heading_style
from app.supra_single_grid import install_supra_single_grid

# La tavola peribuccale originale lascia più bianco sotto i disegni rispetto
# alla sopraciliare. Manteniamo però bocca e mento integralmente visibili.
_perioral_single_grid._IMAGE_ONLY_FRACTION = 0.82


# Nelle sole frasi di stima dell'epoca del decesso con data/ora preferiamo
# "vale a dire" a "ovvero", senza modificare gli altri testi localizzati.
def _replace_ovvero_in_estimate(function):
    def wrapped(*args, **kwargs):
        result = function(*args, **kwargs)
        if isinstance(result, str):
            return result.replace("ovvero", "vale a dire")
        return result

    return wrapped


for _estimate_function_name in (
    "simple_sentence_dt_not_over",
    "simple_sentence_dt_over",
    "simple_sentence_dt_range",
    "final_sentence_dt_over",
    "final_sentence_dt_not_over",
    "final_sentence_dt_range",
):
    setattr(
        _i18n,
        _estimate_function_name,
        _replace_ovvero_in_estimate(getattr(_i18n, _estimate_function_name)),
    )


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
install_special_datetime_ui()
install_inspection_datetime_ui()
