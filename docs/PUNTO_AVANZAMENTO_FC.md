# Punto di avanzamento FC — 19.10.2026

- Repository: scopusjin/codice.
- Branch app di test, confermata dall'utente: refactor-tanatology-keys.
- Commit di partenza verificato: 8e619f6ccf3746884e8b8e93f208d19bb63e9e4b.
- Commit corrente dell'intervento: il commit che contiene questo aggiornamento (vedere git log).
- Ultimo commit con test manuale valido: non identificato; l'utente conferma corretto il grafico della versione di partenza.

## Intervento autorizzato

Nei casi misti Henssge/Potente il dettaglio del raffreddamento usa il medesimo minimo aperto già impiegato dal grafico. Un unico paragrafo spiega l'applicabilità parziale di Henssge e il ricorso a Potente al raggiungimento della soglia critica. Il minimo di Potente compare soltanto nella nota blu, senza presentarlo come una soglia temporale di validità di Henssge. Nessuna separazione dei risultati per scenario nel testo principale.

File: app/graphing.py (aggiorna_grafico), app/textgen.py (due helper testuali), app/graphing_cooling.py (rimozione avviso misto ora inglobato nel nuovo paragrafo), tests/test_mixed_cooling_description.py.
Formule, valori FC, grafico e intersezione con gli altri dati tanatologici invariati. I casi interamente entro o fuori dai limiti conservano i testi precedenti.

## Verifica

Caso: Tr 17.1 °C, T0 37.2 °C, peso 85 kg; 11 °C / FC 0.70 e 15 °C / FC 1.20–1.40. Dettaglio: più di 16 ore e 30 minuti; nota blu Potente: 43 ore. Con ipostasi migrabili perlomeno parzialmente, la conclusione combinata conserva il massimo di 24 ore.
Controllo sintattico e diff; test integrati Streamlit del dettaglio e della conclusione combinata; 7 test di applicabilità; 30 dei 31 test textgen passano. L'unico errore textgen è preesistente e riprodotto con app/textgen.py del commit di partenza: test_potente_paragraph_keeps_current_html_and_inclusive_boundary attende una formulazione diversa da quella già presente.

## Problemi e prossimo passo

Attendere il test manuale dell'utente sull'app di test. Nessuna ulteriore modifica autorizzata.
L'ipotesi iniziale di un errore numerico (43 anziché 50.5 ore) è stata smentita dalla conferma del range 1.20–1.40 nel secondo scenario: non riproporla. L'utente ha respinto la proposta di esporre risultati separati per scenario.

## Precisazione successiva autorizzata

Base verificata: 14bd0f8e0e1c36438d0319babdbfd713d471f74a. Testo principale allineato alla formulazione Potente standard: Henssge può fornire risultati sufficientemente attendibili soltanto per una parte delle combinazioni dei sopracitati parametri. Nota blu Potente introdotta da «Nel caso in esame» e spostata dopo il paragrafo Qd. Test di regressione aggiornato per verificare anche l'ordine. Test manuale ancora da eseguire; calcoli invariati.

## Finestra Caso — intervento autorizzato 19.10.2026

Base verificata: 0b4166a2e6c9918630d427b119fbfa77e9c4dfbe. Il pulsante Caso apre ora un dialogo Streamlit piccolo, con sigla in alto e selettore Salva/Carica. Una sola sezione attiva: salvataggio nel browser e download, oppure archivio browser e caricamento JSON richiudibile. Elenco nativo a quattro righe con scorrimento interno. Chiusura nativa del dialogo. Le chiavi UI aggiunte __case_dialog_open e __case_dialog_mode gestiscono esclusivamente apertura e scheda; nessuna chiave dati esistente rinominata. Importazione differita e archivio IndexedDB conservati.

File coinvolti: app/case_ui.py, app/case_browser.py, app/case_browser_frontend/index.html e main.js; test case_page_checks.py e test_case_browser.cjs. Verificati sintassi Python/JS, diff, test Python dei casi (13 test, inclusa suite integrata), successiva suite integrata con test aggiuntivo apertura/modalità/chiusura/sigla, e test Node dell'archivio browser. Verifica visiva locale non completata perché Chromium non è disponibile e il download non riesce. Prossimo passo: test manuale desktop/mobile dell'utente. Nessuna modifica a formule, risultati, serializzazione dei casi o dati memorizzati.

## 19 ottobre 2026 — esportazione descrizioni per macro Word

Base GitHub verificata: 4861f8ec581cdbd69d2de314dc705d1a1d4b0d09, branch refactor-tanatology-keys. Autorizzato il salvataggio dei testi nel JSON per successiva importazione Word.
Il campo opzionale report contiene detailed_text (testo leggibile con elenchi) e detailed_html (formattazione originale, comprese note blu). Vale null in assenza di una stima corrente. Firma dei dati della stima e flag della pagina impediscono di esportare risultati superati; la modifica della sola sigla non invalida il testo. I vecchi casi restano leggibili; caricando un caso i testi vengono ricalcolati, non ripristinati come HTML eseguibile. Formule invariate.
Verifica: test round-trip, compatibilità, testo/formattazione, invalidazione e payload effettivo Streamlit della pagina completa. Macro Word e ingresso dei dati esterni ancora da realizzare; occorre definire il segnalibro/content control di destinazione e acquisire il modulo JSON VBA in uso. Test manuale sull'app ancora da eseguire.

### Blocchi Word selettivi autorizzati

Base verificata 4dc83cdb. report.word_blocks separa temperatura ambientale, FC/condizioni, raffreddamento, ipostasi, rigidità e conclusione. Ogni blocco contiene html, text e insert_when. La temperatura porta la regola different_from_msil: il confronto va eseguito dalla futura macro con il dato MSIL originale, non con quello eventualmente modificato nell'app. Gli altri blocchi hanno regola always. Prima occorrenza di «macchie ipostatiche» e «rigidità cadaverica» sottolineata nell'HTML. Conclusione senza elenco, preceduta da paragrafo vuoto. Note blu escluse da questi blocchi, conservate nel report completo. Nessuna modifica ai testi visualizzati o ai calcoli. Test integrato del caso misto e dei sei blocchi, con verifica delle sottolineature e dell'assenza delle note blu. Macro non ancora implementata; destinazioni Word da definire.

### Collegamento macro Word — apertura con dati

Base verificata 255ddf39. Nuovo app/word_launch.py: ingresso esplicito mt_open=1 con numero X, data/ora, peso e temperature; validazione prima di sostituire lo stato del caso, rimozione dei parametri URL dopo l'importazione. Usa il ripristino caso esistente; nessun nome o cognome trasferito. Test di parsing (mancanti/non validi) e AppTest con dati reali anonimizzati: X26.115, 17.10.2026 14:25, 85 kg, Ta 11, Tr 17.1. Macro standalone consegnata separatamente in Mortem_Word.zip, basata sullo stampone fornito; non richiede modifiche a ThisDocument o IML_Core. Verificati gli ancoraggi univoci e la struttura VBA; compilazione/esecuzione reale in Word da verificare su copia dall'utente.

### Blocco unico Word con gerarchia elenchi

Base verificata ae36f907. Esportazione estesa a putrefaction e additional, usando i medesimi testi generati per il dettaglio; parametri aggiuntivi conservati come singoli punti. Nessuna modifica ai calcoli o al testo visualizzato. Macro aggiornata separatamente: sostituisce soltanto Mortem_Valutazione, senza cercare/sostituire sezioni esterne. T/FC secondo livello, reperti primo livello, conclusione senza elenco e con riga vuota. Modelli di formato ripresi da introduzione raffreddamento/peso e testo normale nello stampone. Ombreggiatura azzurra RGB 204/238/255, sottolineature mantenute. Vecchie alternative da rimuovere una volta nello stampone. Restano da verificare in Word esecuzione e resa; non disponibile runtime VBA. Ripristino automatico dei casi Mor-tem tramite macro di apertura ancora non implementato.

### Ritorno automatico da Word autorizzato

Base verificata 81449c23081e7ed2c9f56cefd3a59be94d5c2de1. Aperture con mt_request (32 cifre esadecimali) mantengono un contesto di ritorno nella sola sessione. Pulsante Scarica riepilogo per Word dopo stima corrente; nessun pulsante/contesto nelle aperture normali. Esporta il caso completo con report e metadati opzionali word_return, legati a numero X e richiesta; il caricamento ordinario non riattiva automaticamente tali metadati. Cambio di caso cancella il collegamento.
Macro TXT aggiornata: controllo esterno temporaneo WScript (non OnTime, gia' usato da ThisDocument per i CC). Cerca solo il file univoco in Download/cartella documento, attende dimensione stabile e documento attivo; ritorno al documento senza cambio di focus forzato. Callback controlla token, numero X e documento prima di trasferire. Copia su file temporaneo nella cartella destinazione, confronto integrale, conserva eventuale file precedente, rinomina, importa nel segnalibro. Cancella il download solo dopo importazione riuscita. Errori rete/copia lasciano il download disponibile. Termine entro 2 ore o chiusura; richiede Windows Script Host abilitato e usuale singola istanza Word. Nessun cambio policy/associazione file.
Test parsing/validazione, isolamento sessione normale, download effettivo UI, firma dati e rifiuto di dati superati. Esecuzione COM/VBA e su rete non verificabile qui: test reale dell'utente necessario; non dichiarare compatibilita' garantita sulla rete dell'IML. Ripristino dei precedenti FC/scenari all'apertura ancora non implementato.

### Download JSON senza archivio browser — 19 ottobre 2026

Base verificata 405a2aba8c1bedbbce868a03994a9c4807092b7b. Il menu Caso espone soltanto Scarica JSON e Carica da file, con uploader immediatamente visibile. Il componente IndexedDB non viene più importato né montato: nessuna nuova persistenza dei casi nel browser. I precedenti archivi non vengono cancellati automaticamente. Sessione temporanea necessaria al calcolo e flusso Word separato invariati.
Controllo del TXT Word: se non arriva il JSON univoco non sono eseguite copia/importazione; il watcher termina dopo due ore o quando non trova più il documento originale. La chiusura della sola scheda browser non è rilevata immediatamente. Nessuna modifica VBA necessaria per evitare aggiornamenti in caso di abbandono; esecuzione reale Windows/Word ancora da verificare dall'utente.
Verifica: 17 test Python dei casi superati (inclusa suite integrata Streamlit), 4 test del flusso Word superati; diff senza errori di whitespace. Controlli delle due modalità del dialogo aggiornati per verificare assenza del componente browser, download e caricamento da file.

### Testi menu Caso — 20 ottobre 2026

Base f05616e9669ede9750dccd92d6291aa5a1104b56. Su autorizzazione: pulsante «Scarica caso» e nota «Esegui la stima per includere anche le valutazioni.». La nota resta condizionata all’assenza di un report corrente; serializzazione e flusso Word invariati. Verificati sostituzioni puntuali e sintassi Python.

### Word: ritorno con Fatto — 20 ottobre 2026

Avviso download allineato alla nuova macro fornita separatamente: salvare nella cartella del documento e premere Fatto. Dopo segnalazione antivirus eliminati nella macro script esterni, polling e timer. Fatto legge esclusivamente mortem_<caso>_<richiesta>.json e verifica i metadati; non sceglie il primo JSON della cartella. File assente: avviso e finestra aperta. Il modulo DatiCasoJSON originale fornito il 19 ottobre usa il nome fisso _dati_caso.json; eventuali versioni successive restano da controllare. Verificati sintassi Python, struttura VBA, corrispondenza filename app/macro; Word e rete da provare dall’utente.

### Nome stabile stimaX — 20 ottobre 2026

Download Word e menu Caso per codici Xnn.numero: stimaXnn.numero.json, senza token nel nome. Metadati caso invariati. Macro consegnata separatamente: Fatto cerca nome esatto e duplicati browser numerati nella cartella del documento, verifica formato/numero X/presenza dei blocchi; se più compatibili richiede selezione, senza preferire automaticamente il più recente. Nessuna copia, rinomina o cancellazione; importazione solo su clic. Vecchi file mortem_* non vengono scelti automaticamente. Ripristino automatico del caso nell’app ancora non implementato.

### Strati bagnati e coperte — 20 ottobre 2026

Base GitHub verificata ceb03e12deb7920a42aef806a3eea09bcb611cea; branch refactor-tanatology-keys. Modifica autorizzata dall’utente in questa conversazione. Commit corrente: il commit contenente questa sezione (git log); ultimo test manuale valido non identificato.

Range aggiornati nel motore attivo app/fc_panel_frontend/index.html (RULES, wetBlanketDecision): un pesante e quattro leggeri/misti 1.00–1.10; più di due pesanti 1.20 senza aumento automatico a 1.30. Coperte spesse completamente impregnate: 1.00–1.10 singola con al massimo un leggero, 1.10–1.20 per coperture maggiori; correnti 0.70–0.90, oppure 0.90 con almeno due pesanti. Coperte leggere seguono la convenzione già esistente di uno strato pesante.

Domande separate indumenti/teli e coperte, quando distinguibili dai contatori, condivise desktop/mobile: completamente impregnati, solo in parte/umidi, non determinabile. Nel conteggio mobile aggregato, teli/coperture leggere restano nel gruppo vestiti/teli, senza inventarne la suddivisione. Per condizioni parziali o incerte evaluateFC comprende gli scenari interamente bagnato e interamente asciutto della stessa configurazione (non calcola un isolamento misto validato). Se un qualificatore asciutto manca, comprende entrambe le categorie esistenti. Formula, peso, temperature, immersione e regole dell’asciutto invariati. Avviso per imbottiture ancora isolanti; frase sulle coperte mantenuta nella versione richiesta dall’utente. Riferimenti bagnati ed esempi riuniti nel pannello fonti, aggiunti Wang 2016 e Farnworth/Dolhan 1983, senza attribuire loro FC.

Persistenza dei due campi nella bozza/scenari; versione delle regole per ricalcolare i vecchi suggerimenti automatici alla riapertura del pannello, preservando FC manuali. Descrizione delle condizioni estesa in descriptions.js. Nessuna chiave Streamlit rinominata.

Verifiche: tests/test_fc_wet_ranges.cjs superato (esempi concordati, 162 confronti tra scenari, salvataggio/ripristino e scelte manuali); 3600 configurazioni asciutto/immerso identiche al commit iniziale. test_fc_field_controls.cjs e test_fc_water_temperature.cjs superati. Harness DOM aggiornato per API già usate dall’app. Le suite engine, UI, counters, scenarios e contextual examples hanno errori già riprodotti sul commit iniziale (harness corretto): non dichiarate superate. Test Python non avviabili: Streamlit non installato nell’ambiente. Diff controllato. Prossimo passo: test manuale desktop/mobile dell’utente, in particolare una coperta spessa full 1.00–1.10 / partial 1.00–1.80, aria ferma e piano neutro. Non ancora verificata resa grafica in browser reale.
