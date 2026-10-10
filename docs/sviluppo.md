# Ambiente di sviluppo Mortem

Usare Python **3.12**, come nella CI e nel devcontainer. L’app si avvia con:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run Stima_epoca_decesso.py
```

`requirements.txt` fissa le dipendenze dirette; `constraints-py312.txt` fissa le dipendenze indirette del runtime Linux/Python 3.12. Le versioni provengono dall’ultima CI riuscita del 18 settembre 2026, con `pytz` dichiarato anche per il fallback del fuso orario. Non copiare l’intero ambiente degli strumenti di sviluppo dentro i requisiti dell’app.

Aggiornare le versioni in una modifica dedicata e controllata. Verificare l’installazione in un ambiente nuovo, eseguire la suite e controllare desktop/mobile prima di integrare. Il devcontainer non reinstalla Streamlit separatamente e mantiene le protezioni CORS/XSRF predefinite. La versione Python del servizio Streamlit Cloud va verificata nelle impostazioni del servizio: il file del devcontainer non la modifica.

## Controlli

```bash
python -m compileall -q app Stima_epoca_decesso.py pages
python -m unittest discover -s tests -v
node tests/test_fc_panel_engine.cjs
node tests/test_fc_panel_ui.cjs
```

## Stato temporaneo dell’interfaccia

I wrapper Streamlit restano installati una sola volta nel processo. I riferimenti a contenitori, il parametro in corso di rendering e la soppressione delle immagini legacy sono invece conservati in `app/render_context.py`, separatamente per ciascun contesto di esecuzione. `install_minimal_mobile_shell()` li azzera all’inizio della pagina, anche nei rerun sullo stesso thread.

Non salvare contenitori Streamlit in variabili globali o in `session_state`: quest’ultimo viene copiato quando si apre il pannello FC. Le funzioni di installazione dei renderer interessati sono serializzate per evitare catene di wrapper duplicate durante primi accessi simultanei.

I test di isolamento esercitano accessi concorrenti al contesto e il suo azzeramento, oltre ai percorsi applicativi desktop/mobile. Non equivalgono a una prova di carico del sito o a una verifica visiva su tutti i browser. La futura sostituzione dei wrapper globali con renderer espliciti resta un intervento separato.

## Motore FC e catalogo esempi

Il motore attivo resta in `app/fc_panel_frontend/index.html`. I dati delle 16 schede documentali (13 casi sperimentali e 4 casi della pratica medico-legale; una scheda comprende due esperimenti) sono definiti una sola volta in `data/fc_examples.json`: `app/fc_catalog.py` li fornisce sia al componente FC, tramite gli argomenti Streamlit, sia alla pagina Tabelle. Il pannello mantiene soltanto i criteri di abbinamento per identificativo. Non occorrono richieste esterne per caricare gli esempi.

Per aggiungere un esempio, aggiornare il JSON e il criterio in `EXAMPLE_MATCHERS`; i test verificano la corrispondenza degli identificativi e il trasferimento al componente. Le schede conservano sempre il peso originale, anche tra 60 e 80 kg e anche con decimali. I valori FC negli esempi restano quelli documentari, senza arrotondamenti o adattamenti aggiuntivi. La casistica inclusa non rappresenta l'intera casistica pubblicata.

Le descrizioni dei risultati sono in `app/fc_description.py`. `app/factor_calc.py` conserva il vecchio motore esclusivamente per compatibilità storica e riesporta la descrizione: nessun modulo applicativo lo importa. Le vecchie formule non sono usate per i suggerimenti attuali. I test storici in `tests/test_wet_naked_surface_ranges.py` riguardano solo quel modulo; le regole attive sono verificate dai test JavaScript.

## Spazi desktop

`app/desktop_layout.css`, letto da `st.html` a ogni esecuzione, gestisce il layout Full desktop attraverso il titolo reale `#mortem-page-title`. Il margine superiore riserva spazio alla barra Streamlit; il contenuto resta largo al massimo 100 rem. La griglia usa la larghezza disponibile del contenitore (anche con sidebar aperta): sotto 70 rem, una colonna; da 70 rem, campi a sinistra e calcolo/risultati a destra. I risultati scorrono normalmente per evitare sovrapposizioni nei notebook con poca altezza. Il CSS mobile resta separato.

Il foglio di stile desktop non viene importato come costante Python: durante un aggiornamento il processo Streamlit può conservare i moduli importati e continuare a usare il CSS precedente. La lettura del file evita questo ritardo.


## Punto di avanzamento — fonti e tabelle FC, 10 ottobre 2026

Ramo: `refactor-tanatology-keys`. Base verificata: `83a393bc710b53987d60dc8db1a577182aa84902`. Intervento autorizzato dall’utente dopo la revisione delle pagine su Drive.

- Corretta la griglia documentale di adattamento al peso: le prime quattro righe erano disallineate; a 70 kg i riferimenti sono 1.4, 1.6, 1.8, 2.0. I valori delle aree accorpate della fonte sono esplicitati per colonna. Formule e matrice interna del pannello restano invariate.
- Rimossa la numerazione dai titoli IT/EN, conservando i numeri originali nelle citazioni. I rinvii bibliografici numerici nella tabella dei criteri non termici sono riferiti esplicitamente all’articolo originale.
- Le schermate consultate corrispondono a Madea, *Estimation of the Time Since Death*, terza edizione, 2016, cap. 6.1. Corrette le attribuzioni alla quarta edizione; completati riferimenti originari e localizzatori, distinguendo le citazioni indirette.
- Distinti esperimenti su cadaveri, prove su simulatore e casi della pratica medico-legale. Il tipo interno `Caso operativo` resta compatibile con il catalogo, ma l’etichetta visibile è più esplicita. Note scientifiche visibili sia nelle tabelle sia nel pannello.
- Caso 33: riportate ipertermia (41.6 °C rettali), mancato utilizzo del metodo e ipotesi sulla temperatura alla morte; non è una normale conferma sperimentale del FC. Caso 6: riportata l’assenza di verifica investigativa dei tempi della coppia 6/7.
- Individuata la fonte Knörle 1991 (riferimento 90) per i simulatori sui piani di appoggio. Confermato visivamente il coefficiente -3.24596 nell’equazione 6.10. Per le foglie precisati simulatore, spessori e variabilità, senza cambiare il riferimento 2.70 scelto nell’app.

Il primo blocco non aggiunge casi né modifica `RULES`, `EXAMPLE_MATCHERS`, soglie, adattamento, arrotondamento, scenari o salvataggio. Il controllo numerico della tabella e la conservazione di pesi/note sono coperti da regressioni dedicate; restano previsti i test Python/JavaScript del progetto.

Verifica locale del blocco: 241 test Python superati; test JavaScript del motore e dell’interfaccia superati (3385 controlli, 33600 combinazioni, nessun caso pendente). AppTest ha eseguito la pagina Tabelle in italiano e inglese, le due tabelle delle schede (12 righe sperimentali, 4 della pratica) e la bibliografia senza eccezioni. Verificata nel pannello la visibilità di peso, ipertermia, limite del metodo e fonte del caso 33. Questo controllo non attesta il commit effettivamente distribuito sul servizio Streamlit Cloud.

Recupero successivo: nelle tabelle originali 6.17 e 6.21 sono stati identificati 30 casi della pratica medico-legale, di cui 4 già presenti. Restano da trascrivere e verificare i 26 aggiuntivi e le ulteriori serie sperimentali. Per ricostruire la copertura della serie di 72 casi occorre il testo integrale di Henssge et al. 2000, parte I, DOI 10.1007/s004149900089. Non assumere che il libro o l’articolo contengano tutti i dati individuali. Non deduplicare per solo numero del caso: usare studio, serie e identificativo originale.
