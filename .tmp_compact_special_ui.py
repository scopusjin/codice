from pathlib import Path

# 1) Nota adattamento peso: usa il flag del motore e un fallback puramente
# presentazionale basato sul valore che si vedrebbe senza adattamento.
path = Path("app/full_factor_panel.py")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "from app.factor_calc import DressCounts, compute_factor, fattore_vestiti_coperte\n",
    "from app.factor_calc import DressCounts, compute_factor, fattore_vestiti_coperte, floor_to_step\n",
    1,
)
old = '''    side_text = ""
    if result.riassunto.get("peso_adattato", False) and peso_eff is not None:
        side_text = i18n.ui_text(
            "full.fc_adjusted_for_weight", weight=peso_eff, base=result.fattore_base
        )
'''
new = '''    side_text = ""
    peso_adattato = bool(result.riassunto.get("peso_adattato", False))
    if not peso_adattato and peso_eff is not None and result.fattore_base is not None:
        try:
            base_senza_peso = floor_to_step(round(float(result.fattore_base), 2))
            peso_adattato = (
                abs(float(peso_eff) - 70.0) > 1e-9
                and float(result.fattore_base) >= 1.4
                and abs(float(result.fattore_finale) - base_senza_peso) > 1e-9
            )
        except (TypeError, ValueError):
            peso_adattato = False
    if peso_adattato and peso_eff is not None:
        side_text = i18n.ui_text(
            "full.fc_adjusted_for_weight", weight=peso_eff, base=result.fattore_base
        )
'''
if text.count(old) != 1:
    raise SystemExit("weight text block mismatch")
text = text.replace(old, new, 1)

old_css = '''[class*="st-key-{key_prefix}_fc_apply_action_mobile"] button p {{margin:0!important;line-height:1!important;}}}}</style>'''
new_css = '''[class*="st-key-{key_prefix}_fc_apply_action_mobile"] button p {{margin:0!important;line-height:1!important;}} [class*="st-key-{key_prefix}_fc_apply_value_mobile"] .mortem-fc-result-stack {{display:flex!important;flex-direction:column!important;justify-content:center!important;margin:0!important;padding:0!important;}} [class*="st-key-{key_prefix}_fc_apply_value_mobile"] .mortem-fc-result-stack .mortem-fc-inline-result {{min-height:0!important;}} [class*="st-key-{key_prefix}_fc_apply_value_mobile"] .mortem-fc-weight-note-mobile {{font-size:0.74rem!important;line-height:1.15!important;margin:0.12rem 0 0 0!important;padding:0!important;opacity:0.78!important;white-space:normal!important;}}}}</style>'''
if text.count(old_css) != 1:
    raise SystemExit("weight css marker mismatch")
text = text.replace(old_css, new_css, 1)

old_render = '''                st.markdown(
                    f'<div class="mortem-fc-inline-result">FC suggerito:&nbsp;<strong>{result.fattore_finale:.2f}</strong></div>',
                    unsafe_allow_html=True,
                )
'''
new_render = '''                weight_note_html = (
                    f'<div class="mortem-fc-weight-note-mobile">{side_text}</div>'
                    if side_text else ""
                )
                st.markdown(
                    f'<div class="mortem-fc-result-stack">'
                    f'<div class="mortem-fc-inline-result">FC suggerito:&nbsp;<strong>{result.fattore_finale:.2f}</strong></div>'
                    f'{weight_note_html}</div>',
                    unsafe_allow_html=True,
                )
'''
if text.count(old_render) != 1:
    raise SystemExit("weight render block mismatch")
text = text.replace(old_render, new_render, 1)

old_separate = '''        if side_text:
            st.markdown(
                f'<div class="mortem-fc-weight-note-mobile">{side_text}</div>',
                unsafe_allow_html=True,
            )
'''
if text.count(old_separate) != 1:
    raise SystemExit("separate weight note mismatch")
text = text.replace(old_separate, "", 1)
path.write_text(text, encoding="utf-8")

# 2) Compatta pannello generale e spazio titolo -> contenuto su mobile.
path = Path("app/special_heading_ui.py")
text = path.read_text(encoding="utf-8")
marker = '''    original_markdown = st.markdown

    def markdown_with_special_heading(body, *args, **kwargs):
'''
insert = '''    original_markdown = st.markdown

    original_markdown(
        """
        <style>
        @media (max-width: 768px) {
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"]) {
            padding: 0.48rem 0.62rem !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
          [data-testid="stVerticalBlock"] {
            gap: 0.22rem !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
          [data-testid="stElementContainer"]:has(.mortem-section-title) {
            margin: 0 0 -0.18rem 0 !important;
            padding: 0 !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-electrical_pair_layout"] [data-testid="stHorizontalBlock"] {
            margin: 0 !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def markdown_with_special_heading(body, *args, **kwargs):
'''
if text.count(marker) != 1:
    raise SystemExit("special heading marker mismatch")
text = text.replace(marker, insert, 1)
path.write_text(text, encoding="utf-8")

# 3) Compatta le tre righe della griglia sopraciliare.
path = Path("app/supra_single_grid.py")
text = path.read_text(encoding="utf-8")
old = '''        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
            width: 100% !important;
            margin-top: -0.85rem !important;
            margin-bottom: 0.20rem !important;
        }
'''
new = '''        [class*="st-key-eccitabilita_sopraciliare_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0.04rem !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
            width: 100% !important;
            margin-top: -0.98rem !important;
            margin-bottom: -0.24rem !important;
        }
'''
if text.count(old) != 1:
    raise SystemExit("supra compact marker mismatch")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

# 4) Stessa compattezza per la griglia peribuccale.
path = Path("app/perioral_single_grid.py")
text = path.read_text(encoding="utf-8")
old = '''        [class*="st-key-eccitabilita_peribuccale_segment_"] {
            width: 100% !important;
            margin-top: -0.85rem !important;
            margin-bottom: 0.20rem !important;
        }
'''
new = '''        [class*="st-key-eccitabilita_peribuccale_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0.04rem !important;
        }

        [class*="st-key-eccitabilita_peribuccale_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] {
            width: 100% !important;
            margin-top: -0.98rem !important;
            margin-bottom: -0.24rem !important;
        }
'''
if text.count(old) != 1:
    raise SystemExit("perioral compact marker mismatch")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

# Controlli finali mirati.
checks = {
    Path("app/full_factor_panel.py"): [
        "base_senza_peso = floor_to_step",
        "mortem-fc-result-stack",
        "weight_note_html",
    ],
    Path("app/special_heading_ui.py"): [
        "padding: 0.48rem 0.62rem",
        "margin: 0 0 -0.18rem 0",
    ],
    Path("app/supra_single_grid.py"): ["margin-bottom: -0.24rem"],
    Path("app/perioral_single_grid.py"): ["margin-bottom: -0.24rem"],
}
for file_path, needles in checks.items():
    content = file_path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in content]
    if missing:
        raise SystemExit(f"Missing in {file_path}: {missing}")
