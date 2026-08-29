from pathlib import Path

path = Path("app/supra_single_grid.py")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "from PIL import Image, ImageDraw\n",
        "from PIL import Image, ImageDraw, ImageOps\n",
    ),
    (
        "_IMAGE_ONLY_FRACTION = 0.69\n",
        "_IMAGE_SCAN_FRACTION = 0.69\n_CONTENT_THRESHOLD = 246\n_CONTENT_PAD_TOP = 3\n_CONTENT_PAD_BOTTOM = 4\n",
    ),
    (
'''def _image_only_tile(ui, option):
    """Rimuove la didascalia raster dalla cella originale."""
    tile = ui._SUPRA_TILES[option]
    width, height = tile.size
    image_height = max(1, round(height * _IMAGE_ONLY_FRACTION))

    # La cella neutra originale contiene anche la scritta raster
    # "Non valutata": nella griglia corrente il testo è già nel pulsante
    # sottostante, quindi conserviamo soltanto il simbolo.
    if option == "Non valutata":
        visible_height = max(1, round(height * 0.60))
        cleaned = Image.new("RGB", (width, image_height), (255, 255, 255))
        cleaned.paste(tile.crop((0, 0, width, visible_height)).convert("RGB"), (0, 0))
        return cleaned

    return tile.crop((0, 0, width, image_height)).convert("RGB")


def _clean_tile_edges(tile):
    """Rimuove i bordi raster originari e recupera lo spazio bianco periferico."""
    width, height = tile.size
    edge = 7
    if width <= edge * 2 or height <= edge * 2:
        return tile

    interior = tile.crop((edge, edge, width - edge, height - edge))
    return interior.resize((width, height), Image.Resampling.LANCZOS)


def _compose_row(ui, row):
    """Compone tre immagini pulite con la parte superiore della cornice unica."""
    options = ui._SUPRA_TILE_OPTIONS[row * 3:(row + 1) * 3]
    tiles = [_clean_tile_edges(_image_only_tile(ui, option)) for option in options]
''',
'''def _image_scan_tile(ui, option):
    """Esclude la vecchia didascalia raster mantenendo una fascia di scansione uniforme."""
    tile = ui._SUPRA_TILES[option]
    width, height = tile.size
    scan_height = max(1, round(height * _IMAGE_SCAN_FRACTION))
    scan = tile.crop((0, 0, width, scan_height)).convert("RGB")

    # La nona cella conteneva la vecchia scritta raster "Non valutata" più in alto:
    # conserviamo il simbolo e rendiamo bianco il resto prima del crop sul contenuto.
    if option == "Non valutata":
        visible_height = max(1, round(height * 0.60))
        cleaned = Image.new("RGB", (width, scan_height), (255, 255, 255))
        cleaned.paste(tile.crop((0, 0, width, visible_height)).convert("RGB"), (0, 0))
        return cleaned

    return scan


def _strip_original_edges(tile):
    """Elimina i bordi/cornici raster originari senza ridimensionare il disegno."""
    width, height = tile.size
    edge = 7
    if width <= edge * 2 or height <= edge * 2:
        return tile
    return tile.crop((edge, edge, width - edge, height - edge)).convert("RGB")


def _content_vertical_bounds(tile):
    """Trova l'estensione verticale reale del disegno, ignorando il fondo quasi bianco."""
    gray = ImageOps.grayscale(tile)
    mask = gray.point(lambda pixel: 255 if pixel < _CONTENT_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return None
    return bbox[1], bbox[3]


def _row_content_tiles(ui, row):
    """Ritaglia le tre celle della riga sugli stessi limiti reali del contenuto."""
    options = ui._SUPRA_TILE_OPTIONS[row * 3:(row + 1) * 3]
    tiles = [_strip_original_edges(_image_scan_tile(ui, option)) for option in options]
    bounds = [bound for tile in tiles if (bound := _content_vertical_bounds(tile)) is not None]
    if not bounds:
        return tiles

    top = max(0, min(bound[0] for bound in bounds) - _CONTENT_PAD_TOP)
    bottom = min(
        min(tile.height for tile in tiles),
        max(bound[1] for bound in bounds) + _CONTENT_PAD_BOTTOM,
    )
    if bottom <= top:
        return tiles

    return [tile.crop((0, top, tile.width, bottom)) for tile in tiles]


def _compose_row(ui, row):
    """Compone tre immagini pulite con la parte superiore della cornice unica."""
    tiles = _row_content_tiles(ui, row)
'''
    ),
    (
'''        [class*="st-key-eccitabilita_sopraciliare_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
''',
'''        [class*="st-key-eccitabilita_sopraciliare_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_row_click_"] iframe {
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_grid"]
        [data-testid="stElementContainer"]:has([class*="st-key-eccitabilita_sopraciliare_row_click_"]),
        [class*="st-key-eccitabilita_sopraciliare_grid"]
        [data-testid="stElementContainer"]:has([class*="st-key-eccitabilita_sopraciliare_segment_"]) {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] {
'''
    ),
    (
'''            margin-top: -0.08rem !important;
            margin-bottom: 0 !important;
''',
'''            margin-top: 0 !important;
            margin-bottom: -0.18rem !important;
'''
    ),
    (
'''            padding: 2px 2px !important;
''',
'''            padding: 1px 2px !important;
'''
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Replacement mismatch ({count}) for:\n{old[:180]}")
    text = text.replace(old, new, 1)

checks = [
    "_CONTENT_THRESHOLD = 246",
    "def _content_vertical_bounds(tile):",
    "def _row_content_tiles(ui, row):",
    "tiles = _row_content_tiles(ui, row)",
    "line-height: 0 !important;",
    "margin-bottom: -0.18rem !important;",
]
missing = [item for item in checks if item not in text]
if missing:
    raise SystemExit(f"Missing expected changes: {missing}")

# Il vecchio resize, che reintroduceva lo spazio bianco rimosso, non deve restare.
if "return interior.resize((width, height), Image.Resampling.LANCZOS)" in text:
    raise SystemExit("Old edge-resize path still present")

path.write_text(text, encoding="utf-8")
