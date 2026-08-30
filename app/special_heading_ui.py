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

        /* Campi numerici del raffreddamento: larghezza omogenea dimensionata
           sul testo più lungo del gruppo, senza occupare tutta la riga. */
        html body:has([class*="st-key-stima_cautelativa_beta"]) {
          --mortem-cooling-field-width: 24rem;
          --mortem-cooling-suggest-width: 5.4rem;
        }

        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-mortem_decimal_"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_"]) {
          box-sizing: border-box !important;
          width: min(100%, var(--mortem-cooling-field-width)) !important;
          max-width: var(--mortem-cooling-field-width) !important;
          min-width: 0 !important;
          align-self: flex-start !important;
        }

        /* I soli campi che mostrano davvero “Consiglia” conservano a destra
           la larghezza del pulsante; il campo numerico termina prima. */
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-mortem_decimal_fc_other_val"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_fc_other_val"]),
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-mortem_decimal_fattore_correzione"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_fattore_correzione"]) {
          width: min(100%, calc(var(--mortem-cooling-field-width) + var(--mortem-cooling-suggest-width))) !important;
          max-width: calc(var(--mortem-cooling-field-width) + var(--mortem-cooling-suggest-width)) !important;
        }

        /* FC min non deve più riservare un falso pulsante invisibile. */
        html body:has([class*="st-key-stima_cautelativa_beta"])
        .number-control.reserve-suggest .suggest-button {
          display: none !important;
          flex: 0 0 0 !important;
          width: 0 !important;
          min-width: 0 !important;
          max-width: 0 !important;
          padding: 0 !important;
          border: 0 !important;
        }

        /* Valore appena sufficiente per le cifre visualizzate; −/+ restano
           subito dopo l'eventuale unità di misura. */
        html body:has([class*="st-key-stima_cautelativa_beta"])
        .number-control:not(.is-dense) .number-input {
          flex: 0 0 48px !important;
          width: 48px !important;
          min-width: 48px !important;
          padding-left: 1px !important;
          padding-right: 3px !important;
        }

        html body:has([class*="st-key-stima_cautelativa_beta"])
        .number-control:not(.is-dense) .step-button {
          flex: 0 0 30px !important;
          width: 30px !important;
        }

        html body:has([class*="st-key-stima_cautelativa_beta"])
        .number-control .mobile-unit {
          padding-left: 0 !important;
          padding-right: 3px !important;
        }

        /* Peso + ±3 kg: il toggle segue subito il campo compatto invece di
           essere spinto al margine destro del riquadro. */
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_row_mobile"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_row_mobile"] [data-testid="stHorizontalBlock"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_row_desktop"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_row_desktop"] [data-testid="stHorizontalBlock"] {
          display: flex !important;
          flex-direction: row !important;
          flex-wrap: nowrap !important;
          align-items: center !important;
          justify-content: flex-start !important;
          gap: 0.34rem !important;
          width: fit-content !important;
          max-width: 100% !important;
          min-width: 0 !important;
        }

        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_value_mobile"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_value_desktop"] {
          flex: 0 1 var(--mortem-cooling-field-width) !important;
          width: var(--mortem-cooling-field-width) !important;
          max-width: var(--mortem-cooling-field-width) !important;
          min-width: 0 !important;
        }

        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_uncertainty_mobile"],
        html body:has([class*="st-key-stima_cautelativa_beta"])
        [class*="st-key-prudent_weight_uncertainty_desktop"] {
          flex: 0 0 auto !important;
          width: max-content !important;
          min-width: max-content !important;
          margin-left: 0 !important;
        }

        @media (max-width: 768px) {
          html body:has([class*="st-key-stima_cautelativa_beta"]) {
            --mortem-cooling-field-width: 17.5rem;
          }

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

          /* Il pannello di suggerimento sale fino alla riga FC/Consiglia e
             aumenta appena il respiro tra stato del corpo e vestiti/coperte. */
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"] {
            margin-top: -0.22rem !important;
            padding-top: 0.42rem !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"] [class*="st-key-fcpanel_std_switch_row"],
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"] [class*="st-key-fcpanel_caut_switch_row"] {
            margin-top: 0.22rem !important;
            margin-bottom: 0.06rem !important;
          }

          /* FC suggerito + Usalo: centrati come gruppo, con un piccolo spazio
             tra il valore e il pulsante. */
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="fc_apply_block_mobile"] {
            width: 100% !important;
            margin-top: 0.12rem !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="fc_apply_row_mobile"],
          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="fc_apply_row_mobile"] [data-testid="stHorizontalBlock"] {
            width: fit-content !important;
            max-width: 100% !important;
            min-width: 0 !important;
            margin-left: auto !important;
            margin-right: auto !important;
            justify-content: center !important;
            gap: 0.32rem !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="fc_apply_value_mobile"] .mortem-fc-inline-result {
            padding-left: 0 !important;
            padding-right: 0 !important;
          }

          html body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="fc_apply_action_mobile"] {
            margin-left: 0.04rem !important;
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
