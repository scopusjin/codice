# -*- coding: utf-8 -*-
"""Layout responsive della schermata completa di Mor-tem.

Il CSS viene allegato al blocco di stile iniziale ``.final-text`` della pagina,
quindi dopo ``st.set_page_config`` ma prima dei widget, a ogni rerun. In questo
modo il layout mobile è già attivo al primo render e non dipende da
manipolazioni DOM post-render del componente numerico.
"""

import html
import re

import streamlit as st

from app.locales.it_ui import ui_text


_PRUDENT_HELP_TEXT = re.sub(r"<[^>]+>", "", ui_text("full.prudent_default_note")).strip()


_FULL_MOBILE_CSS = r"""
<style>
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent"] button,
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_henssge"] button {
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

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_henssge"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent_electrical_"] {
  flex: 0 0 18px !important;
  width: 18px !important;
  min-width: 18px !important;
  max-width: 18px !important;
  height: 18px !important;
  min-height: 18px !important;
  max-height: 18px !important;
  align-self: center !important;
  margin: 0 !important;
  padding: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent"] button,
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_henssge"] button,
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent_electrical_"] button {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  vertical-align: middle !important;
  margin: 0 !important;
  transform: none !important;
}

/* Il triangolino standard dei popover non serve nei piccoli pulsanti di aiuto
   e li fa apparire decentrati rispetto alle etichette. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent"] button [data-testid="stIconMaterial"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_henssge"] button [data-testid="stIconMaterial"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent_electrical_"] button [data-testid="stIconMaterial"] {
  display: none !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_prudent"] button p,
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_henssge"] button p {
  margin: 0 !important;
  font-size: 0.72rem !important;
  line-height: 1 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_row_prudent"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_row_henssge"] {
  align-items: center !important;
  gap: 0.35rem !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_row_prudent"] [data-testid="stHorizontalBlock"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_help_row_henssge"] [data-testid="stHorizontalBlock"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-electrical_title_help_row_"] [data-testid="stHorizontalBlock"] {
  align-items: center !important;
}

.mortem-help-copy {
  max-width: min(82vw, 30rem);
  font-size: 0.90rem;
  line-height: 1.28;
}

.mortem-help-copy-intro {
  margin: 0 0 0.38rem 0;
}

.mortem-help-copy-bullet {
  margin: 0.12rem 0;
  padding-left: 0.95rem;
  text-indent: -0.78rem;
}

@media (max-width: 768px) {
  /* Le regole principali sono limitate alla schermata completa: la MSIL non
     possiede il toggle stima_cautelativa_beta. */
  body:has([class*="st-key-stima_cautelativa_beta"]) .mortem-full-field-heading {
    display: none !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stElementContainer"]:has(.mortem-full-field-heading) {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Compatta solo i blocchi iniziali della Full mobile. I selettori usati per
     riconoscere i riquadri non esistono insieme nella MSIL. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-usa_orario_custom"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-selettore_macchie_ui"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"]) {
    padding: 0.55rem 0.70rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-usa_orario_custom"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-selettore_macchie_ui"]) {
    margin-bottom: -0.32rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_prudent"] {
    margin-top: -0.20rem !important;
    margin-bottom: -0.20rem !important;
  }

  /* Su mobile la spiegazione generale delle condizioni variabili resta
     disponibile tramite l'helper del toggle e non occupa spazio nel form. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-prudent_explicit_ranges"] {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Riserva subito l'altezza dei componenti numerici custom: l'iframe nasce
     già a 40 px e il layout non deve riassestarsi quando il JS del controllo
     termina l'inizializzazione. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_"] {
    min-height: 40px !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_"] iframe {
    display: block !important;
    height: 40px !important;
    min-height: 40px !important;
    max-height: 40px !important;
  }

  /* Le note aperte dai ? della temperatura restano aderenti al controllo
     senza introdurre il grande spazio verticale del caption predefinito. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-ta_standard_help_note"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-ta_range_help_note"] {
    margin-top: -0.90rem !important;
    margin-bottom: -0.18rem !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-ta_standard_help_note"] [data-testid="stCaptionContainer"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-ta_range_help_note"] [data-testid="stCaptionContainer"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-ta_standard_help_note"] p,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-ta_range_help_note"] p {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 0.82rem !important;
    line-height: 1.22 !important;
  }

  /* Le righe Streamlit dei parametri diventano una pila di controlli a
     tutta larghezza già al primo render. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_rt_val"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_ta_base_val"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_fattore_correzione"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_fc_min_val"]) {
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    gap: clamp(0.10rem, 0.5vw, 0.18rem) !important;
    width: 100% !important;
    margin: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_rt_val"])
  > [data-testid="column"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_ta_base_val"])
  > [data-testid="column"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_fattore_correzione"])
  > [data-testid="column"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_fc_min_val"])
  > [data-testid="column"] {
    flex: 0 0 auto !important;
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_rt_val"])
  > [data-testid="column"] > [data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_ta_base_val"])
  > [data-testid="column"] > [data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_fattore_correzione"])
  > [data-testid="column"] > [data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_fc_min_val"])
  > [data-testid="column"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
  }

  /* Su mobile il comando Consiglia è integrato nel controllo FC. Il vecchio
     toggle Streamlit resta montato per conservare lo stato del pannello, ma
     non occupa più una colonna visibile. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="column"]:has([class*="st-key-toggle_fattore_inline"]) {
    display: none !important;
    width: 0 !important;
    max-width: 0 !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-toggle_fattore_inline"] {
    display: none !important;
  }

  /* Nella modalità con intervalli le righe separate hanno la stessa distanza
     delle righe interne della pila, senza dipendere dal gap di Streamlit. */
  body:has([class*="st-key-prudent_explicit_ranges"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_ta_base_val"]),
  body:has([class*="st-key-prudent_explicit_ranges"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_fc_min_val"]) {
    margin-top: -0.55rem !important;
  }

  /* In modalità standard uniforma lo spazio Peso → T. amb. media alle altre righe. */
  body:has([class*="st-key-stima_cautelativa_beta"]):not(:has([class*="st-key-prudent_explicit_ranges"]))
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_ta_base_val"]) {
    margin-top: -0.55rem !important;
  }

  /* Riga Peso: il controllo prende tutto lo spazio residuo; ±3 kg occupa
     esattamente il proprio contenuto e non può spezzarsi. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-peso_stimato_beta"]):not(:has([class*="st-key-mortem_decimal_rt_val"])) {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) max-content !important;
    align-items: center !important;
    column-gap: clamp(0.10rem, 0.8vw, 0.22rem) !important;
    row-gap: 0 !important;
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-peso_stimato_beta"]):not(:has([class*="st-key-mortem_decimal_rt_val"]))
  > [data-testid="column"] {
    width: auto !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-peso_stimato_beta"]):not(:has([class*="st-key-mortem_decimal_rt_val"]))
  > [data-testid="column"]:nth-child(2),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] [data-testid="stToggle"] {
    width: max-content !important;
    max-width: max-content !important;
    min-width: max-content !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] label {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: clamp(0.16rem, 0.7vw, 0.26rem) !important;
    width: max-content !important;
    min-width: max-content !important;
    margin: 0 !important;
    padding: 0 !important;
    white-space: nowrap !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] label p,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] label span {
    width: max-content !important;
    min-width: max-content !important;
    white-space: nowrap !important;
    overflow-wrap: normal !important;
    word-break: keep-all !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"].mortem-decimal-compact-row {
    gap: clamp(0.22rem, 1vw, 0.36rem) !important;
    row-gap: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlock"].mortem-decimal-compact-stack {
    gap: clamp(0.22rem, 1vw, 0.36rem) !important;
  }

  /* Pannello Suggerisci FC della schermata completa. I prefissi std/caut sono
     distinti da fcpanel_mobile usato dalla MSIL. Il bordo esterno del blocco
     Raffreddamento resta; sul mobile si elimina soltanto il bordo annidato del
     pannello FC per evitare riquadri dentro riquadri. */
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"])),
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"])) {
    border: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0.10rem 0 !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stVerticalBlock"],
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stVerticalBlock"] {
    gap: clamp(0.24rem, 1.1vw, 0.42rem) !important;
  }

  /* I tre stati del corpo devono restare sempre sulla stessa riga, anche sui
     telefoni più stretti. */
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  div[role="radiogroup"],
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  div[role="radiogroup"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: clamp(0.08rem, 0.7vw, 0.18rem) !important;
    width: 100% !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  div[role="radiogroup"] > label,
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  div[role="radiogroup"] > label {
    flex: 0 1 auto !important;
    min-width: 0 !important;
    margin: 0 !important;
    white-space: nowrap !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  div[role="radiogroup"] > label p,
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  div[role="radiogroup"] > label p {
    font-size: clamp(0.74rem, 3.3vw, 0.84rem) !important;
    white-space: nowrap !important;
  }

  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_std_toggle_vestito"]),
  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_caut_toggle_vestito"]) {
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    gap: clamp(0.18rem, 1vw, 0.32rem) !important;
    width: 100% !important;
  }

  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_std_toggle_vestito"])
  > [data-testid="column"],
  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_caut_toggle_vestito"])
  > [data-testid="column"] {
    flex: 0 0 auto !important;
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stToggle"],
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stToggle"] {
    margin: 0 !important;
    padding: 0 !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stSelectbox"] > label,
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stSelectbox"] > label {
    margin-bottom: 0.15rem !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stButton"] button,
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stButton"] button {
    min-height: 2.2rem !important;
  }
}

@media (min-width: 769px) {
  body:has([class*="st-key-stima_cautelativa_beta"]) .block-container {
    padding-top: 2rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-desktop_caut_fc_range_row"] {
    width: 100% !important;
    min-width: 0 !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    gap: 0.40rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-desktop_caut_fc_range_values"] {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-desktop_caut_fc_range_values"] > [data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-desktop_caut_fc_range_action"] {
    flex: 0 0 5.3rem !important;
    width: 5.3rem !important;
    min-width: 5.3rem !important;
    max-width: 5.3rem !important;
    align-self: stretch !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-desktop_caut_fc_range_suggest"] [data-testid="stButton"] > button {
    box-sizing: border-box !important;
    width: 100% !important;
    min-width: 0 !important;
    height: 5.35rem !important;
    min-height: 5.35rem !important;
    max-height: 5.35rem !important;
    margin: 0 !important;
    padding: 0.25rem 0.35rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 0.48rem !important;
    white-space: nowrap !important;
  }
}
</style>
"""


_FIELD_HEADING_TOKENS = (
    "T. rettale",
    "T. ante-mortem",
    "Peso",
    "T. ambientale",
    "Fattore di correzione",
)


def _tag_full_field_heading(body):
    if not isinstance(body, str):
        return body
    if "font-size: 0.88rem;" not in body or "padding-top" in body:
        return body
    body_folded = body.casefold()
    if not any(token.casefold() in body_folded for token in _FIELD_HEADING_TOKENS):
        return body

    source_single = "<div style='font-size: 0.88rem;'>"
    source_double = '<div style="font-size: 0.88rem;">'
    replacement = "<div class='mortem-full-field-heading' style='font-size: 0.88rem;'>"
    if source_single in body:
        return body.replace(source_single, replacement, 1)
    if source_double in body:
        return body.replace(source_double, replacement, 1)
    return body


def _render_click_help(text: str, key: str) -> None:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    blocks = []
    for line in lines:
        escaped = html.escape(line)
        css_class = "mortem-help-copy-bullet" if line.startswith("•") else "mortem-help-copy-intro"
        blocks.append(f'<div class="{css_class}">{escaped}</div>')
    content = f'<div class="mortem-help-copy">{"".join(blocks)}</div>'

    with st.container(width="content", key=key):
        with st.popover("?"):
            st.markdown(content, unsafe_allow_html=True)


def install_full_mobile_layout():
    """Installa il layout senza eseguire comandi Streamlit all'import."""
    if getattr(st, "_full_mobile_layout_installed", False):
        return

    original_markdown = st.markdown
    original_toggle = st.toggle
    original_checkbox = st.checkbox
    original_number_input = st.number_input

    def markdown_with_full_mobile_layout(body, *args, **kwargs):
        tagged_body = _tag_full_field_heading(body)
        if isinstance(tagged_body, str) and ".final-text{" in tagged_body:
            tagged_body = _FULL_MOBILE_CSS + tagged_body
            kwargs["unsafe_allow_html"] = True
        return original_markdown(tagged_body, *args, **kwargs)

    def toggle_with_full_mobile_help(label, *args, **kwargs):
        if kwargs.get("key") != "stima_cautelativa_beta":
            return original_toggle(label, *args, **kwargs)

        kwargs.pop("help", None)
        with st.container(
            horizontal=True,
            horizontal_alignment="left",
            gap="small",
            key="mortem_help_row_prudent",
        ):
            result = original_toggle(label, *args, **kwargs)
            _render_click_help(_PRUDENT_HELP_TEXT, "mortem_help_prudent")
        return result

    def checkbox_with_full_mobile_help(label, *args, **kwargs):
        if kwargs.get("key") != "henssge_non_applicabile":
            return original_checkbox(label, *args, **kwargs)

        help_text = kwargs.pop("help", None) or ui_text("full.henssge_not_applicable_help")
        with st.container(
            horizontal=True,
            horizontal_alignment="left",
            gap="small",
            key="mortem_help_row_henssge",
        ):
            result = original_checkbox(label, *args, **kwargs)
            _render_click_help(help_text, "mortem_help_henssge")
        return result

    def _toggle_desktop_range_fc_suggest() -> None:
        same_open_target = bool(
            st.session_state.get("toggle_fattore_inline", False)
            and st.session_state.get("__full_fc_suggest_target") == "range"
        )
        if same_open_target:
            st.session_state["toggle_fattore_inline"] = False
            st.session_state["toggle_fattore"] = False
            st.session_state.pop("__full_fc_suggest_target", None)
            return

        st.session_state["toggle_fattore_inline"] = True
        st.session_state["toggle_fattore"] = True
        st.session_state["__full_fc_suggest_target"] = "range"

    def number_input_with_desktop_range_action(label, *args, **kwargs):
        key = kwargs.get("key")
        desktop_range = bool(
            not st.session_state.get("__full_device_mobile", False)
            and st.session_state.get("stima_cautelativa_beta", False)
            and st.session_state.get("range_unico_beta", False)
            and key in {"fc_min_val", "fc_other_val"}
        )
        if not desktop_range or args:
            return original_number_input(label, *args, **kwargs)

        if key == "fc_other_val":
            if st.session_state.pop("__desktop_caut_fc_max_pre_rendered", False):
                return st.session_state.pop(
                    "__desktop_caut_fc_max_rendered_value",
                    st.session_state.get("fc_other_val", kwargs.get("value")),
                )
            return original_number_input(label, *args, **kwargs)

        range_mode = st.session_state.get("range_unico_beta", False)
        max_kwargs = dict(kwargs)
        max_kwargs["key"] = "fc_other_val"
        max_kwargs["value"] = st.session_state.get("fc_other_val", kwargs.get("value"))

        with st.container(
            horizontal=True,
            wrap=False,
            vertical_alignment="top",
            gap="small",
            key="desktop_caut_fc_range_row",
        ):
            with st.container(width="stretch", gap="small", key="desktop_caut_fc_range_values"):
                st.session_state["range_unico_beta"] = False
                try:
                    min_value = original_number_input(label, **kwargs)
                    max_value = original_number_input(
                        ui_text("full.fc_max_input"),
                        **max_kwargs,
                    )
                finally:
                    st.session_state["range_unico_beta"] = range_mode

            with st.container(width="content", key="desktop_caut_fc_range_action"):
                active = bool(
                    st.session_state.get("toggle_fattore_inline", False)
                    and st.session_state.get("__full_fc_suggest_target") == "range"
                )
                st.button(
                    "Consiglia",
                    key="desktop_caut_fc_range_suggest",
                    type="primary" if active else "secondary",
                    width="stretch",
                    on_click=_toggle_desktop_range_fc_suggest,
                )

        st.session_state["__desktop_caut_fc_max_pre_rendered"] = True
        st.session_state["__desktop_caut_fc_max_rendered_value"] = max_value
        return min_value

    st.markdown = markdown_with_full_mobile_layout
    st.toggle = toggle_with_full_mobile_help
    st.checkbox = checkbox_with_full_mobile_help
    st.number_input = number_input_with_desktop_range_action
    st._full_mobile_layout_installed = True
