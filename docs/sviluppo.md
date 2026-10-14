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

Il motore attivo resta in `app/fc_panel_frontend/index.html`. `data/fc_examples.json` contiene soltanto le 35 schede selezionate per le spiegazioni contestuali (21 osservazioni sperimentali su cadaveri, 9 prove su simulatori e 6 casi della pratica medico-legale; una scheda comprende due esperimenti). `app/fc_catalog.py` le fornisce al componente FC tramite gli argomenti Streamlit. Il pannello mantiene i criteri di abbinamento per identificativo; non occorrono richieste esterne per caricare gli esempi. La pagina Tabelle presenta la sintesi del metodo combinato e i riferimenti FC, senza tabelle separate di ipostasi, rigidità o casistica.

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
- Nella versione dell'11 ottobre i sei gradi sopraciliari erano separati in tre righe con due coppie Grado/Intervallo: VI ≤6; V 1–7; IV 2–8; III 3–13; II 3.5–16; I 5–22 ore. Correzione della verifica scientifica del 13 ottobre: questi intervalli derivano dall'incrocio delle risposte positive e negative del metodo combinato; non sono la trascrizione letterale della figura 4 di Henssge e Madea (2004). La precedente attribuzione alla figura era errata.
- Il precedente 26 della riga II proveniva dalla trascrizione testuale della tabella del 2000. Non è stato assunto come prova di un errore nei calcoli. I casi 24, 28 e 67 del 2000 sostengono il limite 16, confermato dalla tabella 10.4 del libro (3ª ed.). Per i limiti Sì/No il riferimento diretto è il capitolo 10.1, non la figura 4 del 2004.
- Usata inizialmente una numerazione bibliografica locale: [1] Henssge et al. 2000, parte II, DOI 10.1007/s004149900090; [2] Henssge e Madea 2004, DOI 10.1016/j.forsciint.2004.04.051. La revisione del 13 ottobre conserva [2] per le tabelle 1–2 e aggiunge [3] capitolo 10.1 del libro e [4] Anders et al. 2013. Non si rivendica la consultazione diretta dei lavori storici citati al loro interno.
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

## Punto di avanzamento — integrazione del pannello FC approvato, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base GitHub verificata `5a3f0a69c4a20df0ef9d6b32ff907460da8bdd01`. Integrazione autorizzata dall’utente con «ok, integralo nella app», dopo la revisione delle anteprime e delle etichette min/max. Commit identificabile con `git log -1 --format=%H --grep='Integra il layout compatto approvato del pannello FC'`.

- Campi desktop della temperatura ambientale e del FC larghi entrambi 144 px, anche nella modalità prudente. Controlli, chiavi e valori conservati.
- Pannello FC: comando Più scenari e numeri affiancati; prima apertura e riaperture dallo scenario 1; navigazione interna conservata durante i ricalcoli del componente. Scenario 1 azzurro tenue e scenario 2 verde oliva, distinto dal verde del FC complessivo per la stima.
- Riquadro FC del singolo scenario compatto e di larghezza stabile. Comandi Intervallo? / Valore singolo? come testo, due campi identici affiancati con pulsanti meno/più e min/max piccoli sulla stessa riga. Il ritorno al valore singolo conserva il minimo; se cambia l’estremo superiore registra correttamente la scelta manuale e la nuova base per l’adattamento al peso.
- Temperatura ambientale media o Temperatura dell’acqua e relativo campo sulla stessa riga; campo bianco con bordo giallo, selettori Appoggio e Aria bianchi. Titoletti Vestiti/teli e Coperte più evidenti, conteggi vicini alle etichette e Molto pesanti / piumoni uniti quando lo spazio lo consente.
- Riepilogo Scenari considerati con numeri e colori corrispondenti quando sono attivi più scenari; Condizioni considerate nel caso singolo. Origine preimpostata/manuale e adattamento al peso sotto le descrizioni, mantenendo la distinzione rispetto ai suggerimenti. Nudo resta la descrizione dell’assenza di vestiti; conteggi incompleti sono descritti come da precisare. Le note di presentazione non entrano nel payload dei casi.
- Verifiche locali: 254 test Python superati; suite JavaScript del pannello e motore FC superate (3385 controlli e 33600 combinazioni, zero casi pendenti). Regressioni su primo scenario, conservazione delle temperature e conversione intervallo/singolo con cambio peso; sintassi e diff controllati.
- Nessuna modifica a formule, regole FC, abbinamenti temperatura/FC, risultati, descrizioni dettagliate o archivio dei casi. Pubblicazione limitata al branch di test; `main` non coinvolto. Prossimo passo: controllo visivo e delle interazioni sull’app aggiornata, quindi riscontro dell’utente sul proprio dispositivo.
- Primo controllo online del commit `eb364e50`: campi principali entrambi 144 px, colori e layout corretti. L’apertura mostrava ancora il secondo scenario; il protocollo iniziale del componente ora seleziona esplicitamente il primo anche ricevendo una vecchia bozza. I render successivi non reimpostano la navigazione. Aggiunta regressione con bozza inizialmente sul secondo scenario e temperature distinte, preservate integralmente.
- Verifica online conclusa sul commit `ff3c73f878858f1f9933a43c1910003d2fe3bccf`: apertura e riapertura sul primo scenario; FC dello scenario con riquadro largo 314 px sia singolo sia intervallo; due controlli FC identici e min/max da 11 px sulla stessa riga. Temperatura bianca con bordo giallo, Appoggio e Aria bianchi; colori azzurro/oliva distinti dal riepilogo verde. Prova sintetica con scenario 1 a 20 °C e FC 1.10–1.20, scenario 2 a 18 °C e FC 1.00: applicazione e riapertura conservano gli abbinamenti, il form mostra temperatura 18–20 °C e FC 1.00–1.20, tutti i campi interessati larghi 144 px. Verificata anche la conversione intervallo/singolo e la nota manuale sotto il riepilogo. Nessun dato reale utilizzato.
- GitHub Actions superato sui commit funzionali `eb364e50` (run `38384990869`) e `ff3c73f8` (run `38385400843`). Resa desktop verificata nel browser; resta il riscontro dell’utente sul proprio telefono. Schermata finale del pannello acquisita per il confronto con l’anteprima approvata.

## Punto di avanzamento — esempi compatti e note a 8 pt, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata `f733607d2477fe4a1a282e5afb6c1587b95100f6`. Modifica autorizzata dall’utente con schermata del riepilogo Condizioni considerate.

- Aggiunti i due punti a Condizioni considerate e Scenari considerati. Gli esempi nel pannello FC mostrano tipo/caso, peso e condizioni riuniti, quindi FC e riferimento bibliografico completo già presente nel catalogo; le note restano dopo il riferimento. Ridotti gli spazi tra i paragrafi, senza cambiare i dati degli esempi o i loro criteri di selezione.
- Note blu nelle descrizioni dettagliate impostate esplicitamente a 8 pt (riepilogo parametri, note sul FC manuale, Qd e relativi commenti). Conservati Arial, interlinea minima 14 pt, colore e assenza di grassetto nelle descrizioni.
- Eliminato EPOCA DEL DECESSO STIMATA dalle varianti della frase con e senza data/ora. Il testo successivo della stima, i valori e le finestre temporali restano invariati.
- Verifica delle aspettative testuali aggiornata per i soli cambiamenti richiesti; suite JavaScript degli esempi e del pannello e tutti i 254 test Python superati. Nessuna modifica a calcoli, stato, archivio dei casi o branch `main`. Prossimo passo: verificare online gli esempi, la dimensione delle note e il riepilogo senza titolo.
- Verifica online completata sul commit `6c7d3f8d4c0ba6e54a6d21f6254ed1e6e57680ac`: entrambi i riepiloghi terminano con i due punti; Caso B58 con peso/condizioni riuniti e riferimento esteso immediatamente dopo FC 1.10, margini dei paragrafi pari a 2 px. Con dati sintetici (rettale 36 °C, ambiente 20 °C, 70 kg, FC 1.00), il riepilogo inizia direttamente con tra 30 minuti e 6 ore prima; nelle descrizioni nessun grassetto e note blu con dimensione inline 8 pt, resa DOM 10.6667 px, peso del carattere 400. Rimane da verificare sul Word dell’utente il trasferimento con formattazione originale.
- GitHub Actions superato sullo stesso commit (run `38389521087`).

## Punto di avanzamento — fonti richiudibili e note essenziali, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata `ca4cb89c809a2a2e5663f9ce5be6b45094b8a719`. Correzione esplicita dell’utente: nessuna reference completa ripetuta sotto i casi; eliminare il commento generico sugli esperimenti in acqua e le note analoghe.

- Rimossi i riferimenti estesi dalle singole schede. Restano apribili nella sezione delle fonti; Fonti degli esempi raccoglie una sola volta ogni riferimento dei casi mostrati, conservando i collegamenti. Le fonti delle regole mantengono l’apertura con un clic.
- Eliminate le ripetizioni su soglie universali, intervalli di confidenza, non trasferibilità del valore e indumenti/superfici già descritti. Conservate soltanto brevi informazioni specifiche non altrimenti visibili: temperature delle prove, ipertermia del caso 33, tempo non verificato del caso 6, valore centrale del caso 62, classificazione delle foglie intermedie e asterisco del FC 1,77.
- Controllo automatico del catalogo: per tutti i 34 esempi, ogni dato diverso dalle note è identico alla versione precedente. Superati i 7 test del catalogo, la verifica JavaScript degli esempi e la suite del pannello. Formule, abbinamenti, FC e valori numerici non modificati. Prossimo passo: verificare online i casi in acqua e l’apertura dei riferimenti.
- Ulteriori correzioni richieste: eliminato dalla vista il titoletto Tabelle operative originali di Henssge; FC riunito alla riga con peso e condizioni, senza un paragrafo separato. Decimali degli esempi sempre con il punto, incluse temperature, pesi e note; bibliografie e dati numerici del catalogo conservati. I 7 test del catalogo e le verifiche JavaScript degli esempi e del pannello sono nuovamente superati.
- Verifica online completata sul commit `2510ffe802ec8306d92d0cc51de40b9ba2cdb462`: casi B63, 01 e 10 con FC nello stesso paragrafo di peso/condizioni; temperature 19.3 e 10.2 °C, nessuna virgola decimale o nota generica nei casi in acqua, titolo delle tabelle nascosto. Fonti degli esempi inizialmente chiuso, riferimento completo e collegamento verificati all’apertura, nessuna ripetizione tra i due casi della stessa fonte. Schermata desktop acquisita. Job GitHub Actions test superato (run `38391188354`). Nessuna modifica a `main`.

## Punto di avanzamento — campo FC e comando scenari nella pagina principale, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata `5375f8fb483bb9876099d8dcff6962e2dc304091`. Correzioni richieste dall’utente sul desktop: ripristinare la larghezza del FC, collocare Più scenari a destra fra temperatura e FC, aggiungere un helper al titolo FC.

- Rimossa dal wrapper numerico la vecchia suddivisione in due colonne del solo FC singolo, che dimezzava ulteriormente il contenitore da 144 px. Il campo usa ora tutta la larghezza assegnata, come la temperatura ambientale.
- Nelle due modalità desktop, valori singoli e intervalli, temperatura e FC condividono una colonna e Più scenari con il relativo helper occupa la colonna di destra, centrato rispetto ai controlli. Su mobile il comando resta dopo i campi.
- Helper accanto al titolo FC singolo e range: «Clicca su un campo FC per aprire il pannello che suggerisce il fattore di correzione in base alle condizioni del corpo e ai dati della letteratura». Allineato il testo dei corrispondenti helper numerici.
- Superate l’integrazione Streamlit del pannello FC, le 9 regressioni delle viste di raffreddamento e le verifiche JavaScript dei controlli FC V1/V2. Sintassi e diff verificati. Nessuna variazione a valori, equazioni o abbinamenti degli scenari. Prossimo passo: verifica visiva sull’app di test per valori singoli, intervalli e apertura dell’helper.
- Verifica online completata sul commit `08ba71c5fefe953cb11474c76bc209ae162d7488`: FC e temperatura singoli larghi entrambi 144 px; nella modalità intervalli tutti e quattro i controlli larghi 144 px e allineati su due righe. Più scenari resta a destra fra le due righe, apre il pannello sullo scenario 1 e conserva i valori applicati. Provati scenari sintetici a 20 e 18 °C con FC complessivo 1.00–1.20. Helper FC singolo e range verificati con apertura/chiusura, testo corrispondente alla richiesta. GitHub Actions superato (run `38392551882`); schermata desktop acquisita.

## Punto di avanzamento — riepiloghi e note del FC, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata `aa4e5cab08e57da82ed17ed32ed37a3bbae23184`. Richiesta: condizioni singole sulla stessa riga del titolo, scenari su righe distinte, note sull’origine del FC richiamate da asterisco e rese più discrete.

- Condizioni considerate e relativa descrizione sono in linea nel caso singolo, con ritorno a capo naturale solo se necessario. Gli scenari mantengono righe separate, numeri e colori corrispondenti.
- Asterisco accanto al campo FC singolo o al secondo estremo dell’intervallo quando esiste una nota. Nota sotto il riquadro FC, 10 px e colore blu-grigio, per preimpostato, compilato manualmente e adattamento al peso. La nota segue lo scenario attivo e non viene ripetuta nel riepilogo delle condizioni. Riferimento accessibile dai campi tramite aria-describedby.
- Suite JavaScript del pannello superata, incluse origine del FC, bozze, cambio scenario, singolo/intervallo e adattamento al peso. Nessuna modifica alle regole o ai valori. Prossimo passo: verifica visiva online.
- Domanda aggiuntiva dell’utente sul titolo della tabella: il fallback generico è collegato alla tabella 6.18. Verificato il titolo nel capitolo di Henssge riprodotto in Estimation of the Time Since Death, 4ª ed.: Empirical Corrective Factors of the Body Weight for Cooling Conditions Differing from the Chosen Standard. Presentata in conversazione una proposta di spiegazione; testo dell’app ancora invariato su questo punto.
- Primo controllo online e CI completati sul commit `ba5fedaf`: nota preimpostata da 10 px in blu-grigio con asterisco, titolo e descrizione delle condizioni alla stessa altezza. GitHub Actions superato (run `38396478969`).
- Ulteriori richieste: senza più scenari, il riquadro diventa FC per la stima, verde come il FC complessivo, con titolo, valore e comandi allineati sul desktop. Su schermi stretti i comandi possono andare a capo, conservando i due estremi affiancati. Con più scenari resta il riquadro compatto dello scenario attivo.
- Nessuna nota o asterisco per un FC manuale che coincide esattamente con il suggerimento, sia singolo sia intervallo. Conservata internamente l’origine manuale e la base del valore: cambia solo la presentazione. Restano le note per preimpostato e scelte manuali diverse dal suggerimento.
- Verifica online conclusa sul commit `25aefc82`: FC per la stima, campo e comandi centrati sulla stessa riga nel riquadro verde; in modalità intervallo campi uguali da 109.625 px, senza overflow. Nota e asterisco assenti per FC manuale 0.50 in acqua ferma e per estremi coincidenti con il suggerimento; nota presente per 0.55 rispetto al suggerimento 0.50. Riepilogo a due righe numerate con scenari asciutto/immerso verificato, schermata del caso singolo acquisita. Suite JavaScript del pannello e GitHub Actions superati (run `38397281823`). Nessun dato reale utilizzato; resta il riscontro sul dispositivo mobile dell’utente.
- Formulazione della spiegazione approvata dall’utente: il testo generico della tabella ora recita «Fattore di correzione indicato nella tabella riepilogativa degli studi di Henssge, in base a indumenti, coperture, condizioni del corpo e movimento dell’aria o dell’acqua». Modifica solo testuale; conservate le spiegazioni specifiche delle singole configurazioni e le fonti apribili.

## Punto di avanzamento — temperatura ambientale e FC inizialmente vuoti, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata `1f359eb39bee5b335c9ddd61ddb75c787fb54bb0`. L’utente richiede di eliminare i valori preimpostati della temperatura ambientale e del FC.

- Nuove sessioni con temperatura ambientale e FC vuoti nella vista Completa, desktop e mobile, e nella vista Sopralluogo. Vuoti anche gli estremi iniziali degli intervalli; rimossi i valori sostitutivi di 20 °C e 1.00 nei passaggi tra modalità e nell’applicazione dei suggerimenti.
- La sola apertura del pannello o la modifica del peso non genera un FC preimpostato. La scelta rimane vuota, senza nota manuale o preimpostata, fino all’inserimento del valore o alla selezione delle condizioni del corpo. Restano attivi i suggerimenti su richiesta e gli avvisi per i campi mancanti.
- Conservati i valori delle sessioni esistenti e dei casi caricati, comprese le vecchie note di origine preimpostata. Nessuna modifica alle regole scientifiche o ai calcoli. Superati i 18 controlli di integrazione del pannello, la suite JavaScript, i 4 test sull’origine del FC e i 6 sull’applicazione della scelta; verificate sintassi e diff. Regressioni mirate per apertura/ritorno con campi vuoti, cambio peso, avvisi e selezioni esistenti. Prossimo passo: controllo visivo dell’app dopo la pubblicazione.

## Tabella combinata in forma di domande — 13 ottobre 2026

Base verificata: `2ef27f1b49a3f46a5c0a922ef5382e1b51da0f0c`, branch `refactor-tanatology-keys`. Aggiornamento approvato dopo il confronto con il capitolo 10.1 di Henssge e Madea (3ª ed.) e con Anders et al. (2013).

- Una sola tabella a quattro colonne, con 23 domande e risposte Sì/No. Integrata l'eccitabilità sopraciliare con descrizioni anatomiche cumulative, senza gradi romani. I limiti derivano dalla tabella 10.4 e dalla figura 10.7 del libro, riferimento [3]; rimossa la precedente attribuzione alla figura 4 del 2004.
- Le domande «Ha iniziato a risolversi?» (Sì ≥24 / No ≤96) ed «È completamente risolta?» (Sì ≥24 / No ≤192) sono la rielaborazione approvata degli estremi descrittivi di persistenza e risoluzione della fonte [2]. La nota distingue questa rielaborazione dalle domande originali della tabella combinata. «No» significa «non ancora»; l'inizio della risoluzione comprende anche la fase già completata.
- Ricomparsa dopo mobilizzazione: aggiornato il limite superiore visualizzato a 19 ore, estremo osservato nello studio di Anders et al. su 79 cadaveri/314 articolazioni (Int J Legal Med. 2013;127:127–130; DOI 10.1007/s00414-011-0632-z). Il dato sostituisce l'8 della vecchia tabella; il libro aveva già portato tale valore a 9.5. Riferimento completo [4] e nota approvata: «Dati aggiornati sulla base dei nuovi estremi temporali riportati in casistiche pubblicate in letteratura (Anders et al., 2013)». Gli estremi non sono presentati come soglie biologiche assolute.
- Allineata la traduzione inglese. Decimali con punto in entrambe le lingue. Asterisco per l'aggiornamento a 19 ore e richiamo † separato per la risposta peribuccale. Parametri e algoritmi di stima non modificati: l'intervento aggiorna la tabella documentale.
- Verifiche locali superate: quattro test mirati, inclusa la ricostruzione dei sette esiti sopraciliari e dei cinque stadi della rigidità a partire dalle risposte Sì/No; AppTest della pagina completa in IT/EN senza eccezioni, 23 righe e quattro riferimenti; sintassi e diff. La verifica visiva automatica non è stata eseguita perché il browser locale di Playwright non è installato. Questi controlli non attestano il commit già distribuito da Streamlit Cloud.

## Precisazioni della tabella combinata — 13 ottobre 2026

- Terminologia richiesta: «Macchie ipostatiche», «Rigidità cadaverica», «digitopressione»; completa instaurazione formulata come «Si è già completamente instaurata, con intensità massima e distribuzione generalizzata?».
- Tolti i richiami [2] dalle due domande sulla risoluzione e la frase esplicativa «Ha iniziato a risolversi?» comprende anche la completa risoluzione. Fonte conservata nella nota generale sul decorso e in bibliografia.
- Eccitabilità meccanica: esplicitata la contrazione dell'intero muscolo alla percussione e aggiunta la tumefazione reversibile (≤ 5 h), da Madea, capitolo 3.2, tabella 3.5, nuovo riferimento [5]. La domanda generale comprende anche la piccola tumefazione persistente: mantiene ≤ 13 h / ≥ 1.5 h dal metodo combinato [1]. Il limite minimo negativo vale soltanto in assenza di qualsiasi risposta, non in assenza di una singola forma. La tabella contiene ora 24 domande.
- Precisazione pupillare approvata: «dopo iniezione di atropina/tropicamide/acetilcolina». Le tabelle 3.1–3.2 del libro riportano iniezioni sottocongiuntivali o nella camera anteriore, non una semplice instillazione di collirio. Sostituita «instillazione» con «iniezione» anche negli helper e nelle descrizioni attive e legacy dell'app; fonte inclusa nel riferimento [5].
- Parametri e algoritmi di stima invariati. Test delle risposte meccaniche esteso alle quattro condizioni dell'app, in italiano e inglese.

## Punto di avanzamento — correzioni delle tabelle di riferimento, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`. Base corrente verificata su GitHub: `fc8e0a671ff216e1945f9ca72b183861891600d4`. App collegata secondo il punto di ripresa: `https://mortem-test.streamlit.app/`; verificati online i contenuti della pagina Tabelle prima dell'intervento. Il nuovo commit è identificabile con `git log -1 --format=%H --grep='Corregge testi e impaginazione delle tabelle di riferimento'`. Ultimo commit precedente con prova online esplicitamente documentata: `25aefc82`; ciò non certifica un test dell'utente dell'attuale versione.

- Autorizzazione specifica: «No fai queste correzioni sulla parte delle tabelle di riferimento della app». Modifica limitata a `pages/2_Tabelle di riferimento.py`, funzioni `_render_combined_table`, `_render_henssge_base_table`, `_render_henssge_special_table`, `_render_henssge_weight_table` e rispettivi testi/stili. Allineate le versioni italiana e inglese.
- Eccitabilità meccanica: ripristinata la distinzione fra contrazione dell'intero muscolo/fenomeno di Zsako (Sì ≤2.5 h, No senza limite utile) e tumefazione locale idiomuscolare del bicipite (Sì ≤13 h, No ≥1.5 h, criterio storico del metodo combinato). Rimossa dalla tabella combinata la riga descrittiva intermedia ≤5 h e la domanda cumulativa che mescolava le tre forme. Tabella ora di 23 domande. Nessuna modifica alle fasi o agli intervalli usati dall'app nei calcoli.
- Eliminate le note di lettura Sì/No/trattino e sopraciliare richieste dall'utente. Nota della tabella del peso ridotta alla sola frase concordata sulla trascurabilità della dipendenza dal peso per FC inferiori a 1.4, fino a 0.75. Conservati i valori della matrice e il riferimento visivo a 70 kg.
- Superfici: «Foglie (strato di circa 2 cm)» e «Pavimento di casa, prato, terreno, asfalto». Le categorie termicamente indifferente, isolante e termoconduttiva hanno righe di intestazione separate su tre colonne; i valori restano associati al rispettivo abbigliamento. Riferimenti locali [1]–[3] e asterischi in apice, con nota letterale non trasformata in punto elenco. Tutte le note e citazioni usano `st.caption` con font uniforme; rimosso l'asterisco senza richiamo della nota generale FC.
- Metallo: aggiunta la prova 290 già documentata in `data/fc_examples.json` (Knörle 1991, citato da Henssge in Madea 2016, tab. 6.10): simulatore non rivestito su acciaio appoggiato a calcestruzzo, con acqua circostante, FC 0.55. Le condizioni specifiche sono esplicite; nessuna attribuzione di tale valore a ogni piano metallico. Nota su conducibilità e capacità termica, distinguendo la lamiera sottile dal supporto massiccio. La tesi originale non è stata consultata direttamente.
- Nota dei FC del corpo nudo: i segni +/− sono presentati come possibili refusi tipografici secondo gli autori dell'app, non come errata corrige ufficiale. Confronto con il testo di Henssge (cemento, FC 0.75) e prove su PVC (0.76–0.77), esplicitando che il materiale è diverso. Non sono stati usati come prova del cemento gli esperimenti su corpi bagnati.
- Fonti di controllo: Henssge e Madea 2004, doi:10.1016/j.forsciint.2004.04.051; capitoli 3.2 e 6.1 della quarta edizione Madea 2023 consultati per distinguere le risposte meccaniche e verificare la spiegazione sulle superfici; dati numerici delle prove ripresi dal catalogo già verificato sulla terza edizione 2016. Bibliografia della pagina conservata con i riferimenti pertinenti alla terza edizione.
- Verifiche locali: sintassi, cinque test della tabella (matrice del peso, rigidità, sopraciliare, ricomparsa e criteri meccanici), AppTest della pagina completa IT/EN senza eccezioni, diff controllato. Aggiornato il test meccanico per controllare i criteri documentali, senza obbligare la tabella scientifica a riprodurre gli stati descrittivi dell'app. Ambiente locale con Python 3.12 e Streamlit 1.64.0; non attestata qui l'identità di tutte le dipendenze indirette con la produzione.
- Restano da verificare la resa visiva dopo la distribuzione e il riscontro dell'utente sul proprio dispositivo. Nessun nuovo tentativo funzionale fallito. Prossimo passo: test utente delle tabelle, prima di ulteriori interventi. `main`, motore FC, peso, stato, equazioni, risultati e altre pagine non modificati.

- Verifica online completata sul commit applicativo `bb7eae5d23960afa77f32111a600c3007985855c`: pagina `https://mortem-test.streamlit.app/Tabelle_di_riferimento`, due criteri meccanici distinti, note eliminate, categorie delle superfici correttamente allineate, riga metallo e nota del peso visibili. Tutte le 16 note/citazioni hanno stile effettivo uniforme: Source Sans, 12 px, interlinea 15.6 px. Controllo della griglia HTML in IT/EN: tre colonne correttamente occupate in tutte le 15 righe della tabella superfici, tre asterischi con nota comune. Test del dispositivo mobile dell'utente ancora da eseguire. La CI generale era in corso al termine della verifica visiva (run `38427245359`); i cinque test locali e AppTest IT/EN sono superati.


## Punto di avanzamento — nota limitata ai FC 0.75 e 1.3, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata su GitHub e nel checkout: `de2c3030cee2b69f5210c2ec26636e24e0728136`. L’utente ha precisato l’ambito della nota e proposto la formulazione sui possibili refusi dei segni +/−, dopo aver chiesto di discuterla prima dell’applicazione.

- Nota esplicitamente limitata a 0.75 e 1.3 per il corpo nudo: possibili refusi secondo gli autori dell’app, interpretazione come FC complessivi e coerenza con esempi nei testi di Henssge [3], senza presentarla come rettifica ufficiale. Allineata la traduzione inglese.
- Tolto l’asterisco da 1.1–1.2; restano soltanto i richiami di 0.75 e 1.3. Nota e riferimento sul metallo conservati separatamente. Modifica applicativa limitata al testo e al richiamo nella pagina delle tabelle; valori, calcoli e altre pagine invariati.
- Verifica locale completata: AppTest della pagina IT/EN senza eccezioni, due asterischi associati ai soli valori indicati e ambito esplicito nella nota; cinque test esistenti delle tabelle superati, diff controllato. Nessun nuovo test permanente per la modifica testuale. Prossimo passo: controllo online della nota e riscontro dell’utente sulla pagina di test. `main` non coinvolto.
- Verifica online completata sul commit `48c3820f4378fd0defef360eae410c5becc03b89`: nota aggiornata visibile nella pagina Tabelle di riferimento, asterischi presenti solo accanto a 1.3 e 0.75, nessun richiamo su 1.1–1.2 e nota sul metallo distinta. Resta il riscontro dell’utente sul proprio dispositivo.

- Semplificazione successiva richiesta dall’utente: eliminata la frase introduttiva «La nota riguarda esclusivamente i valori 0.75 e 1.3 per il corpo nudo», anche nella versione inglese. Il richiamo resta delimitato dai soli due asterischi in tabella. Base verificata `1efc19dd40114a2b98e3c04861d0e65c7428af08`; controllati sintassi, permanenza dei richiami e diff.

## Punto di avanzamento — esempi di PVC e metallo nelle tabelle, 13 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata `e62788470cbe5a575445c7e80e4ff6e98ef76644`. Modifiche richieste dall’utente nella sola pagina Tabelle di riferimento, in italiano e inglese.

- Fonte utilizzata per questo intervento: capitolo sul raffreddamento nella cartella Drive «Capitolo raffreddamento», Henssge in Madea, 3ª ed., 2016, cap. 6.1. Controllate direttamente le immagini 12-17-17 e 12-17-20 del 30 settembre 2026 (tab. 6.10) e 12-22-24 (scelta del fattore di correzione). Nessuna nuova fonte web per questi esempi.
- Inseriti in tabella il pavimento rivestito in PVC, FC 0.76–0.77 nelle prove 230–232, e la lamiera metallica sottile fra gli appoggi termicamente indifferenti, in accordo con il passo sulla sua bassa capacità termica. Distinto il piano metallico spesso, con esempio esplicito dell’acciaio su calcestruzzo con acqua circostante e intervallo 0.53–0.55 delle prove 290–292. La fonte non fornisce una soglia numerica di spessore: non ne è stata introdotta una. L’intervallo riguarda l’esempio riportato.
- Eliminate la spiegazione estesa sul metallo e la menzione della tesi originale non consultata; riferimento bibliografico limitato al capitolo utilizzato. Eliminata anche la frase «Indifferente = stesso FC con o senza correnti d’aria» e la traduzione inglese, come richiesto. Conservati i due soli asterischi relativi ai FC 0.75 e 1.3 e la nota concordata sui possibili refusi.
- Verifiche locali superate: AppTest della pagina IT/EN senza eccezioni; griglia HTML di 17 righe e tre colonne, inclusa l’intestazione, con occupazione corretta; valori, richiami e assenza delle note eliminate controllati; diff senza errori. Nessuna modifica a calcoli, stato o altre pagine. Prossimo passo: verifica online dopo l’aggiornamento dell’app di test.
- Verifica online completata sul commit `2f2835722f6ec52e7e44cf69a639213b0d4150d0`: presenti PVC, lamiera sottile e piano spesso; assenti la nota sulla tesi e la frase esplicativa sull’indifferenza alle correnti d’aria.
- Ulteriore richiesta dell’utente: tolta la specifica tra parentesi dal piano metallico spesso nella tabella, anche in inglese. Valori e riferimenti conservati. Controllato il comportamento del pannello attivo: la lamiera sottile usa il medesimo FC della superficie termicamente indifferente nelle condizioni selezionate, senza soglia numerica di spessore. La spiegazione è stata fornita in conversazione; nessuna modifica alle regole di calcolo.
- Verificata online la voce semplificata sul commit `07675174388d3b0caa224e8f240f789c09037518`. Su richiesta successiva, nella sola tabella degli appoggi «No» diventa «Nudo» e «Sì / No» diventa «Indifferente», con traduzioni inglesi coerenti. Inserito «Pavimento molto freddo (es. cantina)» come riga autonoma, Nudo, FC 0.75, riferimento [3] al passo del capitolo già consultato. Cemento/pietra/piastrelle conservano il riferimento [1]. La prima proposta di accorpare gli esempi è stata corretta prima della pubblicazione, secondo la precisazione dell’utente. Nessun asterisco aggiunto alla nuova riga: il valore nell’esempio testuale non presenta il problema dei segni +/− delle tabelle.
- Verifiche locali IT/EN superate: AppTest senza eccezioni, sette celle Nudo e due Indifferente, 18 righe nella tabella, fonte [3] e FC 0.75 associati alla sola nuova riga, due asterischi originali conservati, diff controllato. Calcoli e altre pagine invariati.
- Verifica online completata sul commit `5cf9d7796904b366ffbcd96a8fbea3c06b8d02f0`: etichette aggiornate e riga cantina distinta con il proprio riferimento.
- Ulteriori richieste dell’utente: eliminata la lamiera metallica sottile dalla sola tabella degli appoggi; «vedi FC di base» sostituito con «Nessuna modifica» e rimosso il richiamo [3] dall’intestazione degli appoggi indifferenti. Rimangono la selezione e il comportamento della lamiera nel pannello FC. Nella tabella combinata, spostata l’introduzione integralmente nella prima nota sottostante, con lo stesso font delle altre note; il titolo conserva il testo, usa la classe condivisa delle altre intestazioni e precede il selettore della lingua, senza duplicazione nella tabella.
- Controlli IT/EN superati: AppTest senza eccezioni, titolo condiviso e introduzione presente una sola volta immediatamente dopo la tabella combinata; 23 criteri conservati; tabella appoggi di 17 righe, lamiera assente, nuova dicitura presente e due asterischi conservati. Diff controllato. Intervento limitato alla pagina di riferimento e al presente registro.

## Punto di avanzamento — significato statistico dei limiti temporali, 14 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata su GitHub e nel checkout: `7222ce73d7824db8a01e0452f6749a8ceb71e106`. Prima dell’intervento controllata la pagina online dell’app di test: titolo, ordine delle note e contenuti corrispondono alla base. Formulazione approvata dall’utente con «Ok» dopo il chiarimento sulla standardizzazione della risposta sopraciliare.

- Sostituita soltanto la nota `variation_note` in `_COMBINED_TABLE_TEXT`, italiano e inglese, in `pages/2_Tabelle di riferimento.py`. La nota distingue gli intervalli statistici al 95% dell’eccitabilità elettrica sopraciliare dagli estremi osservati delle altre casistiche. Il motivo esplicitato è la standardizzazione della stimolazione e della valutazione della risposta, con verifiche successive; nessuna affermazione sulla maggiore ampiezza della casistica. Conservata la precisazione che i valori non sono soglie biologiche assolute.
- Fonte verificata in conversazione: Henssge et al. (2000), parte II, tabella 1 e discussione, doi:10.1007/s004149900090, già presente come riferimento [1]. La nota non afferma che per gli altri criteri non esistano studi statistici, ma che ai limiti riportati non si attribuisce un significato statistico altrettanto verificato.
- Verifiche locali superate con Python 3.12 e Streamlit 1.64.0: cinque test esistenti delle tabelle; sintassi; AppTest della pagina completa in IT/EN, nota italiana identica alla formulazione approvata e nessuna eccezione; diff controllato. Il primo ambiente virtuale individuato non aveva un interprete utilizzabile; impiegato l’ambiente disponibile `audit-env`, senza modifiche alle dipendenze del progetto.
- Valori, 23 criteri, calcoli, stato e altre pagine invariati. Nessun nuovo test permanente per la modifica testuale. Prossimo passo: controllo online dopo la distribuzione e riscontro dell’utente sulla leggibilità della nota. Commit dell’intervento identificabile con `git log -1 --format=%H --grep='Chiarisce il significato statistico dei limiti della tabella combinata'`.

- Verifica online completata sul commit applicativo `260ec9ecae095019da2952e8dfd4d108f16db1bc`: nota approvata visibile in italiano, traduzione inglese verificata mediante il selettore della prima tabella. Nessun errore visibile nella pagina. Resta il riscontro dell’utente sulla leggibilità sul proprio dispositivo.

## Punto di avanzamento — modifica delle temperature con più scenari, 14 ottobre 2026

Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base verificata su GitHub e nel checkout isolato: `d1b5ce45a8fa9a09f7e60245152450f6694c67ad`. Controllata online la pagina principale dell’app di test prima della pubblicazione. L’utente richiede l’apertura diretta del pannello FC quando tenta di modificare le temperature con più scenari attivi; aggiunge il riepilogo delle temperature, avvisi specifici sui dati mancanti e un pulsante più riconoscibile denominato «Specifica più scenari».

- In `app/__init__.py`, i due campi della temperatura ambientale della pagina completa riutilizzano l’azione di apertura del pannello FC quando sono applicati più scenari. Clic, tastiera e pulsanti −/+ aprono il pannello; eventuali vecchi eventi di valore non modificano gli estremi separatamente dagli scenari. Apertura sul primo scenario, temperature e abbinamenti ai FC conservati; «Indietro» conserva la scelta applicata e «Usa» aggiorna gli estremi. Un valore singolo o un intervallo senza scenari restano modificabili nella pagina principale. Tooltip V1/V2 adeguato al comando condiviso.
- Nel pannello, il riepilogo complessivo mostra FC e range delle temperature. Le righe dei singoli scenari riportano FC e temperatura associati, distinguendo la temperatura dell’acqua. Temperature uguali mostrate una sola volta nel riepilogo complessivo; temperatura mancante rappresentata da un trattino, senza trattarla come zero. Conservata la precisione di due decimali quando necessaria.
- L’avviso generico «Completare gli scenari» è sostituito da messaggi per numero di scenario, indicando esplicitamente la temperatura ambientale media o dell’acqua mancante e gli eventuali altri errori del relativo scenario. Il comando condiviso di apertura è ora un pulsante secondario con bordo, «Specifica più scenari».
- Verifiche locali superate: 20 controlli di integrazione Streamlit desktop/mobile/MSIL; ulteriori 19 controlli mirati dopo gli ultimi aggiornamenti, inclusi ritorno senza applicazione, aggiornamento tramite «Usa», conservazione delle coppie temperatura–FC e inserimento diretto senza scenari. Suite JavaScript del pannello, controlli numerici V1/V2 e temperatura dell’acqua superati; coperti riepilogo, valori negativi/zero/mancanti, temperature uguali, precisione, aggiornamento per peso e avvisi distinti. Diff senza errori. Nessuna modifica alle formule o ai criteri scientifici; controllo di coerenza nel calcolo conservato.
- Prossimo passo: verifica online di navigazione, riepilogo e avvisi, poi riscontro dell’utente sul proprio dispositivo. Commit applicativo identificabile con `git log -1 --format=%H --grep='Semplifica le temperature negli scenari e completa il riepilogo FC'`.

- Verifica online completata sul commit applicativo `c6f14f7e8ac3bfd390bfac416c92344b74d05604`: pulsante «Specifica più scenari» con bordo visibile; due scenari sintetici (ambiente 20.0 °C/FC 1.00 e acqua 8.0 °C/FC 0.50), avvisi distinti sulle temperature mancanti, riepilogo complessivo e coppie individuali verificati. Clic sul secondo campo temperatura e pulsante + del primo aprono direttamente il pannello sullo scenario 1. Modifica della temperatura dell’acqua a 9.0 °C applicata con «Usa», valore rientrato nella pagina principale e conservato alla riapertura; nessuna variazione involontaria tramite +. GitHub Actions superato (run `38537534573`). Verifica mobile coperta dai test locali; resta il riscontro sul dispositivo dell’utente.
- Pubblicazione tramite connessione GitHub dopo mancata autenticazione del push CLI; albero remoto confrontato con quello locale verificato, identico. Non riprovare il push CLI senza credenziali configurate.

## Punto di avanzamento — avvisi degli scenari senza ripetizioni, 14 ottobre 2026

- Base verificata: `b93678eb62a2108527bfd7eff0afc62e2bf0642f`, branch `refactor-tanatology-keys`. L’utente segnala la duplicazione dell’avviso sul FC, mostrato sia da solo sia nella riga dello scenario.
- Modifica limitata a `app/fc_panel_frontend/scenarios.css`: con più scenari attivi viene mostrato soltanto il riepilogo degli errori per numero di scenario, che include già gli avvisi sul FC e sulle temperature. Il messaggio locale resta disponibile nel caso singolo; validazione e condizioni di abilitazione di «Usa» invariate.
- Suite JavaScript degli scenari superata e diff controllato. Prossimo passo: verifica online della singola occorrenza dell’avviso e della sua permanenza nel caso singolo.

- Verifica online completata sul commit applicativo `545a0df910bfd7440af2ff516b4297a344979b86`: con più scenari è visibile soltanto l’avviso numerato; disattivando «Più scenari» resta visibile l’avviso locale sul FC. Nessun avviso necessario eliminato.

- Formulazione successiva richiesta dall’utente, base verificata `fa706fd5805f89fd7f34221440ae23cd19669b06`: «Scenario 1: selezionare le condizioni del corpo per ricevere suggerimenti o scrivere il FC. Specificare la temperatura.». Il numero segue lo scenario; la richiesta del FC precede quella della temperatura e ciascuna compare soltanto se necessaria. Gli altri messaggi di validazione restano specifici. Modifica testuale in `scenarios.js`, aspettative dei test esistenti allineate; suite JavaScript degli scenari e diff superati. Nessuna modifica ai calcoli o alla validazione.

- Titolo dinamico richiesto dall’utente, base GitHub `2345c38d4c9c7c5ea9c25475900812611997d614` con contenuti locali confrontati: «Gestisci scenari» quando «Più scenari» è attivo, «Consiglia FC» nel caso singolo. Aggiornamento limitato al titolo HTML e al suo testo durante il rendering; suite JavaScript degli scenari e diff superati. Nessuna variazione a dati, calcoli o navigazione.

## Punto di avanzamento — punteggiatura dei range e intestazione breve, 14 ottobre 2026

- Base GitHub e checkout isolato verificati: `a049630c42b3cb86605780e98916165bd262d037`, branch `refactor-tanatology-keys`. Su richiesta dell’utente, sostituite con una virgola le parentesi introduttive nelle descrizioni del range di FC e delle temperature ambientali medie, anche nei riepiloghi generati dagli scenari.
- Ripristinata «EPOCA DEL DECESSO STIMATA:» soltanto all’inizio della descrizione breve, in tutte le varianti con e senza data/ora. Le descrizioni dettagliate restano prive di questa intestazione.
- Allineate le aspettative dei test esistenti; superati 29 test Python su scenari, testi del raffreddamento e frasi temporali, la suite JavaScript degli scenari e il controllo del diff. Nessun nuovo test permanente per queste modifiche testuali; calcoli e dati numerici invariati.

## Punto di avanzamento — helper degli scenari e pulsante vicino ai campi, 14 ottobre 2026

- Base remota verificata `f4cdbebba1873892ea0d54d9d71c847aa73be053`; contenuti dei file interessati confrontati con il checkout. L’helper della pagina principale e la spiegazione nel pannello iniziano ora con «Da usare se il corpo si è trovato…», mantenendo il resto del testo indicato dall’utente.
- Nella pagina principale desktop, il gruppo temperatura–FC occupa la larghezza del contenuto: «Specifica più scenari» resta subito accanto ai campi, anziché essere spinto al margine destro. Aggiornate sia la vista singola sia quella con intervalli.
- Superati i due test di integrazione esistenti mirati all’helper e all’apertura/applicazione degli scenari, con passaggi desktop, mobile e MSIL; diff controllato. Il trasferimento iniziale dei due estremi di temperatura ai nuovi scenari è stato discusso con l’utente e non fa parte di questo intervento.

## Punto di avanzamento — recupero delle temperature nei nuovi scenari, 14 ottobre 2026

- Base remota verificata `183a2cbfb6d1945b81e9d552dfa70868c3a21335`. Dopo l’approvazione dell’utente, i due valori della temperatura nella pagina principale precompilano scenario 1 e scenario 2 nell’ordine di inserimento; con un solo valore valido, anche se è il secondo campo o è zero, vengono precompilati entrambi. Due campi vuoti restano vuoti.
- Il recupero funziona sia dal pulsante della pagina principale sia attivando «Più scenari» nell’editor singolo. Una temperatura modificata nell’editor prevale sui valori iniziali. Gli scenari già applicati conservano le temperature associate; gli estremi nascosti nella modalità singola e in MSIL non vengono recuperati.
- Superati 20 test Python mirati, inclusa l’integrazione desktop/mobile/MSIL, e la suite JavaScript degli scenari. Verificati ordine, valori singoli/uguali/negativi/zero/mancanti, ripristino del pannello, modifica prima dell’attivazione e riapertura degli scenari applicati. Diff controllato; nessuna modifica alle formule.
- Verificata online anche la precedente modifica di posizione: il pulsante desktop ora segue il gruppo temperatura–FC con 16 px di distanza, senza lo spazio vuoto che lo spingeva al margine destro.

- Ulteriore semplificazione testuale richiesta: l’introduzione diventa «Per la valutazione del raffreddamento cadaverico, sono stati stimati i parametri di seguito indicati.». Aspettative dei test testuali esistenti allineate.

- Verificato online sul commit `9b13f5e3f25e03960c025fa9d7987bbb18b25450` il recupero dei due estremi inseriti nella pagina principale: 20 °C nello scenario 1 e 8 °C nello scenario 2, con riepilogo complessivo 8–20 °C e FC conservati.

## Punto di avanzamento — conclusione con un solo parametro e diciture dei range, 14 ottobre 2026

- Base remota verificata `9b13f5e3f25e03960c025fa9d7987bbb18b25450`, branch `refactor-tanatology-keys`. Con una sola famiglia di parametri effettivamente utilizzata, la conclusione dettagliata inizia con «La valutazione dei dati disponibili porta a stimare che la morte sia avvenuta circa». Più scenari del raffreddamento restano un unico parametro.
- Se sono disponibili data e ora dei rilievi, la conclusione riporta direttamente l’intervallo di calendario, senza ripetere la durata relativa. In assenza dell’orario resta il tempo trascorso prima dei rilievi. Conservati i limiti aperti e i casi «non oltre»; la conclusione integrata rimane per più parametri. Intestazione della descrizione breve, calcoli, arrotondamenti e intervalli invariati.
- Ulteriore formulazione richiesta dall’utente: «Per la valutazione del raffreddamento cadaverico, sono stati considerati i parametri di seguito indicati.» e «Range di FC stimati, considerate le varie condizioni in cui potrebbe essersi trovato il corpo:». Aggiornati i riepiloghi generati da Python e JavaScript e le aspettative dei test esistenti; testo delle temperature conservato.
- Superati 33 test Python mirati e la suite JavaScript degli scenari. Verificati il passaggio tra uno e più parametri, il caso senza raffreddamento, data/ora presente o assente, attraversamento della mezzanotte e limiti aperti. Diff controllato. Prossimo passo: controllo online delle nuove diciture dopo la distribuzione.

- Verifica online completata sul commit applicativo `37cb5d09919e340c3144020e7974ba33d4a15f4d`: introduzione «sono stati considerati i parametri», voce «Range di FC stimati» e conclusione con «La valutazione dei dati disponibili…» visibili nel pannello dettagliato. Nel caso sintetico con due scenari e solo raffreddamento, la conclusione riporta direttamente le date e gli orari; l’intestazione resta soltanto nel riepilogo breve. Schermata controllata.

## Punto di avanzamento — eliminazione della conclusione ripetuta senza orario, 14 ottobre 2026

- Base remota verificata `b1fe9856a2c41613951331d14333ec04546aa284`, branch `refactor-tanatology-keys`. Su richiesta dell’utente, quando la stima usa un solo parametro e non dispone di data e ora complete, la conclusione «La valutazione dei dati disponibili…» viene omessa dalle descrizioni dettagliate. Resta il paragrafo del metodo, per esempio «Applicando l’equazione di Henssge…».
- Conservate la conclusione con date e orari, quella integrata per più parametri e la descrizione breve. Modifica limitata alla visualizzazione del paragrafo conclusivo, senza variazioni ai calcoli.
- Aggiornato e superato il test di integrazione esistente: solo raffreddamento, raffreddamento e ipostasi, sole ipostasi, ciascuno con e senza orario. Verificata l’assenza della ripetizione e la permanenza della frase di Henssge. Diff controllato.
- Ulteriore richiesta dell’utente: nelle conclusioni basate su più parametri, «La valutazione complessiva dei dati tanatologici» diventa «La valutazione combinata dei dati tanatologici». Allineate anche le varianti per rilievi eseguiti in orari differenti e le aspettative dei test esistenti. Superati complessivamente 11 test sui testi temporali e sull’integrazione dei parametri.
- Ultima dicitura richiesta: «Range dei fattori di correzione stimati», estesa nei riepiloghi Python e JavaScript. Aggiornate le aspettative dei test esistenti; ulteriori 22 test Python testuali e sugli scenari, suite JavaScript e diff superati.

## Punto di avanzamento — rimozione della sottopagina Raccomandazioni, 14 ottobre 2026

- Base remota verificata `1e5b17648e6abfd78c6d461b4886de1e09aa96f3`, branch `refactor-tanatology-keys`. Su richiesta dell’utente eliminata `pages/Raccomandazioni.py`, con rimozione della corrispondente voce dalla navigazione automatica di Streamlit. La pagina ripeteva indicazioni già disponibili negli helper e nelle reference.
- Nessun collegamento applicativo residuo alla pagina. Gli helper contestuali rimangono disponibili. Aggiornato il test esistente sulle sottopagine ausiliarie; apertura e ritorno dalla pagina Impostazioni e dalla pagina Reference verificati senza eccezioni. Diff controllato.


## Pannello FC compatto e coperture specifiche — 14 ottobre 2026

- Desktop: sei contatori in due righe, separando indumenti e teli/copriletti; mobile: categorie aggregate preesistenti. `counters.js` mantiene i totali del motore e i dettagli descrittivi. I vecchi salvataggi restano generici; modificare i totali su mobile elimina la suddivisione non più ricostruibile.
- Due opzioni indipendenti, disponibili anche su mobile: mantellina termica come una coperta spessa (FC di riferimento 1.8, con tutte le regole preesistenti), sacco mortuario come un telo pesante per convenzione operativa richiesta dall’utente. Il contributo è aggiunto una sola volta nella costruzione dei dati di calcolo, senza modificare i contatori visibili o i totali salvati. L’immersione ignora le coperture. Non attribuire al sacco un FC sperimentalmente validato.
- Descrizioni: indumenti leggeri/pesanti/di diverso spessore; teli sottili/spessi; coperte spesse/molto pesanti. Le opzioni sono nominate esplicitamente senza descriverle anche come teli o coperte. Le condizioni confluiscono nel riepilogo e nel testo finale. La casistica ordinaria non viene abbinata automaticamente alle coperture assimilate.
- B56 usa FC 1.29 del capitolo, mantenendo distinto l’ottimale 1.0 del 1981; B33 usa 2.16, mantenendo distinto 2.4. B33 richiede appoggio su materasso/tappeto spesso e coperture consistenti; un solo copriletto non lo attiva. Le analogie non sono equivalenze sperimentali.
- Il formato di salvataggio accetta i dettagli dei contatori, le due opzioni e `initialScenarioTemperatures`, già prodotto dall’editor degli scenari. I decimali nei testi italiani e negli esempi selezionati usano il punto.

## Punto di avanzamento — nota Più scenari, 14 ottobre 2026

- Repository `scopusjin/codice`, branch dell’app di test `refactor-tanatology-keys`; base remota verificata `72eb290b96af5bd0796e71521d3102236bee398f`. Commit dell’intervento: quello contenente questa voce.
- Su autorizzazione esplicita dell’utente, spostato in `app/fc_panel_frontend/index.html` il paragrafo `scenario-duration-note` da «Come viene consigliato il FC» a subito dopo la barra «Più scenari», prima dell’editor. Testo integralmente conservato. La funzione `render()` di `scenarios.js` conserva la visibilità condizionata alla modalità multipla; nessuna modifica a JavaScript, CSS, calcoli o stato.
- Superati `node tests/test_fc_scenarios.cjs` e `node tests/test_fc_panel_ui.cjs`; diff controllato. Ultima verifica online documentata precedente: `37cb5d09919e340c3144020e7974ba33d4a15f4d` (altra funzione); nessuna nuova conferma visiva dell’utente acquisita per questo intervento.
- Prossimo passo: test manuale nell’app, attivando «Più scenari» e verificando la nota sotto i comandi e la sua assenza nel pannello delle fonti. Nessun tentativo fallito per questo spostamento. Le altre richieste grafiche restano separate.
## Punto di avanzamento FC — layout raffreddamento, 14 ottobre 2026

Repository: `scopusjin/codice`; ramo di destinazione: `refactor-tanatology-keys`.
Base GitHub verificata: `72eb290b96af5bd0796e71521d3102236bee398f`.
Commit dell'intervento: quello che introduce questa sezione (vedere `git log`).

- Corretto il tentativo di uniformare i campi introdotto da `c9b5e382`: il `flex-basis` basato sulla larghezza, applicato anche nei contenitori verticali, produceva grandi spazi vuoti. Non riutilizzare quella regola per dimensionare i campi.
- Temperatura e FC usano colonne native, con larghezza coerente con rettale/ante-mortem. Gli estremi della temperatura sono affiancati su desktop; il pulsante scenari è allineato alla riga FC.
- Comando temperatura `Range?` / `Valore singolo?`, sul modello del pannello FC, che ora usa anch'esso `Range?`.
- Le temperature provenienti dagli scenari restano vincolate: range con temperature diverse, singolo valore con temperature uguali; comando manuale disabilitato. Calcoli, FC scientifico e chiavi dei dati invariati.
- File: `Stima_epoca_decesso.py`, `app/ambient_temperature.py`, `app/full_mobile_layout.py`, `app/fc_panel_frontend/index.html`; aggiornati i relativi test esistenti.
- Verifiche: sintassi/diff; 27 test cooling prima dell'aggiunta della verifica scenari, poi 13 test di pagina inclusa la nuova verifica desktop/mobile; test JavaScript dell'interfaccia FC superati.
- Test manuale utente ancora da eseguire; nessun nuovo commit dichiarato validato dall'utente. Il rendering locale nel browser non è disponibile in questa sessione; verifica visiva sul sito dopo aggiornamento.
- Prossimo passo: verifica utente di compattezza, Range e scenari a temperature uguali/diverse; nessun ulteriore intervento concordato.

Precisazione utente: con scenari a temperature diverse il comando «Valore singolo?» non viene renderizzato. Verificata la sua assenza nei test di pagina desktop/mobile. Pubblicazione inizialmente bloccata dal controllo automatico, poi autorizzata esplicitamente dall’utente.

## Punto di avanzamento — condizioni visibili solo con FC, 14 ottobre 2026

- Base GitHub verificata: `30b0e05e54bc297fc0a4c483cc7e29a202bc8fd1`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`. Commit corrente dell’intervento: quello contenente questa voce.
- Richiesta esplicita dell’utente: non mostrare le descrizioni delle condizioni prima della comparsa del FC. In `app/fc_panel_frontend/scenarios.js`, `renderConditions()`, le righe senza estremi FC numerici vengono omesse; se nessuna riga è disponibile, viene nascosto tutto il riepilogo. Gli scenari disponibili conservano il numero originale. Nessuna modifica ai calcoli o alle chiavi di stato.
- Superati i test esistenti degli scenari e del pannello, estesi al FC vuoto, alla ricomparsa del riepilogo e alla numerazione di scenari parzialmente compilati; diff controllato. Verifica visiva dell’utente ancora da eseguire; nessun tentativo fallito. Ultimo commit pubblicato precedente: `30b0e05e`; nessuna conferma manuale ricevuta.
- Integrato senza modifiche al codice concorrente sopra `d0b819f48a2d55e93136acc3532f5c3df0adefa1` (layout temperature); conservate entrambe le voci di avanzamento.
- Prossimo passo: ricaricare il pannello e verificare che «Condizioni considerate» compaia solo dopo il FC. Le modifiche al layout delle temperature restano separate.

## Punto di avanzamento — comando Range inline, 14 ottobre 2026

- Base remota `39c782d0`, ramo `refactor-tanatology-keys`, repository `scopusjin/codice`. La correzione precedente `d0b819f4` è stata verificata online: spazi vuoti eliminati e range desktop affiancato. L’utente segnala però che il comando nativo è troppo evidente e occupa una riga su mobile; questa presentazione è superata.
- `app/ambient_temperature.py`: su desktop l’azione è accanto ai campi, nella stessa riga, con dimensioni tipografiche ridotte. `Stima_epoca_decesso.py`: spazio per due campi e azione. `app/full_mobile_layout.py`: sola rifinitura del testo, senza sfondo/bordo.
- `app/decimal_number_input_v2.py`: su mobile «Range?» / «Valore singolo?» occupa lo slot azione già presente nel controllo temperatura, sempre alto 40 px. Nessuna riga aggiuntiva, nessuna nuova chiave dati. Il comando riusa il callback della modalità temperatura. Con temperature vincolate dagli scenari l’azione mobile non è renderizzata.
- Formule, intervalli di calcolo, peso e altre funzioni invariati. Il comando a valore singolo resta assente con scenari a temperature diverse.
- Superati 13 test delle pagine cooling e 7 test del componente V2, compresa la transizione della modalità dal callback inline e l’assenza dell’azione nei campi bloccati. Controllati sintassi e diff.
- Da verificare sul telefono dell’utente: leggibilità e posizione del comando inline. Nessuna ulteriore modifica concordata.

## Punto di avanzamento — testo Henssge non applicabile, 14 ottobre 2026

- Base remota verificata `267ebf72886e3278233062e476dfcaa6123210b6`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`. Commit corrente: quello contenente questa voce.
- Applicata la formulazione italiana richiesta dall’utente in `app/locales/it_ui.py`, chiave `full.henssge_not_applicable_help`, condivisa dagli helper desktop/mobile: unite fonte di calore e pavimento riscaldato; sostituito «fattore correttivo di Henssge» con «fattore di correzione». Altre voci e calcoli invariati.
- Aggiornata l’aspettativa del test esistente; otto test `test_ui_i18n.py`, compilazione e diff superati. Verifica manuale dell’helper ancora da eseguire; nessun tentativo fallito. Prossimo passo: controllo del testo nell’app dopo l’aggiornamento.

## Punto di avanzamento — Range nel pannello FC, 14 ottobre 2026

- Base remota verificata `267ebf72886e3278233062e476dfcaa6123210b6`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`.
- In `app/fc_panel_frontend/index.html`, «Range?» / «Valore singolo?» è stato spostato dalla testata alla riga dei campi. In `panel.css` è testo piccolo senza sfondo o bordo, su desktop e mobile; su touch gli incrementi restano alti 44 px e più stretti per lasciare spazio ai valori e all’azione.
- Corretto `recalc()` e il ripristino del suggerimento: quando non esiste ancora un FC suggerito si mostra un solo campo vuoto. Due estremi compaiono per scelta esplicita o per un range effettivamente disponibile. Conservati i range applicati e gli scenari.
- Motore scientifico invariato. Superate le suite JavaScript UI/scenari e motore (3385 controlli, 33600 combinazioni), inclusa la nuova verifica del FC vuoto in modalità singola. Diff controllato. Test utente su desktop/mobile ancora richiesto.

## Punto di avanzamento — etichetta temperatura mobile nel pannello FC, 14 ottobre 2026

- Base remota verificata `4c022e4c1ccf6a345f419a02e60af8c5fe19906a`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`; commit corrente: quello contenente questa voce.
- Su richiesta esplicita, `updateTemperatureLabel()` in `app/fc_panel_frontend/scenarios.js` mostra «T amb media» per il layout mobile, riconosciuto con lo stesso criterio `(pointer: coarse)` del CSS esistente. Etichetta desktop, acqua, helper, nome accessibile e calcoli invariati. La scritta si aggiorna anche al cambio del criterio responsive.
- Controllo sintattico JavaScript, suite del pannello e diff superati. Verifica visiva sul dispositivo dell’utente ancora da eseguire; nessun tentativo fallito. Prossimo passo: controllo della scritta sul mobile.

## Punto di avanzamento — campo temperatura compatto e bordo sul valore, 14 ottobre 2026

- Base remota verificata `b472bc735a3d2396071228f0d93e41cf9c8246da`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`; commit corrente: quello contenente questa voce.
- Richiesta esplicita: nel pannello FC mantenere etichetta e campo sulla stessa riga quando lo schermo lo consente, restringendo il campo; bordo ocra intorno al solo valore, esclusi −/+, su mobile e desktop.
- `app/fc_panel_frontend/panel.css`: campo temperatura da 80 a 60 px, spazio tra etichetta e controllo da 10 a 6 px; il gruppo etichetta/helper mantiene la propria larghezza naturale. La riga flex può andare a capo quando manca spazio. Rimosso il bordo simulato del gruppo e applicato il colore ocra al bordo del solo input. Pulsanti, helper, dati e calcoli invariati; modificate le regole esistenti senza aggiungere override.
- Suite del pannello e diff superati. Verifica visiva locale tentata ma non eseguibile: runtime Playwright presente senza browser Chromium installato. Non è un tentativo di layout fallito; l’esito grafico resta da verificare sul dispositivo dell’utente. Prossimo passo: controllo mobile/desktop, compresi valori negativi e decimali.

## Punto di avanzamento — correzione Range desktop, 14 ottobre 2026

- Base remota verificata `b472bc73`, branch `refactor-tanatology-keys`. Lo screenshot dell’utente mostra ancora Range con bordo azzurro e pulsante tagliato: la regola generale `div.stButton > button` prevaleva sulla precedente regola inline.
- Esclusa l’azione della temperatura dallo stile generale dei pulsanti; spostata la sua tipografia nel foglio desktop caricato a ogni render, con selettore specifico. Range rimane testo piccolo accanto ai campi, senza bordo né sfondo; conservato il focus da tastiera. Mobile e pannello FC conservano le proprie azioni inline.
- Superati i 13 test di regressione della schermata raffreddamento e il controllo diff. Nessuna modifica ai calcoli o alla regola che nasconde Valore singolo per scenari con temperature diverse. Verifica visiva dopo aggiornamento ancora da completare.

## Punto di avanzamento — range nell’helper temperatura, 14 ottobre 2026

- Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base remota verificata `b0e9135aafffd82312fe5c76d02a7c5e1e9ec5b9`. Commit corrente: quello contenente questa voce.
- Aggiunta richiesta dall’utente: «In caso di dubbi, è possibile indicare un range: quanto più è ampio, tanto più ampio sarà l’intervallo temporale stimato.» Testo allineato in `app/locales/it_ui.py` (helper e label temperatura), `app/decimal_number_input_v2.py` (helper del componente) e `app/fc_panel_frontend/counters.js` (pannello FC). Nessuna modifica ai calcoli o al comportamento dei range.
- Aggiornato il test testuale esistente. Otto test i18n, suite JavaScript del pannello, compilazione Python, controllo sintattico JavaScript e diff superati. Verifica visiva dell’helper ancora da eseguire; nessun tentativo fallito. Prossimo passo: controllo del testo dopo l’aggiornamento.
## Punto di avanzamento — comandi Range indipendenti per temperatura e FC, 14 ottobre 2026

- Base remota `b0e9135a`, branch `refactor-tanatology-keys`. Richiesta confermata: ogni parametro deve avere il proprio comando Range/Valore singolo, senza cambiare la modalità dell’altro.
- Aggiunto `app/fc_input_mode.py`: modalità FC separata dalla modalità cautelativa interna, renderer condiviso mobile/desktop e sincronizzazione degli estremi per il calcolo esistente. Aprire il range termico conserva il FC singolo. Chiudere il range FC mantiene il primo valore e aggiorna la scelta manuale; il range termico rimane invariato. Gli scenari determinano la presentazione FC e nascondono il comando manuale; resta il vincolo preesistente sulle temperature degli scenari.
- Il comando FC usa la stessa scritta discreta del comando termico: accanto ai campi su desktop, nello slot inline del controllo mobile. Lo stato viene conservato nel file caso, nella navigazione e nel pannello FC. Nessuna modifica alle formule scientifiche.
- Superati 15 test della schermata raffreddamento, 8 del controllo mobile, 6 della selezione FC e 7 del file caso; incluse sequenze alternate di apertura/chiusura, verifica dei limiti numerici e blocco multi-scenario. Diff controllato. Prossimo passo: verifica visiva dopo aggiornamento e controllo dell’utente sul dispositivo.

- Verifica aggiuntiva: 21 controlli di integrazione del pannello FC superati dopo aver escluso i pulsanti transitori dal ripristino del form. Aggiornati i test che presumevano ancora il legame tra i due range o l’apertura del pannello dai campi temperatura ora bloccati. Preservato l’aggiornamento remoto `752243d9` delle spiegazioni sulla temperatura.

## Punto di avanzamento — spaziatura minimo/massimo nel pannello FC, 14 ottobre 2026

- Base remota verificata `005acb8183ce0c99158e751e189b195c12389434`, repository `scopusjin/codice`, branch `refactor-tanatology-keys`; commit corrente: quello contenente questa voce.
- Esaminata l’immagine allegata: campi del range eccessivamente larghi e «max» vicino al campo precedente. In `app/fc_panel_frontend/panel.css` e `scenarios.css`, limitata a 144 px la larghezza dei gruppi min/max, con 14 px tra gruppi e 5 px tra etichetta e campo; colonna delle etichette uniforme a 24 px. Su contenitori fino a 400 px, etichette sopra i campi del range per preservare spazio al valore. Sostituite le regole esistenti; calcoli e controlli invariati.
- Suite del pannello e diff superati. Controllo visivo sul dispositivo dell’utente ancora da eseguire; browser locale non disponibile come documentato nel precedente intervento. Nessun nuovo tentativo fallito. Prossimo passo: verificare la separazione di «max» e la leggibilità dei campi.

## Punto di avanzamento — Range FC solo nel pannello, 14 ottobre 2026

- Base remota verificata `841d035b`, branch `refactor-tanatology-keys`. Su richiesta dell’utente rimosso il comando Range/Valore singolo del FC dalla schermata principale, sia desktop sia mobile, insieme al callback ora inutilizzato e ai relativi selettori CSS.
- Conservata la modalità FC indipendente: il comando Range della temperatura modifica solo i campi termici. Il FC si modifica aprendo il pannello dal suo campo; i comandi Range del pannello e i vincoli degli scenari restano invariati.
- Verifiche mirate: schermata raffreddamento e controllo mobile, inclusa assenza del comando FC e conservazione di FC singolo/range durante apertura e chiusura del range termico. Diff controllato; nessuna modifica ai calcoli. Prossimo passo: verifica utente dopo ricaricamento.

## Punto di avanzamento — helper Più scenari, 14 ottobre 2026

- Repository `scopusjin/codice`, branch `refactor-tanatology-keys`; base remota verificata `e25ef55ed4eba904ec4246a1371edbd214d27828`, inclusa la rimozione concorrente del comando FC nella schermata principale. Commit corrente: quello contenente questa voce.
- Su richiesta esplicita, testo completo e invariato della spiegazione «Da usare se il corpo…» spostato dal paragrafo fisso al pulsante «?» accanto a «Più scenari». `index.html` raggruppa selettore e helper; `counters.js` riutilizza il costruttore dei popover già usato per temperatura e coperture; `panel.css` condivide lo stile dell’ancoraggio. Rimossi paragrafo, regola CSS e comando di visibilità precedenti da `scenarios.css` e `scenarios.js`. Helper disponibile anche a modalità multipla disattivata. Nessuna variazione a testo, calcoli o dati.
- Controlli sintattici JS, suite del pannello e diff superati. Verifica manuale dell’apertura/chiusura sul dispositivo ancora da eseguire; browser locale non disponibile. Nessun tentativo fallito. Prossimo passo: controllo del nuovo «?» desktop/mobile.

## Punto di avanzamento — allineamento verticale del pulsante scenari, 14 ottobre 2026

- Base remota `140bf45b`, branch `refactor-tanatology-keys`. Su richiesta dell’utente il pulsante «Specifica più scenari» è centrato verticalmente a destra del gruppo temperatura ambientale/FC, anziché allineato alla sola riga FC.
- Riunite le due righe nella medesima colonna desktop, conservando il rapporto 3:1, la larghezza dei campi e il relativo helper. Applicato sia alla visualizzazione standard sia a quella con range. Nessuna modifica a stato, calcoli o pannello FC.
- Controllo diff e regressioni della schermata raffreddamento; verifica utente dopo aggiornamento.

## Punto di avanzamento — nessuno stato del corpo preimpostato, 14 ottobre 2026

- Base remota `38a5e193`, branch `refactor-tanatology-keys`. Richiesta esplicita: nessuna selezione iniziale tra Asciutto, Bagnato e Immerso.
- Rimossi il valore JavaScript iniziale Asciutto e la selezione nel markup. Il ripristino di un pannello nuovo o di una bozza senza stato azzera la selezione, evitando di ereditare quella precedente; una scelta salvata valida viene conservata.
- In assenza di stato non viene generato un suggerimento automatico FC: compare la richiesta di specificarlo. Invariate le regole per gli stati selezionati e l’inserimento manuale FC.
- Superate suite UI e scenari, inclusa la verifica del pannello nuovo e della bozza senza stato; motore FC: 3385 controlli e 33600 combinazioni superati. Diff controllato. Prossimo passo: verifica utente all’apertura di un pannello nuovo.

## Punto di avanzamento — etichetta Cadavere sul desktop, 14 ottobre 2026

- Base remota `0396cb03`, branch `refactor-tanatology-keys`. Aggiunta la scritta «Cadavere:» prima dei pulsanti Asciutto/Bagnato/Immerso, sulla stessa riga esclusivamente nel pannello desktop, usando il criterio `data-desktop` già esistente.
- Mobile e logica di selezione invariati. Suite UI del pannello e controllo diff superati. Prossimo passo: verifica utente sul desktop.

## Punto di avanzamento — messaggio iniziale generico FC, 14 ottobre 2026

- Base remota `9905c225`, branch `refactor-tanatology-keys`. Sostituito su richiesta il messaggio che chiedeva lo stato asciutto/bagnato/immerso con: «Specificare le condizioni in cui si è trovato il cadavere per ricevere suggerimenti basati sui dati di letteratura, oppure inserire direttamente il FC.»
- Modifica esclusivamente testuale nel pannello FC. Controllata la sostituzione unica e il diff; logica invariata.

## Punto di avanzamento — voce piastrelle molto fredde, 14 ottobre 2026

- Base remota `323a9f8c`, branch `refactor-tanatology-keys`. Su richiesta sostituita la voce «Pavimento molto freddo (es. cantina)» con «Piastrelle molto fredde (es. cantina, all’esterno, …)» nel selettore Appoggio e nella tabella di riferimento. Allineata la denominazione nelle descrizioni generate e nella relativa spiegazione dell’app.
- Identificativo della superficie e valori FC invariati; modifica esclusivamente testuale. Controllo diff eseguito.

## Punto di avanzamento — leggibilità superficie metallica, 14 ottobre 2026

- Base remota `5633d588`, branch `refactor-tanatology-keys`. Lo screenshot mostra il testo del menu metallico troncato dal limite generico di 140 px. Riservati 320 px al selettore sui layout ampi; sotto 560 px etichetta e menu occupano righe separate, con menu a larghezza piena.
- Su richiesta rimossa la dicitura «o leggero»: voce «Lamiera/piano metallico sottile», con terminologia coerente nella descrizione e nella spiegazione. Nessuna modifica ai valori FC. Controllo diff e suite UI del pannello eseguiti; verifica utente dopo ricaricamento.

## Punto di avanzamento — temperatura ambientale nel solo pannello multi-scenario, 14 ottobre 2026

- Base remota `b0a0aa7c`, branch `refactor-tanatology-keys`. Nascosta la temperatura ambientale media nel pannello FC singolo; compare attivando Più scenari. Conservati valore e stato senza modificare la temperatura della schermata principale.
- In immersione resta visibile la temperatura dell’acqua, necessaria alla regola già presente per acqua prossima a zero. Verificati passaggi Asciutto/Immerso/Bagnato e attivazione Più scenari; suite UI e controllo diff superati. Nessuna modifica alle formule FC.

## Punto di avanzamento — helper temperatura dello scenario e unità acqua, 14 ottobre 2026

- Base remota `a187c9c7`, branch `refactor-tanatology-keys`. L’helper del pannello chiede la temperatura ambientale media dello scenario considerato, riferita al periodo nelle condizioni descritte; rimosso il riferimento al range.
- In immersione il bordo ocra comprende valore e unità °C, lasciando esterni i comandi meno/più. Suite UI e controllo diff superati; da verificare visivamente nell’app dopo ricaricamento.
