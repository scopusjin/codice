"""Reviewed English wording for the remaining presentation surfaces.

Source strings are lookup keys only, never translated calculation/state values.
"""

TEXT = dict(line.split("\t", 1) for line in """
ESTIMA EPOCA DECESSO	ESTIMATE TIME SINCE DEATH
STIMA EPOCA DECESSO	ESTIMATE TIME SINCE DEATH
STIMA DELL’EPOCA DEL DECESSO	ESTIMATION OF THE TIME SINCE DEATH
Stima epoca decesso	Time since death estimation
Stima epoca decesso — MSIL	Time since death estimation — MSIL
Versione completa	Full version
Modalità sopralluogo	Scene examination
Sopralluogo	Scene examination
Impostazioni	Settings
Riferimenti	References
Tabelle di riferimento	Reference tables
Metodi e tabelle di riferimento	Methods and reference tables
← Indietro al FC	← Back to CF
← Indietro	← Back
Indietro	Back
Avanti	Next
Chiudi	Close
Annulla	Cancel
Conferma	Confirm
Salva	Save
Applica	Apply
Fatto	Done
Sì	Yes
Non valutata	Not assessed
Non valutate	Not assessed
Non valutabile/non attendibile	Not assessable / unreliable
Presente, in aumento	Present, increasing in intensity and extent
Si riforma dopo essere stata vinta?	Does rigor re-establish after being broken?
Mostra ricomparsa della rigidità dopo mobilizzazione	Show re-establishment of rigor after manipulation
Mostra digitopressione nelle ipostasi	Show finger-pressure assessment of lividity
Se disattivata, la sottodomanda non comparirà nei pannelli delle ipostasi e non verrà considerata nel calcolo.	When disabled, this additional question is hidden and the finding is excluded from the calculation.
Specifica con quale arrotondamento vuoi che sia fornito l'output per il raffreddamento cadaverico (metodo di Henssge)	Select the rounding interval for results based on postmortem body cooling (Henssge method)
Impostato a	Set to
Archivio completo dei casi FC — Google Drive	Complete CF case archive — Google Drive
Caso	Case
Scarica caso	Download case
Apri caso	Open case
Sigla / numero del caso	Case identifier / number
Es. x26-05 oppure IL26-10	e.g. x26-05 or IL26-10
Esegui la stima per includere anche le valutazioni.	Run the estimation to include the assessment.
Caso caricato. I risultati saranno ricalcolati con Procedi con la stima.	Case loaded. Select Estimate time since death to recalculate the results.
File salvato con una versione diversa dell’app: verificare la stima ricalcolata.	This file was saved with a different app version: check the recalculated estimate.
File del caso non valido. Dimensione massima: 1 MB.	Invalid case file. Maximum size: 1 MB.
File del caso non valido.	Invalid case file.
Dimensione massima: 1 MB.	Maximum size: 1 MB.
File non valido o non leggibile.	Invalid or unreadable file.
Scarica riepilogo per Word	Download summary for Word
Esegui la stima con i dati attuali per scaricare il riepilogo per Word.	Run the estimation using the current data to download the summary for Word.
Salva il file nella stessa cartella del documento Word, senza cambiarne il nome. Poi torna alla finestrella in Word e premi Fatto.	Save the file in the same folder as the Word document, keeping its filename. Then return to the dialog in Word and select Done.
Impossibile preparare il file per Word:	Unable to prepare the file for Word:
Specifica più scenari	Specify multiple scenarios
Gestisci scenari	Manage scenarios
Quando usare più scenari	When to use multiple scenarios
Da usare se il corpo si è trovato, o potrebbe ragionevolmente essersi trovato, in condizioni diverse. L’app considera le condizioni più favorevoli e più sfavorevoli al raffreddamento e fornisce un intervallo di stima che comprende entrambe.	Use this when the body was, or could reasonably have been, exposed to different conditions. The app considers the conditions most and least conducive to cooling and provides an estimated interval encompassing both.
Variazioni di breve durata delle condizioni del corpo possono ragionevolmente essere trascurate.	Brief changes in the conditions affecting the body may reasonably be disregarded.
Compila scenari	Complete scenarios
Scenario	Scenario
scenari	scenarios
scenario	scenario
Aggiungi scenario	Add scenario
Elimina scenario	Delete scenario
Rimuovi scenario	Remove scenario
Specificare la temperatura.	Specify the temperature.
Valore singolo?	Single value?
Temperature ricavate dai singoli scenari; modificale nel pannello FC.	Temperatures are taken from the individual scenarios; edit them in the CF panel.
Inserisci il valore minimo e massimo plausibili della temperatura ambientale media nel periodo tra il decesso e l’ispezione.	Enter the lowest and highest plausible mean ambient temperatures between death and examination.
Clicca su un campo FC per aprire il pannello che suggerisce il fattore di correzione in base alle condizioni del corpo e ai dati della letteratura.	Select a CF field to open the panel suggesting a corrective factor based on the conditions of the body and published data.
Fattore di correzione (FC)	Corrective factor (CF)
Fattore minimo	Minimum factor
Fattore massimo	Maximum factor
FC minimo	Minimum CF
FC massimo	Maximum CF
FC adattato per il peso	CF adjusted for body weight
FC adattato al peso	CF adjusted for body weight
FC di base	Base CF
Consiglia FC	Suggest CF
Suggerisci FC	Suggest CF
Usa questo FC	Use this CF
Usa questi valori	Use these values
Usa valori	Use values
Come viene consigliato il FC	How the CF is suggested
Origine del fattore di correzione	Basis of the corrective factor
T. ambientale media	Mean ambient temperature
T. ambientale	Ambient temperature
T. amb. media	Mean ambient T.
T. amb.	Ambient T.
T. rettale	Rectal temperature
T. ante-mortem stimata	Estimated antemortem temperature
T. ante-mortem	Antemortem temperature
Temperatura ambientale media	Mean ambient temperature
Temperatura dell’acqua	Water temperature
Temperatura dell'acqua	Water temperature
Peso corporeo	Body weight
Peso stimato	Estimated weight
Peso	Weight
Valore numerico	Numeric value
Data	Date
Orario	Time
Ora	Time
ore	hours
ora	hour
minuti	minutes
minuto	minute
Rilievi	Observations
Raffreddamento	Body cooling
Ipostasi	Lividity
Macchie ipostatiche	Postmortem lividity
Rigidità cadaverica	Rigor mortis
Rigidità	Rigor mortis
Parametri aggiuntivi	Additional findings
Descrizioni dettagliate	Detailed descriptions
Copia testo	Copy text
Copia	Copy
Copiato!	Copied!
Per la stima del raffreddamento:	For the body-cooling estimate:
per la stima del raffreddamento:	for the body-cooling estimate:
tutte le temperature (rettale, ambientale e ante-mortem)	all temperatures (rectal, ambient and antemortem)
uno dei due valori del fattore di correzione	one of the two corrective-factor values
uno dei due valori di temperatura ambientale	one of the two ambient-temperature values
la temperatura rettale	the rectal temperature
la temperatura ambientale	the ambient temperature
la temperatura ante-mortem	the antemortem temperature
il peso corporeo	the body weight
il fattore di correzione	the corrective factor
Mancano	Missing:
Manca	Missing:
mancano	missing:
manca	missing:
Inserire un peso valido, maggiore di zero.	Enter a valid body weight greater than zero.
Con peso stimato ±3 kg, anche il peso minimo deve essere maggiore di zero.	With an estimated weight of ±3 kg, the minimum weight must also be greater than zero.
Asciutto	Dry
Bagnato	Wet
Immerso	Immersed
Indumenti e coperture	Clothing and coverings
Vestiti e coperture	Clothing and coverings
Vestiti/teli	Clothing / sheets
Indumenti leggeri	Light clothing
Indumenti pesanti	Heavy clothing
Copriletti / coperte leggere	Bedspreads / light blankets
Coperte spesse	Thick blankets
Molto pesanti / piumoni	Very heavy / duvets
Piumoni	Duvets
Coperte	Blankets
Teli	Sheets
Leggeri	Light
Pesanti	Heavy
Sottili	Thin
Spessi	Thick
Spesse	Thick
Sono presenti uno o più indumenti particolarmente isolanti, come capi imbottiti, molto spessi o pesantemente foderati?	Are there any highly insulating garments, such as padded, very thick or heavily lined clothing?
Quanto sono bagnati i tessuti sul corpo?	How wet are the fabrics on the body?
Da precisare	Please specify
Fradici	Wet through
Solo in parte bagnati	Partially wet
Piumone imbottito molto voluminoso e avvolgente?	Very bulky, enveloping padded duvet?
Le coperture formano uno strato molto voluminoso?	Do the coverings form a very bulky layer?
Mantellina termica	Thermal foil blanket
Sacco mortuario	Body bag
Coperture aggiuntive	Additional coverings
Appoggio	Supporting surface
Pavimento	Floor
Piano di legno	Wooden base
Asfalto / terreno / prato	Asphalt / soil / grass
Materasso / tappeto spesso	Mattress / thick carpet
Supporto molto imbottito e avvolgente (es. divano, cuscini)	Thick, enveloping padding (e.g. sofa, cushions)
Cemento / pietra	Concrete / stone
Piastrelle molto fredde (es. cantina, all’esterno, …)	Very cold tiles (e.g. cellar, outdoors, …)
Pavimento rivestito in PVC	PVC-covered floor
Piano/lastra metallica	Metal base / sheet
Condizione delle foglie	Condition of the leaves
Il corpo era anche coperto dalle foglie?	Was the body also covered by leaves?
Foglie	Leaves
Bagnate	Wet
Umide	Damp
Secche	Dry
Tipo di superficie metallica	Type of metal surface
Lamiera/piano metallico sottile	Thin metal sheet / base
Piano metallico molto spesso	Very thick metal base
Appoggio abbondantemente impregnato di liquidi?	Is the supporting material thoroughly soaked?
Aria	Air
Nessuna corrente	Still air
Movimento continuo sul corpo	Continuous air movement over the body
Movimento intermittente	Intermittent air movement
Pantaloni e slip fradici, pioggia, su strada o terreno	Wet-through trousers and briefs, rain, on a road or the ground
Condizioni considerate:	Conditions considered:
Condizioni considerate	Conditions considered
Apri le tabelle di riferimento →	Open the reference tables →
Esempi di teli	Examples of sheets
Lenzuola, asciugamani sottili.	Bedsheets, thin towels.
Esempi di piumoni e coperte molto pesanti	Examples of duvets and very heavy blankets
Piumoni o coperte molto pesanti, spesse o imbottite.	Duvets or very heavy, thick or padded blankets.
Quando considerare le correnti d’aria	When to consider air movement
Considerare le correnti d’aria se interessano effettivamente il corpo per un periodo rilevante. Una finestra aperta o una corrente occasionale nell’ambiente non bastano.	Consider air movement when it actually affects the body for a substantial period. An open window or an occasional draught in the room is not sufficient.
Indicare la temperatura ambientale media dello scenario considerato, riferita al periodo in cui il corpo si è trovato, o si ipotizza possa essersi trovato, nelle condizioni descritte.	Enter the mean ambient temperature for this scenario over the period during which the body was, or may have been, exposed to the described conditions.
Completa le domande sulle coperte	Complete the questions about the blankets
Nessun suggerimento automatico	No automatic suggestion
Tabelle operative originali di Henssge	Original Henssge reference tables
Dati sperimentali citati da Henssge/Madea	Experimental data cited by Henssge/Madea
Ragionamento dell’app	Reasoning used by the app
Tabella Henssge	Henssge table
Studio sperimentale	Experimental study
Dati sperimentali	Experimental data
Riferimento sperimentale da adattare	Experimental reference requiring adjustment
Vedi dati sperimentali	See experimental data
Non direttamente tabulato	Not directly tabulated
Vedi fonte	See source
Non univoco	Not uniquely defined
Fonte	Source
Attenzione:	Note:
Per confronto:	For comparison:
tabella	table
Tabella	Table
caso sperimentale	experimental case
FC iniziale:	Initial CF:
FC scelto	Selected CF
FC centrale	Central CF
FC	CF
corpo asciutto	dry body
corpo bagnato	wet body
corpo immerso	immersed body
corpo nudo	naked body
nudo	naked
in acqua stagnante	in still water
in acqua corrente	in flowing water
acqua stagnante	still water
acqua corrente	flowing water
con uno strato di indumenti leggeri	wearing one layer of light clothing
con uno strato di indumenti pesanti	wearing one layer of heavy clothing
con pochi indumenti leggeri	wearing a few light garments
con pochi indumenti pesanti	wearing a few heavy garments
con vari strati di indumenti di diverso spessore	wearing several layers of clothing of different thicknesses
con molti strati di indumenti di diverso spessore	wearing many layers of clothing of different thicknesses
con vari strati di indumenti leggeri	wearing several layers of light clothing
con molti strati di indumenti leggeri	wearing many layers of light clothing
con vari strati di indumenti pesanti	wearing several layers of heavy clothing
con molti strati di indumenti pesanti	wearing many layers of heavy clothing
coperto con coperte di diverso spessore, tra cui un piumone molto voluminoso e avvolgente	covered with blankets of different thicknesses, including a very bulky, enveloping duvet
coperto con un piumone molto voluminoso e avvolgente	covered with a very bulky, enveloping duvet
coperto con teli e coperte di diverso spessore	covered with sheets and blankets of different thicknesses
coperto con più teli di diverso spessore	covered with several sheets of different thicknesses
sotto una coperta spessa	under a thick blanket
sotto due coperte spesse	under two thick blankets
sotto più coperte spesse	under several thick blankets
sotto una coperta molto pesante	under a very heavy blanket
sotto due coperte molto pesanti	under two very heavy blankets
sotto più coperte molto pesanti	under several very heavy blankets
coperto con un telo sottile	covered with a thin sheet
coperto con due teli sottili	covered with two thin sheets
coperto con più teli sottili	covered with several thin sheets
coperto con un telo spesso	covered with a thick sheet
coperto con due teli spessi	covered with two thick sheets
coperto con più teli spessi	covered with several thick sheets
una mantellina termica	a thermal foil blanket
un sacco mortuario	a body bag
adagiato su	lying on
superficie termicamente indifferente	a thermally indifferent base
superficie termicamente isolante	a thermally insulating base
superficie termicamente conduttiva	a thermally conductive base
piano di legno	a wooden base
pavimento in PVC	a PVC-covered floor
pavimento	a floor
piano metallico sottile	a thin metal base
piano metallico molto spesso	a very thick metal base
con copertura di foglie	covered by leaves
appoggio impregnato di liquidi	soaked supporting material
con correnti d’aria continue	with continuous air movement
con correnti d’aria intermittenti	with intermittent air movement
con correnti d’aria	with air movement
senza correnti d’aria	in still air
assenza di correnti d’aria	still air
impregnata d’acqua	wet through
impregnate d’acqua	wet through
impregnati d’acqua	wet through
umida o parzialmente bagnata	damp or partially wet
umide o parzialmente bagnate	damp or partially wet
parzialmente bagnati	partially wet
parzialmente bagnate	partially wet
parzialmente bagnata	partially wet
fradici	wet through
vestizione da precisare	clothing to be specified
coperture da precisare	coverings to be specified
un capo particolarmente isolante	one highly insulating garment
più capi particolarmente isolanti	several highly insulating garments
coperture molto voluminose	very bulky coverings
coperto con	covered with
coperto da	covered by
foglie secche	dry leaves
foglie umide	damp leaves
foglie bagnate	wet leaves
e sotto	and under
 e 	 and 
3ª ed.	3rd ed.
cap. 6.1	chapter 6.1
tab.	table
citati in	cited in
citato in	cited in
Citato in	Cited in
Dati consultati in	Data consulted in
Ripreso in	Reproduced in
Ripresa:	Reproduced in:
Per le condizioni con Qd ≤ 0.2, a titolo esclusivamente orientativo,	For conditions with Qd ≤ 0.2, for guidance only,
A titolo esclusivamente orientativo,	For guidance only,
secondo l’impostazione utilizzata da Swisswuff,	following the approach used by Swisswuff,
il tempo trascorso dal decesso al momento dei rilievi sarebbe stimabile tra	the time since death at examination would be estimated as between
il tempo trascorso dal decesso al momento dei rilievi ricadrebbe complessivamente tra	the overall time since death at examination would fall between
Tale risultato non viene utilizzato nella stima principale	This result is not used in the main estimate
; tale intervallo è da intendersi come del tutto approssimativo, essendo calcolato applicando una variazione di ±20% alla stima centrale e privo di uno specifico fondamento statistico.	; this interval is only an approximation, calculated by applying a ±20% variation to the central estimate without a specific statistical basis.
poiché, per temperature ambientali &gt;23 °C e Q ≤0.5,	because, for ambient temperatures &gt;23 °C and Q ≤0.5,
Potente et al. considerano non adeguatamente validati i limiti di confidenza dell’intervallo calcolato mediante il metodo di Henssge	Potente et al. consider the confidence limits of the interval calculated using Henssge’s method to be insufficiently validated
e propongono, in via prudenziale, di fare riferimento al solo tempo minimo trascorso dal decesso.	and recommend referring only to the minimum time since death as a conservative approach.
per le condizioni con temperatura ambientale &gt;23 °C e Q ≤0.5	for conditions with ambient temperature &gt;23 °C and Q ≤0.5
per le condizioni con Q ≤0.2, l’intervallo Swisswuff è inoltre ottenuto applicando una variazione di ±20% alla stima centrale ed è privo di uno specifico fondamento statistico.	for conditions with Q ≤0.2, the Swisswuff interval is also obtained by applying a ±20% variation to the central estimate and lacks a specific statistical basis.
Nelle condizioni considerate, il metodo di Henssge può fornire risultati sufficientemente attendibili soltanto per una parte delle possibili combinazioni dei sopracitati parametri. Per le altre, secondo il metodo proposto da Potente et al., è possibile stimare soltanto un tempo minimo trascorso dal decesso. Considerando complessivamente tali condizioni, si può stimare che, al momento dell’ispezione legale, fossero trascorse	Under the conditions considered, Henssge’s method provides sufficiently reliable results for only some combinations of the above parameters. For the other combinations, the method proposed by Potente et al. provides only a minimum time since death. Considering these conditions together, the time elapsed since death at the medico-legal examination is estimated to have been
Nel caso in esame, per le condizioni in cui il grado di raffreddamento supera i limiti di applicabilità di Henssge, il metodo di Potente indica un tempo minimo di	In this case, for conditions in which the degree of cooling exceeds the limits of applicability of Henssge’s method, Potente’s method indicates a minimum time of
prima dell’ispezione legale.	before the medico-legal examination.
più di	more than
dal decesso.	since death.
""".strip("\n").splitlines())

TEXT.update(dict(line.split("\t", 1) for line in """
Data e ora rilievi tanatologici	Date and time of postmortem observations
Informazioni	Information
Diminuisci	Decrease
Aumenta	Increase
Consiglia fattore di correzione	Suggest corrective factor
Riduci temperatura	Decrease temperature
Aumenta temperatura	Increase temperature
FC complessivo per la stima	Overall CF for the estimate
Temperature degli scenari	Scenario temperatures
Usa	Use
Più scenari	Multiple scenarios
Scenari	Scenarios
Rimuovi lo scenario selezionato	Remove the selected scenario
Condizioni del corpo	Conditions of the body
FC per la stima:	CF for the estimate:
FC dello scenario	CF for scenario
Ripristina il suggerimento per queste condizioni	Restore the suggestion for these conditions
Crea range FC	Create CF range
Usa un solo FC, mantenendo il minimo	Use a single CF, keeping the minimum
Stato del corpo	Body condition
Selezionare lo stato del corpo	Select the body condition
Cadavere:	Body:
Acqua	Water
Ferma	Still
Corrente	Flowing
T. acqua	Water temperature
T amb media	Mean ambient T.
Temperatura dell’acqua in gradi Celsius	Water temperature in degrees Celsius
Temperatura ambientale media in gradi Celsius	Mean ambient temperature in degrees Celsius
Scenari considerati:	Scenarios considered:
da completare	incomplete
Compila	Complete
selezionare le condizioni del corpo per ricevere suggerimenti o scrivere il FC.	select the conditions of the body for suggestions or enter the CF.
Fattore di correzione considerato	Corrective factor considered
Range stimato per il fattore di correzione, considerate le varie condizioni in cui potrebbe essersi trovato il corpo	Estimated range of corrective factors, considering the different conditions to which the body may have been exposed
temperatura dell’acqua	water temperature
temperatura ambientale e dell’acqua	ambient and water temperatures
corpo immerso in acqua ferma	body immersed in still water
corpo immerso in acqua corrente	body immersed in flowing water
con un indumento o telo leggero	with one light garment or sheet
con un indumento o telo pesante	with one heavy garment or sheet
con pochi indumenti o teli leggeri	with a few light garments or sheets
con pochi indumenti o teli pesanti	with a few heavy garments or sheets
con pochi indumenti o teli di diverso spessore	with a few garments or sheets of different thicknesses
con pochi indumenti di diverso spessore	wearing a few garments of different thicknesses
con vari strati di indumenti o teli leggeri	with several layers of light clothing or sheets
con vari strati di indumenti o teli pesanti	with several layers of heavy clothing or sheets
con vari strati di indumenti o teli di diverso spessore	with several layers of clothing or sheets of different thicknesses
con molti strati di indumenti o teli leggeri	with many layers of light clothing or sheets
con molti strati di indumenti o teli pesanti	with many layers of heavy clothing or sheets
con molti strati di indumenti o teli di diverso spessore	with many layers of clothing or sheets of different thicknesses
sotto più coperte di diverso spessore	under several blankets of different thicknesses
condizioni di umidità non determinabili	degree of wetness unknown
indumenti e teli completamente impregnati d’acqua	clothing and sheets wet through
indumenti e teli umidi o parzialmente bagnati	clothing and sheets damp or partially wet
condizioni di umidità di indumenti e teli non determinabili	degree of wetness of clothing and sheets unknown
coperte completamente impregnate d’acqua	blankets wet through
coperte umide o parzialmente bagnate	blankets damp or partially wet
condizioni di umidità delle coperte non determinabili	degree of wetness of blankets unknown
avvolto in un sacco mortuario	enclosed in a body bag
altre coperture da precisare	other coverings to be specified
pantaloni e slip fradici, pioggia	wet-through trousers and briefs, rain
Esempi ricavati da casistiche della letteratura scientifica con condizioni simili:	Examples from published case series with similar conditions:
Esempi sulle coperture dalla letteratura, anche per confronto: differenze di indumenti, appoggio e coperture sono segnalate quando presenti.	Published examples of coverings, including comparisons: differences in clothing, supporting surface and coverings are indicated where present.
correnti d’aria non equivalenti a quelle della prova	air movement differs from that in the experiment
numero e spessore delle coperture non precisati nella descrizione della prova	number and thickness of coverings not specified in the experimental description
numero di coperture differente	different number of coverings
la prova non documenta un piumone di piume equivalente	the experiment does not document an equivalent feather duvet
copertura non descritta come particolarmente isolante	covering not described as highly insulating
La mantellina termica è conteggiata come una coperta spessa per convenzione dell’app (FC di riferimento 1.8).	The thermal foil blanket is counted as a thick blanket by convention in the app (reference CF 1.8).
Il sacco mortuario è conteggiato come un telo pesante per convenzione dell’app.	The body bag is counted as a thick sheet by convention in the app.
Nella tabella generale di Henssge: FC 1.80 per coperte spesse e FC 2.40 per coperte spesse associate a indumenti.	In Henssge’s general table: CF 1.80 for thick blankets and CF 2.40 for thick blankets combined with clothing.
Per coperture di piume particolarmente isolanti, Henssge (1992; Madea, 2016, tabella 6.20) riporta anche FC 2.80 e 3.00.	For highly insulating feather coverings, Henssge (1992; Madea, 2016, table 6.20) also reports CF 2.80 and 3.00.
L’intervallo suggerito per la combinazione selezionata è proposto dall’app per analogia e può essere adattato dall’operatore.	The app proposes the suggested range for this combination by analogy; the examiner may adjust it.
Tabella di Henssge · strati completamente impregnati d’acqua. Senza correnti d’aria: due pesanti 1.10, più di due 1.20. Con correnti d’aria: nudo o 1–2 leggeri 0.70, almeno due pesanti 0.90.	Henssge’s table · layers wet through. In still air: two heavy layers 1.10, more than two 1.20. In moving air: naked or 1–2 light layers 0.70, at least two heavy layers 0.90.
Henssge e Brinkmann, 1984 · esperimenti senza correnti d’aria: nudo bagnato 0.75–0.77; un camice bagnato 1.00; due camici bagnati 1.10; indumento intimo contenitivo, pantaloni e tre camici bagnati 1.10–1.30.	Henssge and Brinkmann, 1984 · experiments in still air: wet naked body 0.75–0.77; one wet laboratory coat 1.00; two wet laboratory coats 1.10; supportive undergarment, trousers and three wet laboratory coats 1.10–1.30.
FC ricavato da uno studio sperimentale pubblicato, non direttamente riportato come tale nella tabella generale di Henssge.	CF derived from a published experimental study, not directly listed as such in Henssge’s general table.
Gli estremi 	The endpoints 
 corrispondono a condizioni differenti previste nella tabella di Henssge.	 correspond to different conditions listed in Henssge’s table.
In assenza di un riferimento specifico nelle tabelle di Henssge per la condizione indicata, l’app propone un intervallo compreso tra i valori previsti per condizioni differenti	In the absence of a specific reference in Henssge’s tables for this condition, the app proposes a range between the values for different conditions
 e presenta alcuni esempi di casi pubblicati in letteratura e citati da Henssge	 and presents examples of published cases cited by Henssge
. L’intervallo può essere adattato dall’operatore.	. The examiner may adjust the range.
Il valore 	The value 
 è riportato nella tabella originale di Henssge.	 is given in Henssge’s original table.
L’estensione dell’intervallo alle condizioni selezionate è una deduzione dell’app.	Extending the range to the selected conditions is a deduction made by the app.
L’intervallo suggerito deriva da una valutazione per analogia dell’app e non è direttamente tabulato per questa combinazione.	The suggested range is based on the app’s assessment by analogy and is not directly tabulated for this combination.
 nel caso sperimentale H08 (Henssge e Madea, 1988; Madea, 2016, 	 in experimental case H08 (Henssge and Madea, 1988; Madea, 2016, 
), un corpo nudo con addosso due coperte spesse, adagiato su materasso presentava FC 1.44. Il caso documenta la variabilità dell’isolamento effettivo delle coperture. Tenerne conto ed eventualmente modificare/perfezionare l’intervallo suggerito.	), a naked body covered by two thick blankets and lying on a mattress had a CF of 1.44. The case documents variability in the actual insulation of coverings. Take this into account and adjust/refine the suggested range where appropriate.
Il fattore di correzione è stato adattato al peso (FC per 70 kg = 	The corrective factor was adjusted for body weight (CF for 70 kg = 
, per il peso di 	, for a body weight of 
pratica medico-legale	forensic casework
Peso virtuale standard:	Standard virtual weight:
FC compilato manualmente	CF entered manually
, senza un suggerimento automatico disponibile per le condizioni indicate.	, with no automatic suggestion available for the stated conditions.
, diverso dal valore suggerito dall’app (	, different from the value suggested by the app (
, entro l’intervallo suggerito dall’app (	, within the range suggested by the app (
, in parte al di fuori	, partly outside
, al di fuori	, outside
 dell’intervallo suggerito dall’app (	 the range suggested by the app (
Inserire conteggi interi da 0 a 20.	Enter whole-number counts from 0 to 20.
Inserire entrambi gli estremi.	Enter both endpoints.
Inserire il FC o selezionare le condizioni del corpo.	Enter the CF or select the conditions of the body.
Minimo ≥ 0.35 e massimo ≥ minimo.	Minimum ≥ 0.35 and maximum ≥ minimum.
Passi di 0.05: arrotondamento all’uscita dal campo.	Increments of 0.05: rounded when leaving the field.
Inserire un peso tra 4 e 150 kg.	Enter a body weight between 4 and 150 kg.
FC previsto per un cadavere del peso di circa 70 kg. Se verrà inserito un peso diverso nella pagina principale, il FC o il suo range verranno adattati di conseguenza.	CF for a body weighing approximately 70 kg. If a different weight is entered on the main page, the CF or its range will be adjusted accordingly.
 Se desideri valori diversi, reinseriscili manualmente.	 To use different values, enter them manually again.
FC preimpostato, non ancora modificato.	Preset CF, not yet modified.
Valutazione manuale	Manual assessment
Non definito	Undefined
Henssge e Brinkmann, 1984 · casi 51 e 44.	Henssge and Brinkmann, 1984 · cases 51 and 44.
caso	case
""".strip("\n").splitlines()))

TEXT.update(dict(line.split("\t", 1) for line in """
Stima epoca decesso durante ispezione legale	Time since death estimation at the scene
Riferimenti bibliografici	Bibliographic references
Riferimento selezionato	Selected reference
Apri menu	Open menu
Reagiscono fronte, orbita e guancia	Forehead, orbital and cheek muscles contract
Reagiscono fronte e orbita	Forehead and orbital muscles contract
Reagiscono gli orbicolari sup. e inf.	Upper and lower orbicularis oculi contract
Reagisce: palpebra sup. intera	Contraction of the entire upper eyelid
Reagisce: < 2/3 palpebra sup.	Contraction of < 2/3 of the upper eyelid
Reagisce: < 1/3 palpebra sup.	Contraction of < 1/3 of the upper eyelid
Contrazione generalizzata dei muscoli facciali	Generalised contraction of the facial muscles
Contrazione dei muscoli peribuccali	Contraction of the perioral muscles
Reazione focale vicino agli elettrodi	Focal response near the electrodes
Nessuna contrazione muscolare	No muscle contraction
Non valutabile / non attendibile	Not assessable / unreliable
Nel caso in esame, il grado di raffreddamento corporeo, calcolabile sulla base della temperatura rettale e ambientale, ricade al di fuori dei range nei quali il metodo di Henssge consente una stima sufficientemente attendibile del tempo post-mortale; la sua applicazione porterebbe pertanto a formulare stime tendenzialmente inaffidabili.	In this case, the degree of body cooling calculated from the rectal and ambient temperatures falls outside the ranges in which Henssge’s method provides a sufficiently reliable estimate of the postmortem interval; applying it would therefore tend to yield unreliable estimates.
pubblicazione online: 6 dicembre 2023	online publication: 6 December 2023
Edizione delle pagine consultate per tabelle e casi FC; distinta da	Edition of the pages consulted for CF tables and cases; distinct from
Casi consultati nella terza edizione di Madea, tabelle 6.17 e 6.21; testo integrale originale da acquisire.	Cases consulted in the third edition of Madea, tables 6.17 and 6.21; original full text not yet obtained.
Dati sul bagnato citati in	Wet-condition data cited in
Dati sull’immersione citati in	Immersion data cited in
per gli esperimenti con indumenti e coperture	for experiments with clothing and coverings
originale non consultato	original not consulted
riferimento 90, per le prove su simulatore e piani di appoggio; tesi non consultata integralmente	reference 90, for experiments with dummies and supporting surfaces; full thesis not consulted
tabelle	tables
App · classificazione degli strati bagnati.	App · classification of wet layers.
App · coperture completamente bagnate.	App · wet-through coverings.
Henssge, 1988 · tabella dei fattori empirici.	Henssge, 1988 · table of empirical factors.
Henssge e Brinkmann, 1984 · casi 50 e 52.	Henssge and Brinkmann, 1984 · cases 50 and 52.
Aria ferma 1.00; corrente 0.75	Still air 1.00; moving air 0.75
Aria ferma 1.10; corrente 0.90	Still air 1.10; moving air 0.90
1.10, senza altri strati o coperte	1.10, without other layers or blankets
Piumone di piume su materasso.	Feather duvet on a mattress.
Precisare la superficie di appoggio.	Specify the supporting surface.
L’app assimila le foglie 	The app treats 
umide al materasso	damp leaves as equivalent to a mattress
secche a un supporto molto imbottito	dry leaves as equivalent to heavily padded support
bagnate a un appoggio neutro	wet leaves as equivalent to a thermally indifferent base
Corpo bagnato su superficie disperdente.	Wet body on a cooling-accelerating base.
Corpo bagnato su superficie isolante.	Wet body on an insulating base.
Precisare il tipo di piumone.	Specify the type of duvet.
Precisare il volume delle coperture.	Specify the bulk of the coverings.
Appoggio di foglie bagnate.	Base of wet leaves.
Precisare la condizione delle foglie.	Specify the condition of the leaves.
Corpo adagiato e coperto da foglie.	Body lying on and covered by leaves.
Con circa 2 cm di foglie 	With approximately 2 cm of 
Precisare il tipo di superficie metallica.	Specify the type of metal surface.
Precisare il movimento dell’aria.	Specify air movement.
) e in aria mobile (	) and in moving air (
Intervallo sul piano metallico molto spesso.	Range for a very thick metal base.
Copertura molto pesante.	Very heavy covering.
Coperta spessa.	Thick blanket.
Casi	Cases
Esperimento	Experiment
Simulatore	Dummy
Valore sperimentale	Experimental value
Descrizione completa:	Full description:
FC adottato dalla	CF taken from
del capitolo	in the chapter
il lavoro del 1981 riporta separatamente un FC ottimale di	the 1981 paper separately reports an optimal CF of
Il confronto con un piumone è un’analogia dell’app.	Comparison with a duvet is an analogy used by the app.
Tesi di medicina; riferimento 90 del capitolo.	MD thesis; reference 90 in the chapter.
Tesi citata nel libro; testo integrale non consultato.	Thesis cited in the book; full text not consulted.
Cap. 6.1	Chapter 6.1
""".strip("\n").splitlines()))

TEXT.update(dict(line.split("\t", 1) for line in """
Appartiene alla coppia 36/37. Il FC tiene conto sia del supporto conduttivo sia degli indumenti; è riportato un confronto investigativo.	One of the pair of cases 36/37. The CF accounts for both the conductive base and the clothing; a comparison with investigative findings is reported.
Appartiene alla coppia 46/47, esaminata nello stesso ambiente. Il FC comprende indumenti e superficie di appoggio.	One of the pair of cases 46/47, examined in the same environment. The CF includes clothing and the supporting surface.
Appartiene alla coppia 6/7. L’indagine non consente di verificare i tempi di morte: non è una validazione rispetto a un tempo noto.	One of the pair of cases 6/7. The investigation does not establish the times of death: this is not validation against a known time.
Appartiene alla coppia 70/71. Il tempo del decesso dell’uomo non è chiarito con precisione; il FC considera il contatto esteso con l’imbottitura.	One of the pair of cases 70/71. The man’s time of death is not precisely established; the CF accounts for extensive contact with the padding.
Appartiene alla coppia 70/71. Per questo caso il tempo del decesso è ricostruito dall’indagine, diversamente dal caso 70.	One of the pair of cases 70/71. In this case, unlike case 70, the time of death was reconstructed from the investigation.
FC 1.77 contrassegnato da asterisco nella fonte per la possibile influenza dell’umidità residua delle foglie.	CF 1.77 is marked with an asterisk in the source because of the possible influence of residual moisture in the leaves.
FC adattato per il peso; tempo del decesso non verificato dall’indagine.	CF adjusted for body weight; time of death not verified by the investigation.
FC ipotetico, con punto interrogativo nella fonte. Per la fase sul terreno è riportato 0.90–1.10. Il metodo termico non è utilizzato per mancanza di esperienza sulle condizioni specifiche.	Hypothetical CF, marked with a question mark in the source. A range of 0.90–1.10 is reported for the period on the ground. The temperature-based method was not used because of a lack of experience with these specific conditions.
FC sperimentale dell’insieme delle condizioni descritte, riferito al peso della prova; non è un incremento da sommare per singolo indumento.	Experimental CF for the combined conditions described, at the weight used in the experiment; it is not an increment to be added for each garment.
Gli autori attribuiscono al sacco un effetto isolante. Il range è una scelta nel caso concreto, non una misura sperimentale di quel supporto.	The authors attribute an insulating effect to the sack. The range was selected for this particular case; it is not an experimental measurement of that supporting material.
Gli autori dichiarano il range ipotizzato per mancanza di esperienza sul pannolino. Il solo limite superiore 1.70 viene adattato a 2.20 per il basso peso; non è un coefficiente sperimentale del pannolino.	The authors state that the range was assumed because of a lack of experience with the nappy. Only the upper limit of 1.70 was adjusted to 2.20 for the low body weight; this is not an experimental coefficient for the nappy.
Gli investigatori chiudono la finestra un’ora prima dell’esame e rilevano 18,5 °C. La storia della ventilazione è parte del caso.	Investigators closed the window one hour before examination and recorded 18.5 °C. The history of ventilation is part of the case.
Il contatto con seduta e schienale contribuisce all’isolamento. È considerata anche la temperatura rilevata dagli investigatori due ore prima dell’esame.	Contact with the seat and backrest contributes to insulation. The temperature recorded by investigators two hours before examination is also considered.
Il materasso è già compreso nella prova; il FC non misura l’effetto della sola coperta.	The mattress is already included in the experiment; the CF does not measure the effect of the blanket alone.
Il range comprende l’effetto delle condizioni della scena. È riportato un confronto con i tempi ricostruiti dall’indagine.	The range includes the effect of conditions at the scene. A comparison with times reconstructed from the investigation is reported.
Il valore riguarda l’insieme delle condizioni, compresa la ventilazione intermittente; non misura il solo effetto del pigiama.	The value concerns the combined conditions, including intermittent ventilation; it does not measure the effect of the pyjamas alone.
La finestra viene chiusa dopo il rinvenimento, riaperta per circa 30 minuti e nuovamente chiusa. Non è un esempio di condizioni ambientali costanti.	The window was closed after discovery, reopened for approximately 30 minutes and closed again. This is not an example of constant environmental conditions.
La fonte adatta il range al peso elevato. La rimozione della copertura prima della misurazione è una condizione essenziale del caso.	The source adjusts the range for the high body weight. Removal of the covering before measurement is an essential condition of the case.
La fonte descrive l’appoggio come «metal road»: la formulazione non basta a identificarlo come lastra metallica. La stima tiene conto della temperatura minima della notte precedente.	The source describes the supporting surface as “metal road”: this wording is insufficient to identify it as a metal sheet. The estimate accounts for the minimum temperature on the previous night.
La fonte riporta solo il limite inferiore del tempo ricostruito dall’indagine. Il confronto investigativo è quindi incompleto.	The source reports only the lower limit of the time interval reconstructed from the investigation. Comparison with investigative findings is therefore incomplete.
La posizione cambia durante il primo intervento. Il FC e la ricostruzione termica si riferiscono al caso nel suo insieme.	The position changed during the initial response. The CF and reconstruction of thermal conditions refer to the case as a whole.
La ricostruzione comprende la temperatura della notte precedente. Il range è quello scelto nel caso; non viene ricalcolato o arrotondato dalla scheda.	The reconstruction includes the previous night’s temperature. The range is the one selected in the case; the record does not recalculate or round it.
La ricostruzione termica considera la temperatura media notturna esterna; l’esame avviene a mezzogiorno. Il valore non deriva dalla sola temperatura misurata all’esame.	The reconstruction of thermal conditions considers the mean overnight outdoor temperature; examination took place at noon. The value is not derived solely from the temperature measured during examination.
La temperatura notturna è ricostruita il giorno successivo ripetendo lo spegnimento automatico del riscaldamento. Il confronto investigativo utilizza l’arresto dell’orologio danneggiato.	The overnight temperature was reconstructed the following day by repeating the automatic heating shutdown. The investigative comparison uses the time at which the damaged watch stopped.
La temperatura precedente è ricostruita con dati meteorologici. La tabella non indica un tempo di morte accertato con cui confrontare la stima.	The preceding temperature was reconstructed from meteorological data. The table does not give an established time of death against which to compare the estimate.
La temperatura rettale scende da 33,3 a 31,2 °C in un’ora. La tabella riporta calcoli termici, ma specifica il mancato utilizzo del metodo; la stima si basa sui criteri non termici.	Rectal temperature fell from 33.3 to 31.2 °C in one hour. The table reports temperature-based calculations but specifies that the method was not used; the estimate is based on non-temperature findings.
Le misure ambientali provengono da più punti della scala e dall’esterno presso la porta aperta. Il FC comprende anche gli indumenti.	Ambient measurements were taken at several points on the staircase and outside near the open door. The CF also includes clothing.
Le temperature sono rilevate vicino al corpo, negli armadi e sotto i tappeti. Le differenze ambientali entrano nella ricostruzione delle condizioni di raffreddamento.	Temperatures were measured near the body, in cupboards and under carpets. Environmental differences are included in reconstructing the cooling conditions.
Metodo non applicato nel caso; elaborazione nell’ipotesi di ipertermia maligna, con temperatura alla morte di 43.5 °C.	Method not applied in this case; calculation assumes malignant hyperthermia with a temperature at death of 43.5 °C.
Peso virtuale di raffreddamento, non massa di un cadavere. “Parzialmente asciutte” riprende la condizione intermedia della fonte; l’app la denomina umide.	Virtual cooling weight, not the mass of a body. “Partially dry” follows the intermediate condition in the source; the app calls it damp.
Peso virtuale di raffreddamento; prova su simulatore, non su cadavere.	Virtual cooling weight; experiment with a dummy, not a body.
Peso virtuale standard medio 64,7 kg; temperatura ambiente 14–19 °C, salvo prova 260 a 6,1 °C. Non è un esperimento su cadavere.	Mean standard virtual weight 64.7 kg; ambient temperature 14–19 °C, except experiment 260 at 6.1 °C. This is not an experiment on a body.
Prova in acqua quasi ferma, distinta dall’acqua corrente. Valore individuale, non soglia universale.	Experiment in nearly still water, distinct from flowing water. Individual value, not a universal threshold.
Serie con acqua prossima a 0 °C. Il comportamento termico differisce dalle prove a circa 10 e 20 °C; conservare temperatura e peso del caso.	Series with water close to 0 °C. Thermal behaviour differs from experiments at approximately 10 and 20 °C; retain the temperature and weight of the case.
Valore sperimentale al peso della prova, in correnti continue; non descrive esposizioni intermittenti.	Experimental value at the weight used in the experiment, in continuous air movement; it does not describe intermittent exposure.
Il file non è un caso Mor-tem.	The file is not a Mor-tem case.
Versione del file non supportata. Nessun dato è stato modificato.	Unsupported file version. No data have been changed.
Il caso supera la dimensione massima di 1 MB.	The case exceeds the maximum size of 1 MB.
Dimensione massima del file: 1 MB.	Maximum file size: 1 MB.
Il file contiene campi duplicati.	The file contains duplicate fields.
""".strip("\n").splitlines()))

TEXT.update(dict(line.split("\t", 1) for line in """
Aggiorna gli estremi di calcolo senza modificare i campi inseriti.	Update the calculation bounds without changing the entered fields.
Numero X non valido.	Invalid X number.
Codice di collegamento Word non valido.	Invalid Word connection code.
Dati inviati da Word non validi:	Invalid data received from Word:
Valore non valido:	Invalid value:
, movimento dell’aria non ricostruibile	, air movement cannot be reconstructed
Specificare la temperatura di ogni scenario.	Specify the temperature for each scenario.
Temperature modificate: aggiornare le temperature nel pannello Più scenari.	Temperatures changed: update them in the Multiple scenarios panel.
Base del FC dello scenario non coerente.	Inconsistent base CF for the scenario.
Completare minimo e massimo di	Complete the minimum and maximum for
devono essere maggiori di zero.	must be greater than zero.
uno dei due valori del	one of the two values for
La combinazione di FC e peso non consente il calcolo con questa formula. Verificare i valori.	This combination of CF and body weight cannot be calculated using this formula. Check the values.
Completare le temperature per calcolare il raffreddamento.	Complete the temperatures to calculate body cooling.
Nelle condizioni considerate, il grado di raffreddamento corporeo, calcolato sulla base della temperatura rettale e dei diversi valori di temperatura ambientale considerati, ricade in tutti i casi al di fuori dei range nei quali il metodo di Henssge consente una stima sufficientemente attendibile del tempo post-mortale; la sua applicazione porterebbe pertanto a formulare stime tendenzialmente inaffidabili.	Under the conditions considered, the degree of body cooling calculated from the rectal temperature and the different ambient temperatures falls in every case outside the ranges in which Henssge’s method provides a sufficiently reliable estimate of the postmortem interval; applying it would therefore tend to yield unreliable estimates.
Inserire un FC valido, maggiore di zero.	Enter a valid CF greater than zero.
Il metodo valuta la persistenza dell’eccitabilità muscolare elettrica residua mediante stimolazione elettrica della regione sopraciliare e classificazione dell’estensione della risposta muscolare. Posizionare gli elettrodi distanziati di circa 2 cm nella parte nasale del sopracciglio, a una profondità di circa 0.5 - 0.7 cm, e applicare uno stimolo di 30 mA · 10 ms · 50 Hz.	This method assesses the persistence of residual electrical muscle excitability by electrical stimulation of the supraciliary region and classification of the extent of the muscle response. Place the electrodes approximately 2 cm apart in the medial part of the eyebrow, at a depth of approximately 0.5–0.7 cm, and apply a stimulus of 30 mA · 10 ms · 50 Hz.
Il metodo valuta la persistenza dell’eccitabilità muscolare elettrica residua mediante stimolazione elettrica della regione peribuccale e classificazione della risposta come contrazione dei muscoli facciali, dei muscoli peribuccali, reazione focale o assenza di reazione. Posizionare gli elettrodi a circa 1 cm dagli angoli della bocca, a una profondità di circa 0.5 - 0.7 cm, e applicare uno stimolo di 30 mA · 10 ms · 50 Hz.	This method assesses the persistence of residual electrical muscle excitability by electrical stimulation of the perioral region and classification of the response as contraction of the facial muscles, contraction of the perioral muscles, a focal response or no response. Place the electrodes approximately 1 cm from the corners of the mouth, at a depth of approximately 0.5–0.7 cm, and apply a stimulus of 30 mA · 10 ms · 50 Hz.
Il metodo valuta la persistenza dell’eccitabilità muscolare meccanica residua mediante percussione del muscolo bicipite del braccio, osservando la risposta: contrazione dell’intero muscolo, tumefazione reversibile, piccola tumefazione persistente o nessuna reazione.	This method assesses the persistence of residual mechanical muscle excitability by percussion of the biceps brachii and observation of the response: contraction of the entire muscle, reversible local swelling, small persistent swelling or no response.
Il metodo valuta la persistenza dell’eccitabilità chimica dell’iride mediante iniezione di atropina, tropicamide o acetilcolina e osservazione del diametro pupillare: dilatazione, riduzione o assenza di variazione.	This method assesses the persistence of chemical excitability of the iris by injection of atropine, tropicamide or acetylcholine and observation of pupil diameter: dilatation, constriction or no change.
Raffreddamento non calcolato:	Body cooling not calculated:
Orario del rilievo	Time of observation
File del caso troppo complesso.	Case file too complex.
Data del salvataggio non valida.	Invalid save date.
Scenari del caso non validi.	Invalid case scenarios.
Data dei rilievi non valida.	Invalid observation date.
File del caso non valido. Nessun dato è stato modificato.	Invalid case file. No data have been changed.
Peso modificato: ricontrollare il FC.	Body weight changed: check the CF again.
FC non valido	Invalid CF
Inserire minimo e massimo.	Enter the minimum and maximum.
Valori non validi.	Invalid values.
Il FC deve essere espresso in passi di 0.05.	The CF must be expressed in increments of 0.05.
Specificare almeno due scenari completi.	Specify at least two complete scenarios.
Il range deve comprendere tutti gli scenari.	The range must encompass all scenarios.
Gli scenari devono usare lo stesso peso.	All scenarios must use the same body weight.
Inserire un valore numerico valido per costruire l’intervallo.	Enter a valid numeric value to construct the interval.
Specificare almeno uno scenario completo.	Specify at least one complete scenario.
Scenario non coerente con gli intervalli selezionati.	Scenario inconsistent with the selected ranges.
Intervallo FC di base non valido	Invalid base CF range
Valori non validi	Invalid values
Adattamento al peso non calcolabile	Adjustment for body weight cannot be calculated
Strati leggeri (indumenti o teli sottili)	Light layers (clothing or thin sheets)
Strati pesanti (indumenti o teli spessi)	Heavy layers (clothing or thick sheets)
""".strip("\n").splitlines()))

TEXT.update(dict(line.split("\t", 1) for line in """
Coperture completamente impregnate d’acqua.	Coverings wet through.
Combinazione da precisare.	Specify the combination.
Correggere i conteggi.	Correct the counts.
Corpo vestito appoggiato sulle foglie.	Clothed body lying on leaves.
Corpo nudo su foglie secche.	Naked body on dry leaves.
Corpo nudo su foglie umide.	Naked body on damp leaves.
Con circa 2 cm di foglie secche: FC 1.5.	With approximately 2 cm of dry leaves: CF 1.5.
Con circa 2 cm di foglie umide: FC 1.3.	With approximately 2 cm of damp leaves: CF 1.3.
Acqua stagnante prossima a 0 °C.	Still water close to 0 °C.
Immersione continua.	Continuous immersion.
Corpo nudo su piano metallico molto spesso.	Naked body on a very thick metal base.
Corpo nudo sulla superficie selezionata.	Naked body on the selected base.
corrente	flowing water
stagnante	still water
asciutto	dry
bagnato	wet
Modifica nel pannello FC	Edit in the CF panel
Informazioni sulla temperatura ambientale	Information about ambient temperature
""".strip("\n").splitlines()))

TEXT.update({
    "aria ferma": "still air",
    "aria in movimento": "moving air",
    "FC impostato manualmente negli scenari": "CF entered manually in scenarios",
    "FC impostato manualmente": "CF entered manually",
    "FC 1.10 a 69.5 kg; FC 1.30 a 65 kg.": "CF 1.10 at 69.5 kg; CF 1.30 at 65 kg.",
    "Range iniziale; nella fonte adattato a 1.80 - 2.50 per 89 kg.": "Initial range; adjusted in the source to 1.80 - 2.50 for 89 kg.",
    "; a ": "; at ",
    " e applica ": " and applies ",
    "Esperimenti": "Experiments",
})
