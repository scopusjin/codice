# -*- coding: utf-8 -*-
"""Regole di compattezza aggiuntive per la sola Full mobile."""

import streamlit as st


_FULL_MOBILE_COMPACT_CSS = r"""
<style>
@media (max-width: 768px) {
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"]) {
    padding: 0.42rem 0.34rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_row_mobile"] {
    width: 100% !important;
    min-width: 0 !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_title_mobile"] {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_actions_mobile"] {
    flex: 0 0 auto !important;
    width: max-content !important;
    min-width: max-content !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] {
    width: max-content !important;
    min-width: max-content !important;
    gap: 0.10rem !important;
    margin: 0 !important;
    padding: 0 !important;
    justify-content: flex-end !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] {
    width: 1.55rem !important;
    min-width: 1.55rem !important;
    max-width: 1.55rem !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 1.55rem !important;
    min-width: 1.55rem !important;
    height: 1.55rem !important;
    min-height: 1.55rem !important;
    margin: 0 !important;
    padding: 0 !important;
    cursor: pointer !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label > * {
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label::after {
    content: "⦸";
    position: static !important;
    display: block !important;
    font-size: 1.22rem !important;
    line-height: 1 !important;
    font-weight: 500 !important;
    opacity: 0.58;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label:has(input:checked)::after {
    opacity: 1 !important;
    color: #c62828 !important;
    font-weight: 700 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] {
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0.34rem 0.24rem !important;
    border: 0 !important;
    border-radius: 0.55rem !important;
    box-shadow: none !important;
    background: rgba(33, 150, 243, 0.055) !important;
  }

  /* Il pannello FC mobile usa meno spazio verticale tra stato del corpo,
     switch e superficie di appoggio. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"][data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] > [data-testid="stVerticalBlock"] {
    gap: 0.16rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] [class*="st-key-fcpanel_std_switch_row"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] [class*="st-key-fcpanel_caut_switch_row"] {
    margin-top: 0.12rem !important;
    margin-bottom: -0.08rem !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  /* I quattro stepper vestiti sono volutamente più bassi degli altri V2. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"] {
    height: 34px !important;
    min-height: 34px !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"] iframe {
    display: block !important;
    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_vest_help_slot"] button,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_vest_help_slot"] button {
    width: 1.42rem !important;
    min-width: 1.42rem !important;
    height: 1.42rem !important;
    min-height: 1.42rem !important;
    padding: 0 !important;
    border-radius: 50% !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_vest_help_slot"] button p,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_vest_help_slot"] button p {
    margin: 0 !important;
    font-size: 0.74rem !important;
    line-height: 1 !important;
  }

  /* La superficie resta un controllo distinto dal conteggio degli strati. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_surface_select_mobile"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_surface_select_mobile"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: color-mix(in srgb, var(--st-secondary-background-color) 86%, var(--st-primary-color) 14%) !important;
    border-color: color-mix(in srgb, var(--st-primary-color) 38%, transparent) !important;
  }


/* Rifiniture finali pannello FC Full mobile. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_std_switch_row"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_caut_switch_row"] {
  width: 100% !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_std_corr_slot"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_caut_corr_slot"] {
  flex: 0 0 auto !important;
  width: max-content !important;
  min-width: max-content !important;
  max-width: 44% !important;
  margin-left: auto !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_std_corr_slot"] [data-testid="stToggle"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_caut_corr_slot"] [data-testid="stToggle"] {
  width: max-content !important;
  min-width: max-content !important;
  max-width: max-content !important;
  margin-left: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_std_vest_group"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_caut_vest_group"] {
  flex: 1 1 0 !important;
  width: auto !important;
  min-width: 0 !important;
  max-width: 56% !important;
}

/* I V2 della Full occupano l'intera larghezza disponibile nel wrapper. */
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_decimal_"] {
  width: 100% !important;
  max-width: none !important;
  min-width: 0 !important;
  align-self: stretch !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_decimal_"] iframe {
  width: 100% !important;
  max-width: none !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_"]) {
  width: 100% !important;
  max-width: none !important;
}

/* Risultato FC standard mobile: valore e azione su una sola riga. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_row_mobile"] {
  box-sizing: border-box !important;
  width: 100% !important;
  min-width: 0 !important;
  height: 2.25rem !important;
  min-height: 2.25rem !important;
  max-height: 2.25rem !important;
  gap: 0 !important;
  align-items: center !important;
  overflow: hidden !important;
  border: 1px solid color-mix(in srgb, var(--st-primary-color) 78%, transparent) !important;
  border-radius: 0.58rem !important;
  background: color-mix(in srgb, var(--st-secondary-background-color) 78%, var(--st-primary-color) 22%) !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_value_mobile"] {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.mortem-fc-inline-result {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  height: 2.25rem;
  min-height: 2.25rem;
  max-height: 2.25rem;
  padding: 0 0.52rem;
  font-size: 0.88rem;
  line-height: 1.1;
  font-weight: 600;
  color: var(--st-text-color);
  white-space: nowrap;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] {
  flex: 0 0 auto !important;
  width: max-content !important;
  min-width: max-content !important;
  margin: 0 !important;
  padding: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] button {
  height: 2.25rem !important;
  min-height: 2.25rem !important;
  max-height: 2.25rem !important;
  margin: 0 !important;
  padding: 0 0.52rem !important;
  border-top: 0 !important;
  border-right: 0 !important;
  border-bottom: 0 !important;
  border-left: 1px solid color-mix(in srgb, var(--st-primary-color) 45%, transparent) !important;
  border-radius: 0 !important;
  background: color-mix(in srgb, var(--st-primary-color) 24%, transparent) !important;
  white-space: nowrap !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] > [data-testid="stVerticalBlock"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] [data-testid="stElementContainer"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] [data-testid="stButton"] {
  height: 2.25rem !important;
  min-height: 2.25rem !important;
  max-height: 2.25rem !important;
  margin: 0 !important;
  padding: 0 !important;
}

.mortem-fc-weight-note-mobile {
  box-sizing: border-box;
  width: 100%;
  margin: 0.10rem 0 0.04rem 0;
  padding: 0 0.10rem;
  font-size: 0.78rem;
  line-height: 1.22;
  white-space: normal;
  overflow: visible;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stElementContainer"]:has(.mortem-fc-weight-note-mobile) {
  width: 100% !important;
  overflow: visible !important;
  margin-bottom: 0.10rem !important;
}

/* Il selettore della superficie deve distinguersi chiaramente dagli stepper. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_std_surface_select_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_caut_surface_select_mobile"] {
  padding: 0.07rem !important;
  border: 1px solid color-mix(in srgb, #d79a00 72%, transparent) !important;
  border-radius: 0.58rem !important;
  background: color-mix(in srgb, var(--st-secondary-background-color) 78%, #ffc107 22%) !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_std_surface_select_mobile"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-fcpanel_caut_surface_select_mobile"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: color-mix(in srgb, var(--st-secondary-background-color) 82%, #ffc107 18%) !important;
  border-color: transparent !important;
  box-shadow: none !important;
}
}
</style>
"""


def install_full_mobile_compact_css() -> None:
    """Allega le regole al CSS iniziale della Full, senza render tardivi."""
    if getattr(st, "_full_mobile_compact_css_installed", False):
        return

    original_markdown = st.markdown

    def markdown_with_full_mobile_compact_css(body, *args, **kwargs):
        if isinstance(body, str) and ".final-text{" in body:
            body = body + _FULL_MOBILE_COMPACT_CSS
            kwargs["unsafe_allow_html"] = True
        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_full_mobile_compact_css
    st._full_mobile_compact_css_installed = True
