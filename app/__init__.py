# -*- coding: utf-8 -*-

import app.sopraciliare_ui as _sopraciliare_ui
from app.special_heading_ui import install_special_heading_style
from app.supra_single_grid import install_supra_single_grid

install_supra_single_grid(_sopraciliare_ui)
_sopraciliare_ui.install_sopraciliare_click_selector()
install_special_heading_style()
