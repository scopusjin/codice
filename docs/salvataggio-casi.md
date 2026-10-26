# Salva caso / Apri caso

Nel branch `refactor-tanatology-keys`, il menu **Caso** è disponibile nella pagina completa, nella modalità Sopralluogo e nel pannello FC.

- **Sigla / numero del caso**: testo libero, fino a 80 caratteri; esempi `x26-05`, `IL26-10`, `12345`. La sigla è conservata nel file. Solo nel nome del file i caratteri incompatibili sono sostituiti da `_`.
- **Salva caso** scarica `mortem_<sigla>.json`; senza sigla usa data e ora. Non crea un archivio dei casi sul server né un salvataggio automatico nel browser.
- **Apri caso** legge un file JSON (massimo 1 MB), ne verifica formato e versione, quindi presenta **Sostituisci e apri**. Il caso attuale viene sostituito soltanto dopo questa conferma. File non validi non modificano gli input.
- Il file conserva dati tanatologici, date e orari dei rilievi, temperature, peso, intervalli, arrotondamento, FC applicato e basi per gli adattamenti al peso. Il pannello in corso e i suoi scenari incompleti restano distinti dai valori già applicati.
- La riapertura usa la modalità salvata (Completa o Sopralluogo), mantenendo il layout del dispositivo ricevente. I risultati si ricalcolano premendo **Procedi con la stima**; non vengono ripristinati grafici o risultati memorizzati.
- Metadati: `format=mortem-case`, `schema_version=1`, sigla, data/ora con fuso Europe/Zurich e impronta del codice. Una diversa impronta produce una nota prima dell'apertura; una versione di formato non supportata blocca l'importazione.

Il file è JSON in chiaro. Come gli altri input dell'app, quando viene caricato passa al backend Streamlit per essere elaborato; non è un'applicazione offline.

## Verifiche

`test_case_file.py` verifica esportazione/importazione, sigle, file malformati, metadati esclusi, scenari, basi FC e uguaglianza del calcolo. `case_page_checks.py`, eseguito in isolamento da `test_case_page.py`, verifica il ripristino reale Streamlit fra desktop e mobile, la sostituzione di un caso, i rilievi aggiuntivi e le bozze FC. La suite JavaScript e i test preesistenti restano obbligatori.
