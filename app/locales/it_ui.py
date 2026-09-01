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
    "full.livor_heading": "Ipostasi",
    "full.livor_select_label": "Macchie ipostatiche:",
    "full.rigor_heading": "Rigidità cadaverica",
    "full.rigor_select_label": "Rigidità cadaverica:",

    # UI completa — raffreddamento / fattore di correzione
    "full.cooling_heading": "Raffreddamento cadaverico",
    "full.prudent_toggle": "Condizioni variabili?",
    "full.henssge_not_applicable": "Henssge non applicabile",
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
        "Usa questa modalità quando la temperatura ambientale media e il fattore di correzione "
        "potrebbero essere cambiati nel tempo o sono incerti. Per ciascun parametro, inserisci "
        "i due estremi plausibili dell’intervallo, cioè il valore minimo e il valore massimo da "
        "considerare nel calcolo. Per il fattore di correzione, «Consiglia» aiuta a individuare "
        "il valore da associare a ciascun estremo."
        "</div>"
    ),
    "full.specify_range": "Specifica range",
    "full.ta_mean_label": (
        "T. ambientale media (°C): "
        "<span title='Considera la temperatura ambientale media alla quale il corpo può essere stato esposto "
        "tra il decesso e l’ispezione. Non corrisponde necessariamente alla temperatura misurata al momento "
        "del rilievo, soprattutto se il cadavere si trova all’aperto.'>ⓘ</span>"
    ),
    "full.ta_range_label": (
        "Range di T. ambientale media (°C): "
        "<span title='Considera la temperatura ambientale media alla quale il corpo può essere stato esposto "
        "tra il decesso e l’ispezione. Non corrisponde necessariamente alla temperatura misurata al momento "
        "del rilievo, soprattutto se il cadavere si trova all’aperto.'>ⓘ</span>"
    ),
    "full.ta_mean_help": (
        "Considera la temperatura ambientale media alla quale il corpo può essere stato esposto tra il decesso "
        "e l’ispezione. Non corrisponde necessariamente alla temperatura misurata al momento del rilievo, "
        "soprattutto se il cadavere si trova all’aperto."
    ),
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
    "full.estimate_button": "Procedi con la stima",
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

    # ------------------------------------------------------------------
    # Rendering grafico / messaggi condivisi
    # ------------------------------------------------------------------
    "graph.missing_inspection_datetime_html": "<p style='color:red;font-weight:bold;'>⚠️ Inserisci data e ora dell'ispezione legale.</p>",
    "graph.invalid_inspection_time_html": "<p style='color:red;font-weight:bold;'>⚠️ Errore: formato ora ispezione legale non valido. Usa HH:MM.</p>",
    "graph.invalid_weight": "⚠️ Peso non valido. Inserire un valore > 0 kg.",
    "graph.invalid_factor": "⚠️ Fattore di correzione non valido. Inserire un valore > 0.",
    "graph.missing_temperatures": "⚠️ Temperature mancanti.",
    "graph.invalid_special_time": "⚠️ {parameter}: escluso perchè ora '{time}' non valida (usa HH:MM).",
    "graph.missing_special_description": "Descrizione non trovata per '{state}'.",
    "graph.special_without_range": "{parameter} ({state}) senza range definito.",
    "graph.no_useful_data": "Mancanza di dati utili per la stima",
    "graph.shifted_ranges_note": "Alcuni parametri sono stati rilevati in orari diversi; i range indicati con \"*\" sono stati traslati per renderli confrontabili.",
    "graph.henssge_missing_invalid": "Non è stato possibile applicare il metodo di Henssge per il raffreddamento cadaverico: dati mancanti o non validi.",
    "graph.henssge_incoherent": "Non è stato possibile applicare il metodo di Henssge per il raffreddamento cadaverico: dati incoerenti o fuori range",
    "graph.henssge_equal_temperature_warning": (
        "T. rettale e T. ambientale sono uguali: il metodo di Henssge non è applicabile "
        "per assenza di gradiente termico."
    ),
    "graph.henssge_equal_temperature_detail": (
        "<ul><li>La temperatura rettale e la temperatura ambientale sono entrambe pari a <b>{temperature} °C</b>. "
        "Questo suggerisce che il corpo abbia raggiunto l’equilibrio termico con l’ambiente, condizione che non permette di applicare il metodo di Henssge.</li></ul>"
    ),
    "graph.henssge_below_ambient_warning": (
        "T. rettale inferiore alla T. ambientale: metodo di Henssge non applicabile. "
        "Verificare i dati inseriti."
    ),
    "graph.henssge_below_ambient_detail": (
        "<ul><li>La temperatura ambientale media è superiore alla temperatura rettale; pertanto non è possibile effettuare una stima "
        "dell’epoca del decesso basata sul raffreddamento cadaverico. Verificare che le misurazioni o i dati inseriti siano corretti; "
        "in alternativa, il corpo potrebbe aver raggiunto l’equilibrio termico con l’ambiente e le condizioni ambientali potrebbero "
        "essersi successivamente modificate. Ricordarsi di utilizzare la temperatura ambientale media (che potrebbe essere inferiore "
        "alla temperatura misurata durante l’ispezione legale).</li></ul>"
    ),
    "graph.high_ambient_factor_warning": "Per temperature ambientali &gt; 25 °C, variazioni del fattore di correzione possono influenzare notevolmente i risultati.",
    "graph.low_ambient_factor_warning": "Per temperature ambientali &lt; 18 °C, la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati.",
    "graph.thermal_equilibrium_warning": "Essendo minima la differenza tra temperatura rettale e ambientale, è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione.",
    "graph.plateau_warning": "Considerato che la T rettale è molto simile alla T ante-mortem stimata, è verosimile che il raffreddamento corporeo non fosse ancora iniziato e/o si trovasse nella fase di plateau. In tale fase, la precisione del metodo è ridotta.",
    "graph.discordant_html": "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
    "graph.discordant_detail_html": "<ul><li><b>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</b></li></ul>",
    "graph.descriptions_popover": "📖 Descrizioni dettagliate",
    "graph.warnings_popover": "⚠️ Avvisi",
    "graph.parameter_livor": "Macchie ipostatiche",
    "graph.parameter_rigor": "Rigidità cadaverica",
    "graph.parameter_cooling": "raffreddamento cadaverico",
    "graph.parameter_cooling_prudent_open": "raffreddamento cadaverico (cautelativo: limite superiore aperto)",
    "graph.parameter_cooling_potente": "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)",

    # ------------------------------------------------------------------
    # Grafico — etichette
    # ------------------------------------------------------------------
    "plot.livor": "Ipostasi",
    "plot.rigor": "Rigor",
    "plot.cooling": "Raffreddamento",
    "plot.generic_parameter": "Parametro",
    "plot.hours_since_death": "Ore dal decesso",

    # ------------------------------------------------------------------
    # Sorgenti dati / messaggi tecnici
    # ------------------------------------------------------------------
    "data.weight_table_missing": "Tabella correttiva del peso non trovata: continuo senza.",
    "data.openpyxl_missing": "Per leggere il file .xlsx serve 'openpyxl'. Installa con: pip install openpyxl",
    "data.weight_table_read_error": "Impossibile leggere l'Excel della tabella peso: {error}",
}


def ui_text(key: str, **values) -> str:
    """Restituisce un testo UI italiano, formattandolo se richiesto."""
    text = UI_TEXT[key]
    return text.format(**values) if values else text


__all__ = ["UI_TEXT", "ui_text"]
