from pathlib import Path

path = Path("app/supra_single_grid.py")
text = path.read_text(encoding="utf-8")

replacements = []

replacements.append((
    "from PIL import Image\n",
    "from PIL import Image, ImageDraw\n",
))

replacements.append((
'''def _image_only_tile(ui, option):
    """Rimuove la didascalia raster dalla cella originale."""
    tile = ui._SUPRA_TILES[option]
    width, height = tile.size
    image_height = max(1, round(height * _IMAGE_ONLY_FRACTION))
    return tile.crop((0, 0, width, image_height)).convert("RGB")


def _compose_row(ui, row):
''',
'''def _image_only_tile(ui, option):
    """Rimuove la didascalia raster dalla cella originale."""
    tile = ui._SUPRA_TILES[option]
    width, height = tile.size
    image_height = max(1, round(height * _IMAGE_ONLY_FRACTION))

    # La cella neutra originale contiene anche la scritta raster
    # "Non valutata": nella griglia corrente il testo è già nel pulsante
    # sottostante, quindi conserviamo soltanto il simbolo.
    if option == "Non valutata":
        visible_height = max(1, round(height * 0.68))
        cleaned = Image.new("RGB", (width, image_height), (255, 255, 255))
        cleaned.paste(tile.crop((0, 0, width, visible_height)).convert("RGB"), (0, 0))
        return cleaned

    return tile.crop((0, 0, width, image_height)).convert("RGB")


def _uniform_tile_frame(tile):
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


def _compose_row(ui, row):
'''))

replacements.append((
'''    tiles = [_image_only_tile(ui, option) for option in options]
''',
'''    tiles = [_uniform_tile_frame(_image_only_tile(ui, option)) for option in options]
'''))

replacements.append((
'''        [class*="st-key-eccitabilita_sopraciliare_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0.04rem !important;
        }
''',
'''        [class*="st-key-eccitabilita_sopraciliare_grid"] {
            margin-top: -0.72rem !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }
'''))

replacements.append((
'''        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
            width: 100% !important;
            margin-top: -0.98rem !important;
            margin-bottom: -0.24rem !important;
        }
''',
'''        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
            width: 100% !important;
            margin-top: -1.20rem !important;
            margin-bottom: -0.34rem !important;
        }
'''))

replacements.append((
'''        [class*="st-key-eccitabilita_sopraciliare_segment_"] button {
            min-width: 0 !important;
            width: 100% !important;
            min-height: 2.65rem !important;
            padding: 3px 3px !important;
            white-space: normal !important;
            border-color: rgba(128, 128, 128, 0.35) !important;
            background: transparent !important;
        }
''',
'''        [class*="st-key-eccitabilita_sopraciliare_segment_"] button {
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
'''))

replacements.append((
'''            box-shadow: inset 0 0 0 1px #008F84 !important;
''',
'''            box-shadow: none !important;
'''))

replacements.append((
'''            line-height: 1.10 !important;
            font-size: clamp(0.57rem, 2.15vw, 0.72rem) !important;
''',
'''            line-height: 1.05 !important;
            font-size: clamp(0.55rem, 2vw, 0.69rem) !important;
'''))

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Replacement mismatch ({count}) for:\n{old[:120]}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

# Controlli mirati: la correzione deve essere presente e non deve toccare
# testi/opzioni della griglia.
checks = [
    'if option == "Non valutata":',
    'def _uniform_tile_frame(tile):',
    'margin-top: -0.72rem !important;',
    'margin-top: -1.20rem !important;',
    'border-top: none !important;',
    'font-size: clamp(0.55rem, 2vw, 0.69rem) !important;',
]
updated = path.read_text(encoding="utf-8")
missing = [item for item in checks if item not in updated]
if missing:
    raise SystemExit(f"Missing expected changes: {missing}")
