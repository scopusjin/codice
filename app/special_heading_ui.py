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

    original_markdown(
        """
        <style>
        @media (max-width: 768px) {
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"]) {
            padding: 0.42rem 0.62rem !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
          [data-testid="stVerticalBlock"] {
            gap: 0.10rem !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
          [data-testid="stElementContainer"]:has(.mortem-section-title) {
            margin: 0 0 -0.58rem 0 !important;
            padding: 0 !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
          [data-testid="stElementContainer"]:has(.mortem-section-title--supra) {
            margin-bottom: -1.18rem !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-electrical_pair_layout"] [data-testid="stHorizontalBlock"] {
            margin: 0 !important;
          }
        }

        body:has([class*="st-key-mostra_parametri_aggiuntivi"])
        [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
        [data-testid="stElementContainer"]:has(.mortem-section-title--supra) {
          margin-bottom: -1.18rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
            title_class = "mortem-section-title"
            if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY:
                title_class += " mortem-section-title--supra"
            body = (
                f"<div class='{title_class}'>"
                f"{html.escape(nome_parametro)}"
                "</div>"
            )
            kwargs["unsafe_allow_html"] = True

        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_special_heading
    st._special_heading_style_installed = True
