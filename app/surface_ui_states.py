# -*- coding: utf-8 -*-
"""Identificatori UI stabili per le superfici di appoggio del pannello FC.

Le etichette italiane e i valori legacy sono mantenuti identici a quelli
attualmente esposti da ``app.factor_calc.SURF_DISPLAY_ORDER``. Il modulo non
contiene né modifica regole di calcolo o classificazione delle superfici.
"""

from __future__ import annotations

from typing import Dict


SURFACE_HOME_FLOOR_WOOD = "surface_home_floor_wood"
SURFACE_DRY_ASPHALT_GROUND_GRASS = "surface_dry_asphalt_ground_grass"
SURFACE_MATTRESS_THICK_CARPET = "surface_mattress_thick_carpet"
SURFACE_SOFA_SLEEPING_BAG_POLYSTYRENE = "surface_sofa_sleeping_bag_polystyrene"
SURFACE_CONCRETE_STONE_PVC = "surface_concrete_stone_pvc"
SURFACE_COLD_FLOOR = "surface_cold_floor"
SURFACE_METAL_INDOOR = "surface_metal_indoor"
SURFACE_THICK_METAL_OUTDOOR = "surface_thick_metal_outdoor"
SURFACE_WET_LEAVES = "surface_wet_leaves"
SURFACE_DRY_LEAVES = "surface_dry_leaves"

SURFACE_LABEL_IT: Dict[str, str] = {
    SURFACE_HOME_FLOOR_WOOD: "Pavimento di casa/piano in legno.",
    SURFACE_DRY_ASPHALT_GROUND_GRASS: "Asfalto/terreno/prato asciutti",
    SURFACE_MATTRESS_THICK_CARPET: "Materasso/tappeto spesso",
    SURFACE_SOFA_SLEEPING_BAG_POLYSTYRENE: "Divano/sacco a pelo tecnico/polistirolo",
    SURFACE_CONCRETE_STONE_PVC: "Cemento/pietra/PVC",
    SURFACE_COLD_FLOOR: "Pavimento freddo (all’aperto/in cantina)",
    SURFACE_METAL_INDOOR: "Piano metallico (all’interno)",
    SURFACE_THICK_METAL_OUTDOOR: "Piano metallico spesso (all’aperto)",
    SURFACE_WET_LEAVES: "Strato di foglie umide (≥2 cm)",
    SURFACE_DRY_LEAVES: "Strato di foglie secche (≥2 cm)",
}

SURFACE_ID_BY_LABEL_IT: Dict[str, str] = {
    label: surface_id for surface_id, label in SURFACE_LABEL_IT.items()
}


def surface_state_id(ui_label: str) -> str:
    """Restituisce l'identificatore stabile associato all'etichetta italiana."""
    return SURFACE_ID_BY_LABEL_IT[ui_label]


def surface_legacy_value(ui_label: str) -> str:
    """Restituisce la stringa legacy attualmente attesa da factor_calc."""
    return SURFACE_LABEL_IT[surface_state_id(ui_label)]


__all__ = [
    "SURFACE_HOME_FLOOR_WOOD",
    "SURFACE_DRY_ASPHALT_GROUND_GRASS",
    "SURFACE_MATTRESS_THICK_CARPET",
    "SURFACE_SOFA_SLEEPING_BAG_POLYSTYRENE",
    "SURFACE_CONCRETE_STONE_PVC",
    "SURFACE_COLD_FLOOR",
    "SURFACE_METAL_INDOOR",
    "SURFACE_THICK_METAL_OUTDOOR",
    "SURFACE_WET_LEAVES",
    "SURFACE_DRY_LEAVES",
    "SURFACE_LABEL_IT",
    "SURFACE_ID_BY_LABEL_IT",
    "surface_state_id",
    "surface_legacy_value",
]
