# Punto di avanzamento FC — 19.10.2026

## Descrizioni inglesi più dirette — 23.10.2026

- Revisione approvata dall'utente: inglese più sintetico e naturale, senza
  corrispondenza obbligatoria parola per parola con l'italiano.
- Base GitHub verificata `aa1d0bd23d939be46f387414b4af5feded643d43`, branch
  `refactor-tanatology-keys`, repository `scopusjin/codice`.
- Riscritti i testi di raffreddamento, Qd, Potente, ipostasi/digitopressione,
  rigor/ricomparsa, eccitabilità elettrica/meccanica/farmacologica, putrefazione,
  dati utilizzati e conclusioni. Le formule introduttive ripetitive diventano
  frasi che collegano direttamente reperto e indicazione temporale.
- Mantenuti tutti i numeri delle descrizioni dei reperti, i limiti aperti/chiusi
  e le precisazioni cliniche. La sola modifica in `app/graphing.py` riguarda
  tre stringhe inglesi per inserire l'orario termometrico e il contesto dei
  rilievi effettuati in orari diversi. Nessuna modifica al motore scientifico,
  ai testi italiani o al formato dei casi. Footer e assunzioni rosse invariati.
- Verifiche mirate: 12 test risorse, 7 test lingua (di cui uno esegue 5 controlli
  integrati di pagina), 4 test report/Word e 3 test raffreddamento misto.
  Verificati i limiti numerici, la parità dei risultati IT/EN, il riconoscimento
  dei blocchi Word, le sottolineature e l'esclusione delle note blu dai blocchi.
  Questi controlli non equivalgono all'esecuzione della macro dentro Word.
- Confronto bilingue rigenerato con `scripts/preview_translation_en.py`.
  Commit corrente: quello contenente questa nota. Main invariato.


## Selettore non fisso e assunzioni sulle coperture — 23.10.2026

- Ultima indicazione dell’utente: selettore lingua piccolo in fondo alla pagina,
  **non sticky**; sacco mortuario e mantellina devono risultare chiaramente
  assunzioni degli autori, in rosso, con riferimento Henssge sintetico.
- Base verificata su GitHub: `fe08554276b0a185cde032df6c720a2e5d5dd228`,
  repository `scopusjin/codice`, branch `refactor-tanatology-keys`; main invariato.
- Rimosso `st.bottom`: selettore nel normale flusso alla fine di Full, MSIL,
  FC/scenari, impostazioni, tabelle e riferimenti, anche prima degli stop previsti.
  Restano bandiere, sigle, dimensione compatta e chiavi della lingua.
- Nel pannello FC: assunzioni in rosso per entrambi i dispositivi; riferimento
  separato e neutro a FC 1.2 per 1–2 strati pesanti asciutti e FC 1.8 per una
  coperta spessa. Soppressa la generica attribuzione verde del FC alla tabella
  per questi dispositivi. Testi italiani/inglesi allineati; chiarita anche la
  nota sulla mantellina nelle tabelle. Le normali coperte conservano i dettagli
  e il confronto H08; l’avviso esteso non compare per le equivalenze dei dispositivi.
- Nessuna modifica a categorie numeriche, formule, valori FC, peso o input.
  La spiegazione salvata nel caso precisa l’assunzione anche quando la categoria
  utilizzata nel calcolo proviene dalla tabella.
- Superati 7 test `test_language_*` (inclusi 5 controlli integrati di pagina,
  cambio IT/EN, FC, stop per dati mancanti, report e casi) e il nuovo controllo
  JavaScript delle assunzioni, dei colori e della parità numerica per condizioni
  asciutte/bagnate, pesi 50/70/100 kg e tre appoggi. Sintassi e diff superati.
- Quattro verifiche JavaScript preesistenti (`test_fc_counters`,
  `test_fc_panel_engine`, `test_fc_panel_ui`, `test_fc_scenarios`) non passano:
  riprodotti gli stessi errori sulla base precedente in worktree separato.
  Non dichiarare verde l’intera suite.
- Commit corrente: quello contenente questa nota. Dopo la pubblicazione,
  verificare la resa sul server; resta il riscontro dell’utente sul telefono.

## Selettore lingua e diciture inglesi — 23.10.2026

**Decisione finale aggiornata durante lo stesso intervento:** l'utente ha
sostituito l'indicazione «in alto» con «sempre in basso, in piccolo, abbreviato,
con bandiere». Posizione finale: contenitore nativo Streamlit `st.bottom`,
selettore `🇮🇹 IT / 🇬🇧 EN`, allineato a destra e disponibile anche scorrendo
la pagina e nei pannelli FC. Rimosso il raggruppamento temporaneo col titolo;
la pagina principale recupera il suo contenitore titolo originario. Il CSS
aggiunto regola soltanto font e padding del selettore; il posizionamento è nativo.
L'abbreviazione `Mean amb. T.` riguarda i campi compatti/mobile; sul desktop
resta `Mean ambient temperature`. La cronologia seguente documenta il primo
passaggio, superato per quanto riguarda la posizione del selettore.

- Repository `scopusjin/codice`; branch dell'app di test `refactor-tanatology-keys`.
  Base GitHub verificata `1c4a7dbb62e07d23036b56a0fa9d76ee23abd88a`; commit
  corrente: quello contenente questa sezione. Ultimo commit integralmente
  confermato dal test manuale dell'utente: non identificato.
- Richiesta autorizzata: selettore Italiano/English in alto, traduzioni mancanti
  delle etichette dell'eccitabilità, temperatura media compatta e titolo
  `Time since death estimation`.
- `app/mobile_shell.py`, `install_minimal_mobile_shell`: reset dei contesti di
  layout prima di emettere i controlli; sulla Full desktop un unico contenitore
  nativo con titolo e lingua. `Stima_epoca_decesso.py` riempie lo slot del titolo
  riservato nell'intestazione. Su mobile il selettore resta prima del titolo e
  dei dati; nessun nuovo CSS o stato duplicato.
- `app/locales/en_runtime.py`: tradotte le etichette abbreviate elettriche,
  meccaniche e pupillari, che erano effettivamente rimaste italiane negli output
  AppTest; `Mean amb. T.` nelle etichette compatte, significato esteso mantenuto
  negli helper. `app/locales/en_ui.py`: titolo compatto nella Full e in MSIL.
  Allineati `docs/TRANSLATION_EN.md` e il confronto bilingue rigenerato.
- Nessuna modifica a formule, motore FC, soglie, peso, temperature, chiavi di
  sessione, valori legacy o testi dei risultati. Le funzioni della pagina
  principale sono identiche alla base, verificato tramite AST.
- Superati sintassi e diff; 6 test del gruppo `test_language_*` (la prova di
  pagina esegue 4 controlli integrati, inclusi i cicli IT/EN con parametri
  aggiuntivi aperti), più 12 test delle risorse inglesi. Verificati permanenza
  del selettore nell'intestazione dopo rerun, traduzione delle etichette
  desktop/mobile, identità degli input e risultati, round-trip dei report,
  riapertura casi e decisioni/bozze FC JavaScript.
- Suite `test_full_mobile_flow`: 7 successi, 2 failure e 1 error; gli stessi
  tre test non passano sul commit iniziale, verificato in worktree separato.
  Nessuna nuova failure osservata. Non dichiarare l'intera suite verde.
- App pubblica osservata nel browser prima dell'intervento: titolo esteso e
  selettore separato sulla riga successiva. Prossimo controllo: intestazione
  distribuita, poi test dell'utente sul proprio desktop/telefono, soprattutto
  spazio per `Mean amb. T.` e parametri aggiuntivi. Nessun ulteriore intervento
  funzionale concordato.

### Verifica pubblicazione e aggiornamento del traduttore in memoria

- Primo commit `652e992`: intestazione e titolo verificati nel browser pubblico;
  le etichette elettriche restavano invece italiane, pur essendo corrette in una
  nuova esecuzione locale. Registrato come tentativo incompleto per la parte
  traduzioni, non come risultato già verificato sul server.
- Causa individuata in `app/presentation_translation.py`,
  `install_presentation_translation`: dopo il ricaricamento dei moduli applicativi
  Streamlit conservava i wrapper già installati nei propri moduli, con i vecchi
  cataloghi. Il controllo `_mortem_translation` impediva di aggiornarli.
- Correzione nello stesso blocco funzionale: sostituzione dei soli wrapper di
  traduzione, recuperando le funzioni originali con `__wrapped__`; nessuna
  sovrapposizione di wrapper a ogni rerun. Aggiornati sia l'output sia le
  etichette trasmesse dai selettori. Formule, stato e valori legacy invariati.
- Test mirato di ricaricamento fallisce sulla base e passa con la correzione;
  superati tutti i 7 test `test_language_*`, compresi 4 controlli integrati di
  pagina, cambio lingua ripetuto, casi, report e confronto dei risultati FC.
  Sintassi e diff superati. Base del secondo commit: `652e9927f722d7f09da10524f774e46e1250da22`.
  Commit funzionale pubblicato: `1ecb07b962b8b49138890ae3c496908d2f7e8ea0`.
- Verifica nel browser pubblico dopo la pubblicazione: titolo
  `TIME SINCE DEATH ESTIMATION`, etichette `Electrical excitability — supraciliary`
  e `Electrical excitability — perioral` correttamente inglesi, selettore
  piccolo `🇮🇹 IT / 🇬🇧 EN` nella fascia inferiore nativa. Sul desktop la
  temperatura conserva `Mean ambient temperature`. App:
  `https://mortem-test.streamlit.app/`. Resta il test manuale dell'utente sul
  proprio telefono per lo spazio della dicitura compatta `Mean amb. T.`.

## Traduzione inglese — primo blocco, 22.10.2026

- Richiesta autorizzata: traduzione dell'intera app con terminologia scientifica,
  in particolare secondo il capitolo raffreddamento sul Drive; attuazione per
  blocchi con verifica manuale prima della fase successiva.
- Base GitHub verificata: `b15a18b17aa77f688393e96617fac7c2a4487efe`, branch
  `refactor-tanatology-keys`. Commit corrente: quello che contiene questa sezione.
- Aggiunte sette risorse inglesi in `app/locales/en*.py` e registrata la lingua
  esplicita `en` in `app/i18n.py`. Coperti tutti gli ID delle etichette, tutte le
  chiavi del catalogo UI esistente, descrizioni dei reperti, testi Henssge/Qd,
  Potente e conclusioni. Inclusi i sei esiti pupillari correnti specifici per
  farmaco. L'italiano resta il default; nessun selettore globale ancora attivato.
- Nessuna modifica alle risorse italiane, alle formule, ai valori scientifici,
  al motore FC, ai file dei casi o alle chiavi di sessione. Le stringhe ancora
  incorporate nelle pagine e nel JavaScript richiedono il blocco di integrazione.
- Terminologia, fonti consultate e attività residue in `docs/TRANSLATION_EN.md`.
  Confronto bilingue: `docs/translation_review_en.html`, rigenerabile con
  `scripts/preview_translation_en.py` (192 confronti, dati dimostrativi).
- Verifiche locali: sintassi Python e diff; 21 test i18n superati, di cui 12 nuovi
  per inglese, copertura delle chiavi/segnaposto, ID, formati, soglie e round-trip
  MSIL verso i valori legacy. Suite complessiva: 361 test, 19 failure e 11 error;
  sul commit iniziale 349 test con gli stessi 19 failure e 11 error e le medesime
  identità dei test non superati. Nessuna nuova failure/error osservata. Non
  dichiarare la suite interamente verde. Python 3.12 / Streamlit 1.64.0; le altre
  dipendenze locali non riproducono integralmente le versioni bloccate della CI.
- Resa verificata strutturalmente nell'HTML (coppie IT/EN); nessuna verifica in
  browser reale. Prossimo passo: revisione manuale del confronto bilingue e
  prova di regressione dell'app italiana, quindi selettore e integrazione delle
  schermate, FC/scenari/esempi e report/Word. L'intera app non è ancora tradotta.


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

### Rimozione separata del vecchio motore FC

Su autorizzazione esplicita rimosso app/factor_calc.py, privo di import applicativi, e il test esclusivo delle vecchie regole tests/test_wet_naked_surface_ranges.py. Il test delle etichette delle superfici conserva l’elenco storico come riferimento indipendente; moduli di compatibilità UI mantenuti. Documentazione aggiornata. Nessuna formula attiva eliminata. Controllo AST degli import, sintassi Python e test JS mirati superati; esecuzione Python con Streamlit da verificare nell’ambiente applicativo.

### Testi dei controlli bagnati — 20 ottobre 2026

Base GitHub 78e346cd190468668b6ba71d8c7e03eefb56f082 verificata. Su richiesta: «Quanto sono bagnate le coperte?» con Fradicie / Solo in parte (Da precisare come segnaposto); stessa semplificazione per indumenti/teli. Eliminati i due avvisi sotto i controlli. Spiegazione in «Come viene consigliato il FC»: riferimenti Henssge secondo il movimento dell’aria, confronto bagnato/asciutto, isolamento residuo dei materiali e adattabilità al caso. Modifiche solo in app/fc_panel_frontend/index.html, wetCoverExplanation e presentazione; range invariati. Test wet_ranges (162 confronti e persistenza), field_controls e diff superati. Da provare su desktop/mobile.


### Descrizione della coperta impregnata — 20 ottobre 2026

Base bb55e7b verificata. Correzione autorizzata in app/fc_panel_frontend/descriptions.js: stato della coperta unito alla sua descrizione, con accordo singolare/plurale («sotto una coperta spessa impregnata d’acqua»), senza ripetizione separata. Esteso alle sole coperture spesse/molto pesanti anche quando parzialmente bagnate; combinazioni con teli mantenute distinte. Verificati singolare, plurale, parziale e test wet_ranges. Nessuna modifica dei range.


### Precisazioni testuali esempi bagnati — 20 ottobre 2026

Base c4f02b9 verificata. Su richiesta esplicita: «due camici bagnati 1.10» e «tre camici bagnati, FC 1.10–1.30» nel riepilogo delle fonti. Solo due stringhe di presentazione, nessuna modifica delle regole o dei dati sperimentali di dettaglio.


### Unificazione spiegazione bagnati — 20 ottobre 2026

Su richiesta: riferimenti tabellari riuniti in un paragrafo; esempi Henssge/Brinkmann in un secondo paragrafo; eliminati richiamo generico ripetuto e ripetizione dei valori tabellari in wetCoverExplanation. Spiegazione breve specifica per fradicie/parzialmente bagnate con isolamento residuo e adattabilità al caso. Range invariati; test wet_ranges superato (162 confronti e persistenza), diff verificato. Resa da confermare dall’utente.

### Domande sulle coperte — 21 ottobre 2026
- Domanda sulle coperte bagnate accanto alle altre domande delle coperture; sul desktop ogni domanda usa tutta la larghezza dei contatori.
- Domande da completare in rosso e ! accanto ai contatori delle coperte presenti finché manca una risposta visibile.
- Testo semplificato: «Le coperture formano uno strato molto voluminoso?»; specificato «correnti d’aria» nei riferimenti.
- Verificati range bagnati, 162 confronti bagnato/asciutto, persistenza e comparsa/scomparsa dell’avviso; test controlli FC superato. Verifica visiva non eseguita: browser Playwright non installato.

### Domanda unica sui tessuti — 21 ottobre 2026
- Unificate le domande: «Quanto sono bagnati i tessuti sul corpo?» — «Tutti fradici» / «Solo in parte intrisi».
- Mantenuti i criteri del range: tutti fradici usa il bagnato; condizioni parziali estendono verso l’asciutto dell’intera configurazione.
- Etichette degli indumenti e delle coperte selezionati rosse finché mancano risposte pertinenti; conservato ! per le coperte.
- Recupero delle vecchie risposte dei soli gruppi presenti, conservazione delle scelte manuali e sincronizzazione dei campi precedenti per compatibilità.
- Superati test range bagnati (162 confronti), migrazione, persistenza, avvisi ed editor FC. Verifica visiva ancora da eseguire nell’app.

### Download e apertura diretti; compatibilità dei casi — 21 ottobre 2026

- Repository `scopusjin/codice`, branch dell’app di test `refactor-tanatology-keys`; base GitHub verificata `45c271a31b0c50f03fdbe2a37bedbddb005e6d29`. Commit corrente: quello contenente questa sezione; correzione del formato separata nel commit `78cdfa08`. Ultimo commit confermato da test manuale dell’utente: non identificato.
- Autorizzati due soli comandi nel dialogo Caso: **Scarica caso** scarica direttamente; **Apri caso** apre il selettore del sistema e importa il JSON valido, senza schede intermedie o ulteriore conferma. Sigla, nome `stimaXnn.numero.json`, nota sulle valutazioni e avviso di versione conservati.
- `app/case_ui.py` (`_case_dialog`) usa il download nativo e un piccolo selettore file in `app/case_file_picker.py` / `app/case_file_picker_frontend/`. Nessun accesso all’archivio browser, nessuna persistenza aggiunta. L’apertura passa dal validatore e dall’importazione differita esistenti. Un solo nuovo stato UI, `__case_upload_event`, evita di ripetere lo stesso caricamento; nessuna chiave dei dati del caso rinominata.
- Errore dello screenshot riprodotto: `_validate_draft` in `app/case_file.py` non accettava `wetRulesVersion`, `wet-textiles`, `wet-clothes`, `wet-covers`, già prodotti dal pannello attivo. Aggiunti alla validazione, mantenendo la compatibilità con i file precedenti. In `render_word_download` un eventuale `CaseFileError` viene mostrato senza interrompere il resto della pagina.
- Formule, range FC, peso, temperature, testi dei risultati e metadati Word invariati. Nessuna modifica al motore FC.
- Verificati sintassi Python/JS e diff. Superati 22 test Python (più 14 sottocasi), inclusa la suite Streamlit di ripristino desktop/mobile e Completa/Sopralluogo; verificati file non validi e assenza di ripetizione dell’importazione. Test Node del selettore: clic diretto, annullamento, limite 1 MB, UTF-8 non valido, eventi superati. Superati anche i 162 confronti dei range bagnati. Verificato il percorso con payload reale JS: pannello FC → esportazione JSON → riapertura → download per Word.
- Limite della verifica: Chromium non disponibile; download Playwright falliti sia per la versione corrente sia per una precedente. Nessuna verifica visiva o prova del selettore in browser reale dichiarata. Prossimo passo: test manuale dei due pulsanti e del caso X26.117 nell’app aggiornata. La vecchia soluzione Scarica/Carica più pulsante sottostante è stata respinta dall’utente: non riproporla.

### Compattezza e descrizione dei tessuti parzialmente bagnati — 21 ottobre 2026

- Base GitHub verificata `d0aa5523da133a2d1842a87a0f623bd80f200765`, repository e branch invariati. Commit corrente: quello contenente questa sezione. Ultimo commit confermato integralmente da test manuale: non identificato.
- Su richiesta: opzioni **Fradici** / **Solo in parte bagnati** in `app/fc_panel_frontend/index.html`; valori interni `full` / `partial` invariati. La sola riga `wet-textiles-row` in `panel.css` usa un gruppo flex con distanza orizzontale di 8 px e ritorno a capo naturale; eliminata la colonna elastica che spingeva la risposta sul bordo opposto. Le altre domande restano invariate.
- In `descriptions.js`, `conditions` usa `partiallyWetTextiles` per indicare una sola volta la condizione parziale comune a indumenti e coperture. Esempio verificato: «corpo bagnato, con uno strato di indumenti leggeri e sotto una coperta spessa parzialmente bagnati, adagiato su pavimento». Accordi singolare/plurale e maschile/femminile verificati anche per sole coperte o teli; mantellina termica e sacco mortuario restano distinti dalla qualificazione dei tessuti.
- Nessuna modifica al motore FC, alle chiavi di sessione o ai calcoli. Confrontati gli script di calcolo prima/dopo: identici. Superati controllo sintattico JS, diff, 162 confronti bagnato/asciutto, test dei controlli FC e verifiche mirate delle descrizioni. Asciutto, immersione, tessuti fradici e condizione non precisata mantengono i testi precedenti.
- Da provare nell’app: vicinanza domanda/risposta su desktop e ritorno a capo su mobile. Per una scelta FC già applicata, riaprire il pannello e premere Usalo per rigenerare la descrizione. Verifica visiva automatica ancora non disponibile; non riprovati i download Chromium già falliti. La disposizione con domanda e risposta ai lati opposti è stata respinta: non riproporla.

### FC manuale e riconoscimento del riepilogo Word — 23 ottobre 2026

- Repository `scopusjin/codice`; branch dell'app di test `refactor-tanatology-keys`; base GitHub verificata `0df2414288cf515fa9fe7dd9d790829e400b7dd9`. Commit corrente: quello contenente questa sezione. Ultimo commit validato manualmente dall'utente: non identificato. Modifica autorizzata dopo riproduzione dell'errore segnalato.
- `app/case_file.py`, `_validate_draft`: il pannello usa `state=""` quando la condizione del corpo non è selezionata. Questo valore è valido nelle bozze, nelle scelte manuali e nelle bozze degli scenari, ma veniva rifiutato durante `capture_report`. Accettata la stringa vuota; valori sconosciuti e tipi non testuali continuano a essere rifiutati. Nessuna modifica a formule, logica FC, valori scelti, peso, temperature, testi o chiavi di sessione.
- Nuovo `tests/test_manual_fc_case.py`: FC singolo/intervallo, pagina completa/Sopralluogo, bozze annidate, esportazione/riapertura, report Word, rifiuto valori non validi e risultati superati, percorso reale della pagina completa fino al download Word. I casi di regressione falliscono sul codice iniziale; dopo la correzione superati 25 test Python e 40 sottocasi nella selezione case_file/case_report/word_launch/manual_fc_case. Superati sintassi, diff e 162 confronti dei range bagnati. Verificato anche payload reale JavaScript del pannello -> apply_choice -> capture_report -> JSON Word -> riapertura. Nessuna prova visiva in browser o esecuzione di Word effettuata.
- Word: il modulo `modMortemWord` estratto dall'ultima perizia disponibile (caricata il 23.10.2026), coerente con `modMortemWord_RC6_corretto.txt`, cerca ancora `mortem_<caso>_<richiesta>.json`. L'app produce già `stimaXnn.numero.json`. Preparato separatamente `modMortemWord_STIMAX_RC6.txt`: recupera la ricerca già presente in `modMortemWord_STIMAX.bas`, verifica formato/numero X/presenza dei blocchi Word, accetta duplicati browser numerati e richiede una scelta se più file sono validi. Legge direttamente il file senza copiarlo/rinominarlo/cancellarlo. Conservati `DatiCaso_LeggiJSONFile`, formattazione e finestra Fatto. Nessuna modifica automatica al documento Word.
- Prossima verifica dell'utente: ricaricare l'app, inserire FC manuale senza condizione del corpo, eseguire la stima e scaricare nuovamente il JSON nella cartella del documento. Sostituire il contenuto del modulo Word e provare Fatto; verificare anche duplicati e numero X differente. Il JSON effettivamente rifiutato dall'utente non è stato fornito: la discordanza del nome è accertata nel modulo disponibile, eventuali ulteriori difetti del singolo file restano da verificare.


### Orari conclusivi e cautela interpretativa — 26 ottobre 2026

- Repository `scopusjin/codice`, branch `refactor-tanatology-keys`, base GitHub verificata `cb76f970f6236b2d866fa862454acd89a0fda526`. Collegamento all’app di test documentato nel repository; commit effettivamente in esecuzione su Streamlit non verificato. Commit corrente identificabile dal messaggio «Arrotonda gli orari conclusivi al quarto d’ora e aggiunge cautela interpretativa». Ultimo commit confermato manualmente dall’utente: non identificato.
- Richiesta esplicita dell’utente: orari di decesso al quarto d’ora più vicino, nota blu piccola nelle descrizioni, due paragrafi integrali in corsivo dopo la conclusione. `app/textgen.py`: arrotondamento solo delle date/ore stimate, coerenza della data dopo mezzanotte; orario dei rilievi mantenuto esatto. Riutilizzata la funzione esistente in `app/utils_time.py`, correggendo la considerazione dei secondi e il mezzo passo in aumento; non aveva altri chiamanti attivi. Nessuna modifica a equazioni, intervalli scientifici, FC, peso, temperature o chiavi di sessione.
- `app/graphing.py`: nota blu nelle descrizioni con orari, cautela dopo conclusione dettagliata e riepilogo visibile, inclusa nel blocco conclusivo Word. Italiano conservato integralmente; corrispondente inglese disponibile. Nessuna macro Word modificata.
- Superati 14 test mirati (formattazione e nuovi casi: secondi, mezzo passo, cambio giorno, lingue, rilievi esatti, corsivo nel blocco Word) e 4 test case_report, compreso il percorso reale della pagina completa. Sintassi/import e diff verificati. La suite presentational_i18n contiene una discrepanza sul paragrafo Potente non interessato dall’intervento: non dichiarata superata. Nessuna verifica grafica in browser o esecuzione Word.
- Prossimo passo: test utente nell’app aggiornata, controllando orari non multipli di 15 minuti, nota blu e corsivo nelle descrizioni e nel riepilogo. Nessun ulteriore intervento concordato.


### Selettore lingua discreto e bandiere incorporate — 26 ottobre 2026

- Base GitHub verificata `e462a3ae7a4d02ce644ccd312070695c30b07449`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`. Richiesta esplicita: bandierine visibili e selezione meno marcata.
- Solo presentazione in `app/language.py`: `render_language_selector` usa piccole bandiere SVG incorporate tramite Markdown supportato dal controllo nativo, al posto delle emoji dipendenti dal sistema. Sigle IT/EN, posizione in basso non fissa, chiavi di stato, callback e traduzioni invariati. Selezione grigio tenue e bordo neutro; CSS circoscritto al selettore, senza cambiamenti strutturali. Usato anche il testid Active verificato nel frontend Streamlit installato.
- Sintassi/import, diff e 6 test language_presentation superati. Verificato con AppTest il passaggio IT/EN, le etichette con immagini e l’invalidazione dei report. Da confermare nell’app la resa visiva su desktop/mobile; nessun test in browser reale dichiarato. Prossimo passo: test utente delle bandiere e dell’evidenziazione. Nessuna modifica a calcoli o FC.


### Cautela soltanto nelle descrizioni dettagliate — 26 ottobre 2026

Base GitHub verificata `7891d3166569307221cf0ae09df38a0a2959e755`, branch `refactor-tanatology-keys`, repository `scopusjin/codice`. Su correzione esplicita dell’utente rimossa in `app/graphing.py`, `aggiorna_grafico`, la chiamata che mostrava i due paragrafi di cautela sotto il riepilogo breve. Conservati integralmente e in corsivo nelle descrizioni dettagliate e nel relativo blocco conclusivo Word; arrotondamenti e ogni altra funzione invariati. Sintassi/import, diff e 8 test case_report/final_time_rounding superati. Da confermare nell’app l’assenza sotto il riepilogo breve e la presenza nel dettaglio; nessuna verifica grafica in browser dichiarata.


### Nota discreta anche sotto la descrizione breve — 26 ottobre 2026

Base GitHub verificata `f2c4f333bd0570c69973085b5607d65c692e9f8e`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`. La nuova indicazione esplicita sostituisce la precedente: mostrare la cautela anche sotto la descrizione breve, in piccolo e blu. In `app/graphing.py`, `aggiorna_grafico`, ripristinata la nota esterna al riquadro breve con carattere 8pt blu, corsivo e margini contenuti. Testo italiano integrale, inglese già sintetico; dettagli e blocco Word invariati. Nessuna modifica ai calcoli, agli orari o al FC. Sintassi/import, diff e 8 test case_report/final_time_rounding superati. Resa grafica da confermare dall’utente nell’app aggiornata; nessuna verifica in browser reale dichiarata.


### Nota breve senza corsivo — 26 ottobre 2026

Base GitHub verificata `1850e30ad561d4f0c9d10562310b28e2046068d1`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`. Su richiesta esplicita rimossi soltanto i tag di corsivo dalla copia della cautela mostrata sotto il riepilogo breve in `app/graphing.py`, `aggiorna_grafico`. Dimensione 8pt, colore blu, testo e posizione invariati. Descrizioni dettagliate e blocco Word conservano il corsivo. Diff limitato alla presentazione della nota; sintassi/import e 4 test final_time_rounding superati. Resa visiva da confermare nell’app.


### Avviso raffreddamento compatto dopo la nota breve — 26 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`, base GitHub verificata `2052d969a5d4f62d1772ae9381c912979cf75e47`. Su richiesta esplicita, in `app/graphing.py`, `aggiorna_grafico`, eliminato il riquadro di avviso prima del grafico e mostrato il messaggio dopo la nota blu sotto il riepilogo breve, in 8pt senza corsivo. Helper di sola presentazione `_cooling_unavailable_note`: «Raffreddamento non calcolato (non compilati temperatura rettale, temperatura ambientale, peso corporeo e fattore di correzione).» con elenco dinamico dei dati effettivamente mancanti; equivalente inglese. Gli altri errori di validazione conservano il motivo e vengono presentati nella stessa posizione. Validatore, calcoli, dettagli, Word e chiavi invariati. Superati 12 test cooling_input_regressions/case_report; AppTest della pagina reale verifica un solo avviso, testo, 8pt, assenza del corsivo e posizione dopo la nota blu. Sintassi/import e diff verificati. Da confermare visivamente nell’app su desktop/mobile.


### Avviso in giallo — 26 ottobre 2026

Base GitHub `a8f0ff5d39eb34d4896d25a938d6218f19c234ca`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`. Richiesta esplicita: avviso raffreddamento in giallo. Modificato esclusivamente il colore della nota in `_cooling_unavailable_note` (`app/graphing.py`) in giallo ambrato #a66b00, mantenendo 8pt, posizione dopo nota blu e assenza di corsivo. Arrotondamenti non modificati: impostazione Henssge 6/15/30 minuti (default 30) su tempo centrale e limiti; orari conclusivi al quarto d’ora indipendentemente da tale scelta. Da confermare la resa visiva nell’app.


### Arrotondamento soltanto finale e impostazione condivisa — 26 ottobre 2026

- Repository `scopusjin/codice`, branch dell’app di test `refactor-tanatology-keys`, base GitHub verificata `12e3579a7f57dbdc7e5d16acadeed671a417295a`. Collegamento dell’app documentato; commit effettivamente distribuito da Streamlit non verificato. Commit corrente identificabile dal messaggio «Applica l’arrotondamento solo finale e collega note e Impostazioni». Ultimo commit confermato integralmente dall’utente: non identificato.
- Autorizzazione esplicita dopo gli esempi: 15 minuti, per difetto sul limite inferiore e per eccesso sul superiore; durate e orari ricavati separatamente dai valori originali, mai l’uno dalla rappresentazione già arrotondata dell’altro. Conservare entrambe le indicazioni e i riferimenti approssimativi.
- `app/henssge.py`: aggiunta modalità `round_minutes=None` che restituisce tempo centrale e limiti originali; conservata per compatibilità l’API numerica storica. `app/graphing_cooling.py`: la app usa la modalità non arrotondata sia nel calcolo singolo sia negli scenari/range; rimosso l’arrotondamento intermedio a 30 minuti del limite Potente. Equazioni, tolleranze scientifiche, soglie Qd e logica FC invariati.
- `app/graphing.py`: intervalli dei rilievi aggiuntivi traslati rispetto all’orario reale senza arrotondamenti intermedi; intersezioni/discordanze sui valori originali. Nessun CSS o layout del grafico modificato: le barre ricevono i valori originali. `app/textgen.py` / `app/utils_time.py`: arrotondamento diretto dei soli risultati presentati, con protezione dei multipli esatti dall’errore floating-point e corretta data a mezzanotte. Nei limiti aperti la conclusione usa il limite originale effettivo, senza sostituirlo con un valore Potente vicino. L’estremo tardivo non può superare l’orario noto dei rilievi. Descrizioni brevi/dettagliate e Word usano le stesse funzioni, compresi limiti aperti e note informative.
- Una sola chiave preesistente `henssge_round_minutes`, senza copie: opzioni 6/15/30, nuovo predefinito 15 nella pagina Impostazioni, nei due ingressi e nello snapshot JSON. Una scelta esplicita salvata in un vecchio caso resta rispettata. Non rinominata alcuna chiave. `pages/Impostazioni.py`: titolo riferito ai risultati finali, spiegazione del criterio e delle due rappresentazioni indipendenti; italiano/inglese aggiornati.
- Nota blu dettagliata italiana a 15 minuti: «Gli intervalli temporali e gli orari stimati del decesso sono arrotondati al quarto d’ora (per difetto al limite inferiore e per eccesso al limite superiore). L’ampiezza dell’arrotondamento è modificabile nelle Impostazioni.» A 6/30 minuti la nota riporta il valore effettivo. Disponibile anche senza data/ora. Inglese equivalente; cautela lunga e nota breve senza corsivo conservate.
- Esempio verificato: rilievi 14:08, valori originali 1h12–6h22; a 15 minuti durate 1h–6h30 e orari 07:45–13:00. A 30 minuti orari 07:30–13:00. Il test esclude l’errato 07:30 nel caso a 15 minuti che deriverebbe sottraendo la durata già arrotondata 6h30.
- Superati 56 test selezionati: final_rounding_policy, textgen_time_formatting, final_time_rounding, mixed_cooling_description, case_report, cooling_input_regressions, fc_scenarios e textgen_henssge_i18n. Inclusi 1803 confronti di contenimento dei limiti su 6/15/30 minuti, multipli esatti, cambio giorno, limiti aperti, rilievi invariati, invariabilità dei risultati grezzi al cambio impostazione, AppTest delle Impostazioni e del report breve/dettagliato/Word a 15 e 30 minuti. Aggiornate le sole aspettative dei test interessate dal nuovo criterio (precedente arrotondamento al più vicino e nota Potente 43h ora 42h45). Sintassi/import e diff controllati. La suite presentational_i18n conserva la discrepanza preesistente sul testo Potente: non dichiarata superata. Nessuna prova visiva in browser reale né esecuzione Word.
- Tentativi da non riproporre: arrotondamenti concatenati delle durate e poi degli orari; orari finali con minuti ricavati dall’orario dei rilievi senza arrotondamento; modifica del solo orario senza mantenere la durata; criterio al più vicino (superato dalla decisione esplicita per difetto/per eccesso). Prossimo passo: test utente su app aggiornata, Impostazioni 15/30 e nuova stima, desktop/mobile. Nessun altro intervento concordato.


### Rimozione Anteprima desktop e sospensione App MSIL — 26 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`, base GitHub verificata `4921e75646cff9d2bfc5bf040090eff645c48b28` (arrotondamento finale approvato dall’utente). Su richiesta esplicita eliminata `pages/99_Anteprima desktop.py`, il relativo test esclusivo e la traduzione del collegamento. App MSIL temporaneamente tolta dalla navigazione automatica spostando, senza modificarlo, `pages/App_MSIL.py` in `disabled_pages/App_MSIL.py`. Moduli di calcolo e formato dei casi MSIL conservati. In `app/case_ui.py` l’apertura di un caso MSIL segnala che la pagina è sospesa prima di modificare il caso corrente o tentare un collegamento inesistente. In `app/page_navigation.py` il pulsante Indietro di una sessione già aperta torna alla pagina principale se la cronologia punta alla pagina sospesa. Restano attive pagina principale, Tabelle di riferimento, Reference e Impostazioni. Superati 17 test page_navigation/language_presentation/case_report e AppTest della pagina principale e del rifiuto dell’importazione MSIL senza alterare il caso corrente. Sintassi e diff verificati. I test dedicati all’interfaccia MSIL non sono applicabili alla navigazione attualmente disattivata; il sorgente è conservato per ripristino. Da confermare il menu nell’app ricaricata. Nessuna modifica ai calcoli o all’arrotondamento appena approvato.


### Convalida completa prima di aggiornare main — 26 ottobre 2026

Richiesta esplicita dell’utente: convalidare tutto il branch e aggiornare l’app principale, conservando il sistema che la tiene sveglia. Base esaminata `cb9db235d1d1c0760c56ac89459d923f7a0c888c`; main `43ab9bca62a9b8cd27f2831f08f7050049265d0f`. Keepalive identico, URL e main da preservare. Esito complessivo non superato: suite globale 385 test con 30 failure/15 error; isolamento con dipendenze prescritte 45 moduli superati/17 negativi/1 senza unittest; JavaScript 6/12 programmi superati, incluso language con argomento corretto. Riprodotte le sei suite JS negative e test_tanatology_data anche su cb76f970: problemi di test/aspettative anteriori agli ultimi interventi, da distinguere da difetti reali. Compilazione e pip check superati. Dettagli, moduli e prossimo intervento in `docs/VALIDAZIONE_BRANCH_2026-10-26.md`. Nessun codice applicativo modificato e main non aggiornato: la convalida completa non può essere dichiarata positiva. Resta autorizzato l’aggiornamento dell’app principale soltanto dopo aver completato la verifica; non chiedere di nuovo permesso per quella pubblicazione già richiesta.


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


### 26 ottobre — convalida finale per rilascio

Suite completa 387 test Python OK, 12 suite JS OK, 5 controlli dispositivo OK; motore FC 33.600 combinazioni. Un solo skip esplicito nel wrapper FC per la navigazione MSIL sospesa, con test separati di esclusione della pagina e rifiuto dell'import. Aggiornati soltanto test e documentazione alle decisioni storiche; nessuna formula modificata. Promozione sul main esistente mantenendo keepalive.yml identico e MSIL nascosta. Dettagli in VALIDAZIONE_BRANCH_2026-10-26.md.

### Introduzione completa nel dettaglio e download finale — 27 ottobre 2026

- Repository scopusjin/codice, branch main; base GitHub verificata 7e1ed52f9c3d16caef72be755d9ec1a42dc00164. Intervento esplicitamente confermato dall’utente.
- Completato il riepilogo con intervalli in graphing_cooling/i18n/locales: temperature misurate (ambientale distinta dal range medio), peso, temperatura iniziale, quindi range ambientale e FC/condizioni già esistenti. Nessuna duplicazione del peso. Titolo delle temperature senza orario anche per valori singoli; italiano concordato e inglese corrispondente. Un dato ambientale misurato assente resta indicato come mancante, senza sostituirlo con il limite del range.
- graphing.aggiorna_grafico: Scarica caso dopo il testo del popover. Cattura del report corrente prima di generare il download, stesso snapshot/serializzazione/nome del menu Caso. case_ui.render_case_download mostra il promemoria di salvare nella cartella Word solo se il contesto Word corrisponde al caso. Il percorso non è trasmesso dal bridge: nessuna preselezione automatica della cartella.
- Sintassi, import durante AppTest, diff e 34 test mirati superati (detailed_inputs_download, textgen_presentational_i18n, case_report, mixed_cooling_description, final_rounding_policy, word_launch). Verificati dati visualizzati, report attuale, blocchi Word, pulsante e visibilità condizionata del promemoria. Calcoli, FC, arrotondamenti, keepalive e navigazione invariati. Nessuna esecuzione reale della macro Word o verifica visiva del server dichiarata.
- Commit corrente: quello contenente questa nota. Prossimo passo: prova utente nell’app principale del dettaglio e del download nella procedura Word. Ultimo commit con conferma visiva precedente non identificato; nessun tentativo fallito in questo intervento.

### Riepilogo e formattazione Word — 29 ottobre 2026

- Repository scopusjin/codice, branch main, base verificata 02a810e25844a6c33dc0dc26e24081ab154241ef. Deploy main documentato anche in keepalive.yml; workflow invariato. Autorizzazione esplicita dell'utente per app e modulo Word.
- henssge_detail_paragraph IT/EN: paragrafo senza punto elenco, rientro HTML di 40 px corrispondente all'inizio del testo dell'elenco principale. Stesse parole, orari e numeri.
- report_formatting.underline_findings e graphing._wrap_final: sottolineature delle denominazioni dei reperti e delle stimolazioni quando il nome del parametro non compare nel testo. Stessa enfasi nei blocchi Word. Nessuna modifica a formule, stato, FC o soglie.
- Modulo Word consegnato separatamente come modMortemWord_corretto.txt, derivato dal modMortemWord effettivo del DOCM allegato, più recente del vecchio integrations/word/ModMortem.txt. Importazione di report.detailed_html con elenchi nativi del documento, corsivi, sottolineature e note blu; nessuna introduzione ricostruita né omissione di peso/temperatura iniziale. Conservate le altre procedure del documento. Non sostituire il modulo con la vecchia copia del repository. Verifiche statiche VBA soltanto; compilazione ed esecuzione Word da collaudare dall'utente.
- 38 test Python mirati superati: detailed_inputs_download (3), case_report (4), mixed_cooling_description (3), textgen_henssge_i18n (2), textgen_presentational_i18n (12), i18n_english (12), report_formatting (2). Sintassi/import e diff verificati. Suite completa non rieseguita.
- Aperto su segnalazione dell'utente: summarize_scenarios ripete lo scenario che contribuisce a entrambi gli estremi. Proposta ancora da confermare: range complessivo seguito da ogni scenario una volta con il proprio FC/intervallo. Nessuna modifica a questa funzione in questo intervento.
- Commit corrente: quello contenente questa nota. Ultima conferma manuale dell'app precedente al nuovo intervento, senza SHA identificato. Prossimo passo: prova del download e import Word; conferma della nuova presentazione degli scenari. Nessun errore di regressione accertato; fallimenti iniziali dei test dovuti a dipendenze locali mancanti risolti installandole, e aspettative HTML aggiornate alla modifica autorizzata.
