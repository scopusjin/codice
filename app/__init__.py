# -*- coding: utf-8 -*-

import streamlit as st

from app.sopraciliare_ui import install_sopraciliare_click_selector

install_sopraciliare_click_selector()

# Override finale del solo layout 3x3 sopraciliare: tre celle sempre uguali,
# senza wrapping, indipendentemente dalla larghezza del telefono.
st.markdown(
    """
    <style>
    [class*="st-key-eccitabilita_sopraciliare_row_"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    [class*="st-key-eccitabilita_sopraciliare_row_"][data-testid="stHorizontalBlock"],
    [class*="st-key-eccitabilita_sopraciliare_row_"] div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    [class*="st-key-eccitabilita_sopraciliare_row_"][data-testid="stHorizontalBlock"] > div,
    [class*="st-key-eccitabilita_sopraciliare_row_"] div[data-testid="stHorizontalBlock"] > div {
        flex: 0 0 calc((100% - 4px) / 3) !important;
        width: calc((100% - 4px) / 3) !important;
        min-width: 0 !important;
        max-width: calc((100% - 4px) / 3) !important;
    }

    [class*="st-key-eccitabilita_sopraciliare_tile_"] {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }

    [class*="st-key-eccitabilita_sopraciliare_tile_"] iframe {
        width: 100% !important;
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
