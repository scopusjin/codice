# Revisione dei 152 esempi FC — 29 ottobre 2026

Repository: `scopusjin/codice`; branch dell’app principale: `main`; base verificata: `ea1d5a6e04cbd9f7844990451bbcf0c3a14dfdca`.

Sono state rilette tutte le schede già trascritte nel catalogo, incluse condizioni, FC, pesi, note e riferimenti. Questa attività verifica la pertinenza dei collegamenti nell’app; non equivale a una nuova verifica integrale di tutte le immagini originali. I dati scientifici originali del JSON restano identici.

Esito: **41 collegamenti già presenti e riesaminati, 107 nuovi confronti, 4 esclusioni motivate**. Le 35 regole esplicite erano affiancate da sei schede già richiamate nel confronto sulle coperte, benché etichettate come archivio. Per questo il vecchio conteggio 35/117 non descriveva esattamente ciò che poteva già comparire nel pannello.

## Regole di presentazione

- I nuovi collegamenti sono confronti editoriali con condizioni simili o contigue, non nuove regole scientifiche né nuovi valori suggeriti di FC.
- Stato del corpo e tipo d’acqua restano distinti. Le prove in acqua quasi ferma non vengono proposte per acqua corrente; la serie prossima a 0 °C rimane separata da quella a circa 10–20 °C. Sono conservate le temperature originali delle prove, incluso 1.2 °C nella relativa serie fredda: nessuna modifica alla soglia operativa dell’app.
- Le differenze di ventilazione, indumenti, coperture, appoggio o stato delle foglie sono esplicite. I confronti aggiuntivi ammettono al massimo una dimensione sostanziale differente; l’assenza di dettagli nella fonte viene segnalata. Questo filtro organizza gli esempi e non misura una distanza termica.
- Le sei prove con foglie come appoggio compaiono senza copertura di foglie; le quattordici con copertura compaiono selezionando anche la copertura. Le diverse condizioni di umidità sono mostrate e quelle differenti vengono segnalate. Spessori della prova e natura del simulatore restano visibili.
- Cemento/pietra e piastrelle fredde richiamano i confronti pertinenti. Se il confronto usa cemento invece delle piastrelle selezionate, la differenza è indicata. Moquette, materasso, supporto avvolgente, PVC e metallo non sono trasformati in materiali equivalenti.
- Le prove su simulatori restano identificate come tali. Il caso pediatrico con pannolino è richiamato solo nel contesto di basso peso e supporto compatibile, con i limiti e l’adattamento originali; non diventa una misura dell’effetto del pannolino.
- Le note sui casi con FC ipotizzato, tempi non verificati, coperture rimosse o cambiamenti ambientali restano visibili. Anche la nota del caso 33 (metodo non applicato e ipertermia ipotizzata) viene ora conservata nella scheda visibile.
- Sei esempi rimangono immediatamente visibili; tutti gli altri pertinenti sono accessibili in “Altri esempi pertinenti”, senza esclusione dal catalogo. I riferimenti restano nella sezione delle fonti. Le nuove note sono disponibili in italiano e inglese.

## File

`data/fc_examples.json` conserva i dati originali. `data/fc_example_review.json` registra una decisione per tutti i 152 identificativi e i criteri di confronto. `app/fc_catalog.py` trasmette i metadati al pannello; `app/fc_panel_frontend/example_comparisons.js` applica soltanto i confronti documentali. L’algoritmo FC, il peso, le temperature e i dati del caso non vengono modificati.

## Registro completo

| ID | Esito | Criterio / motivazione |
|---|---|---|
| `wet-51-44` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `wet-case-15` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `wet-41` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `wet-52` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `wet-50` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `still-B63` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `still-B58` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `still-H6` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `still-B54` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `wind-H15` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `wind-H14` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `blanket-B33` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `blanket-B56` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `blanket-H08` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `case-33` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `case-6` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `case-55` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `case-22` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `case-62` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_3-28` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_7-01` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_7-10` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_7-15` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_7-16` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_8-55` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_8-47` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_10-200` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_10-230` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_10-260` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_10-290` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_11-riga-1` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_11-riga-2` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_11-riga-5` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_12-riga-1` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_12-riga-13` | Già collegato, riesaminato | Collegamento contestuale già presente, mantenuto; valori e condizioni originali conservati. |
| `t6_3-01` | Nuovo confronto | Nella prova le correnti sono continue; l’appoggio non è precisato nella scheda. |
| `t6_3-02` | Nuovo confronto | Nella prova le correnti sono continue; l’appoggio non è precisato nella scheda. |
| `t6_3-27` | Nuovo confronto | Nella prova le correnti sono continue; l’appoggio non è precisato nella scheda. |
| `t6_3-29` | Nuovo confronto | Nella prova le correnti sono continue; l’appoggio non è precisato nella scheda. |
| `t6_3-30` | Nuovo confronto | Nella prova le correnti sono continue; l’appoggio non è precisato nella scheda. |
| `t6_3-38` | Nuovo confronto | Nella prova le correnti sono continue; l’appoggio non è precisato nella scheda. |
| `t6_4-B61` | Nuovo confronto | La fonte descrive indumenti distribuiti in modo diverso sul corpo; il conteggio degli strati dell’app non ne riproduce esattamente la disposizione. |
| `t6_4-H66` | Nuovo confronto | La fonte descrive indumenti distribuiti in modo diverso sul corpo; il conteggio degli strati dell’app non ne riproduce esattamente la disposizione. |
| `t6_4-B64` | Nuovo confronto | La fonte descrive indumenti distribuiti in modo diverso sul corpo; il conteggio degli strati dell’app non ne riproduce esattamente la disposizione. |
| `t6_4-B37` | Nuovo confronto | La fonte descrive indumenti distribuiti in modo diverso sul corpo; il conteggio degli strati dell’app non ne riproduce esattamente la disposizione. |
| `t6_4-B57` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_4-H2` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_4-B53` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_4-H4` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_4-B60-a` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_4-B36` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_4-B59` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_4-B60-b` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti, non strati uniformi su tutto il corpo. |
| `t6_5-H12` | Nuovo confronto | La prova riguarda gli indumenti e le correnti continue descritti; il numero di strati è soltanto un criterio di confronto. |
| `t6_5-H11` | Nuovo confronto | La prova riguarda gli indumenti e le correnti continue descritti; il numero di strati è soltanto un criterio di confronto. |
| `t6_5-B66` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti con correnti continue. |
| `t6_5-H13` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti con correnti continue. |
| `t6_5-B67` | Nuovo confronto | La prova riguarda l’insieme degli indumenti descritti con correnti continue. |
| `t6_6-B62` | Già collegato, riesaminato | Già richiamato nel confronto sulle coperte, pur contrassegnato come archivio; criteri e limiti del confronto ora esplicitati. |
| `t6_6-B51` | Già collegato, riesaminato | Già richiamato nel confronto sulle coperte, pur contrassegnato come archivio; criteri e limiti del confronto ora esplicitati. |
| `t6_6-B52` | Già collegato, riesaminato | Già richiamato nel confronto sulle coperte, pur contrassegnato come archivio; criteri e limiti del confronto ora esplicitati. |
| `t6_6-H07` | Già collegato, riesaminato | Già richiamato nel confronto sulle coperte, pur contrassegnato come archivio; criteri e limiti del confronto ora esplicitati. |
| `t6_6-H10` | Già collegato, riesaminato | Già richiamato nel confronto sulle coperte, pur contrassegnato come archivio; criteri e limiti del confronto ora esplicitati. |
| `t6_6-H06` | Già collegato, riesaminato | Già richiamato nel confronto sulle coperte, pur contrassegnato come archivio; criteri e limiti del confronto ora esplicitati. |
| `t6_6-H09` | Nuovo confronto | Nella prova sono presenti due pannolini, non rappresentati dal conteggio ordinario degli indumenti; coperture non precisate. |
| `t6_6-senza-ID` | Solo archivio | Descrizione non ripetuta nella fonte: copertura, indumenti e soggetto non identificabili con sufficiente precisione. |
| `t6_7-20` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-21` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-22` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-24` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-25` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-27` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-28` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-30` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-02` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-03` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-04` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-05` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-08` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-11` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-12` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-13` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-14` | Nuovo confronto | Corpo nudo sospeso in acqua quasi ferma; vestiti, coperture e contatto con il fondo non sono documentati da questa prova. |
| `t6_7-06` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_7-07` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_7-09` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_7-17` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_7-18` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_7-19` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_7-23` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_7-29` | Nuovo confronto | Serie in acqua prossima a 0 °C, distinta dalle prove a circa 10–20 °C; non è una prova in acqua corrente. |
| `t6_8-42` | Nuovo confronto | Due camici completamente bagnati; non è una prova con tessuti soltanto in parte bagnati. |
| `t6_8-68` | Nuovo confronto | La prova riguarda gli indumenti bagnati descritti con correnti continue, senza coperte. |
| `t6_8-80` | Nuovo confronto | Prova notturna su prato bagnato e cielo sereno: non implica che tutti gli indumenti fossero completamente impregnati; non equivale a ogni condizione di corpo bagnato. |
| `t6_8-81` | Nuovo confronto | Prova notturna su prato bagnato e cielo sereno: non implica che tutti gli indumenti fossero completamente impregnati; non equivale a ogni condizione di corpo bagnato. |
| `t6_8-82` | Nuovo confronto | Prova notturna su prato bagnato e cielo sereno: non implica che tutti gli indumenti fossero completamente impregnati; non equivale a ogni condizione di corpo bagnato. |
| `t6_10-201` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-202` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-270` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-300` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-310` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-210` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-211` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-212` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-225` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-231` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-232` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-240` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-250` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-251` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-252` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-291` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_10-292` | Nuovo confronto | Prova su simulatore senza rivestimento isolante; il peso virtuale non è la massa di un cadavere. |
| `t6_11-riga-3` | Nuovo confronto | Simulatore su circa 2 cm di foglie; spessore e contatto del corpo reale possono differire. |
| `t6_11-riga-4` | Nuovo confronto | Simulatore su circa 2 cm di foglie; spessore e contatto del corpo reale possono differire. |
| `t6_11-riga-6` | Nuovo confronto | Simulatore su circa 2 cm di foglie; spessore e contatto del corpo reale possono differire. |
| `t6_12-riga-2` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-3` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-4` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-5` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-6` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-7` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-8` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-9` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-10` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-11` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-12` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `t6_12-riga-14` | Nuovo confronto | Simulatore su circa 2 cm di foglie e sotto circa 10 cm di foglie; la scheda non precisa lo stato delle foglie per questa singola riga. |
| `case-11` | Nuovo confronto | Caso della pratica medico-legale: il FC è scelto per l’insieme della scena, non misurato sperimentalmente. |
| `case-13` | Nuovo confronto | Caso della pratica medico-legale: pavimento non ulteriormente caratterizzato; ricostruzione ambientale specifica. |
| `case-25` | Nuovo confronto | Caso con ventilazione temporanea o cambiata nel tempo; il FC non isola l’effetto dei soli indumenti. |
| `case-26` | Nuovo confronto | Caso su scala in calcestruzzo: FC scelto considerando anche indumenti e ambiente. |
| `case-27` | Nuovo confronto | Caso della pratica medico-legale: il FC è scelto per l’insieme della scena, non misurato sperimentalmente. |
| `case-31` | Solo archivio | Resti carbonizzati e spegnimento del fuoco non rappresentati nei controlli dell’app; la fonte non usa il metodo termico. |
| `case-42` | Nuovo confronto | Caso della pratica medico-legale: pavimento non ulteriormente caratterizzato; ricostruzione ambientale specifica. |
| `case-43` | Nuovo confronto | Caso con finestre aperte e ventilazione temporanea; non è una prova in aria ferma o con correnti continue. |
| `case-44` | Nuovo confronto | Caso su moquette con porte e finestre aperte; la scheda non quantifica durata e intensità delle correnti. |
| `case-45` | Solo archivio | Permanenza in una balla di paglia e successivo spostamento non rappresentati; FC interrogativo e metodo termico non utilizzato. |
| `case-48` | Nuovo confronto | Caso con contatto esteso con seduta e schienale; il grado di avvolgimento può differire da quello del corpo reale. |
| `case-49` | Nuovo confronto | Caso con più indumenti e temperatura notturna ricostruita; non è una prova di isolamento del singolo indumento. |
| `case-54` | Nuovo confronto | Caso su divano con finestra poi chiusa; il cambiamento della ventilazione fa parte della ricostruzione. |
| `case-56` | Nuovo confronto | Caso sul letto con apertura e chiusura della finestra in tempi diversi. |
| `case-64` | Nuovo confronto | Caso all’esterno con correnti temporanee e cambiamento di posizione; FC della scena complessiva. |
| `case-66` | Nuovo confronto | Nel caso la copertura è rimossa 2.5 ore prima della misura; non equivale a una copertura mantenuta per tutto il raffreddamento. |
| `case-72` | Nuovo confronto | Caso con ventilazione temporanea o cambiata nel tempo; il FC non isola l’effetto dei soli indumenti. |
| `case-7` | Solo archivio | Corpo sospeso per impiccamento: manca nell’app una condizione senza appoggio; non assimilabile automaticamente al pavimento. |
| `case-36` | Nuovo confronto | Caso su pietra con pigiama spesso: indumenti e appoggio sono compresi insieme. |
| `case-37` | Nuovo confronto | Caso pediatrico di 14 kg, con pannolino: range ipotizzato dagli autori, non coefficiente sperimentale del pannolino. |
| `case-46` | Nuovo confronto | Caso su piastrelle in seminterrato; il tipo di ambiente è parte del confronto. |
| `case-47` | Nuovo confronto | Il supporto del caso è un secchio con sacco di polvere, non un divano: il confronto riguarda soltanto l’isolamento dell’appoggio. |
| `case-70` | Nuovo confronto | Caso con contatto esteso con seduta e schienale; il grado di avvolgimento può differire da quello del corpo reale. |
| `case-71` | Nuovo confronto | Caso su moquette, non su materasso; il FC riguarda la scena nel suo insieme. |

## Verifiche e limiti del collaudo

Passano 7 test del catalogo, 2 test della revisione e 4 test di traduzione runtime; le verifiche JavaScript controllano tutti i 107 nuovi collegamenti, i profili esistenti arricchiti, foglie, superfici, confini, esclusioni e apertura degli esempi aggiuntivi. Il confronto con il motore della base su 2'640 configurazioni restituisce risultati identici. I dati originali del catalogo sono confrontati campo per campo e restano invariati.

La suite generale della pagina FC presenta tre failure già riprodotte anche sulla base precedente (apertura/ripresa del pannello); non vengono dichiarate risolte. Non è stata effettuata una nuova verifica visuale del server né una nuova esecuzione Word. Il modulo Word già consegnato rimane invariato.
