# -*- coding: utf-8 -*-
"""Geometria comune delle griglie di eccitabilità elettrica."""

from PIL import Image, ImageDraw


# Le immagini sorgente dei due metodi hanno già volti di scala sovrapponibile,
# ma tele di larghezza diversa. La misura della cella peribuccale conserva
# integralmente elettrodi e spalle e diventa quindi la tela comune.
ELECTRICAL_TILE_SIZE = (247, 211)


def normalize_electrical_tile(tile):
    """Centra una figura sulla tela comune senza ingrandirla o deformarla."""
    target_width, target_height = ELECTRICAL_TILE_SIZE
    image = tile.convert("RGB")

    scale = min(1.0, target_width / image.width, target_height / image.height)
    if scale < 1.0:
        image = image.resize(
            (
                max(1, round(image.width * scale)),
                max(1, round(image.height * scale)),
            ),
            Image.Resampling.LANCZOS,
        )

    canvas = Image.new("RGB", ELECTRICAL_TILE_SIZE, (255, 255, 255))
    x = round((target_width - image.width) / 2)
    # Allineamento superiore: fronte e vertice restano alla stessa quota nelle
    # due metodiche; l'eventuale spazio residuo rimane sotto le spalle.
    canvas.paste(image, (x, 0))
    return canvas


def neutral_electrical_tile():
    """Crea la medesima cella neutra per entrambe le griglie."""
    canvas = Image.new("RGB", ELECTRICAL_TILE_SIZE, (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    width, height = canvas.size
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
    return canvas
