"""Text-only FC descriptions for current output and historical summaries."""

from typing import Any, Dict, Optional

from app import i18n

def build_cf_description(
    cf_value: float,
    riassunto: Optional[Dict[str, Any]],
    fallback_text: Optional[str] = None,
    manual_override: bool = False  # True se FC inserito/modificato manualmente
) -> str:
    """
    Rende una stringa tipo:
    "1.40 (corpo nudo sotto una coperta pesante, adagiato su superficie termicamente conduttiva, con correnti d'aria. Il fattore di correzione è stato adattato per il peso corporeo.)"
    Regole:
      - Nessuna parentesi se manual_override=True.
      - Non menzionare 'asciutto'; 'bagnato' non usato; 'Immerso' → 'corpo immerso' + stato acqua.
      - Superficie solo se ≠ indifferente.
      - Correnti d'aria solo se presenti.
      - Aggiungi frase peso se riassunto['peso_adattato'] è True.
    """
    return i18n.factor_correction_description(
        cf_value=cf_value,
        summary=riassunto,
        fallback_text=fallback_text,
        manual_override=manual_override,
    )
