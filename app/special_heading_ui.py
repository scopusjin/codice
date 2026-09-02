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

_FULL_DESKTOP_LAYOUT_CSS = """
<style>
[class*="st-key-mortem_result_box"] {
  box-sizing: border-box !important;
  background: color-mix(in srgb, var(--st-primary-color, #168AC1) 6%, var(--st-background-color, #FFFFFF)) !important;
  border-color: color-mix(in srgb, var(--st-primary-color, #168AC1) 32%, transparent) !important;
  border-radius: 10px !important;
  padding: 0.45rem 0.55rem 0.55rem !important;
  margin-top: 0.15rem !important;
  margin-bottom: 0.30rem !important;
}

[class*="st-key-mortem_result_box"] > [data-testid="stVerticalBlock"] {
  gap: 0.30rem !important;
}

/* Le righe dei titoli elettrici devono avere altezza naturale: nessuna
   scrollbar, ma il titolo resta aderente alla griglia di immagini. */
[class*="st-key-electrical_title_help_row_"],
[class*="st-key-electrical_title_help_row_"] [data-testid="stHorizontalBlock"] {
  box-sizing: border-box !important;
  height: auto !important;
  min-height: 0 !important;
  max-height: none !important;
  overflow: visible !important;
  margin-top: 0 !important;
  margin-bottom: -0.30rem !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

[class*="st-key-electrical_title_text_"],
[class*="st-key-electrical_title_text_"] .mortem-section-title {
  height: auto !important;
  min-height: 0 !important;
  max-height: none !important;
  overflow: visible !important;
}

@media (min-width: 769px) {
  [class*="st-key-electrical_title_help_row_"],
  [class*="st-key-electrical_title_help_row_"] [data-testid="stHorizontalBlock"] {
    margin-bottom: -0.65rem !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] {
    box-sizing: border-box !important;
    width: min(100%, 46rem) !important;
    max-width: 46rem !important;
    margin-left: 0 !important;
    margin-right: auto !important;
  }

  /* Data/ora principale: niente riquadro esterno, restano solo titolo e campi. */
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-inspection_datetime_row"]),
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-inspection_datetime_row"])
  > [data-testid="stVerticalBlock"] {
    border: 0 !important;
    border-width: 0 !important;
    border-color: transparent !important;
    outline: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-inspection_datetime_row"]) {
    padding: 0 !important;
  }

  /* Raffreddamento: titolo/Henssge e Condizioni variabili più vicini. */
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"]):has([class*="st-key-stima_cautelativa_beta"])
  > [data-testid="stVerticalBlock"] {
    gap: 0.18rem !important;
  }

  /* Nelle versioni recenti di Streamlit il contenitore con bordo coincide
     con lo stVerticalBlock: limita direttamente gli intervalli tra intestazione,
     helper, campi di temperatura e fattore di correzione. */
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stVerticalBlock"]:has(> [data-testid="stLayoutWrapper"] [class~="st-key-mortem_help_row_henssge"]):has(> [data-testid="stLayoutWrapper"] > [class~="st-key-mortem_help_row_prudent"]) {
    gap: 0.45rem !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [class*="st-key-cooling_heading_row_desktop"] {
    margin-bottom: -0.08rem !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [class*="st-key-mortem_help_row_prudent"] {
    margin-top: -0.08rem !important;
    margin-bottom: 0 !important;
  }
}

/* Sotto 1440 px deve vincere sempre il flusso naturale Streamlit, anche sulla
   vecchia regola elettrica che viene emessa più tardi durante il primo render. */
@media (min-width: 769px) and (max-width: 1439px) {
  html body:has(.mortem-full-title):has(.mortem-full-title):has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] {
    width: min(100%, 46rem) !important;
    max-width: 46rem !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title):has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    display: block !important;
    position: static !important;
    grid-template-columns: none !important;
    grid-auto-flow: initial !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title):has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {
    grid-column: auto !important;
    grid-row: auto !important;
    position: static !important;
    top: auto !important;
    left: auto !important;
    right: auto !important;
    width: auto !important;
    max-width: none !important;
    z-index: auto !important;
  }
}

/* Desktop realmente largo: tutti gli input, compresi i dati speciali, restano
   nello stack sinistro. Pulsante e risultato occupano la colonna destra. */
@media (min-width: 1440px) {
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] {
    width: min(100%, 82rem) !important;
    max-width: 82rem !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    display: grid !important;
    position: relative !important;
    grid-template-columns: minmax(44rem, 46rem) minmax(28rem, 34rem) !important;
    grid-auto-flow: row !important;
    justify-content: start !important;
    column-gap: 1rem !important;
    row-gap: 0.30rem !important;
    align-items: start !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {
    grid-column: 1 !important;
    grid-row: auto !important;
    min-width: 0 !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > *:has(.mortem-full-title) {
    grid-column: 1 / -1 !important;
    grid-row: 1 !important;
  }

  /* Dati speciali nello stack sinistro. */
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > [class*="st-key-mostra_parametri_aggiuntivi"],
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > *:has([class*="st-key-mostra_parametri_aggiuntivi"]),
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > [class*="st-key-electrical_pair_layout"],
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > *:has([class*="st-key-electrical_pair_layout"]) {
    grid-column: 1 !important;
    grid-row: auto !important;
    position: static !important;
    top: auto !important;
    left: auto !important;
    right: auto !important;
    width: auto !important;
    max-width: none !important;
    margin: 0 !important;
    z-index: auto !important;
  }

  /* Pulsante di calcolo: colonna destra, sopra il risultato e sempre raggiungibile. */
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > *:has([class*="st-key-btn_stima"]) {
    grid-column: 2 !important;
    grid-row: 2 !important;
    position: sticky !important;
    top: 1rem !important;
    width: 100% !important;
    max-width: 34rem !important;
    align-self: start !important;
    margin: 0 !important;
    z-index: 4 !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > *:has([class*="st-key-btn_stima"]) [data-testid="stHorizontalBlock"] {
    width: 100% !important;
    max-width: 100% !important;
    overflow: visible !important;
  }

  /* Grafico + frase di riepilogo: sotto il pulsante, sticky nella stessa colonna. */
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > [class*="st-key-mortem_result_box"],
  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
  > *:has([class*="st-key-mortem_result_box"]) {
    grid-column: 2 !important;
    grid-row: 3 / span 12 !important;
    position: sticky !important;
    top: 4.7rem !important;
    width: 100% !important;
    max-width: 34rem !important;
    align-self: start !important;
    margin: 0 !important;
    z-index: 3 !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
  > [data-testid="stVerticalBlock"] {
    gap: 0.16rem !important;
  }

  html body:has(.mortem-full-title):has(.mortem-full-title)
  [class*="st-key-special_datetime_row_"] {
    margin-top: -0.12rem !important;
    margin-bottom: 0 !important;
  }
}
</style>
"""


def install_special_heading_style():
    """Rende più evidenti e ravvicinati i titoli senza modificare le stringhe localizzate."""
    if getattr(st, "_special_heading_style_installed", False):
        return

    original_markdown = st.markdown
    original_set_page_config = st.set_page_config
    original_pyplot = st.pyplot
    original_container = st.container
    original_columns = st.columns
    result_box_state = {
        "container": None,
        "full_page": False,
    }

    def _called_from_graphing(function_name):
        frame = inspect.currentframe().f_back
        for _ in range(10):
            if frame is None:
                break
            filename = str(frame.f_globals.get("__file__", "")).replace("\\", "/")
            if filename.endswith("/app/graphing.py") and frame.f_code.co_name == function_name:
                return True
            frame = frame.f_back
        return False

    def _result_box():
        if result_box_state["container"] is None:
            result_box_state["container"] = original_container(
                border=True,
                key="mortem_result_box",
            )
        return result_box_state["container"]

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

    def set_page_config_with_full_layout(*args, **kwargs):
        result = original_set_page_config(*args, **kwargs)
        result_box_state["container"] = None
        result_box_state["full_page"] = kwargs.get("page_title") == "Mor-tem"
        if result_box_state["full_page"]:
            original_markdown(_FULL_DESKTOP_LAYOUT_CSS, unsafe_allow_html=True)
        return result

    def pyplot_with_result_box(*args, **kwargs):
        if result_box_state["full_page"] and _called_from_graphing("aggiorna_grafico"):
            with _result_box():
                return original_pyplot(*args, **kwargs)
        return original_pyplot(*args, **kwargs)

    def columns_with_result_box(*args, **kwargs):
        # Il layout elettrico sottostante legge parametro_id dal chiamante
        # immediato: propaghiamo il contesto attraverso questo wrapper.
        frame = inspect.currentframe().f_back
        parametro_id = frame.f_locals.get("parametro_id") if frame else None
        if result_box_state["full_page"] and _called_from_graphing("aggiorna_grafico"):
            with _result_box():
                return original_columns(*args, **kwargs)
        return original_columns(*args, **kwargs)

    def markdown_with_special_heading(body, *args, **kwargs):
        if result_box_state["full_page"] and _called_from_graphing("render_frase_breve"):
            with _result_box():
                return original_markdown(body, *args, **kwargs)

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

    st.set_page_config = set_page_config_with_full_layout
    st.pyplot = pyplot_with_result_box
    st.columns = columns_with_result_box
    st.markdown = markdown_with_special_heading
    st._special_heading_style_installed = True
