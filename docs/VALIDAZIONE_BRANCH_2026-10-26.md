# Verifica completa del branch — 26 ottobre 2026

**Esito: convalida non completata con successo; non promuovere ancora su main.**

Repository: scopusjin/codice. Revisione esaminata: cb9db235d1d1c0760c56ac89459d923f7a0c888c, refactor-tanatology-keys. Main verificato: 43ab9bca62a9b8cd27f2831f08f7050049265d0f. Nessun codice applicativo modificato durante questa verifica.

## App principale e sistema che la mantiene sveglia

Il workflow `.github/workflows/keepalive.yml` è identico tra main e il branch esaminato. Conserva il ping ogni 15 minuti e il commit vuoto su main, URL https://mor-tem.streamlit.app/. Conserva anche il lavoro separato su MSIL/ispezionelegale.streamlit.app: la sospensione della pagina MSIL interna non ha modificato quel workflow. L’aggiornamento futuro va effettuato sullo stesso main, senza creare una nuova app né cambiare URL o configurazione del keepalive. Stato di esecuzione live del workflow non verificato: l’endpoint relativo ai workflow non è supportato dal connettore disponibile.

## Controlli eseguiti

- Installazione completata con requirements.txt e constraints-py312.txt; Streamlit 1.64.0, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2 e streamlit-extras 1.6.0. `pip check`: nessun conflitto.
- Compilazione app, pagine attive, pagina MSIL archiviata e ingresso principale superata. Diff whitespace superato.
- Suite unittest globale: 385 test, esito negativo (30 failure e 15 error, inclusi sottocasi). Non scambiare questi numeri con il numero di moduli.
- Verifica separata dei 63 moduli Python nell’ambiente con versioni prescritte: 45 moduli superati, 17 con errori/failure, 1 senza test unittest raccolti (test_device_mode.py usa funzioni pytest). L’isolamento riduce l’interferenza dei wrapper globali Streamlit. I test wrapper avviano a loro volta ulteriori test di pagina.
- JavaScript: 12 programmi test esaminati. 6 superati, 6 non superati. test_fc_language.cjs richiede il catalogo italiano/inglese come argomento: riprovato correttamente con catalogo corrente e superato; il primo lancio privo di argomento non è un difetto dell’app.
- Superate, tra le altre, le suite dei nuovi arrotondamenti, case_report, case_file, FC wet ranges, assunzioni coperture, temperatura acqua, picker file e archivio casi. Nessun test in browser reale e nessuna prova end-to-end del deploy pubblico dichiarati.

## Discrepanze accertate da risolvere prima della promozione

1. Test che puntano ancora a pages/App_MSIL.py, ora sospesa per richiesta dell’utente. Altri cercano selectbox di ipostasi sostituiti da componenti personalizzati o avvisi spostati dal riquadro warning alla nota finale. Vanno riscritti per l’interfaccia attiva, mantenendo una prova esplicita della sospensione MSIL.
2. test_audit_numeric_regressions richiede ancora valori interni già arrotondati: contraddice la decisione successiva sull’arrotondamento soltanto finale. Il test di pagina chiede minuti di calendario non arrotondati, anch’esso superato dalla decisione successiva. Aggiornare le aspettative usando risultati grezzi e verifica delle rappresentazioni finali, senza reintrodurre l’errore corretto.
3. Sei suite JavaScript FC non passano: contextual_examples, counters, field_controls, panel_engine, panel_ui, scenarios. Riprodotte TUTTE con esito negativo anche sul commit precedente cb76f970 (23 ottobre), quindi non introdotte dall’arrotondamento o dalla rimozione pagine. Esempi: engine attende [1.4,1.4] per tre strati pesanti mentre la app rende [1.4,1.6]; il test degli esempi cerca un peso che l’UI sintetica non mostra; field_controls simula un DOM privo di querySelectorAll richiesto dal componente. Separare aspettative storiche da eventuali problemi reali: non modificare la logica scientifica soltanto per far passare i test.
4. Test catalogo: attesa di 6 casi operativi contro 30 nel catalogo attuale; confronto tra elenco completo e soli esempi contestuali. Confermare il perimetro documentale prima di aggiornare i controlli.
5. Test tanatologici e tabelle: vecchia attesa 1–4 ore per ipostasi in confluenza contro 0–4 nel codice; categorie aggiunte non presenti nella vecchia attesa. Le due failure test_tanatology_data si riproducono anche su cb76f970. Altre failure sono testuali («almeno 1 ora» contro «almeno un’ora») o harness della tabella non compatibile con il rendering corrente. Verificare la corrispondenza con le decisioni/fonti e aggiornare solo i controlli superati.
6. Failure mobile, intestazioni e testi Potente richiedono confronto con UI attuale e con i commit che hanno cambiato i testi; non sono stati qualificati indiscriminatamente come difetti applicativi o ignorati.

## Esiti Python per modulo

| Modulo | Esito | Durata s |
|---|---|---:|
| test_audit_numeric_regressions.py | NON SUPERATO | 1.8 |
| test_audit_pages_regressions.py | NON SUPERATO | 7.2 |
| test_case_browser.py | superato | 0.9 |
| test_case_file.py | superato | 1.9 |
| test_case_file_picker.py | superato | 0.8 |
| test_case_page.py | NON SUPERATO | 10.3 |
| test_case_report.py | superato | 4.1 |
| test_cautelativa_presentational_i18n.py | superato | 1.5 |
| test_combined_reference_observations.py | NON SUPERATO | 0.7 |
| test_cooling_applicability.py | superato | 1.5 |
| test_cooling_input_regressions.py | superato | 1.5 |
| test_cooling_pages_regressions.py | NON SUPERATO | 18.3 |
| test_cooling_validation_details.py | superato | 1.4 |
| test_decimal_number_input_v2.py | superato | 1.5 |
| test_device_mode.py | nessun test unittest raccolto | 0.7 |
| test_factor_description_i18n.py | superato | 0.6 |
| test_factor_ui_states.py | superato | 0.6 |
| test_fc_catalog.py | NON SUPERATO | 1.7 |
| test_fc_page.py | NON SUPERATO | 45.9 |
| test_fc_provenance.py | superato | 0.7 |
| test_fc_reference_table.py | NON SUPERATO | 0.7 |
| test_fc_scenarios.py | superato | 1.3 |
| test_fc_selection.py | superato | 0.6 |
| test_fc_two_phase_prototype.py | superato | 1.6 |
| test_fc_ui_helpers_and_time.py | superato | 0.6 |
| test_fc_weight.py | NON SUPERATO | 0.7 |
| test_final_rounding_policy.py | superato | 3.1 |
| test_final_time_rounding.py | superato | 0.8 |
| test_full_factor_ui.py | superato | 0.6 |
| test_full_mobile_flow.py | NON SUPERATO | 5.3 |
| test_full_tanatology.py | superato | 0.7 |
| test_graphing_tanatology.py | superato | 0.6 |
| test_i18n.py | superato | 0.7 |
| test_i18n_english.py | superato | 0.6 |
| test_language_page.py | NON SUPERATO | 12.7 |
| test_language_presentation.py | superato | 2.1 |
| test_livor_compact_layout.py | NON SUPERATO | 0.7 |
| test_livor_pressure_visibility.py | superato | 0.7 |
| test_locale_it_compatibility.py | superato | 0.7 |
| test_manual_fc_case.py | superato | 3.6 |
| test_mixed_cooling_description.py | superato | 3.8 |
| test_msil_factor_ui.py | superato | 0.6 |
| test_msil_tanatology.py | superato | 0.6 |
| test_page_navigation.py | superato | 0.6 |
| test_plotting_i18n.py | superato | 1.2 |
| test_render_context.py | superato | 0.7 |
| test_rigor_temperature_warnings.py | superato | 1.8 |
| test_runtime_ui_i18n.py | superato | 0.7 |
| test_special_tanatology_states.py | superato | 0.6 |
| test_subpage_headings.py | NON SUPERATO | 0.1 |
| test_surface_ui_states.py | superato | 0.7 |
| test_tanatology_data.py | NON SUPERATO | 0.6 |
| test_tanatology_regression.py | NON SUPERATO | 0.7 |
| test_tanatology_states.py | superato | 0.6 |
| test_tanatology_texts_it.py | superato | 0.7 |
| test_tanatology_time_labels.py | superato | 0.7 |
| test_textgen_henssge_i18n.py | superato | 0.7 |
| test_textgen_presentational_i18n.py | NON SUPERATO | 0.7 |
| test_textgen_special_paragraphs.py | superato | 0.7 |
| test_textgen_tanatology.py | superato | 0.6 |
| test_textgen_time_formatting.py | superato | 0.7 |
| test_ui_i18n.py | NON SUPERATO | 0.6 |
| test_word_launch.py | superato | 3.4 |

## Prossimo intervento

Aggiornare gli harness e le aspettative esplicitamente superate dalle decisioni già approvate; mantenere test indipendenti su range scientifici e dati di origine. Indagare le discrepanze restanti, ripetere la suite e le prove desktop/mobile reali. Soltanto dopo promuovere il commit convalidato sul main esistente, preservando integralmente keepalive.yml. Non dichiarare il branch interamente convalidato sulla base dei soli test mirati dei singoli interventi.


## Aggiornamento dei test per decisioni già adottate — 26 ottobre 2026

Dopo il riscontro dell’utente e la verifica della cronologia sono allineate le sole aspettative già superate:

- FC ordinario multistrato 1.40–1.60: commit c5fad888 e aggiornamento della guida 3a9bde74 del 17 ottobre. Corretto il caso pertinente nel test del motore; verifica mirata superata. La suite engine complessiva mantiene altre discrepanze non trattate qui.
- Ipostasi in via di confluenza 0–4 ore: commit 3ce0f3bf e testo 3425f760 del 16 ottobre. Test delle mappe aggiornato anche alle categorie confluite aggiunte con eeef49b0. Le formulazioni «almeno un’ora» e «tra 1 e 6 ore» seguono i testi concordati (869f997b).
- test_audit_numeric_regressions ora verifica valori interni non arrotondati e indipendenti dall’impostazione, coerentemente con la decisione del 26 ottobre. La suite final_rounding_policy continua a verificare entrambe le rappresentazioni finali e le impostazioni.
- Test del catalogo: 30 casi operativi (763f83cb); distinzione fra archivio completo e selezione contestuale importata (b143643d). Conservato il confronto dei dati per tutte le 152 schede, senza pretendere un matcher per ogni scheda di archivio. Le condizioni sintetiche omettono il richiamo ridondante al tronco inferiore, mantenendo il confronto con i dati originali.
- Test del riepilogo contestuale aggiornato soltanto per le omissioni dei pesi, concordate nella presentazione compatta (6c7d3f8d). Il peso originale del caso resta verificato nel catalogo. Il controllo successivo sulla denominazione del simulatore continua a fallire: non è stato cancellato né adeguato automaticamente all’implementazione.
- Descrizione Potente aggiornata alla formulazione già implementata con 525852a1, mantenendo i controlli sulle soglie di applicabilità.
- Aggiunto test esplicito delle pagine disattivate e del rifiuto dell’import MSIL senza alterare il caso corrente. I vecchi test di navigazione MSIL richiedono ancora una revisione tecnica separata.

Superati 54 test Python selezionati (50 test su dati tanatologici, testi, audit numerico, arrotondamenti e report; 2 test mirati catalogo; 2 sospensione pagine) e la verifica JavaScript mirata FC 1.40–1.60. Nessun codice applicativo, parametro scientifico, formula, workflow o main modificato. Le altre suite negative del rapporto iniziale non sono dichiarate risolte. La convalida complessiva e la pubblicazione restano da completare.

## Secondo allineamento alle decisioni confermate

Aggiornati i test di pagina dell'audit e del raffreddamento: valori grezzi prima dell'arrotondamento finale, nota FC accanto all'etichetta, errori di raffreddamento resi nella nota finale, selettore ipostasi personalizzato. Il controllo della temperatura rettale mancante verifica anche colore giallo e dimensione 8pt. I controlli prima dedicati alla navigazione MSIL verificano ora l'assenza della pagina attiva e la conservazione del sorgente disattivato; la persistenza del FC resta verificata nella pagina principale. Il test statico del peso legge il sorgente MSIL archiviato senza riattivarlo. Selettore ipostasi: aggiornate le aspettative sulle etichette traducibili (0df24142) e sul font compatto (c501b24d).

Superati separatamente 6 test audit, 15 test raffreddamento, 8 test selettore e 20 test peso FC: 49 test. Nessuna modifica al codice applicativo o al main. Non costituisce convalida dell'intero branch: restano i wrapper storici di navigazione/lingua/FC, le tabelle e le suite JavaScript da completare.
