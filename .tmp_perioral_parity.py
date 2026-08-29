from pathlib import Path

perioral_path = Path("app/perioral_single_grid.py")
heading_path = Path("app/special_heading_ui.py")

text = perioral_path.read_text(encoding="utf-8")

old_import = "from PIL import Image, ImageDraw\n"
new_import = "from PIL import Image, ImageDraw, ImageOps\n"
if text.count(old_import) != 1:
    raise SystemExit("Import PIL peribuccale inatteso")
text = text.replace(old_import, new_import, 1)

start_marker = "_IMAGE_ONLY_FRACTION = 0.76\n"
end_marker = "\ndef _option_from_row_click(row, click):\n"
if text.count(start_marker) != 1 or text.count(end_marker) != 1:
    raise SystemExit("Blocco immagini peribuccale inatteso")
start = text.index(start_marker)
end = text.index(end_marker)

new_image_block = '''_IMAGE_ONLY_FRACTION = 0.76
_CONTENT_THRESHOLD = 246
_CONTENT_PAD_TOP = 3
_CONTENT_PAD_BOTTOM = 4


def _source_tile(ui, index):
    """Ricava una cella dalla tavola peribuccale originale 3 x 2."""
    image = ui._PERIORAL_IMAGE
    width, height = image.size
    row, col = divmod(index, 3)
    cell_width = width / 3
    cell_height = height / 2

    x0 = round(col * cell_width) + 3
    x1 = round((col + 1) * cell_width) - 3
    y0 = round(row * cell_height) + 3
    y1 = round((row + 1) * cell_height) - 3
    return image.crop((x0, y0, x1, y1)).convert("RGB")


def _image_only_tile(tile):
    """Rimuove la didascalia raster dalla cella originale."""
    width, height = tile.size
    image_height = max(1, round(height * _IMAGE_ONLY_FRACTION))
    return tile.crop((0, 0, width, image_height)).convert("RGB")


def _strip_original_edges(tile):
    """Elimina i bordi/cornici raster originari senza ridimensionare il disegno."""
    width, height = tile.size
    edge = 7
    if width <= edge * 2 or height <= edge * 2:
        return tile
    return tile.crop((edge, edge, width - edge, height - edge)).convert("RGB")


def _content_vertical_bounds(tile):
    """Trova l'estensione verticale reale del disegno ignorando il fondo quasi bianco."""
    gray = ImageOps.grayscale(tile)
    mask = gray.point(lambda pixel: 255 if pixel < _CONTENT_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return None
    return bbox[1], bbox[3]


def _build_tiles(ui):
    """Costruisce le cinque immagini pulite e la cella neutra 'Non valutata'."""
    tiles = {
        option: _strip_original_edges(_image_only_tile(_source_tile(ui, index)))
        for index, option in enumerate(_PERIORAL_TILE_OPTIONS[:5])
    }

    sample = next(iter(tiles.values()))
    neutral = Image.new("RGB", sample.size, (255, 255, 255))
    draw = ImageDraw.Draw(neutral)
    width, height = neutral.size
    radius = min(width, height) * 0.20
    cx, cy = width / 2, height / 2
    stroke = max(2, round(min(width, height) * 0.018))
    gray = (170, 170, 170)

    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        outline=gray,
        width=stroke,
    )
    draw.line(
        (
            cx - radius * 0.72,
            cy + radius * 0.72,
            cx + radius * 0.72,
            cy - radius * 0.72,
        ),
        fill=gray,
        width=stroke,
    )

    tiles["Non valutata"] = neutral
    return tiles


def _row_content_tiles(tiles, row):
    """Ritaglia le tre celle della riga sugli stessi limiti reali del contenuto."""
    options = _PERIORAL_TILE_OPTIONS[row * 3:(row + 1) * 3]
    row_tiles = [tiles[option] for option in options]
    bounds = [bound for tile in row_tiles if (bound := _content_vertical_bounds(tile)) is not None]
    if not bounds:
        return row_tiles

    top = max(0, min(bound[0] for bound in bounds) - _CONTENT_PAD_TOP)
    bottom = min(
        min(tile.height for tile in row_tiles),
        max(bound[1] for bound in bounds) + _CONTENT_PAD_BOTTOM,
    )
    if bottom <= top:
        return row_tiles

    return [tile.crop((0, top, tile.width, bottom)) for tile in row_tiles]


def _compose_row(tiles, row):
    """Compone tre immagini pulite con la parte superiore della cornice unica."""
    row_tiles = _row_content_tiles(tiles, row)
    sample = row_tiles[0]
    tile_width, tile_height = sample.size
    row_width = tile_width * 3
    row_image = Image.new("RGB", (row_width, tile_height), (255, 255, 255))

    for col, tile in enumerate(row_tiles):
        if tile.size != sample.size:
            tile = tile.resize(sample.size, Image.Resampling.LANCZOS)
        row_image.paste(tile, (col * tile_width, 0))

    frame = (105, 105, 105)
    draw = ImageDraw.Draw(row_image)
    draw.line((0, 0, row_width - 1, 0), fill=frame, width=1)
    for x in (0, tile_width, tile_width * 2, row_width - 1):
        draw.line((x, 0, x, tile_height - 1), fill=frame, width=1)

    return row_image
'''

text = text[:start] + new_image_block + text[end:]

css_start_marker = "def _install_label_css():\n"
css_end_marker = "\ndef _render_segmented_labels(*, row, selected, widget_key, options, language=None):\n"
if text.count(css_start_marker) != 1 or text.count(css_end_marker) != 1:
    raise SystemExit("Funzione CSS peribuccale inattesa")
css_start = text.index(css_start_marker)
css_end = text.index(css_end_marker)

new_css_function = '''def _install_label_css():
    st.markdown(
        """
        <style>
        [class*="st-key-eccitabilita_peribuccale_grid"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_grid"][data-testid="stVerticalBlock"],
        [class*="st-key-eccitabilita_peribuccale_grid"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_grid"] {
            position: relative !important;
            top: -0.80rem !important;
            margin-bottom: -0.80rem !important;
        }

        @media (max-width: 768px) {
            [class*="st-key-eccitabilita_peribuccale_grid"] {
                top: -2.40rem !important;
                margin-bottom: -2.40rem !important;
            }
        }

        [class*="st-key-eccitabilita_peribuccale_row_click_"] {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_row_click_"] iframe {
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_grid"]
        [data-testid="stElementContainer"]:has([class*="st-key-eccitabilita_peribuccale_row_click_"]),
        [class*="st-key-eccitabilita_peribuccale_grid"]
        [data-testid="stElementContainer"]:has([class*="st-key-eccitabilita_peribuccale_segment_"]) {
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] {
            width: 100% !important;
            margin-top: 0 !important;
            margin-bottom: 0.22rem !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] div[role="group"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            width: 100% !important;
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button {
            min-width: 0 !important;
            width: 100% !important;
            min-height: 0 !important;
            height: auto !important;
            padding: 1px 2px !important;
            margin: 0 !important;
            white-space: normal !important;
            border: 0 !important;
            border-left: 1px solid rgba(105, 105, 105, 0.72) !important;
            border-bottom: 1px solid rgba(105, 105, 105, 0.72) !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            align-items: center !important;
            justify-content: center !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button:last-child {
            border-right: 1px solid rgba(105, 105, 105, 0.72) !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button > div,
        [class*="st-key-eccitabilita_peribuccale_segment_"] [data-testid="stMarkdownContainer"] {
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button[kind="segmented_controlActive"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-pressed="true"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-checked="true"],
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[data-selected="true"] {
            background: #00A699 !important;
            box-shadow: none !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button p {
            margin: 0 !important;
            padding: 0 !important;
            white-space: pre-line !important;
            overflow-wrap: anywhere !important;
            text-align: center !important;
            line-height: 1.00 !important;
            font-size: clamp(0.53rem, 1.85vw, 0.66rem) !important;
            font-weight: 600 !important;
        }

        [class*="st-key-eccitabilita_peribuccale_segment_"] button[kind="segmented_controlActive"] *,
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-pressed="true"] *,
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[aria-checked="true"] *,
        [class*="st-key-eccitabilita_peribuccale_segment_"] button[data-selected="true"] * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
'''

text = text[:css_start] + new_css_function + text[css_end:]
perioral_path.write_text(text, encoding="utf-8")

heading = heading_path.read_text(encoding="utf-8")
old_override = '''
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_grid"] > [data-testid="stVerticalBlock"] {
            gap: 0 !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] {
            margin-top: -1.04rem !important;
            margin-bottom: -0.30rem !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] button {
            min-height: 2.50rem !important;
            padding: 2px 2px !important;
          }

          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [class*="st-key-eccitabilita_peribuccale_segment_"] button p {
            font-size: clamp(0.55rem, 2vw, 0.69rem) !important;
            line-height: 1.05 !important;
          }
'''
if heading.count(old_override) != 1:
    raise SystemExit("Override peribuccali legacy inattesi")
heading = heading.replace(old_override, "", 1)
heading_path.write_text(heading, encoding="utf-8")

updated = perioral_path.read_text(encoding="utf-8")
checks = [
    "from PIL import Image, ImageDraw, ImageOps",
    "def _strip_original_edges(tile):",
    "def _row_content_tiles(tiles, row):",
    "top: -2.40rem !important;",
    '[class*="st-key-eccitabilita_peribuccale_grid"][data-testid="stVerticalBlock"]',
    "margin-top: 0 !important;",
    "border-bottom: 1px solid rgba(105, 105, 105, 0.72) !important;",
    "font-size: clamp(0.53rem, 1.85vw, 0.66rem) !important;",
]
missing = [item for item in checks if item not in updated]
if missing:
    raise SystemExit(f"Modifiche peribuccali mancanti: {missing}")

if "margin-top: -1.04rem !important;" in heading_path.read_text(encoding="utf-8"):
    raise SystemExit("Override peribuccale legacy ancora presente")
