# Punto di avanzamento FC — 19.10.2026

- Repository: scopusjin/codice.
- Branch app di test, confermata dall'utente: refactor-tanatology-keys.
- Commit di partenza verificato: 8e619f6ccf3746884e8b8e93f208d19bb63e9e4b.
- Commit corrente dell'intervento: il commit che contiene questo aggiornamento (vedere git log).
- Ultimo commit con test manuale valido: non identificato; l'utente conferma corretto il grafico della versione di partenza.

## Intervento autorizzato

Nei casi misti Henssge/Potente il dettaglio del raffreddamento usa il medesimo minimo aperto già impiegato dal grafico. Un unico paragrafo spiega l'applicabilità parziale di Henssge e il ricorso a Potente al raggiungimento della soglia critica. Il minimo di Potente compare soltanto nella nota blu, senza presentarlo come una soglia temporale di validità di Henssge. Nessuna separazione dei risultati per scenario nel testo principale.

File: app/graphing.py (aggiorna_grafico), app/textgen.py (due helper testuali), app/graphing_cooling.py (rimozione avviso misto ora inglobato nel nuovo paragrafo), tests/test_mixed_cooling_description.py.
Formule, valori FC, grafico e intersezione con gli altri dati tanatologici invariati. I casi interamente entro o fuori dai limiti conservano i testi precedenti.

## Verifica

Caso: Tr 17.1 °C, T0 37.2 °C, peso 85 kg; 11 °C / FC 0.70 e 15 °C / FC 1.20–1.40. Dettaglio: più di 16 ore e 30 minuti; nota blu Potente: 43 ore. Con ipostasi migrabili perlomeno parzialmente, la conclusione combinata conserva il massimo di 24 ore.
Controllo sintattico e diff; test integrati Streamlit del dettaglio e della conclusione combinata; 7 test di applicabilità; 30 dei 31 test textgen passano. L'unico errore textgen è preesistente e riprodotto con app/textgen.py del commit di partenza: test_potente_paragraph_keeps_current_html_and_inclusive_boundary attende una formulazione diversa da quella già presente.

## Problemi e prossimo passo

Attendere il test manuale dell'utente sull'app di test. Nessuna ulteriore modifica autorizzata.
L'ipotesi iniziale di un errore numerico (43 anziché 50.5 ore) è stata smentita dalla conferma del range 1.20–1.40 nel secondo scenario: non riproporla. L'utente ha respinto la proposta di esporre risultati separati per scenario.

## Precisazione successiva autorizzata

Base verificata: 14bd0f8e0e1c36438d0319babdbfd713d471f74a. Testo principale allineato alla formulazione Potente standard: Henssge può fornire risultati sufficientemente attendibili soltanto per una parte delle combinazioni dei sopracitati parametri. Nota blu Potente introdotta da «Nel caso in esame» e spostata dopo il paragrafo Qd. Test di regressione aggiornato per verificare anche l'ordine. Test manuale ancora da eseguire; calcoli invariati.
