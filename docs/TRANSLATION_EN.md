# Traduzione inglese — attivazione nell’app

Base dell’integrazione: `4c862d08d359542006f9059ce9ed38fc7aa613e9`, branch
`refactor-tanatology-keys`, repository `scopusjin/codice`.

## Stato

Attivazione del 22.10.2026 nel branch `refactor-tanatology-keys`.
Il selettore unico **Italiano / English** mantiene la preferenza nella sessione
su Full, Sopralluogo, pannello FC, impostazioni, tabelle e riferimenti.
Sono tradotti anche gli aiuti, i componenti mobili, gli esempi FC e i blocchi
per Word. Il cambio lingua rigenera i report a partire dagli stessi input.

Rimossa dal catalogo la voce obsoleta **Condizioni variabili**. Restano
l’inserimento di range e la gestione di più scenari. I nomi tecnici storici
come `stima_cautelativa_beta` non vengono rinominati: appartengono allo stato
e ai casi salvati, non alle etichette visibili.

Le formule scientifiche, i limiti temporali, le regole FC, i dati dei 152
esempi e i valori memorizzati delle opzioni restano quelli della versione di
partenza. Non viene eseguita una migrazione dei casi.

## Terminologia

| Italiano | Inglese adottato | Criterio |
|---|---|---|
| Raffreddamento cadaverico | Postmortem body cooling | Denominazione del capitolo di riferimento |
| Tempo trascorso dal decesso | Time since death | Durata, distinta dalla data/ora del decesso |
| Stima del tempo trascorso dal decesso | Time since death estimation | Titolo compatto richiesto il 23.10.2026; il pulsante usa il verbo “Estimate time since death” |
| Tempo trascorso dal decesso stimato | Estimated time since death | Riepilogo espresso soltanto come durata |
| Epoca del decesso stimata | Estimated time of death | Momento o finestra temporale del decesso |
| Fattore di correzione | Corrective factor (CF) | Terminologia della tabella 6.18; “correction factor” compare anche nella fonte |
| Temperatura ambientale media | Mean ambient temperature | “Mean amb. T.” nei campi compatti; non coincide necessariamente con il rilievo puntuale |
| Aria ferma / correnti d'aria | Still air / moving air | Categoria termica, senza soglie di velocità aggiunte |
| Acqua stagnante / corrente | Still water / flowing water | “Stagnante” qui indica assenza di flusso |
| Tessuti fradici | Wet-through clothing and coverings | Terminologia del pannello FC |
| Tessuti parzialmente bagnati | Partially wet clothing and coverings | Distinti dai tessuti completamente impregnati |
| Piano termicamente indifferente | Thermally indifferent base | Terminologia del capitolo; nessuna nuova classificazione |
| Ipostasi | Postmortem lividity | “Lividity” nelle etichette brevi |
| Migrabilità | Shifting | Variazione dopo riposizionamento del corpo |
| Ipostasi completamente migrabili | Complete shifting (of livores) | Termine della figura 6.33; conservare separata l'informazione sulla confluenza |
| Ipostasi parzialmente migrabili | Incomplete shifting (of livores) | Termine della figura 6.33 |
| Ipostasi migrabili perlomeno parzialmente | Shifting present (extent unspecified) | Voce dell'app: migrazione presente, estensione non determinabile; non equivale a migrazione incompleta |
| Scomparsa alla digitopressione | Blanching under finger pressure | Reperto distinto dalla migrabilità |
| Rigidità cadaverica | Rigor mortis | Termine scientifico corrente |
| Metodo integrato | Compound method | Testi relativi all'integrazione dei reperti secondo Henssge |
| Ispezione legale | Medico-legal examination | Evita “legal inspection” |

Inglese britannico coerente (`generalised`, `dilatation`). Punto decimale,
unità, date numeriche e formato 24 ore conservati. I nomi delle chiavi restano
italiani o inglesi come nel codice di partenza; CF è soltanto una sigla visibile.

Revisione terminologica approvata il 22.10.2026: adottati `complete shifting`
e `incomplete shifting` nelle etichette e nelle descrizioni. `Estimation` indica
il procedimento, `estimate` resta corretto come verbo o per il risultato della
stima. I riepiloghi brevi senza data usano `Estimated time since death`; quelli
con data/ora mantengono `Estimated time of death`. Limiti temporali e ID invariati.

## Fonti e limiti della revisione

- Henssge, capitolo 6.1 in B. Madea (ed.), *Estimation of the Time Since Death*,
  3rd edition (2016), pp. 63–113. Consultate le immagini nel Drive
  [Capitolo raffreddamento](https://drive.google.com/drive/folders/149ynmZeFt9GlxvafByBJ4jjQ--ZhzgnN),
  compresa la tabella 6.18 (file `187TYLditJonh7fyWVhUyeFLzX4-2FDNW`) e i passaggi
  sulle condizioni standard, sul peso e sulla temperatura ambientale media.
  Per la revisione terminologica, consultate anche le figure 6.32 e 6.33
  ([pagina sul Drive](https://drive.google.com/file/d/1k8uFSBZNmy9Xa3kM5_aYadfRmFJSQz0w/view)):
  `Estimated time of death`, `complete shifting of livores` e
  `incomplete shifting of livores`. Nel capitolo introduttivo, sezione 1.1,
  `Estimation of the time since death`; a p. 2 compare anche il sostantivo
  `estimate` per il risultato della valutazione
  ([anteprima dell'editore](https://api.pageplace.de/preview/DT0400.9781444181777_A36323142/preview-9781444181777_A36323142.pdf)).
- Potente et al. (2017), DOI `10.1016/j.forsciint.2017.09.012`,
  [PubMed](https://pubmed.ncbi.nlm.nih.gov/29102846/): terminologia relativa al
  **minimum time since death**, con cautela per temperature ambientali >23 °C.
- Per gli altri reperti: traduzione delle descrizioni e degli intervalli
  effettivamente presenti in `app/locales/it.py` e `app/parameters.py`, con
  confronto delle etichette inglesi già presenti nelle tabelle dell'app.
  Non è stata eseguita una nuova validazione scientifica indipendente di ogni
  limite temporale. Le risorse traducono il comportamento autorizzato esistente.

Non attribuire validazione statistica ai range proposti dall'app. Mantenere
distinti limiti osservati, limiti di confidenza al 95% e range adattabili scelti
dall'operatore. Potente fornisce un minimo, non un intervallo con massimo chiuso.
I titoli originali delle pubblicazioni restano nella lingua di pubblicazione.

Le opzioni pupillari storiche `positive`/`negative` contengono ancora le frasi
legacy su atropina e limiti 30/5 ore; non sono nel menu corrente. Non riutilizzarle
al posto degli esiti specifici `atropine_*`, `tropicamide_*`, `acetylcholine_*`.
La distinzione è preesistente e non viene corretta implicitamente traducendo.

## Integrazione e verifiche

- `app/language.py`: preferenza per sessione e proxy linguistico per i renderer
  scientifici. Nessuna lingua globale condivisa fra gli utenti.
- `app/presentation_translation.py`: testo di presentazione localizzato dopo
  il calcolo dell’identità dei widget. Streamlit 1.64 trasmette le selezioni
  come stringhe formattate: il ponte di serializzazione converte le etichette
  inglesi nei valori originali prima di callback e calcoli. I valori dei campi
  di testo, gli URL e gli identificatori non vengono tradotti.
- Pannello FC: traduzione reversibile dei nodi di testo e delle etichette
  accessibili; valori delle opzioni, condizioni, regole e bozze invariati.
  I cataloghi distinguono dati sperimentali, scelte nei casi pubblicati e
  ragionamenti per analogia dell’app.
- I report sono associati anche alla lingua. Al cambio lingua vengono
  rigenerati e Word riceve soltanto i blocchi nella lingua corrente.

Test mirati: 32 test superati nel gruppo composto da
`test_language_presentation`, `test_language_page`, `test_i18n_english`,
`test_case_report` e `test_case_file`; il controllo di pagina esegue a sua
volta tre prove integrate. Ulteriori sette prove di importazione/esportazione
casi (`case_page_checks.py`) superate.

Verificati Full desktop/mobile e Sopralluogo: IT → EN → IT, mantenimento di
input e scelte FC, ripristino dello stesso report italiano, importazione dei
vecchi casi, selezioni native inglesi, blocchi Word, digitopressione,
ricomparsa del rigor e reperti rilevati in orari diversi. Il test JavaScript
confronta decisioni numeriche e bozze FC prima e dopo il cambio lingua.

La suite generale contiene già errori e aspettative non aggiornate nella
base di partenza; non viene dichiarata interamente verde. Il controllo dei
componenti è automatico (AppTest e ambiente DOM simulato): in questa sessione
non è stato possibile installare Chromium per una verifica visiva completa.
La compatibilità del ponte dei widget è legata alla versione Streamlit
vincolata dal repository; va ricontrollata se tale dipendenza cambia.

Il confronto bilingue è rigenerabile con `scripts/preview_translation_en.py`.
