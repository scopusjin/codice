# -*- coding: utf-8 -*-
"""Compatibility entry points for the dedicated FC page."""

# Entry points retained for existing desktop/mobile callers.
def pannello_suggerisci_fc(peso_default: float = 70.0, key_prefix: str = "fcpanel"):
    from app.fc_page import open_fc_page, FULL_PAGE
    open_fc_page(FULL_PAGE)


def pannello_suggerisci_fc_mobile(peso_default: float = 70.0, key_prefix: str = "fcpanel_m"):
    from app.fc_page import open_fc_page, MSIL_PAGE
    open_fc_page(MSIL_PAGE)
