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

## Motore FC precedente

Il nuovo pannello usa `app/fc_panel_frontend/`. Gli import inutilizzati del vecchio motore sono rimossi dalla pagina sopralluogo. `app/factor_calc.py` resta disponibile per descrizioni e compatibilità; non è stato eliminato né modificato nelle formule durante questa manutenzione.
