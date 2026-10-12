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

Il motore attivo resta in `app/fc_panel_frontend/index.html`. `data/fc_examples.json` contiene soltanto le 34 schede selezionate per le spiegazioni contestuali (20 osservazioni sperimentali su cadaveri, 9 prove su simulatori e 6 casi della pratica medico-legale; una scheda comprende due esperimenti). `app/fc_catalog.py` le fornisce al componente FC tramite gli argomenti Streamlit. Il pannello mantiene i criteri di abbinamento per identificativo; non occorrono richieste esterne per caricare gli esempi. La pagina Tabelle presenta la sintesi del metodo combinato e i riferimenti FC, senza tabelle separate di ipostasi, rigidità o casistica.

L’archivio completo di manutenzione è conservato privatamente su Drive, fuori dal repository e dai dati trasmessi al browser. Contiene anche le ulteriori serie del capitolo su acqua, aria, indumenti, coperture, superfici e foglie, con fonti, limiti e indice delle tabelle. Non integrare l’archivio completo nel JSON pubblico né aggiungere percorsi o credenziali di accesso. La rimozione dal ramo corrente non elimina le versioni già presenti nello storico Git.

Per aggiungere un esempio, aggiornare il JSON e il criterio in `EXAMPLE_MATCHERS`; i test verificano la corrispondenza degli identificativi e il trasferimento al componente. Le schede conservano sempre il peso originale, anche tra 60 e 80 kg e anche con decimali. I valori FC negli esempi restano quelli documentari, senza arrotondamenti o adattamenti aggiuntivi. La casistica inclusa non rappresenta l'intera casistica pubblicata.

Ogni modifica parte dalla verifica della fonte nell’archivio di manutenzione. Pubblicare solo la sintesi necessaria alla spiegazione pertinente, con riferimento bibliografico e condizioni essenziali. Il foglio privato non aggiorna automaticamente il codice o i calcoli. I casi 22 (bagnato, pioggia e correnti continue) e 62 (nudo sul letto) sono ora richiamati nelle condizioni corrispondenti, senza modificare le regole numeriche. Ulteriori esempi selezionati documentano immersione, correnti continue, indumenti bagnati, appoggi e foglie. Le schede distinguono peso corporeo e peso virtuale del simulatore; ogni richiamo include la fonte e i limiti del confronto. Gli esempi in acqua quasi ferma non compaiono per l’acqua corrente, che ha un richiamo bibliografico dedicato.

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


## Integrazioni — tabelle e casistica, 11 ottobre 2026

- Completati i sei riferimenti numerici della tabella del metodo combinato ([4], [7]–[11]), mantenendo la numerazione di Henssge et al. 2000, parte II. Le citazioni sono recuperate dalla bibliografia dell’articolo; non si dichiara la lettura diretta di ogni lavoro storico.
- Aggiunto l’asterisco alle 11 ore per la risposta peribuccale positiva, con nota breve sull’uso binario della risposta. Il valore 11 è già nella tabella originale del 2000: non è documentata qui una modifica storica da 13 a 11.
- Aggiunti asterischi a 1.3, 1.1–1.2 e 0.75 per il corpo nudo. La nota distingue i FC complessivi dagli incrementi/decrementi per il corpo vestito, in accordo con il testo e gli esempi del cap. 6.1 di Madea 2016. Spiegazione allineata nel pannello FC.
- Rimossa la parola appartamento dalla categoria del pavimento domestico. Etichette IT/EN della tabella del peso allineate alle categorie dell’app: vestiti/teli, coperte spesse, vestiti/teli + coperte spesse, coperte molto pesanti/piumone. I valori numerici non cambiano.
- Aggiunte 26 schede della pratica medico-legale, portando a 30 i casi delle tabelle 6.17 e 6.21: immagini 002–007 e 115–117 caricate dall’utente su Drive, controllate visivamente. Le schede conservano peso, range, fonte e limiti; sono sintesi documentali, non la trascrizione integrale delle tabelle.
- Le nuove schede hanno `referenceOnly: true`: sono consultabili nella pagina Tabelle e non introducono abbinamenti automatici o regole di calcolo. I 16 abbinamenti preesistenti restano invariati.
- Caso 31: misure ripetute dopo incendio/spegnimento e mancato uso del metodo termico. Caso 45: FC ipotetico con punto interrogativo, cambiamento di condizioni e mancato uso del metodo. Caso 37: pannolino senza validazione sperimentale, adattamento documentato del solo limite superiore a 2.2. Caso 66: adattamento 1.6–2.0 → 1.4–1.7 e piumino rimosso prima dell’esame. La dicitura «metal road» del caso 27 non è equiparata a una lastra metallica.

Copertura: completata la selezione di 30 casi pratici nelle due tabelle del libro, non l’intera serie di 72. La pagina editoriale della parte I (https://doi.org/10.1007/s004149900089) richiede accesso al testo integrale. Restano da acquisire quel testo e da riconciliare le ulteriori serie sperimentali indicate nel controllo del 10 ottobre. Non è dimostrato che tutti i dati individuali dei 72 casi siano pubblicati integralmente.

Revisione del riuso: la pagina Tabelle è generata in HTML e le schede sono sintesi riscritte; questo intervento non pubblica le fotografie del libro. Le tabelle restano derivate dalle fonti dichiarate. L’attribuzione e la riformulazione non equivalgono a un’autorizzazione e non consentono di dichiarare chiusa la verifica dei diritti sulla selezione/disposizione originale. La guida dell’editore distingue i dati dalla loro presentazione creativa e richiede attenzione anche alle traduzioni. Prima di una riproduzione integrale occorre verificare la licenza o i permessi applicabili. Nessuna richiesta di autorizzazione è stata inviata.
Fonte editoriale consultata: https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/using-third-party-material/

Verifiche di questo blocco: 18 test Python mirati superati; motore FC (3385 controlli, 33600 combinazioni) e interfaccia JavaScript superati. AppTest: pagina Tabelle senza eccezioni in IT/EN, sei riferimenti bibliografici visibili, quattro asterischi corretti, nuove etichette e 30 schede pratiche ordinate per numero. Verificati l’adattamento del caso 66 e il solo limite superiore del caso 37. Questi controlli non certificano quale commit sia già distribuito da Streamlit Cloud.

## Tabella del metodo combinato — versione approvata, 11 ottobre 2026

- Sostituita la griglia derivata dall'articolo originale con la sintesi approvata: 15 righe, colonne Parametro/Criterio/Presente/Assente, gruppi con celle unite e richiami bibliografici. La pagina presenta la base scientifica del metodo combinato di Henssge, senza descrivere il funzionamento del software.
- Separati i sei gradi sopraciliari in tre righe con due coppie Grado/Intervallo. Gli intervalli sono quelli della figura 4 di Henssge e Madea (2004), controllata visivamente: VI ≤6; V 1–7; IV 2–8; III 3–13; II 3.5–16; I 5–22 ore. Nessuna reazione: ≥5 ore, da Henssge et al. (2000).
- Il precedente 26 della riga II proveniva dalla trascrizione testuale della tabella del 2000. Non è stato assunto come prova di un errore nei calcoli: la figura del 2004 e i casi 24, 28 e 67 dell'articolo del 2000 sostengono il limite 16. La nuova tabella cita esplicitamente il 2004 per i gradi osservati; non confonde il limite inferiore di un grado con l'assenza di quello stesso grado.
- Usata una numerazione bibliografica locale: [1] Henssge et al. 2000, parte II, DOI 10.1007/s004149900090; [2] Henssge e Madea 2004, DOI 10.1016/j.forsciint.2004.04.051, figura 4 e tabelle 1–2. Sostituiti i precedenti numeri ereditati dalla bibliografia dell'articolo. Non si rivendica la consultazione diretta dei lavori storici citati al suo interno.
- Note brevi su significato dei limiti di variazione, distinzione dai limiti di confidenza al 95%, assenza di un limite utile (trattino), interpretazione di presente/assente e 11 ore per qualsiasi risposta peribuccale positiva. Testi e separatori decimali localizzati in italiano e inglese.
- Il CSS a quattro colonne si adatta alla larghezza disponibile. Il refactor riguarda soltanto il contenuto documentale e la sua presentazione; non modifica parametri, algoritmi o risultati di calcolo. La riorganizzazione non costituisce una certificazione di assenza di vincoli di copyright.

Verifica locale: compilazione Python e controllo diff superati; test preesistente della matrice FC al peso superato; AppTest della pagina Tabelle eseguito in IT/EN senza eccezioni, con controllo di tutte le 30 celle temporali, dei sei intervalli sopraciliari, delle note e dei due riferimenti. Questa verifica non attesta la versione distribuita su Streamlit Cloud.

### Integrazione delle fasi tardive della rigidità

Su richiesta dell'utente, aggiunte direttamente alla tabella combinata le righe Persistenza (24–96 ore) e Risoluzione (24–192 ore), tratte dalla tabella 1 di Henssge e Madea (2004), riferimento [2]. I due intervalli descrivono il decorso: sono mostrati in celle unite, esplicitamente etichettati come limiti di variazione, senza ricavare soglie distinte per presenza o assenza. L'introduzione identifica queste righe come integrazioni del 2004. Le altre tabelle non sono state rimosse e non sono cambiati i parametri di calcolo.

AppTest IT/EN superato: 17 righe, gruppo rigidità esteso a 5 righe, entrambi i nuovi intervalli associati a [2], conservazione delle 30 celle temporali precedenti e dei sei intervalli sopraciliari. Controllo diff superato.

## Punto di avanzamento — descrizioni per Word, 12 ottobre 2026

Repository: `scopusjin/codice`. Branch: `refactor-tanatology-keys`, collegato a `https://mortem-test.streamlit.app/` secondo la conferma dell'utente già acquisita. Commit di partenza verificato su GitHub: `e84af2d63b691b2b4b0fa149ea8c5ac8d3674c7e`. Il commit di questo intervento è identificabile con `git log -1 --format=%H --grep='Stabilizza interlinea e punti elenco delle descrizioni per Word'`. Il commit effettivamente distribuito da Streamlit non è attestato dalle sole informazioni del repository.

- Modifica autorizzata: in `app/graphing.py`, `_wrap_final`, applicata direttamente a ogni paragrafo e voce di elenco la coppia `line-height:14pt` / `mso-line-height-rule:at-least`. Impostato il pallino tondo standard (`disc`) mantenendo elenchi HTML reali e i livelli di annidamento.
- Conservati testi, enfasi, colori, dimensioni dei caratteri e rientri esistenti. Le note blu mantengono la propria dimensione. Nessuna modifica a logica FC, equazioni, risultati, chiavi di stato o dati scientifici; `main` non coinvolto.
- Precedente da non riproporre come soluzione sufficiente: commit `4ff1614a`, con l'interlinea soltanto sul contenitore esterno. Il 12 ottobre l'utente ha segnalato che Word perde talvolta la modalità Minima 14 pt. La nuova modifica ripete l'indicazione sui blocchi copiati; la compatibilità effettiva dipende ancora dal percorso browser/Word.
- Verifiche locali: compilazione e import del modulo riusciti; 29 test testuali e 8 regressioni Streamlit delle pagine superati, inclusi desktop/mobile e sopralluogo. Controllo mirato su elenchi annidati e note blu: testo e struttura conservati, indicazioni di interlinea presenti su ogni paragrafo/voce. Diff controllato. Runtime di verifica Python 3.12 / Streamlit 1.64.0; le altre librerie locali non replicano integralmente il lock di produzione.
- Ultimo commit con conferma di test utente recuperata dal precedente punto di ripresa: `9577c619`; non equivale alla validazione dei commit successivi. Questo intervento resta da provare in Word.

Prossimo passo concordato: dopo l'aggiornamento dell'app, copiare descrizioni con voci annidate e note blu, incollare con Mantieni formattazione originale e verificare in Word Interlinea = Minima, valore = 14 pt e punti elenco modificabili. Non considerare il controllo HTML una prova del comportamento di Word. Nessun ulteriore intervento funzionale concordato prima di questo riscontro.


## Punto di avanzamento — menu Caso e helper scenari, 12 ottobre 2026

- Repository: `scopusjin/codice`; branch: `refactor-tanatology-keys`, collegato all’app di test secondo la conferma dell’utente già acquisita. Base verificata su GitHub: `9ad4e88591a13165e726e4b8a10a6f2f32e04ce1`. Il commit di questo intervento è identificabile con `git log -1 --format=%H --grep='Compatta menu Caso e helper Più scenari'`. `main` non coinvolto.
- Richiesta autorizzata: menu Caso in fondo a destra, nella colonna della stima sul desktop; helper accanto a Più scenari; spiegazione senza riferimenti alle durate, basata sulle condizioni effettive o ragionevolmente possibili e sull’intervallo che comprende gli estremi.
- `Stima_epoca_decesso.py`: rimosso lo spazio riservato al menu sopra gli input; menu finale e contenitore dei risultati conservato prima di esso anche in presenza dell’avviso di dati mancanti. Conservato il marcatore di layout esistente. Il pulsante scenari e il suo helper sono mostrati insieme quando Henssge è applicabile.
- `app/desktop_layout.css`: il menu finale occupa la seconda colonna della griglia desktop esistente, dopo i risultati. La disposizione verticale sugli schermi stretti conserva il menu in fondo. Nessun posizionamento fisso o nuova correzione CSS sovrapposta.
- `app/fc_page.py`, `render_scenarios_button()`: pulsante e helper nella stessa riga nativa Streamlit. `render_fc_route_if_requested()` e `pages/App_MSIL.py`: menu Caso dopo il contenuto.
- `app/fc_panel_frontend/index.html`: anche la nota sugli scenari nel pannello usa il nuovo testo; eliminato il riferimento a 30–60 minuti. L’identificativo DOM esistente è conservato per evitare modifiche alla logica JavaScript.
- Invariati calcoli, accoppiamenti temperatura/FC, adattamento al peso, risultati, formattazione Word, salvataggio/ripristino e chiavi di sessione.
- Ultimo commit con test utente documentato: `9577c619`; le modifiche successive non sono automaticamente validate da quel riscontro. Questa disposizione richiede il test visivo dell’utente su desktop e telefono.
- Tentativi falliti pertinenti: nessuna nuova disposizione scartata; il browser di controllo remoto non raggiunge il server locale (connessione rifiutata). La versione online precedente è stata osservata.
- Verifiche: compilazione e controllo diff; integrazione del salvataggio casi su desktop/mobile/sopralluogo; 14 test scenari; suite JavaScript del pannello. Nel test preesistente della nota blu è stata accettata la proprietà aggiuntiva dell’interlinea introdotta dal commit `9ad4e885`, conservando il controllo su colore, dimensione e testo.
- Prossimo passo: verificare nella versione di test Caso in basso a destra, helper vicino a Più scenari e apertura corretta dei due comandi. Restano aperti il riscontro in Word sulle descrizioni e gli altri punti scientifici/documentali già annotati.


### Pulsante Più scenari discreto — 12 ottobre 2026

Base verificata su GitHub: `a63c347ed3f382f373e24023a184c90e85a298b4`, branch `refactor-tanatology-keys`, repository `scopusjin/codice`. Commit di questo intervento identificabile con `git log -1 --format=%H --grep='Rende discreto il pulsante Più scenari'`.

L’utente ha respinto la resa del pulsante dopo il precedente spostamento: troppo simile al comando principale della stima. Non riproporre bordo blu e padding dei pulsanti principali per Più scenari. In `app/fc_page.py`, `render_scenarios_button()`, impostato lo stile nativo `tertiary`, senza bordo/sfondo e con larghezza limitata al contenuto. In `Stima_epoca_decesso.py` e `app/theme.py`, esclusa soltanto la chiave `btn_fc_scenarios` dalle regole grafiche generali che lo rendevano evidente; nessuna nuova toppa CSS. Il comando della stima, il menu Caso, l’helper, i testi, le chiavi di sessione e i calcoli restano invariati.

Verifiche: compilazione Python, import tramite AppTest, diff controllato e test preesistente di apertura/applicazione scenari nelle viste desktop/mobile/sopralluogo. La precedente modifica `a63c347e` ha superato anche GitHub Actions; menu Caso e helper sono stati verificati online. Ultimo commit con test utente documentato resta `9577c619`; la nuova resa grafica è da confermare con l’utente. Prossimo passo: verificare che Più scenari sia un comando discreto vicino al punto interrogativo e apra correttamente il pannello.


### Menu Caso sticky sul desktop — 12 ottobre 2026

Richiesta esplicita successiva dell’utente: mantenere il comando e la sigla Caso visibili in basso nella colonna destra durante lo scorrimento. Base GitHub verificata: `0b3e4b898e968633d7429f8a87cf8766ef5b2070`, stesso repository e branch di test. Commit identificabile con `git log -1 --format=%H --grep='Mantiene Caso sticky in basso a destra sul desktop'`.

In `app/desktop_layout.css` la regola esistente del contenitore `full_case_footer` usa `position: sticky`, margine inferiore 0.75rem e allineamento inferiore, limitatamente al layout desktop a due colonne. La posizione resta vincolata alla colonna; su schermi stretti il menu conserva il flusso normale. Nessuna variazione ai calcoli, ai dati, al salvataggio, ai testi o ai controlli. Diff controllato; verifica visiva con scorrimento e riscontro dell’utente come prossimo passo.


## Punto di avanzamento — origine del FC nel pannello, 12 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata su GitHub `fed69df605ce87134ad54ba5a05c1bbae4978d38`. Commit identificabile con `git log -1 --format=%H --grep='Distingue FC preimpostato e scelte manuali nel pannello'`. Ultimo commit con test utente documentato: `9577c619`; non attesta le modifiche successive.

- Richiesta: non classificare come manuale il FC iniziale mai modificato; distinguere le modifiche manuali comprese nell’intervallo suggerito da quelle che lo superano.
- Causa: `_current_fc_draft()` in `app/fc_page.py` assegnava `manual=True` anche senza una scelta precedente. Ora riconosce il valore preimpostato solo in assenza di una scelta esplicita; conserva il range già usato da Sopralluogo senza alterarlo. Una scelta manuale già registrata mantiene sempre tale origine, anche se pari a 1.00. Non è possibile ricostruire retroattivamente se un vecchio file etichettato manuale fosse in realtà ancora preimpostato.
- `app/fc_panel_frontend/index.html`: introdotta l’informazione `preset` nella bozza del pannello, senza rinominare o duplicare le chiavi `st.session_state`. Apertura, semplice uscita dal campo, cambio peso e ripristino della bozza non costituiscono una compilazione manuale. Digitazione e pulsanti +/- del FC la registrano anche se il valore finale coincide col suggerimento. Modificare le condizioni o ripristinare il suggerimento mantiene il comportamento automatico esistente.
- La nota confronta entrambi gli estremi scelti con il suggerimento corrente, già adattato al peso. Distingue: coincidenza con un valore singolo; valore diverso da un suggerimento singolo; intervallo interamente compreso (estremi inclusi), parzialmente esterno o interamente esterno; assenza di suggerimento automatico. Il confronto è soltanto descrittivo e non limita le scelte né cambia gli estremi.
- Testi: «FC preimpostato, non ancora modificato»; «FC compilato manualmente, entro l’intervallo suggerito dall’app (…)»; «… in parte al di fuori …»; «… al di fuori …». Il riferimento è al suggerimento dell’app, perché non tutti i range sono direttamente tabulati nella letteratura.
- `app/case_file.py`: consentito il nuovo dato opzionale `preset` nelle bozze, incluse quelle dei singoli scenari. I file precedenti restano leggibili; la distinzione si conserva nell’esportazione e nella riapertura. I veri FC manuali mantengono le note nei risultati; il valore preimpostato non genera più una falsa attribuzione manuale.
- Equazioni, regole FC, adattamento al peso, temperatura, arrotondamenti e intervalli di calcolo non modificati. Testi dei risultati e loro formattazione invariati; cambia soltanto la corretta provenienza della scelta.
- Verifiche mirate: nuovi test sulla distinzione fra valore iniziale e FC 1 inserito volontariamente, ripristino/esportazione/cambio peso e casi storici manuali; prove frontend di confini inclusi, intervalli parzialmente/totalmente esterni e suggerimento assente. Suite FC del frontend e integrazione Streamlit, regressioni degli scenari e dei file caso; diff e sintassi controllati.
- Prossimo passo: test dell’utente con un caso nuovo, FC iniziale 1.00, successiva scelta delle condizioni e modifica manuale dentro/fuori i limiti. Vecchi casi già manuali non riclassificati automaticamente. Nessun altro intervento concordato.


## Punto di avanzamento — casi nel browser, 12 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base GitHub verificata `4b57a0f6c06c6e88ae414bc0287c58fa35e8c762`. Commit identificabile con `git log -1 --format=%H --grep='Salva e riapre i casi nel browser'`. Intervento autorizzato con «Fai» dopo la proposta di aggiungere salvataggio e archivio locali mantenendo il download. Successiva indicazione: menu Caso non necessario nel pannello FC; rimosso da quella vista, conservato nelle viste Completa e Sopralluogo.

- `app/case_browser.py` e `app/case_browser_frontend/`: componente locale per l’archivio IndexedDB `mortem-cases`, schema 1. Nessuna nuova dipendenza o servizio. Salva soltanto su richiesta; non modifica i calcoli né salva automaticamente le modifiche successive.
- Il menu propone Salva nel browser, oppure Aggiorna nel browser se esiste già la stessa sigla esatta. Ogni salvataggio senza sigla crea una voce distinta con data/ora. Casi salvati è un elenco compatto e richiudibile; l’apertura è esplicita e segnala che sostituisce i dati attuali. Scarica file e Apri da file conservano il formato JSON precedente.
- Il contenuto usa `encode_case`/`decode_case` e il percorso di ripristino esistenti: input, segni, FC applicato, scenari, bozza FC e modalità. La bozza resta distinta dai valori applicati, anche tornando dal pannello con Indietro. Risultati da ricalcolare come per l’importazione da file. I vecchi file restano compatibili.
- I casi archiviati restano nel browser: elenco e salvataggio non trasmettono l’archivio a Streamlit. Solo il caso scelto per l’apertura viene inviato al normale percorso applicativo e validato interamente prima della sostituzione. Stato di controllo `__case_browser` con identificativo di istanza ed evento consumato, escluso dai file e dalle copie del form FC; impedisce eventi obsoleti o ripetuti dopo un’importazione.
- Il successo viene mostrato solo dopo il completamento della transazione. Il confronto nella transazione di scrittura evita di sovrascrivere silenziosamente un salvataggio più recente effettuato da un’altra scheda. Archivio non disponibile, errori e spazio esaurito lasciano utilizzabile il download; non vengono dichiarati salvataggi riusciti in caso di errore.
- Limiti mostrati nell’interfaccia: stesso browser e dispositivo; la cancellazione dei dati del sito elimina l’archivio. Non è una sincronizzazione tra dispositivi né abilita l’uso offline dell’app. Documentazione tecnica consultata: https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API/Using_IndexedDB .
- Verifiche: test JavaScript su conservazione di input/bozze, aggiornamenti nominativi, voci senza sigla, conflitti, errori di scrittura e apertura esplicita; test Python su validazione, dimensione, eventi ripetuti/obsoleti. AppTest delle due viste: ripristino reale dal componente senza replay, bozza FC conservata dopo Indietro e assenza del menu nel pannello. Suite dei file caso, integrazione FC, sintassi e diff controllati; nuovo test JavaScript aggiunto alla CI.
- Verifica online completata sul commit `6f1b0716c56e3b66d657c5d58865cd3f20fbf3df`, anche con GitHub Actions superato: caso sintetico PROVA-browser salvato a 70 kg, aggiornato a 83 kg mantenendo una sola voce, app ricaricata (nuova sessione a 70 kg), caso riaperto con recupero della sigla e degli 83 kg. Verificati il menu compatto e la sua assenza nel pannello FC. Nessun dato reale usato nella prova.
- Prossimo passo: prova dell’utente sul proprio browser. Ultimo test utente documentato resta quello indicato sopra; i controlli automatici non ne costituiscono conferma. `main` e logica scientifica non modificati.


## Punto di avanzamento — diciture dei range e descrizioni senza grassetto, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base GitHub verificata `419c6075634bad5e11ba428a38ba59e97edc104d`. Commit identificabile con `git log -1 --format=%H --grep='Uniforma i range e rimuove il grassetto dalle descrizioni'`. Richiesta esplicita dell’utente, accompagnata da schermata con due scenari immersi a 20 °C: mantenere la dicitura generale delle temperature, usare la stessa dicitura dei FC anche con scenari e non mostrare alcun grassetto nelle descrizioni dettagliate.

- Conservata «Range di temperature ambientali medie (tenendo conto delle possibili escursioni termiche verificatesi tra decesso e ispezione legale)». Eliminata la riga aggiuntiva Temperature degli scenari e il relativo parametro di sola presentazione. I singoli scenari conservano temperatura e FC abbinati nel calcolo.
- Uniformato l’incipit «Range di FC considerati (considerate le varie condizioni in cui potrebbe essersi trovato il corpo)» per intervalli e scenari. Conservate le condizioni associate a ciascun estremo. Allineata la descrizione generata dal pannello con quella ricostruita in Python, anche per casi salvati in precedenza.
- Quando i due estremi coincidono, la descrizione mostra una sola volta il valore di temperatura o FC; gli estremi numerici usati nel calcolo rimangono entrambi presenti e invariati.
- In `_wrap_final()` rimossi i tag di grassetto e normalizzate le eventuali indicazioni esplicite di peso del font, prima della creazione dell’HTML delle sole descrizioni dettagliate. Il carattere normale è indicato anche sui paragrafi e sulle voci di elenco per il trasferimento a Word. Conservati Arial 10 pt, interlinea Minima 14 pt, colori, note, elenchi HTML e rientri. Il riepilogo separato mantiene la propria formattazione.
- Verifiche locali: 14 test scenari (inclusa conservazione degli abbinamenti e dei risultati), 5 test dei testi, suite JavaScript del pannello FC e 8 regressioni Streamlit desktop/mobile/Sopralluogo superati. Verificata l’assenza del grassetto nell’HTML finale e la conservazione dell’enfasi nel riepilogo separato. Sintassi e diff controllati.
- Prossimo passo: verifica sull’app di test delle descrizioni con più scenari, quindi riscontro dell’utente sulla resa e sulla copia in Word. Nessuna modifica a equazioni, coefficienti, intervalli di calcolo, salvataggio dei casi o branch `main`.

## Punto di avanzamento — valori singoli, temperature dell’acqua e campi mancanti, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base GitHub verificata `bf66e7d3552f9f4ddc548ca475e1d5a4e0246941`. Continuazione richiesta dall’utente durante la verifica del blocco precedente: non chiamare range due valori uguali, specificare quando la temperatura è dell’acqua e indicare esattamente i dati mancanti.

- Con estremi uguali, anche provenienti da scenari diversi, le descrizioni usano Temperatura ambientale media e Fattore di correzione considerato. Con estremi diversi restano le diciture dei range concordate. Descrizioni dettagliate sempre prive di grassetto.
- Per condizioni immerse viene aggiunta la parentesi temperatura dell’acqua. Quando tutti gli scenari sono immersi compare una sola volta dopo il valore o l’intervallo; negli scenari misti accompagna la temperatura pertinente. Se acqua e ambiente condividono lo stesso valore, questo compare una volta con parentesi temperatura ambientale e dell’acqua. Considerati anche scenari intermedi e scelta singola. Nessuna attribuzione a condizioni precedenti se FC, peso o temperature non corrispondono più alla scelta applicata.
- Validazione condivisa dei campi mancanti: rettale, ambientale, ante-mortem, peso e FC; elenca tutte le assenze insieme e distingue un intervallo incompleto. Il messaggio generico iniziale della vista Completa viene sostituito dal motivo specifico. Vista Completa e Sopralluogo continuano a stimare dagli altri parametri quando il raffreddamento è incompleto, mostrando l’avviso anche senza temperatura rettale. Restano le verifiche esistenti sui valori non validi e sui limiti dei metodi.
- Verifiche: 254 test Python della suite completa superati, inclusi 16 test scenari, 8 regressioni degli input e 9 regressioni delle viste; superata anche la suite JavaScript del pannello. Corrette le aspettative dell’integrazione FC che, nella CI del blocco precedente, cercavano ancora la riga Temperature degli scenari rimossa dalla richiesta. Sintassi e diff verificati. GitHub Actions completato con successo sul commit funzionale `cabef683db5d272d1c7c56eaf046e4c3a686dbcb` (run `38323106956`).
- Verifica online completata: avviso Manca la temperatura rettale con il campo vuoto; caso sintetico PROVA-range riaperto dall’archivio e ricalcolato con scenari immersi corrente/ferma a 20 °C. Temperatura mostrata una volta, parentesi acqua unica, FC 0.35–0.50 con condizioni, medesima stima precedente di non oltre 5 ore e 30 minuti. Controllo del DOM: zero tag b/strong e peso del carattere 400 in tutti i paragrafi e le voci delle descrizioni. Nessun dato reale usato nella prova.
- Non cambiano formule, abbinamenti temperatura/FC, estremi numerici né formato dei file caso. Prossimo passo: riscontro dell’utente sui testi e sulla copia in Word; la verifica HTML non sostituisce quella nel suo documento.
