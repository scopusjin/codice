from app.factor_calc import DressCounts, compute_factor


def _wet_naked(surface: str, currents: bool = False):
    return compute_factor(
        stato="Bagnato",
        acqua=None,
        counts=DressCounts(),
        superficie_display=surface,
        correnti_aria=currents,
        peso=70.0,
        tabella2_df=None,
    )


def test_wet_naked_neutral_surface_keeps_single_075():
    result = _wet_naked("Asfalto/terreno/prato asciutti")
    assert result.fattore_finale == 0.75
    assert result.riassunto["fc_range_suggerito"] is None


def test_wet_naked_conductive_surface_suggests_range():
    result = _wet_naked("Cemento/pietra/PVC")
    assert result.riassunto["fc_range_suggerito"] == (0.60, 0.75)


def test_wet_naked_mattress_suggests_range():
    result = _wet_naked("Materasso/tappeto spesso")
    assert result.riassunto["fc_range_suggerito"] == (0.85, 0.95)


def test_wet_naked_highly_insulating_surface_suggests_range():
    result = _wet_naked("Divano/sacco a pelo tecnico/polistirolo")
    assert result.riassunto["fc_range_suggerito"] == (0.95, 1.10)


def test_wet_naked_highly_conductive_metal_suggests_range():
    result = _wet_naked("Piano metallico spesso (all’aperto)")
    assert result.riassunto["fc_range_suggerito"] == (0.55, 0.75)


def test_wet_naked_with_air_currents_remains_single_070():
    result = _wet_naked("Cemento/pietra/PVC", currents=True)
    assert result.fattore_finale == 0.70
    assert result.riassunto["fc_range_suggerito"] is None
