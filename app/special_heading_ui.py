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
        .final-text,
        .final-text p,
        .final-text li {
          text-align: justify !important;
          font-weight: 400 !important;
        }

        .final-text b,
        .final-text strong {
          font-weight: 400 !important;
        }

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

          /* L'intestazione del raffreddamento deve restare su una sola riga
             senza creare barre di scorrimento nel contenitore orizzontale. */
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_row_mobile"],
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_row_mobile"] [data-testid="stHorizontalBlock"] {
            box-sizing: border-box !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            overflow: visible !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_title_mobile"] {
            flex: 1 1 0 !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: none !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_actions_mobile"],
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"] {
            flex: 0 0 auto !important;
            width: auto !important;
            max-width: 100% !important;
            min-width: 0 !important;
            overflow: visible !important;
          }
        }

        body:has([class*="st-key-mostra_parametri_aggiuntivi"])
        [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
        [data-testid="stElementContainer"]:has(.mortem-section-title--supra) {
          margin-bottom: -1.18rem !important;
        }

        @media (min-width: 769px) {
          /* Desktop: titolo + comando Henssge nella stessa riga, senza overflow.
             Le regole hanno specificità volutamente maggiore delle vecchie
             rifiniture che trasformavano il checkbox nel solo simbolo ⦸. */
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_row_desktop"],
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_row_desktop"] [data-testid="stHorizontalBlock"] {
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 0.55rem !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            overflow: visible !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_title_desktop"] {
            flex: 1 1 0 !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-cooling_heading_actions_desktop"] {
            flex: 0 1 auto !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: 62% !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"],
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"] [data-testid="stHorizontalBlock"] {
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 0.20rem !important;
            width: auto !important;
            max-width: 100% !important;
            min-width: 0 !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] {
            flex: 0 1 auto !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: 100% !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label {
            position: relative !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: 100% !important;
            height: auto !important;
            min-height: 1.55rem !important;
            max-height: none !important;
            margin: 0 !important;
            padding: 0 !important;
            white-space: nowrap !important;
            overflow: visible !important;
            cursor: pointer !important;
          }

          /* Il controllo desktop conserva la stessa logica del checkbox ma
             visualizza il testo richiesto al posto del simbolo di divieto. */
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label > * {
            position: absolute !important;
            opacity: 0 !important;
            pointer-events: none !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label::after {
            content: "Metodo di Henssge non applicabile" !important;
            position: static !important;
            display: block !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            font-size: 0.82rem !important;
            line-height: 1.15 !important;
            font-weight: 500 !important;
            color: inherit !important;
            opacity: 0.72 !important;
            white-space: nowrap !important;
            overflow: visible !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label:has(input:checked)::after {
            color: #c62828 !important;
            opacity: 1 !important;
            font-weight: 700 !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-mortem_help_henssge"] {
            flex: 0 0 auto !important;
            width: 1.6rem !important;
            min-width: 1.6rem !important;
            max-width: 1.6rem !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def markdown_with_special_heading(body, *args, **kwargs):
        if isinstance(body, str) and "mortem-full-title" in body:
            original_markdown(
                """
                <style>
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
