from pathlib import Path

# 1) Rimuove dalla UI generale gli override sopraciliari del tentativo
# precedente: erano più specifici del CSS del renderer e ne impedivano
# l'effetto. La peribuccale resta invariata.
heading = Path("app/special_heading_ui.py")
text = heading.read_text(encoding="utf-8")

pairs = [
(
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_sopraciliare_grid"] > [data-testid="stVerticalBlock"],
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0 !important;
          }
''',
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0 !important;
          }
'''
),
(
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_sopraciliare_segment_"],
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] {
            margin-top: -1.04rem !important;
            margin-bottom: -0.30rem !important;
          }
''',
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] {
            margin-top: -1.04rem !important;
            margin-bottom: -0.30rem !important;
          }
'''
),
(
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_sopraciliare_segment_"] button,
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] button {
            min-height: 2.50rem !important;
            padding: 2px 2px !important;
          }
''',
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] button {
            min-height: 2.50rem !important;
            padding: 2px 2px !important;
          }
'''
),
(
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_sopraciliare_segment_"] button p,
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] button p {
            font-size: clamp(0.55rem, 2vw, 0.69rem) !important;
            line-height: 1.05 !important;
          }
''',
'''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] button p {
            font-size: clamp(0.55rem, 2vw, 0.69rem) !important;
            line-height: 1.05 !important;
          }
'''
),
]
for old, new in pairs:
    if text.count(old) != 1:
        raise SystemExit("special_heading_ui.py non corrisponde allo stato verificato")
    text = text.replace(old, new, 1)
heading.write_text(text, encoding="utf-8")

# 2) Revisione diretta del renderer sopraciliare.
supra = Path("app/supra_single_grid.py")
text = supra.read_text(encoding="utf-8")

if 'from PIL import Image, ImageDraw' not in text:
    raise SystemExit("Import PIL inatteso")
text = text.replace('from PIL import Image, ImageDraw', 'from PIL import Image', 1)

old_frame = '''def _uniform_tile_frame(tile):
    """Uniforma la sottile cornice delle celle senza alterarne il contenuto."""
    framed = tile.copy()
    width, height = framed.size
    draw = ImageDraw.Draw(framed)
    erase = 3
    white = (255, 255, 255)
    frame = (95, 95, 95)

    draw.rectangle((0, 0, width - 1, erase), fill=white)
    draw.rectangle((0, height - erase - 1, width - 1, height - 1), fill=white)
    draw.rectangle((0, 0, erase, height - 1), fill=white)
    draw.rectangle((width - erase - 1, 0, width - 1, height - 1), fill=white)
    draw.rectangle((0, 0, width - 1, height - 1), outline=frame, width=1)
    return framed


'''
new_frame = '''def _clean_tile_edges(tile):
    """Elimina soltanto le linee/cornici raster presenti ai bordi originali."""
    width, height = tile.size
    edge = 4
    if width <= edge * 2 or height <= edge * 2:
        return tile

    cleaned = Image.new("RGB", (width, height), (255, 255, 255))
    interior = tile.crop((edge, edge, width - edge, height - edge))
    cleaned.paste(interior, (edge, edge))
    return cleaned


'''
if text.count(old_frame) != 1:
    raise SystemExit("Blocco cornice sopraciliare inatteso")
text = text.replace(old_frame, new_frame, 1)

old_tiles = '    tiles = [_uniform_tile_frame(_image_only_tile(ui, option)) for option in options]\n'
new_tiles = '    tiles = [_clean_tile_edges(_image_only_tile(ui, option)) for option in options]\n'
if text.count(old_tiles) != 1:
    raise SystemExit("Composizione tiles inattesa")
text = text.replace(old_tiles, new_tiles, 1)

old_css = '''        [class*="st-key-eccitabilita_sopraciliare_grid"] {
            margin-top: -0.72rem !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
            width: 100% !important;
            margin-top: -1.20rem !important;
            margin-bottom: -0.34rem !important;
        }
'''
new_css = '''        @media (max-width: 768px) {
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stElementContainer"]:has([class*="st-key-eccitabilita_sopraciliare_grid"]) {
              margin-top: -1.50rem !important;
              margin-bottom: 0 !important;
          }
        }

        [class*="st-key-eccitabilita_sopraciliare_grid"] {
            margin-top: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
            width: 100% !important;
            margin-top: -1.50rem !important;
            margin-bottom: -0.42rem !important;
        }
'''
if text.count(old_css) != 1:
    raise SystemExit("CSS iniziale sopraciliare inatteso")
text = text.replace(old_css, new_css, 1)

old_button = '''        [class*="st-key-eccitabilita_sopraciliare_segment_"] button {
            min-width: 0 !important;
            width: 100% !important;
            min-height: 2.45rem !important;
            padding: 2px 2px !important;
            white-space: normal !important;
            border-color: rgba(128, 128, 128, 0.35) !important;
            border-top: none !important;
            border-top-left-radius: 0 !important;
            border-top-right-radius: 0 !important;
            background: transparent !important;
        }
'''
new_button = '''        [class*="st-key-eccitabilita_sopraciliare_segment_"] button {
            min-width: 0 !important;
            width: 100% !important;
            min-height: 1.95rem !important;
            height: auto !important;
            padding: 1px 2px !important;
            white-space: normal !important;
            border-color: rgba(128, 128, 128, 0.35) !important;
            border-top: none !important;
            border-top-left-radius: 0 !important;
            border-top-right-radius: 0 !important;
            background: transparent !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button > div {
            min-height: 0 !important;
            padding: 0 !important;
        }
'''
if text.count(old_button) != 1:
    raise SystemExit("CSS pulsanti sopraciliari inatteso")
text = text.replace(old_button, new_button, 1)

old_text = '''            line-height: 1.05 !important;
            font-size: clamp(0.55rem, 2vw, 0.69rem) !important;
'''
new_text = '''            line-height: 1.00 !important;
            font-size: clamp(0.54rem, 1.9vw, 0.67rem) !important;
'''
if text.count(old_text) != 1:
    raise SystemExit("CSS testo sopraciliare inatteso")
text = text.replace(old_text, new_text, 1)

supra.write_text(text, encoding="utf-8")

# Controlli finali mirati.
heading_text = heading.read_text(encoding="utf-8")
supra_text = supra.read_text(encoding="utf-8")
assert 'st-key-eccitabilita_sopraciliare_segment_\"] button,' not in heading_text
assert 'def _uniform_tile_frame' not in supra_text
assert 'def _clean_tile_edges' in supra_text
assert 'margin-top: -1.50rem !important;' in supra_text
assert 'min-height: 1.95rem !important;' in supra_text
assert 'border-top: none !important;' in supra_text
assert 'if option == "Non valutata":' in supra_text
