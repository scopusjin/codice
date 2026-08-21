# -*- coding: utf-8 -*-
"""Testi italiani delle interfacce Streamlit.

Il catalogo contiene soltanto testo/presentazione. Chiavi di sessione, default,
regole di calcolo e valori legacy restano nei moduli applicativi.
"""

from __future__ import annotations


UI_TEXT = {
    # UI completa — raffreddamento / fattore di correzione
    "full.prudent_toggle": "Stima prudente",
    "full.henssge_not_applicable": "Metodo di Henssge non applicabile",
    "full.henssge_not_applicable_help": (
        "Il metodo di Henssge non può essere applicato nelle seguenti circostanze:\n"
        "• Non è possibile stabilire che il luogo di rinvenimento del corpo coincida con il luogo del decesso.\n"
        "• Presenza di una fonte di calore nelle immediate vicinanze del corpo.\n"
        "• Presenza di riscaldamento a pavimento sotto il corpo.\n"
        "• Ipotermia accertata o sospetta (temperatura corporea iniziale < 35 °C).\n"
        "• Impossibilità di determinare la temperatura ambientale media.\n"
        "• Impossibilità di stimare il fattore correttivo di Henssge.\n"
        "• Aumento significativo della temperatura ambientale (da valori bassi a elevati)."
    ),
    "full.prudent_default_note": (
        "<div style='font-size:0.9rem; color:#444; padding:6px 8px; "
        "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
        "Se non diversamente specificato, si considererà "
        "un range di incertezza di ±1.0 °C per la T. ambientale media "
        "e di ±0.10 per il fattore di correzione."
        "</div>"
    ),
    "full.specify_range": "Specifica range",
    "full.ta_mean_label": "T. ambientale media (°C):",
    "full.ta_range_label": "Range di T. ambientale media (°C):",
    "full.fc_label": "Fattore di correzione (FC):",
    "full.fc_range_label": "Range del fattore di correzione (FC):",
    "full.rectal_temp_label": "T. rettale (°C):",
    "full.antemortem_temp_label": "T. ante-mortem (°C):",
    "full.antemortem_temp_estimated_label": "T. ante-mortem stimata (°C):",
    "full.weight_label": "Peso (kg):",
    "full.weight_label_standard": "Peso  (kg):",
    "full.ta_input_label": "T. ambientale (°C):",
    "full.ta_base_input": "TA base",
    "full.ta_other_input": "TA altro estremo",
    "full.fc_input_label": "Fattore di correzione:",
    "full.fc_min_input": "FC min",
    "full.fc_max_input": "FC max",
    "full.fc_input": "FC",
    "full.suggest_fc": "Suggerisci FC",
    "full.fc_suggested": "Fattore di correzione suggerito: {value:.2f}",
    "full.fc_adjusted_for_weight": "Adattato per {weight:.1f} kg (valore per 70 kg: {base:.2f})",
    "full.use_this_factor": "✅ Usa questo fattore",
    "full.add_to_fc_range": "➕ Aggiungi a range FC",
    "full.clothed_covered": "Vestito/coperto?",
    "full.count_column": "Numero?",
    "full.support_surface": "Superficie di appoggio",
    "full.air_currents": "Correnti d'aria presenti?",
}


def ui_text(key: str, **values) -> str:
    """Restituisce un testo UI italiano, formattandolo se richiesto."""
    text = UI_TEXT[key]
    return text.format(**values) if values else text


__all__ = ["UI_TEXT", "ui_text"]
