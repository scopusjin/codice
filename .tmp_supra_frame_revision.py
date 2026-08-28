from pathlib import Path

supra_path = Path("app/supra_single_grid.py")
heading_path = Path("app/special_heading_ui.py")

supra = supra_path.read_text(encoding="utf-8")
heading = heading_path.read_text(encoding="utf-8")

# ------------------------------------------------------------
# Sopraciliare: pulizia raster e cornice coerente immagine+etichetta
# ------------------------------------------------------------
if "from PIL import Image\n" not in supra:
    raise SystemExit("Import PIL inatteso")
supra = supra.replace("from PIL import Image\n", "from PIL import Image, ImageDraw\n", 1)

if "_IMAGE_ONLY_FRACTION = 0.76" not in supra:
    raise SystemExit("Frazione immagine inattesa")
supra = supra.replace("_IMAGE_ONLY_FRACTION = 0.76", "_IMAGE_ONLY_FRACTION = 0.69", 1)

if "visible_height = max(1, round(height * 0.68))" not in supra:
    raise SystemExit("Crop Non valutata inatteso")
supra = supra.replace(
    "visible_height = max(1, round(height * 0.68))",
    "visible_height = max(1, round(height * 0.60))",
    1,
)

clean_start = supra.index("def _clean_tile_edges(tile):")
clean_end = supra.index("\n\ndef _compose_row", clean_start)
new_clean = '''def _clean_tile_edges(tile):
    """Rimuove i bordi raster originari e recupera lo spazio bianco periferico."""
    width, height = tile.size
    edge = 7
    if width <= edge * 2 or height <= edge * 2:
        return tile

    interior = tile.crop((edge, edge, width - edge, height - edge))
    return interior.resize((width, height), Image.Resampling.LANCZOS)
'''
supra = supra[:clean_start] + new_clean + supra[clean_end:]

compose_start = supra.index("def _compose_row(ui, row):")
compose_end = supra.index("\n\ndef _option_from_row_click", compose_start)
new_compose = '''def _compose_row(ui, row):
    """Compone tre immagini pulite con la parte superiore della cornice unica."""
    options = ui._SUPRA_TILE_OPTIONS[row * 3:(row + 1) * 3]
    tiles = [_clean_tile_edges(_image_only_tile(ui, option)) for option in options]
    sample = tiles[0]
    tile_width, tile_height = sample.size
    row_width = tile_width * 3
    row_image = Image.new("RGB", (row_width, tile_height), (255, 255, 255))

    for col, tile in enumerate(tiles):
        if tile.size != sample.size:
            tile = tile.resize(sample.size, Image.Resampling.LANCZOS)
        row_image.paste(tile, (col * tile_width, 0))

    # La cornice è unica con l'etichetta sottostante: qui disegniamo soltanto
    # bordo superiore e divisori verticali; il bordo inferiore appartiene
    # all'etichetta, senza linea di demarcazione tra immagine e testo.
    frame = (105, 105, 105)
    draw = ImageDraw.Draw(row_image)
    draw.line((0, 0, row_width - 1, 0), fill=frame, width=1)
    for x in (0, tile_width, tile_width * 2, row_width - 1):
        draw.line((x, 0, x, tile_height - 1), fill=frame, width=1)

    return row_image
'''
supra = supra[:compose_start] + new_compose + supra[compose_end:]

css_start = supra.index("def _install_label_css():")
css_end = supra.index("\n\ndef _render_segmented_labels", css_start)
new_css = '''def _install_label_css():
    st.markdown(
        """
        <style>
        [class*="st-key-eccitabilita_sopraciliare_grid"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
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
            margin-top: -0.08rem !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] div[role="group"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            width: 100% !important;
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button {
            min-width: 0 !important;
            width: 100% !important;
            min-height: 0 !important;
            height: auto !important;
            padding: 2px 2px !important;
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

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button:last-child {
            border-right: 1px solid rgba(105, 105, 105, 0.72) !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button > div,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] [data-testid="stMarkdownContainer"] {
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[kind="segmented_controlActive"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-pressed="true"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-checked="true"],
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[data-selected="true"] {
            background: #00A699 !important;
            box-shadow: none !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button p {
            margin: 0 !important;
            padding: 0 !important;
            white-space: pre-line !important;
            overflow-wrap: anywhere !important;
            text-align: center !important;
            line-height: 1.00 !important;
            font-size: clamp(0.53rem, 1.85vw, 0.66rem) !important;
            font-weight: 600 !important;
        }

        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[kind="segmented_controlActive"] *,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-pressed="true"] *,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[aria-checked="true"] *,
        [class*="st-key-eccitabilita_sopraciliare_segment_"] button[data-selected="true"] * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
'''
supra = supra[:css_start] + new_css + supra[css_end:]

# ------------------------------------------------------------
# Titolo sopraciliare: classe specifica per ridurre davvero il gap
# ------------------------------------------------------------
generic_heading_css = '''          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
          [data-testid="stElementContainer"]:has(.mortem-section-title) {
            margin: 0 0 -0.58rem 0 !important;
            padding: 0 !important;
          }
'''
if generic_heading_css not in heading:
    raise SystemExit("CSS titolo generico inatteso")
heading = heading.replace(
    generic_heading_css,
    generic_heading_css + '''
          body:has([class*="st-key-mostra_parametri_aggiuntivi"])
          [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-electrical_pair_layout"])
          [data-testid="stElementContainer"]:has(.mortem-section-title--supra) {
            margin-bottom: -1.18rem !important;
          }
''',
    1,
)

old_body = '''            body = (
                "<div class='mortem-section-title'>"
                f"{html.escape(nome_parametro)}"
                "</div>"
            )
'''
new_body = '''            title_class = "mortem-section-title"
            if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY:
                title_class += " mortem-section-title--supra"
            body = (
                f"<div class='{title_class}'>"
                f"{html.escape(nome_parametro)}"
                "</div>"
            )
'''
if old_body not in heading:
    raise SystemExit("Markup titolo inatteso")
heading = heading.replace(old_body, new_body, 1)

supra_path.write_text(supra, encoding="utf-8")
heading_path.write_text(heading, encoding="utf-8")

# Guardie finali: nessuna vecchia cornice/compensazione deve restare.
supra_final = supra_path.read_text(encoding="utf-8")
heading_final = heading_path.read_text(encoding="utf-8")
for forbidden in (
    "_IMAGE_ONLY_FRACTION = 0.76",
    "margin-top: -1.50rem !important;",
    "min-height: 1.95rem !important;",
):
    if forbidden in supra_final:
        raise SystemExit(f"Residuo inatteso: {forbidden}")

for required in (
    "_IMAGE_ONLY_FRACTION = 0.69",
    "from PIL import Image, ImageDraw",
    "draw.line((0, 0, row_width - 1, 0)",
    "border-bottom: 1px solid rgba(105, 105, 105, 0.72)",
    "gap: 0 !important;",
):
    if required not in supra_final:
        raise SystemExit(f"Modifica mancante: {required}")

if "mortem-section-title--supra" not in heading_final:
    raise SystemExit("Classe titolo sopraciliare mancante")
