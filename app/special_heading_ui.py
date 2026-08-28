# -*- coding: utf-8 -*-
"""Stile dei titoli dei parametri tanatologici speciali."""

import html
import inspect

import streamlit as st

from app.special_tanatology_states import (
    PARAM_CHEMICAL_PUPILLARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_MECHANICAL_MUSCLE,
)


_SPECIAL_PARAM_IDS = {
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_MECHANICAL_MUSCLE,
    PARAM_CHEMICAL_PUPILLARY,
}


def install_special_heading_style():
    """Rende più evidenti e ravvicinati i titoli senza modificare le stringhe localizzate."""
    if getattr(st, "_special_heading_style_installed", False):
        return

    original_markdown = st.markdown

    def markdown_with_special_heading(body, *args, **kwargs):
        # Altri piccoli wrapper UI possono trovarsi tra questa funzione e il
        # ciclo dei parametri: recuperiamo il contesto risalendo pochi frame.
        frame = inspect.currentframe().f_back
        parametro_id = None
        nome_parametro = None
        for _ in range(5):
            if frame is None:
                break
            if parametro_id is None:
                parametro_id = frame.f_locals.get("parametro_id")
            if nome_parametro is None:
                nome_parametro = frame.f_locals.get("nome_parametro")
            if parametro_id is not None and nome_parametro is not None:
                break
            frame = frame.f_back

        if (
            parametro_id in _SPECIAL_PARAM_IDS
            and isinstance(body, str)
            and isinstance(nome_parametro, str)
            and nome_parametro in body
        ):
            body = (
                "<div class='mortem-section-title'>"
                f"{html.escape(nome_parametro)}"
                "</div>"
            )
            kwargs["unsafe_allow_html"] = True

        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_special_heading
    st._special_heading_style_installed = True
