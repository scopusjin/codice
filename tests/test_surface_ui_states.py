# -*- coding: utf-8 -*-

from app.factor_calc import SURF_DISPLAY_ORDER
from app.surface_ui_states import (
    SURFACE_LABEL_IT,
    surface_legacy_value,
    surface_state_id,
)


def test_surface_labels_match_legacy_order_exactly():
    assert list(SURFACE_LABEL_IT.values()) == list(SURF_DISPLAY_ORDER)


def test_surface_round_trip_preserves_legacy_strings():
    for surface_id, label in SURFACE_LABEL_IT.items():
        assert surface_state_id(label) == surface_id
        assert surface_legacy_value(label) == label
