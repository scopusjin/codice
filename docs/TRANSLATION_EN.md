# Traduzione inglese — blocco 1: risorse linguistiche

Base verificata: `b15a18b17aa77f688393e96617fac7c2a4487efe`, branch
`refactor-tanatology-keys`, repository `scopusjin/codice`.

## Stato

Disponibili tramite chiamate esplicite `language="en"`: etichette per ID,
descrizioni tanatologiche, conclusioni con/senza data, testi Henssge/Qd e
Potente, descrizioni FC legacy e tutte le chiavi del catalogo `it_ui`.
Le griglie sopraciliare/peribuccale e le etichette MSIL hanno risorse inglesi.
Il menu pupillare inglese include i sei esiti specifici per farmaco presenti
in `app/parameters.py`, oltre alle opzioni storiche conservate per compatibilità.

L'app continua a usare l'italiano. Questo blocco **non attiva il selettore**
e non costituisce una versione interamente tradotta dell'app. Nessuna chiave
di sessione, opzione memorizzata, formula o regola FC viene modificata.

## Terminologia

| Italiano | Inglese adottato | Criterio |
|---|---|---|
| Raffreddamento cadaverico | Postmortem body cooling | Denominazione del capitolo di riferimento |
| Tempo trascorso dal decesso | Time since death | Durata, distinta dalla data/ora del decesso |
| Stima del tempo trascorso dal decesso | Estimation of the time since death | Titolo; il pulsante usa il verbo “Estimate time since death” |
| Tempo trascorso dal decesso stimato | Estimated time since death | Riepilogo espresso soltanto come durata |
| Epoca del decesso stimata | Estimated time of death | Momento o finestra temporale del decesso |
| Fattore di correzione | Corrective factor (CF) | Terminologia della tabella 6.18; “correction factor” compare anche nella fonte |
| Temperatura ambientale media | Mean ambient temperature | Non coincide necessariamente con il rilievo puntuale |
| Aria ferma / correnti d'aria | Still air / moving air | Categoria termica, senza soglie di velocità aggiunte |
| Acqua stagnante / corrente | Still water / flowing water | “Stagnante” qui indica assenza di flusso |
| Tessuti fradici | Wet-through clothing and coverings | Da usare nel pannello FC nel blocco successivo |
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

## Integrazione ancora da eseguire dopo verifica del blocco

1. Selettore unico Italiano / English con preferenza per sessione; mantenimento
   di tutti i dati e delle selezioni attraverso i valori stabili, senza migrare
   o duplicare le chiavi di sessione. Non impostare una lingua globale di processo.
2. Testi ancora incorporati nelle pagine, intestazioni mobile, impostazioni,
   dialoghi Caso/Word, dettagli con orari diversi e paragrafi misti Henssge/Potente.
3. Pannello FC JavaScript: etichette, spiegazioni, condizioni grammaticalmente
   corrette, scenari e 152 schede di esempio. Conservare i valori interni italiani.
4. Tabelle/riferimenti: collegare il selettore esistente a quello unico,
   uniformare la sigla CF; mantenere i titoli bibliografici originali.
5. Ricalcolo dei testi al cambio lingua e invalidazione dei report obsoleti.
   `build_word_blocks` riconosce ancora prefissi italiani: aggiornarlo prima di
   esporre l'esportazione inglese. Un testo libero passato come fallback deve
   già essere nella lingua richiesta: il renderer non lo traduce automaticamente.
6. Prove integrate desktop/mobile, cambio lingua IT→EN→IT con dati e risultati
   invariati, importazione dei vecchi casi e download Word nella lingua corrente.

La verifica del presente blocco avviene sul confronto bilingue generato da
`scripts/preview_translation_en.py` e con un controllo di regressione dell'app
italiana. La revisione manuale precede il blocco di integrazione, secondo il
metodo di lavoro richiesto dall'utente.
