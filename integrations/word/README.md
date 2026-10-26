# Ripresa completa di un caso Mortem da Word

Il modulo `ModMortem.txt` sostituisce il contenuto del modulo Mortem esistente.
Mantiene `frmMortemAttesa`, i moduli JSON e `ThisDocument`.
Richiede anche le modifiche `app/word_resume.py`, `app/word_resume_frontend/index.html`
e `app/word_launch.py` presenti nello stesso branch: non installare il modulo prima
dell'aggiornamento dell'app.

All'apertura controlla i file stimaX*.json nella cartella del documento. Riutilizza
il caso piu' recente con lo stesso numero X, senza finestre di scelta. Il ripristino include tutti i campi serializzati nel JSON,
segni tanatologici, scelta FC, bozza e scenari. I risultati vengono ricalcolati con
il comando della stima; il riepilogo salvato non viene presentato come ricalcolato.

Il browser apre una pagina HTML temporanea locale che contiene il JSON e mostra
l'app in un iframe. Un messaggio con token casuale trasferisce i dati al componente
dell'app. Nessun JSON viene incluso nell'URL e nessun file originale viene modificato.
Non ci sono timer o polling. Il file HTML resta nella cartella temporanea del computer.
Se il browser impedisce il trasferimento, l'app offre la selezione manuale del JSON.
L'app valida il file completo e il numero X prima di sostituire lo stato corrente.

Se manca il segnalibro Mortem: cursore in un paragrafo vuoto, poi Alt+F8 >
Mortem_InstallaPulsante. Il comando ha sfondo azzurro, testo blu e bordo applicati ai soli caratteri, non al paragrafo; mantiene
l'attributo testo nascosto. Per aggiornare un comando gia' presente eseguire la stessa macro.

Controlli automatici: test ripristino, isolamento caso/token, attesa senza cancellare
lo stato, integrazione con l'importazione Streamlit e test JavaScript della consegna.
Il JSON fornito dall'utente e' stato verificato separatamente senza includerlo nel repository.
Compilazione/esecuzione VBA e passaggio reale Word/browser ancora da collaudare.
L'errore di importazione Word precedentemente segnalato resta da localizzare tramite
la diagnostica di fase mantenuta nel modulo.

L'apertura ordinaria non istanzia il componente Word. Nessun accesso del sito alla cartella locale: la pagina locale contiene soltanto il file scelto da Word e ne trasmette il contenuto all'app, come un caricamento del file.

## Download unico e importazione

Usare il normale pulsante Scarica caso nel menu Caso. Non viene aggiunto un secondo
pulsante per Word. Le descrizioni appena calcolate vengono acquisite prima di
preparare il download normale.

Fatto cerca automaticamente nella cartella del documento la stima piu recente che
contenga report.word_blocks validi e corrisponda al numero X. Usa saved_at, con data
di modifica come spareggio; nei file senza data interpretabile usa la modifica.
Il lettore JSON privato Mortem elimina la dipendenza dal codec dei moduli anagrafici.

Sono stati controllati separatamente i JSON allegati: il file stimaX26.84(2).json
contiene effettivamente report e word_blocks. Nessun dato dei casi e incluso nel repository.
