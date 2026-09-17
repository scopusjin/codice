# Integrazione del pannello FC

Base: `refactor-tanatology-keys`, commit `226a2507b4be9b5a1bd63cbd331f7b4a499d813c`.
Origine: prova `fc-scelta-diretta.html`, versione 19.

## Comportamento

- «Consiglia FC» apre una vista dedicata, comune a desktop, telefono e modalità sopralluogo.
- Il componente locale conserva interfaccia e regole JavaScript della prova, senza tradurre il motore in una seconda implementazione Python.
- Peso condiviso con la stima; un peso assente non viene sostituito silenziosamente con 70 kg.
- Minimo e massimo sono modificabili. «Usalo» trasferisce esattamente il range visualizzato, già adattato al peso e arrotondato, sostituendo i suggerimenti precedenti.
- Se si applica un intervallo dalla modalità standard, si attiva la stima con intervalli; la temperatura ambientale iniziale resta un intervallo puntuale. Un intervallo ambientale già impostato rimane invariato.
- Anche la modalità sopralluogo conserva l’intervallo scelto, anziché ricostruire automaticamente ±0.10 attorno al valore centrale. Il suo campo centrale resta disponibile per l’inserimento manuale; una modifica manuale ripristina il precedente comportamento della modalità sopralluogo.
- «Indietro» conserva la bozza e gli aggiornamenti del peso senza applicare il FC. Temperature, data, ora e selezioni della stima vengono ripristinate al ritorno.
- Il collegamento «Apri le tabelle» apre la pagina già presente nell’app; il catalogo non viene duplicato nel pannello. Tornando al FC, la bozza rimane disponibile.
- Nessun limite superiore di 3 viene imposto al FC scelto.

## Controlli eseguiti

- Suite Python dell’app e test di integrazione Streamlit: passati.
- 3.369 verifiche del motore e 33.600 configurazioni complete: passate.
- Messaggi del componente, intervalli manuali, ripristino della bozza, modifica del peso, immersione e navigazione alle tabelle: verificati con un simulatore DOM.
- I test accertano coerenza con la prova e corretta integrazione; non costituiscono validazione clinica o sperimentale.

Comandi:

```sh
python -m unittest discover -s tests -v
node tests/test_fc_panel_engine.cjs
node tests/test_fc_panel_ui.cjs
```

## Prima della pubblicazione

Verificare visivamente desktop e telefono: allineamento dei contatori, assenza di tagli nel componente, spiegazioni aperte, peso e trasferimento del range. I test Streamlit non verificano il rendering effettivo nel browser.

Il catalogo comprende i 15 record documentali presenti nella prova, non l’intera casistica pubblicata. Le fonti già segnalate come incomplete rimangono indicate come tali. La formula del peso è quella concordata nella prova: il coefficiente 3.24596 proviene dalla trascrizione consultata; resta da confrontarlo visivamente con la pagina originale. L’integrazione non risolve queste verifiche bibliografiche pendenti.

La sostituzione è proposta su un ramo dedicato. Nessuna modifica a `main` e nessuna pubblicazione automatica richiesta.
