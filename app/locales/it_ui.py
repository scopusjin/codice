# -*- coding: utf-8 -*-
"""Testi italiani delle interfacce Streamlit.

Il catalogo contiene soltanto testo/presentazione. Chiavi di sessione, default,
regole di calcolo e valori legacy restano nei moduli applicativi.
"""

from __future__ import annotations


UI_TEXT = {
    # ------------------------------------------------------------------
    # UI completa — struttura generale
    # ------------------------------------------------------------------
    "full.title": "STIMA EPOCA DECESSO",
    "full.add_datetime": "Aggiungi data/ora rilievi tanatologici",
    "full.inspection_date": "Data ispezione legale:",
    "full.inspection_time": "Ora ispezione legale (HH:MM):",
    "full.livor_heading": "Ipostasi:",
    "full.livor_select_label": "Macchie ipostatiche:",
    "full.rigor_heading": "Rigidità cadaverica:",
    "full.rigor_select_label": "Rigidità cadaverica:",

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
    "full.weight_uncertainty": "±3 kg",
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

    # UI completa — dati tanatologici aggiuntivi / azioni
    "full.add_special_data": "Aggiungi dati tanatologici speciali",
    "full.special_datetime_hint": (
        "<div style='font-size:0.9rem; color:#666; padding:6px 8px; "
        "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
        "Per specificare orari dei rilievi, attiva in alto "
        "<b>“Aggiungi data/ora rilievi”</b>."
        "</div>"
    ),
    "full.assessed_different_time": "Valutato ad un'ora diversa?",
    "full.measurement_date": "Data rilievo:",
    "full.measurement_time": "Ora rilievo:",
    "full.measurement_time_input": "Ora rilievo (HH:MM):",
    "full.putrefactive_changes": "Alterazioni putrefattive?",
    "full.estimate_button": "STIMA EPOCA DECESSO",
    "full.no_data_warning": "Nessun dato inserito per la stima",
    "full.henssge_incoherent_warning": (
        "Non è stato possibile applicare il metodo di Henssge "
        "(temperature incoerenti o fuori range)."
    ),

    # ------------------------------------------------------------------
    # UI MSIL — struttura generale
    # ------------------------------------------------------------------
    "msil.page_title": "STIMA EPOCA DECESSO - MSIL",
    "msil.no_description": "<p style='opacity:.7'>Nessuna descrizione disponibile.</p>",
    "msil.add_datetime": "Aggiungi data/ora rilievi tanatologici",
    "msil.inspection_date": "Data ispezione legale",
    "msil.inspection_time": "Ora ispezione legale (HH:MM)",
    "msil.livor_select_label": "Macchie ipostatiche",
    "msil.rigor_select_label": "Rigidità cadaverica",
    "msil.rectal_temp": "T. rettale (°C)",
    "msil.ta_mean": "T. ambientale media (°C)",
    "msil.weight": "Peso (kg)",
    "msil.fc_label": "Fattore di correzione (FC)",
    "msil.suggest_fc": "Suggerisci FC",
    "msil.clothed_covered": "Vestiti/coperte su addome/bacino?",
    "msil.item_column": "Voce",
    "msil.count_column": "Numero?",
    "msil.support_surface": "Superficie di appoggio",
    "msil.air_currents": "Correnti d'aria presenti?",
    "msil.estimate_button": "STIMA EPOCA DECESSO",
    "msil.recommendations_button": "ℹ️ Raccomandazioni",
    "msil.recommendations_html": (
        "<div style=\"font-size:0.9rem; line-height:1.45; color:#444;\">\n"
        "      <b>LA VALUTAZIONE DEL RAFFREDDAMENTO CADAVERICO NON È APPLICABILE SE:</b><br><br>\n"
        "      • Luogo di ispezione/rinvenimento ≠ luogo del decesso.<br>\n"
        "      • Fonti di calore nelle vicinanze del corpo.<br>\n"
        "      • Riscaldamento a pavimento sotto il corpo.<br>\n"
        "      • Ipotermia certa/sospetta (T iniziale < 35 °C).<br>\n"
        "      • Temperatura ambientale media non determinabile o temperatura aumentata molto dopo il decesso.<br>\n"
        "      • Fattore di correzione non stimabile<br><br>\n"
        "      <b>DA RICORDARE:</b><br><br>\n"
        "      • Non usare direttamente la temperatura ambientale misurata, ma ragiona su come è cambiata la temperatura tra decesso e ispezione (è aumentata durante il giorno? vi era più freddo nella notte?). Stima la temperatura media in cui potrebbe essersi trovato il corpo. Tieni conto di eventuali dati meteorologici.<br>\n"
        "      • Migrabilità ≠ improntabilità (quest'ultimo dato non serve per questa app). Cambia posizione al cadavere e valuta se si modificano le ipostasi dopo 20 minuti.<br>\n"
        "      • Per il fattore di correzione, considera solo gli indumenti e le coperture a livello delle porzioni caudali del tronco del cadavere. Il sistema che suggerisce il fattore di correzione è indicativo. Prova varie combinazioni e un range di fattori.<br>\n"
        "      • L'applicazione considera di default, prudentemente, possibili variazioni di ±1 °C per la temperatura ambientale inserita, di ± 0.1 per il fattore di correzione, di ±3 kg per il peso stimato.<br><br> \n"
        "    </div>"
    ),
}


def ui_text(key: str, **values) -> str:
    """Restituisce un testo UI italiano, formattandolo se richiesto."""
    text = UI_TEXT[key]
    return text.format(**values) if values else text


__all__ = ["UI_TEXT", "ui_text"]
