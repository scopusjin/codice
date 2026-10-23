import re
from html import escape

import streamlit as st

from app.mobile_shell import install_minimal_mobile_shell
from app.language import render_language_selector
from app.page_heading import render_page_heading
from app.page_navigation import TABLES_PAGE, record_page_visit, render_back_button


install_minimal_mobile_shell()
record_page_visit(st.session_state, TABLES_PAGE)


# All short citations lead to the internal bibliography page.
_CITATION_PATTERN = re.compile(
    r"(?:Henssge(?: et al\.| e Madea)?|Anders et al\.|Althaus et al\.|"
    r"Henriksson et al\.|Potente et al\.|Madea)(?:, in Madea)?, \d{4}|\[\d+(?:\s*[,–-]\s*\d+)*\]"
)


def _reference_link(label: str) -> str:
    # The navigation bridge uses Streamlit to preserve the current session.
    return f'<a class="mortem-reference-link" href="Reference" target="_self">{escape(label)}</a>'


def _reference_caption(text: str) -> None:
    st.caption(
        _CITATION_PATTERN.sub(lambda match: _reference_link(match.group()), text),
        unsafe_allow_html=True,
    )


def _reference_numbers_html(text: str) -> str:
    return re.sub(
        r"\[\d+(?:\s*[,–-]\s*\d+)*\]",
        lambda match: _reference_link(match.group()),
        text,
    )


_COMBINED_REFERENCE = 'Henssge et al., 2000, parte II, tab. 1.'

# Local numbering for the scientific synthesis, independent of the source bibliography.
_COMBINED_BIBLIOGRAPHY = ('[1] Henssge et al., 2000, parte II, tab. 1.', '[2] Henssge e Madea, 2004, tab. 1–2.', '[3] Henssge e Madea, in Madea, 2016, cap. 10.1, tab. 10.4 e fig. 10.7.', '[4] Anders et al., 2013.', '[5] Madea, 2016, cap. 3, tab. 3.1–3.2 e 3.5.')

_HENSSGE_BASE_REFERENCE = 'Henssge, 1988; ripreso in Henssge, in Madea, 2016, cap. 6.1, tab. 6.18.'

_HENSSGE_SPECIAL_REFERENCE = 'Henssge, 2002; ripreso in Henssge, in Madea, 2016, cap. 6.1, tab. 6.19.'

_HENSSGE_WEIGHT_REFERENCE = 'Henssge, 1992; Madea, 2016, Methods for determining time of death, tab. 10; ripreso in Henssge, in Madea, 2016, cap. 6.1, tab. 6.20.'


_COMBINED_TABLE_TEXT = {
    "it": {
        "caption": "Criteri tanatologici non basati sul raffreddamento cadaverico per il metodo combinato di Henssge",
        "intro": (
            "Rielaborazione pratica dei limiti temporali del metodo combinato "
            "di Henssge [1, 3], integrata anche con ulteriori fasi della rigidità cadaverica [2] "
            "e con dati di letteratura più recenti [4]. "
            "Tutti i tempi sono espressi in ore post-mortem."
        ),
        "parameter": "Parametro",
        "criterion": "Criterio",
        "yes": "Sì",
        "no": "No",
        "lividity": "Macchie ipostatiche",
        "lividity_beginning": "Sono già comparse?",
        "confluence": "Sono confluite?",
        "thumb_pressure": "Scompaiono completamente alla digitopressione?",
        "complete_shifting": "Sono completamente migrabili?",
        "maximum_row": "Hanno raggiunto la massima estensione e intensità?",
        "incomplete_shifting": "Sono migrabili almeno parzialmente?",
        "rigor": "Rigidità cadaverica",
        "rigor_beginning": "È già comparsa?",
        "rigor_complete": "Si è già completamente instaurata, con intensità massima e distribuzione generalizzata?",
        "reestablishment": "Ricompare dopo essere stata vinta con la mobilizzazione?",
        "rigor_persistence": "Ha iniziato a risolversi?",
        "rigor_resolution": "È completamente risolta?",
        "mechanical": "Eccitabilità muscolare meccanica",
        "whole_muscle": "La percussione provoca la contrazione dell’intero muscolo (fenomeno di Zsako)?",
        "mechanical_response": "La percussione del bicipite provoca una tumefazione locale (contrazione idiomuscolare)?",
        "eyebrow": "Eccitabilità elettrica sopraciliare",
        "supra_cheek": "La contrazione coinvolge le palpebre superiore e inferiore, la fronte e la guancia?",
        "supra_forehead": "La contrazione coinvolge le palpebre superiore e inferiore e la fronte?",
        "supra_lower_lid": "La contrazione coinvolge le palpebre superiore e inferiore?",
        "supra_whole_upper_lid": "La contrazione coinvolge tutta la palpebra superiore?",
        "supra_partial_upper_lid": "La contrazione coinvolge almeno un terzo della palpebra superiore?",
        "supra_nasal": "È presente almeno una contrazione localizzata all’angolo interno della palpebra superiore?",
        "mouth": "Eccitabilità elettrica peribuccale",
        "muscle_response": "È presente una risposta muscolare (indipendentemente dalla sua estensione) all’applicazione di uno stimolo elettrico?",
        "chemical": "Eccitabilità chimica pupillare",
        "atropin": "La pupilla si dilata dopo iniezione di atropina?",
        "tropicamide": "La pupilla si dilata dopo iniezione di tropicamide?",
        "acetylcholine": "La pupilla si restringe dopo iniezione di acetilcolina?",
        "variation_note": (
            "Tra i criteri riportati, solo i limiti dell’eccitabilità elettrica sopraciliare derivano "
            "da intervalli statistici al 95%, basati su modalità standardizzate di stimolazione e "
            "valutazione della risposta e verificati in studi successivi. Per gli altri criteri, "
            "i dati disponibili non consentono di attribuire ai limiti temporali un significato "
            "statistico altrettanto verificato: si utilizzano pertanto i limiti minimi o massimi "
            "osservati nelle casistiche di letteratura. Questi valori non costituiscono soglie "
            "biologiche assolute."
        ),
    },
    "en": {
        "caption": "Postmortem criteria not based on body cooling for Henssge’s compound method",
        "intro": (
            "Practical adaptation of the time limits in Henssge’s compound method [1, 3], "
            "also supplemented with further stages of rigor mortis [2] and more recent literature data [4]. "
            "All times are expressed in hours postmortem."
        ),
        "parameter": "Parameter",
        "criterion": "Criterion",
        "yes": "Yes",
        "no": "No",
        "lividity": "Postmortem lividity",
        "lividity_beginning": "Has lividity appeared?",
        "confluence": "Is lividity confluent?",
        "thumb_pressure": "Does lividity disappear completely under finger pressure?",
        "complete_shifting": "Can lividity shift completely?",
        "maximum_row": "Has lividity reached its maximum extent and intensity?",
        "incomplete_shifting": "Can lividity shift at least partially?",
        "rigor": "Rigor mortis",
        "rigor_beginning": "Has rigor appeared?",
        "rigor_complete": "Has rigor mortis already fully developed, with maximum intensity and generalized distribution?",
        "reestablishment": "Does rigor re-establish after being broken by mobilization?",
        "rigor_persistence": "Has rigor started to resolve?",
        "rigor_resolution": "Has rigor completely resolved?",
        "mechanical": "Mechanical muscle excitability",
        "whole_muscle": "Does percussion cause contraction of the whole muscle (Zsako’s phenomenon)?",
        "mechanical_response": "Does percussion of the biceps cause a local muscular swelling (idiomuscular contraction)?",
        "eyebrow": "Supraciliary electrical excitability",
        "supra_cheek": "Does the contraction involve the upper and lower eyelids, the forehead and the cheek?",
        "supra_forehead": "Does the contraction involve the upper and lower eyelids and the forehead?",
        "supra_lower_lid": "Does the contraction involve the upper and lower eyelids?",
        "supra_whole_upper_lid": "Does the contraction involve the entire upper eyelid?",
        "supra_partial_upper_lid": "Does the contraction involve at least one third of the upper eyelid?",
        "supra_nasal": "Is at least a localized contraction at the inner corner of the upper eyelid present?",
        "mouth": "Perioral electrical excitability",
        "muscle_response": "Is a muscular response present (regardless of its extent) following the application of an electrical stimulus?",
        "chemical": "Chemical excitability of the pupil",
        "atropin": "Does the pupil dilate after atropine injection?",
        "tropicamide": "Does the pupil dilate after tropicamide injection?",
        "acetylcholine": "Does the pupil constrict after acetylcholine injection?",
        "variation_note": (
            "Among the criteria shown, only the time limits for supraciliary electrical "
            "excitability derive from 95% statistical intervals, based on standardized stimulation "
            "and response assessment procedures and verified in subsequent studies. For the other "
            "criteria, the available data do not allow the time limits to be assigned an equally "
            "verified statistical meaning: the minimum or maximum limits observed in published "
            "case series are therefore used. These values are not absolute biological thresholds."
        ),
    },
}

_HENSSGE_BASE_TABLE_TEXT = {
    "it": {
        "caption": "FC empirico del peso corporeo",
        "dry": "Vestiti/teli e coperte asciutti",
        "in_air": "Correnti d’aria",
        "factor": "FC",
        "wet": "Vestiti/teli e coperte bagnati o corpo bagnato",
        "in_water": "In acqua",
        "naked": "Nudo",
        "moving": "Sì",
        "still": "No",
        "flowing": "Corrente",
        "water_still": "Ferma",
        "thin_1_2": "1–2 strati leggeri",
        "thicker_2_plus": "2 o più strati spessi",
        "more_than_2_thicker": "Più di 2 strati spessi",
        "thicker_2": "2 strati spessi",
        "thin_2_3": "2–3 strati leggeri",
        "thicker_1_2": "1–2 strati spessi",
        "thin_3_4": "3–4 strati leggeri",
        "more_layers": "Più strati leggeri/spessi",
        "moving_or_still": "Indifferente",
        "without_influence": "Indifferente",
        "thick_bedspread": "Coperte spesse",
        "clothing_combined": "+ vestiti/teli",
        "note": (
            "I valori indicati si riferiscono a corpi di peso medio (riferimento: 70 kg), "
            "in posizione distesa su una base termicamente indifferente."
        ),
        "lower_trunk": (
            "Per la scelta del FC contano solo i vestiti/teli "
            "e le coperte sul tronco inferiore."
        ),
        "thermal_foil": (
            "Assunzione degli autori dell’app: mantellina termica assimilata a una coperta spessa (riferimento Henssge: FC 1.8). Henriksson et al., 2009 hanno studiato l’isolamento su manichino, senza attribuire un FC cadaverico alla mantellina."
        ),
        "body_bag": "Un sacco mortuario in plastica semplice in questa app viene assimilato per analogia a un telo pesante. Lo studio su manichino di Henriksson et al., 2009 documenta l’effetto isolante di un telo plastico. L’assimilazione proposta è una valutazione degli autori dell’app, non essendo stati individuati in letteratura dati sufficientemente affidabili per attribuire un FC specifico al sacco mortuario.",
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Empirical body-weight FC",
        "dry": "Dry clothes/sheets and blankets",
        "in_air": "Air currents",
        "factor": "FC",
        "wet": "Wet clothes/sheets and blankets or wet body",
        "in_water": "In water",
        "naked": "Naked",
        "moving": "Yes",
        "still": "No",
        "flowing": "Flowing",
        "water_still": "Still",
        "thin_1_2": "1–2 thin layers",
        "thicker_2_plus": "2 or more thick layers",
        "more_than_2_thicker": "More than 2 thick layers",
        "thicker_2": "2 thick layers",
        "thin_2_3": "2–3 thin layers",
        "thicker_1_2": "1–2 thick layers",
        "thin_3_4": "3–4 thin layers",
        "more_layers": "More thin/thick layers",
        "moving_or_still": "No influence",
        "without_influence": "No influence",
        "thick_bedspread": "Thick blankets",
        "clothing_combined": "+ clothes/sheets",
        "note": (
            "The listed values apply to bodies of average weight (reference: 70 kg), "
            "in an extended position on a thermally indifferent base."
        ),
        "lower_trunk": (
            "For the selection of the FC, only the clothing "
            "or covering of the lower trunk is relevant."
        ),
        "thermal_foil": (
            "Assumption by the app authors: a thermal foil blanket is treated as one thick blanket (Henssge reference: CF 1.8). Henriksson et al., 2009 studied insulation on a manikin without assigning a postmortem CF to the thermal foil blanket."
        ),
        "body_bag": "In this app, a simple plastic body bag is treated by analogy as a thick sheet. The manikin study by Henriksson et al., 2009 documents the insulating effect of a plastic sheet. This classification is an assessment by the app authors, as sufficiently reliable data to assign a specific FC to a body bag were not identified in the literature.",
        "adapted": "Adapted from",
    },
}


_HENSSGE_SPECIAL_TABLE_TEXT = {
    "it": {
        "caption": "Adattamento del FC alla superficie di appoggio",
        "ground": "Superficie di appoggio",
        "clothing": "Abbigliamento",
        "factor": "FC",
        "indifferent": "Termicamente indifferente",
        "indifferent_ground": "Pavimento di casa, prato, terreno, asfalto",
        "isolating": "Isolante",
        "heavy_padding": "Forte imbottitura",
        "mattress": "Materasso, tappeto spesso",
        "leaves": "Foglie (strato di circa 2 cm)",
        "leaves_factors": "1.0 (bagnate)<br>1.3 (umide)<br>1.5 (secche)<br>1.8–2.7 (anche copertura di circa 10 cm)",
        "leaves_reference": "Althaus et al., 2007. Prove su simulatori.",
        "naked_note": (
            "In alcune tabelle pubblicate questi valori sono preceduti da segni − o +, "
            "che possono farli interpretare come quantità da sottrarre o aggiungere al FC di base. "
            "Gli autori dell’app ipotizzano che tali segni siano refusi tipografici e interpretano "
            "pertanto i due valori come **FC complessivi**, anziché come correzioni additive o sottrattive. "
            "Questa interpretazione è coerente con alcuni esempi di casi riportati nei testi di Henssge [3], "
            "ma non costituisce una rettifica ufficiale delle fonti."
        ),
        "pvc": "Pavimento rivestito in PVC",
        "pvc_factors": "0.76–0.77",
        "metal": "Piano metallico spesso",
        "metal_factors": "0.53–0.55",
        "support_reference": (
            "Henssge, in Madea, 2016. "
            "Cap. 6.1, tab. 6.10 e paragrafo sulla scelta del fattore di correzione."
        ),
        "conducting": "Termoconduttiva",
        "concrete": "Cemento, pietra, piastrelle",
        "cold_floor": "Piastrelle molto fredde (es. cantina, all’esterno, …)",
        "yes": "Sì",
        "naked": "Nudo",
        "clothing_indifferent": "Indifferente",
        "thick": "Spesso",
        "thin": "Sottile",
        "very_thin": "Molto sottile",
        "no_adjustment": "Nessuna modifica",
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Adaptation of the FC to the supporting surface",
        "ground": "Ground under body",
        "clothing": "Clothing",
        "factor": "FC",
        "indifferent": "Indifferent",
        "indifferent_ground": "House flooring, lawn, ground, asphalt",
        "isolating": "Isolating",
        "heavy_padding": "Heavy padding",
        "mattress": "Mattress, thick carpet",
        "leaves": "Leaves (layer about 2 cm thick)",
        "leaves_factors": "1.0 (wet)<br>1.3 (partly dry)<br>1.5 (dry)<br>1.8–2.7 (also covered by about 10 cm of leaves)",
        "leaves_reference": "Althaus et al., 2007. Experiments using dummies.",
        "naked_note": (
            "In some published tables these values are preceded by − or + signs, "
            "which may lead them to be interpreted as amounts to subtract from or add to the basic FC. "
            "The app authors hypothesize that these signs are typographical errors and therefore interpret "
            "the two values as **overall FCs**, rather than additive or subtractive adjustments. "
            "This interpretation is consistent with some case examples reported in Henssge’s texts [3], "
            "but does not constitute an official correction of the sources."
        ),
        "pvc": "PVC-covered floor",
        "pvc_factors": "0.76–0.77",
        "metal": "Thick metal surface",
        "metal_factors": "0.53–0.55",
        "support_reference": (
            "Henssge, in Madea, 2016. "
            "Chapter 6.1, Table 6.10 and section on evaluating the corrective factor."
        ),
        "conducting": "Conducting heat",
        "concrete": "Concrete, stone, tiles",
        "cold_floor": "Very cold floor (e.g. cellar)",
        "yes": "Yes",
        "naked": "Naked",
        "clothing_indifferent": "Any",
        "thick": "Thick",
        "thin": "Thin",
        "very_thin": "Very thin",
        "no_adjustment": "No adjustment",
        "adapted": "Adapted from",
    },
}

_HENSSGE_WEIGHT_TABLE_TEXT = {
    "it": {
        "weight": "Peso corporeo reale (kg)",
        "cooling": "Condizioni di raffreddamento",
        "clothing": "Vestiti/teli, più strati",
        "bedspread": "Coperte spesse",
        "clothing_bedspread": "Vestiti/teli + coperte spesse",
        "feather_bed": "Coperte molto pesanti/piumone",
        "note": (
            "Per un FC inferiore a 1.4 (fino a 0.75), "
            "la dipendenza dal peso corporeo può essere trascurata."
        ),
        "adapted": "Adattato da",
    },
    "en": {
        "weight": "Real body weight (kg)",
        "cooling": "Cooling conditions",
        "clothing": "Clothes/sheets, multiple layers",
        "bedspread": "Thick blankets",
        "clothing_bedspread": "Clothes/sheets + thick blankets",
        "feather_bed": "Very heavy blankets/duvet",
        "note": (
            "For an FC below 1.4 (down to 0.75), dependence on body weight may be neglected."
        ),
        "adapted": "Adapted from",
    },
}


def _render_combined_table(language: str) -> None:
    text = _COMBINED_TABLE_TEXT[language]
    # Limiti bibliografici, indipendenti dai range del motore.
    # Ogni risposta delle domande originali diventa un reperto esplicito.
    # Le fasi sopraciliari combinano i limiti di due risposte consecutive.
    groups = (
        ("lividity", "[1, 2]", (
            ("Non ancora comparse", "Not yet apparent", "0–3"),
            ("Presenti, ma non ancora confluite", "Present, but not yet confluent", "0–4"),
            ("Confluite; migrabilità non specificata o non valutata", "Confluent; shifting unspecified or not assessed", "≥ 1"),
            ("Completamente migrabili (confluenza non specificata)", "Fully shiftable; confluence not specified", "0–6"),
            ("Confluite e completamente migrabili", "Confluent and fully shiftable", "1–6"),
            ("Parzialmente migrabili", "Partially shiftable", "4–24"),
            ("Migrabili almeno parzialmente, senza precisarne il grado", "Shiftable at least partially, degree unspecified", "0–24"),
            ("Completamente fisse", "Completely fixed", "≥ 4"),
            ("Scomparsa completa alla digitopressione", "Complete fading under finger pressure", "0–20"),
            ("Scomparsa non completa alla digitopressione", "Incomplete fading under finger pressure", "≥ 1"),
        )),
        ("rigor", "[1–4]", (
            ("Non ancora apprezzabile", "Not yet appreciable", "0–7"),
            ("Presente, in via di intensificazione e generalizzazione", "Present, developing and spreading", "0,5–20"),
            ("Presente, intensa e generalizzata", "Present, intense and generalized", "2–96"),
            ("In via di risoluzione", "Resolving", "24–192"),
            ("Completamente risolta", "Completely resolved", "≥ 24"),
            ("Si riforma dopo essere stata vinta", "Re-establishes after being broken", "≤ 19 [4]"),
        )),
        ("mechanical", "[1, 5]", (
            ("Contrazione dell’intero muscolo alla percussione", "Whole-muscle contraction following percussion", "0–2,5"),
            ("Tumefazione reversibile alla percussione", "Reversible swelling following percussion", "0–5"),
            ("Piccola tumefazione persistente alla percussione", "Small persistent swelling following percussion", "0–13"),
            ("Nessuna reazione alla percussione", "No response following percussion", "≥ 1,5"),
        )),
        ("eyebrow", "[1, 3]", (
            ("Contrazione della fronte, dell’orbita e della guancia allo stimolo elettrico", "Contraction of forehead, orbital muscles and cheek following electrical stimulation", "0–6"),
            ("Contrazione della fronte e dei muscoli attorno all’occhio allo stimolo elettrico", "Contraction of forehead and muscles around the eye following electrical stimulation", "1–7"),
            ("Contrazione delle palpebre superiore e inferiore allo stimolo elettrico", "Contraction of upper and lower eyelids following electrical stimulation", "2–8"),
            ("Contrazione dell’intera palpebra superiore allo stimolo elettrico", "Contraction of the entire upper eyelid following electrical stimulation", "3–13"),
            ("Contrazione di parte della palpebra superiore allo stimolo elettrico", "Contraction of part of the upper eyelid following electrical stimulation", "3,5–16"),
            ("Contrazione minima localizzata alla palpebra superiore allo stimolo elettrico", "Minimal contraction localized to the upper eyelid following electrical stimulation", "5–22"),
            ("Nessuna contrazione allo stimolo elettrico", "No contraction following electrical stimulation", "≥ 5"),
        )),
        ("mouth", "[1]", (
            ("Contrazione muscolare allo stimolo elettrico, indipendentemente dall’estensione", "Muscular contraction following electrical stimulation, regardless of extent", "≤ 11"),
            ("Nessuna contrazione allo stimolo elettrico", "No contraction following electrical stimulation", "≥ 3"),
        )),
        ("chemical", "[1, 5]", (
            ("Dilatazione pupillare con atropina", "Pupillary dilation after atropine", "≤ 10"),
            ("Nessuna variazione con atropina", "No change after atropine", "≥ 3"),
            ("Dilatazione pupillare con tropicamide", "Pupillary dilation after tropicamide", "≤ 30"),
            ("Nessuna variazione con tropicamide", "No change after tropicamide", "≥ 5"),
            ("Restringimento pupillare con acetilcolina", "Pupillary constriction after acetylcholine", "≤ 46"),
            ("Nessuna variazione con acetilcolina", "No change after acetylcholine", "≥ 14"),
        )),
    )
    headings = {
        "it": ("Reperto osservato", "Limite/intervallo (h)"),
        "en": ("Observed finding", "Time limit / interval (h)"),
    }
    rows = []
    for parameter, reference, findings in groups:
        rows.append(
            '<tr class="combined-section">'
            f'<th scope="rowgroup" colspan="2" class="combined-group">'
            f'{escape(text[parameter])} {_reference_link(reference)}</th></tr>'
        )
        for italian, english, interval in findings:
            finding = escape(italian if language == "it" else english)
            if finding.startswith(("Fase ", "Phase ")):
                phase, separator, detail = finding.partition(" — ")
                finding = f"<strong>{phase}</strong>{separator}{detail}"
            display_interval = interval.replace(",", ".")
            rows.append(
                f'<tr><td class="combined-criterion">{finding}</td>'
                f'<td class="combined-limit">{_reference_numbers_html(display_interval)}</td></tr>'
            )
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table combined-table">
            <colgroup><col style="width:74%"><col style="width:26%"></colgroup>
            <thead>
              <tr><th scope="col">{headings[language][0]}</th>
              <th scope="col">{headings[language][1]}</th></tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _reference_caption(text["intro"])
    _reference_caption(text["variation_note"])
    for reference in _COMBINED_BIBLIOGRAPHY:
        _reference_caption(reference)


def _render_henssge_base_table(language: str) -> None:
    text = _HENSSGE_BASE_TABLE_TEXT[language]
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table henssge-base-table">
            <thead>
              <tr>
                <th>{text['dry']}</th>
                <th>{text['in_air']}</th>
                <th>{text['factor']}</th>
                <th>{text['wet']}</th>
                <th>{text['in_air']}</th>
                <th>{text['in_water']}</th>
              </tr>
            </thead>
            <tbody>
              <tr><td></td><td></td><td>0.35</td><td>{text['naked']}</td><td></td><td>{text['flowing']}</td></tr>
              <tr><td></td><td></td><td>0.50</td><td>{text['naked']}</td><td></td><td>{text['water_still']}</td></tr>
              <tr><td></td><td></td><td>0.70</td><td>{text['naked']}</td><td>{text['moving']}</td><td></td></tr>
              <tr><td></td><td></td><td>0.70</td><td>{text['thin_1_2']}</td><td>{text['moving']}</td><td></td></tr>
              <tr><td>{text['naked']}</td><td>{text['moving']}</td><td>0.75</td><td class="fc-experimental">{text['naked']}</td><td class="fc-experimental">{text['still']}</td><td></td></tr>
              <tr><td>{text['thin_1_2']}</td><td>{text['moving']}</td><td>0.90</td><td>{text['thicker_2_plus']}</td><td>{text['moving']}</td><td></td></tr>
              <tr><td>{text['naked']}</td><td>{text['still']}</td><td>1.00</td><td></td><td></td><td></td></tr>
              <tr><td>{text['thin_1_2']}</td><td>{text['still']}</td><td>1.10</td><td>{text['thicker_2']}</td><td>{text['still']}</td><td></td></tr>
              <tr><td>{text['thin_2_3']}</td><td>{text['still']}</td><td>1.20</td><td>{text['more_than_2_thicker']}</td><td>{text['still']}</td><td></td></tr>
              <tr><td>{text['thicker_1_2']}</td><td>{text['moving_or_still']}</td><td>1.20</td><td></td><td></td><td></td></tr>
              <tr><td>{text['thin_3_4']}</td><td>{text['moving_or_still']}</td><td>1.30</td><td></td><td></td><td></td></tr>
              <tr><td>{text['more_layers']}</td><td>{text['without_influence']}</td><td>1.40</td><td></td><td></td><td></td></tr>
              <tr><td>{text['thick_bedspread']}</td><td>{text['without_influence']}</td><td>1.80</td><td></td><td></td><td></td></tr>
              <tr><td>{text['clothing_combined']}</td><td>{text['without_influence']}</td><td>2.40</td><td></td><td></td><td></td></tr>
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _reference_caption(text['note'])
    st.caption(
        ("In rosso-bruno: FC 0.75 per corpo nudo bagnato, in aria ferma, "
         "ricavato da dati sperimentali su casistiche numericamente limitate ("
         if language == "it" else
         "In reddish brown: FC 0.75 for a naked wet body in still air, "
         "based on experimental data from a small case series (")
        + _reference_link("Henssge e Brinkmann, 1984")
        + ").",
        unsafe_allow_html=True,
    )
    _reference_caption(text['lower_trunk'])
    _reference_caption(text['thermal_foil'])
    _reference_caption(text['body_bag'])
    _reference_caption(f"{text['adapted']}: {_HENSSGE_BASE_REFERENCE}")


def _render_henssge_special_table(language: str) -> None:
    text = _HENSSGE_SPECIAL_TABLE_TEXT[language]
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table henssge-special-table">
            <colgroup><col style="width:43%"><col style="width:22%"><col style="width:35%"></colgroup>
            <thead>
              <tr>
                <th scope="col">{text['ground']}</th>
                <th scope="col">{text['clothing']}</th>
                <th scope="col">{text['factor']}</th>
              </tr>
            </thead>
            <tbody>
              <tr class="surface-category"><th colspan="3" scope="rowgroup">{text['indifferent']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[1]</a></sup></th></tr>
              <tr>
                <th scope="row">{text['indifferent_ground']}</th>
                <td>{text['clothing_indifferent']}</td><td>{text['no_adjustment']}</td>
              </tr>
            </tbody>
            <tbody>
              <tr class="surface-category"><th colspan="3" scope="rowgroup">{text['isolating']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[1, 2]</a></sup></th></tr>
              <tr>
                <th rowspan="3" scope="rowgroup">{text['heavy_padding']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[1]</a></sup></th>
                <td>{text['thick']}</td><td>+0.1</td>
              </tr>
              <tr><td>{text['thin']}</td><td>+0.3</td></tr>
              <tr><td>{text['naked']}</td><td>1.3<sup>*</sup></td></tr>
              <tr>
                <th rowspan="2" scope="rowgroup">{text['mattress']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[1]</a></sup></th>
                <td>{text['yes']}</td><td>+0.1</td>
              </tr>
              <tr><td>{text['naked']}</td><td>1.1–1.2</td></tr>
              <tr>
                <th scope="row">{text['leaves']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[2]</a></sup></th>
                <td>{text['naked']}</td><td>{text['leaves_factors']}</td>
              </tr>
            </tbody>
            <tbody>
              <tr class="surface-category"><th colspan="3" scope="rowgroup">{text['conducting']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[1, 3]</a></sup></th></tr>
              <tr>
                <th rowspan="3" scope="rowgroup">{text['concrete']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[1]</a></sup></th>
                <td>{text['thick']}</td><td>−0.1</td>
              </tr>
              <tr><td>{text['very_thin']}</td><td>−0.2</td></tr>
              <tr><td>{text['naked']}</td><td>0.75<sup>*</sup></td></tr>
              <tr>
                <th scope="row">{text['cold_floor']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[3]</a></sup></th>
                <td>{text['naked']}</td><td>0.75</td>
              </tr>
              <tr>
                <th scope="row">{text['pvc']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[3]</a></sup></th>
                <td>{text['naked']}</td><td>{text['pvc_factors']}</td>
              </tr>
              <tr>
                <th scope="row">{text['metal']} <sup><a class="mortem-reference-link" href="Reference" target="_self">[3]</a></sup></th>
                <td>{text['naked']}</td><td>{text['metal_factors']}</td>
              </tr>
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _reference_caption(r"\* " + text['naked_note'])
    _reference_caption(f"[1] {text['adapted']}: {_HENSSGE_SPECIAL_REFERENCE}")
    _reference_caption(f"[2] {text['leaves_reference']}")
    _reference_caption(f"[3] {text['support_reference']}")


def _render_henssge_weight_table(language: str) -> None:
    text = _HENSSGE_WEIGHT_TABLE_TEXT[language]
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table henssge-weight-table">
            <thead>
              <tr>
                <th rowspan="2">{text['cooling']}</th>
                <th colspan="18">{text['weight']}</th>
              </tr>
              <tr>
                <th>4</th><th>6</th><th>8</th><th>10</th><th>20</th><th>30</th>
                <th>40</th><th>50</th><th>60</th><th class="weight-reference">70</th><th>80</th><th>90</th>
                <th>100</th><th>110</th><th>120</th><th>130</th><th>140</th><th>150</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td rowspan="2">{text['clothing']}</td>
                <td>1.6</td><td>1.6</td><td>1.6</td><td>1.6</td><td>1.5</td><td>1.4</td><td>1.4</td><td>1.4</td><td>1.4</td><td class="weight-reference">1.4</td><td>1.4</td><td>1.4</td><td>1.4</td><td>1.4</td><td>1.3</td><td>1.2</td><td>1.2</td><td>1.2</td>
              </tr>
              <tr>
                <td>2.1</td><td>2.1</td><td>2.0</td><td>2.0</td><td>1.9</td><td>1.8</td><td>1.6</td><td>1.6</td><td>1.6</td><td class="weight-reference">1.6</td><td>1.6</td><td>1.6</td><td>1.6</td><td>1.4</td><td>1.4</td><td>1.4</td><td>1.3</td><td>1.3</td>
              </tr>
              <tr>
                <td rowspan="3">{text['bedspread']}</td>
                <td>2.7</td><td>2.7</td><td>2.6</td><td>2.5</td><td>2.3</td><td>2.2</td><td>2.1</td><td>2.0</td><td>1.8</td><td class="weight-reference">1.8</td><td>1.8</td><td>1.8</td><td>1.6</td><td>1.6</td><td>1.6</td><td>1.5</td><td>1.4</td><td>1.4</td>
              </tr>
              <tr>
                <td>3.5</td><td>3.4</td><td>3.3</td><td>3.2</td><td>2.8</td><td>2.6</td><td>2.4</td><td>2.3</td><td>2.0</td><td class="weight-reference">2.0</td><td>2.0</td><td>1.8</td><td>1.8</td><td>1.7</td><td>1.6</td><td>1.6</td><td>1.5</td><td>1.5</td>
              </tr>
              <tr>
                <td>4.5</td><td>4.3</td><td>4.1</td><td>3.9</td><td>3.4</td><td>3.0</td><td>2.8</td><td>2.6</td><td>2.4</td><td class="weight-reference">2.2</td><td>2.1</td><td>2.0</td><td>1.9</td><td>1.8</td><td>1.7</td><td>1.7</td><td>1.6</td><td>1.6</td>
              </tr>
              <tr>
                <td rowspan="2">{text['clothing_bedspread']}</td>
                <td>5.7</td><td>5.3</td><td>5.0</td><td>4.8</td><td>4.0</td><td>3.5</td><td>3.2</td><td>2.9</td><td>2.7</td><td class="weight-reference">2.4</td><td>2.3</td><td>2.2</td><td>2.1</td><td>1.9</td><td>1.9</td><td>1.8</td><td>1.7</td><td>1.6</td>
              </tr>
              <tr>
                <td>7.1</td><td>6.6</td><td>6.2</td><td>5.8</td><td>4.7</td><td>4.0</td><td>3.6</td><td>3.2</td><td>2.9</td><td class="weight-reference">2.6</td><td>2.5</td><td>2.3</td><td>2.2</td><td>2.1</td><td>2.0</td><td>1.9</td><td>1.8</td><td>1.7</td>
              </tr>
              <tr>
                <td rowspan="2">{text['feather_bed']}</td>
                <td>8.8</td><td>8.1</td><td>7.5</td><td>7.0</td><td>5.5</td><td>4.6</td><td>3.9</td><td>3.5</td><td>3.2</td><td class="weight-reference">2.8</td><td>2.7</td><td>2.5</td><td>2.3</td><td>2.2</td><td>2.0</td><td>1.9</td><td>1.8</td><td>1.7</td>
              </tr>
              <tr>
                <td>10.9</td><td>9.8</td><td>8.9</td><td>8.3</td><td>6.2</td><td>5.1</td><td>4.3</td><td>3.8</td><td>3.4</td><td class="weight-reference">3.0</td><td>2.8</td><td>2.6</td><td>2.4</td><td>2.3</td><td>2.1</td><td>2.0</td><td>1.9</td><td>1.8</td>
              </tr>
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _reference_caption(text['note'])
    _reference_caption(f"{text['adapted']}: {_HENSSGE_WEIGHT_REFERENCE}")


render_page_heading("Metodi e tabelle di riferimento")
if st.session_state.get("__fc_tables_return"):
    _reference_caption("I richiami bibliografici aprono la sezione «Riferimenti bibliografici», con le citazioni complete. I numeri tra parentesi quadre si riferiscono alle fonti elencate sotto ciascuna tabella.")

st.markdown(
    """
    <style>
    .mallach-table-wrap {
        width: 100%;
        overflow-x: auto;
        margin: 0 0 0.10rem 0;
    }
    table.mallach-table {
        width: max-content;
        max-width: none;
        border-collapse: collapse;
        font-size: 0.70rem;
        line-height: 1.02;
    }
    table.mallach-table caption {
        font-size: 0.73rem;
        line-height: 1.05;
        padding-bottom: 0.08rem !important;
        text-align: left !important;
    }
    .mallach-table th,
    .mallach-table td {
        border: 1px solid rgba(128,128,128,.35);
        padding: 0.08rem 0.10rem;
        vertical-align: middle;
        text-align: center;
    }
    .mallach-table thead th {
        text-align: center;
        font-weight: 650;
        background: rgba(128,128,128,.08);
        line-height: 1.02;
        white-space: normal;
    }
    .mallach-table:not(.henssge-weight-table) thead th {
        max-width: 8rem;
    }
    .mallach-table td:first-child {
        text-align: center;
        min-width: 7.2rem;
        white-space: normal;
    }
    .mallach-table td:not(:first-child) {
        text-align: center;
        white-space: normal;
    }
    .mallach-table .group-row td {
        font-weight: 650;
        background: rgba(128,128,128,.05);
        text-align: center;
    }
    .henssge-base-table .fc-experimental {
        color: #994738;
        font-weight: 650;
    }
    .mallach-table .subcriterion {
        padding-left: 0.10rem;
    }
    .mallach-table .subcriterion.nested {
        padding-left: 0.15rem;
    }
    table.combined-table {
        width: 100%;
        max-width: 48rem;
        table-layout: fixed;
    }
    .combined-table td,
    .combined-table th {
        padding: 0.20rem 0.25rem;
    }
    .combined-table td:first-child {
        min-width: 0;
    }
    .combined-table th.combined-group,
    .combined-table td.combined-criterion {
        text-align: left;
        overflow-wrap: anywhere;
    }
    .combined-table .combined-group {
        background: rgba(128,128,128,.05);
    }
    .combined-table td.combined-limit {
        white-space: nowrap;
    }
    .henssge-base-table td:first-child,
    .henssge-base-table td:nth-child(4) {
        min-width: 6.8rem;
        max-width: 8rem;
        white-space: normal;
    }
    .henssge-base-table th:nth-child(2),
    .henssge-base-table th:nth-child(5),
    .henssge-base-table th:nth-child(6) {
        min-width: 3.4rem;
    }
    .henssge-base-table th:nth-child(3) {
        min-width: 3.8rem;
    }
    table.henssge-special-table {
        width: 100%;
        max-width: 48rem;
        table-layout: fixed;
    }
    table.henssge-special-table th,
    table.henssge-special-table td {
        min-width: 0;
        max-width: none;
        padding: 0.25rem;
        overflow-wrap: anywhere;
    }
    .henssge-special-table tbody th {
        text-align: left;
        font-weight: 400;
    }
    .henssge-special-table .surface-category th {
        font-weight: 650;
        background: rgba(128,128,128,.08);
    }
    .henssge-special-table sup {
        white-space: nowrap;
    }
    .henssge-weight-table {
        font-size: 0.64rem !important;
    }
    .henssge-weight-table td:first-child {
        min-width: 6.4rem;
        white-space: normal;
    }
    .henssge-weight-table th:not(:first-child),
    .henssge-weight-table td:not(:first-child) {
        min-width: 1.65rem;
        padding-left: 0.05rem;
        padding-right: 0.05rem;
        white-space: nowrap;
    }
    .henssge-weight-table .weight-reference {
        font-weight: 700;
        background: rgba(128,128,128,.10);
    }
    .henssge-table-title {
        font-size: 0.78rem;
        font-weight: 650;
        line-height: 1.02;
        margin: 0.12rem 0 -0.16rem 0;
    }
    div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
        margin-top: -0.48rem !important;
        margin-bottom: -0.62rem !important;
    }
    div[data-testid="stRadio"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.02rem !important;
        margin: -0.04rem 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label {
        margin: 0 !important;
        padding: 0 0.01rem 0 0 !important;
    }
    div[data-testid="stRadio"] label p {
        font-size: 0.68rem !important;
        line-height: 1 !important;
    }
    div[data-testid="stCaptionContainer"] p {
        font-family: inherit;
        font-size: 0.75rem !important;
        line-height: 1.3 !important;
    }
    div[data-testid="stMarkdownContainer"] h2 {
        font-size: 1.15rem !important;
        margin-top: 0.55rem !important;
        margin-bottom: -0.16rem !important;
    }
    @media (min-width: 900px) {
        table.mallach-table {
            font-size: 0.82rem;
            line-height: 1.08;
        }
        table.mallach-table caption {
            font-size: 0.84rem;
            line-height: 1.10;
        }
        .henssge-weight-table {
            font-size: 0.72rem !important;
        }
        .henssge-table-title {
            font-size: 0.86rem;
        }
        div[data-testid="stRadio"] label p {
            font-size: 0.74rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""<style>
.method-section-title {font-size:1.0rem;font-weight:650;line-height:1.2;margin:0.3rem 0 0.06rem;}
.method-subtitle {font-size:0.86rem;font-weight:600;line-height:1.2;margin:0.15rem 0 0.04rem;}
</style>""", unsafe_allow_html=True)

from app.language import current_language
table_language = current_language()

# --- Metodi basati sul raffreddamento cadaverico ---
st.markdown(
    "<div class='method-section-title'>Metodi basati sul raffreddamento cadaverico</div>"
    if table_language == "it" else
    "<div class='method-section-title'>Methods based on body cooling</div>"
    , unsafe_allow_html=True
)
st.markdown("<div class='method-subtitle'>Metodo di Henssge</div>" if table_language == "it" else "<div class='method-subtitle'>Henssge method</div>", unsafe_allow_html=True)
st.caption(
    "Il metodo di Henssge permette di stimare il tempo trascorso dal decesso sulla base della "
    "temperatura rettale, della temperatura ambientale media, del peso corporeo e di un fattore "
    "di correzione (FC) che tiene conto delle condizioni del cadavere. La stima viene espressa "
    "mediante un intervallo temporale, la cui attendibilità diminuisce con il progredire del "
    "raffreddamento corporeo. Il parametro Q esprime il grado di raffreddamento: rapporta la "
    "differenza tra temperatura rettale e ambientale alla differenza tra temperatura corporea "
    "iniziale presunta e ambientale, diminuendo progressivamente da 1 verso 0. "
    "Per temperature ambientali fino a 23 °C, l’incertezza aumenta sensibilmente quando Q scende "
    "sotto 0.3 e l’intervallo non è più considerato attendibile per Q ≤ 0.2. Per temperature "
    "ambientali superiori a 23 °C, il limite critico è Q ≤ 0.5, anche in considerazione della "
    "limitata numerosità delle casistiche utilizzate da Henssge in tali condizioni."
    if table_language == "it" else
    "Henssge's method estimates time since death using rectal temperature, mean ambient temperature, "
    "body weight and a correction factor (FC) accounting for the body's conditions. The resulting "
    "time interval becomes less reliable as cooling progresses. Q describes the degree of cooling "
    "as the difference between rectal and ambient temperature divided by the difference between "
    "assumed initial body temperature and ambient temperature, falling from 1 towards 0. "
    "At ambient temperatures up to 23 °C, uncertainty increases substantially below Q = 0.3, "
    "and the interval is considered unreliable for Q ≤ 0.2. Above 23 °C, the critical "
    "threshold is Q ≤ 0.5, also reflecting the limited size of Henssge's case series under these conditions."
)
st.latex(r"Q=\frac{T_r-T_a}{T_0-T_a}=Ae^{Bt}+(1-A)e^{\frac{A}{A-1}Bt}")
st.caption(
    "Tr: temperatura rettale; Ta: temperatura ambientale media; T0: temperatura corporea "
    "iniziale presunta; t: tempo dal decesso; A e B: coefficienti del modello."
    if table_language == "it" else
    "Tr: rectal temperature; Ta: mean ambient temperature; T0: assumed initial body temperature; "
    "t: time since death; A and B: model coefficients."
)
_reference_caption("Henssge, 1988.")
st.markdown("<div class='method-subtitle'>Metodo di Potente et al.</div>" if table_language == "it" else "<div class='method-subtitle'>Potente et al. method</div>", unsafe_allow_html=True)
st.caption(
    "Quando il grado di raffreddamento corporeo non consente di ottenere un intervallo temporale "
    "sufficientemente attendibile mediante il metodo di Henssge, Potente et al. propongono "
    "di stimare soltanto un tempo minimo trascorso dal decesso, corrispondente al tempo necessario "
    "per raggiungere il grado critico di raffreddamento."
    if table_language == "it" else
    "When the degree of body cooling does not allow a sufficiently reliable time interval "
    "using Henssge's method, Potente et al. propose reporting only a minimum time since death, "
    "corresponding to the time needed to reach the critical degree of cooling."
)
_reference_caption("Potente et al., 2017.")
st.markdown("<div class='method-subtitle'>Fattore di correzione (FC)</div>" if table_language == "it" else "<div class='method-subtitle'>Corrective factor (CF)</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='henssge-table-title'>"
    + ("FC di base" if table_language == "it" else "Base CF")
    + "</div>",
    unsafe_allow_html=True,
)

# Guida operativa preliminare: la tabella originale rimane sotto, invariata.
_GUIDE_ROWS = {
    "it": [
        ("Corpo asciutto — indumenti", [
            ("Nudo","1.00","0.75","g","g"),
            ("1 leggero","1.10","0.90","g","g"),
            ("2 leggeri","1.10–1.20","0.90","g","g"),
            ("3 leggeri","1.20–1.30","1.30","g","g"),
            ("4 leggeri","1.30","1.30","g","g"),
            ("1–2 pesanti","1.20","1.20","g","g"),
            ("1–2 pesanti + 1–2 leggeri","1.20–1.40","1.20–1.40","r","r"),
            ("Molti strati ordinari","1.40–1.60","1.40–1.60","r","r"),
            ("Molti strati, uno o più capi particolarmente isolanti","1.40–1.80","1.40–1.80","g","g"),
        ]),
        ("Corpo bagnato — indumenti", [
            ("Nudo","0.75","0.70","y","g"),
            ("1 leggero","0.90–1.00","0.70","r","g"),
            ("2 leggeri","1.00–1.10","0.70","r","g"),
            ("3 leggeri","1.00–1.10","0.70–0.90","r","r"),
            ("4 leggeri","1.05–1.10","0.70–0.90","r","r"),
            ("1 pesante","1.00–1.05","0.70–0.90","r","r"),
            ("2 pesanti","1.10","0.90","g","g"),
            ("Più di 2 pesanti","1.20","0.90","g","g"),
            ("1 pesante + 1 leggero","1.00–1.10","0.70–0.90","r","r"),
            ("1 pesante + 2 leggeri","1.05–1.10","0.70–0.90","r","r"),
            ("Vestizione multistrato molto consistente","1.20–1.30","—","r",""),
        ]),
    ],
    "en": [
        ("Dry body — clothing", [
            ("Naked","1.00","0.75","g","g"),("1 light layer","1.10","0.90","g","g"),
            ("2 light layers","1.10–1.20","0.90","g","g"),("3 light layers","1.20–1.30","1.30","g","g"),
            ("4 light layers","1.30","1.30","g","g"),("1–2 heavy layers","1.20","1.20","g","g"),
            ("1–2 heavy + 1–2 light layers","1.20–1.40","1.20–1.40","r","r"),
            ("Many ordinary layers","1.40–1.60","1.40–1.60","r","r"),
            ("Many layers, one or more highly insulating items","1.40–1.80","1.40–1.80","g","g"),
        ]),
        ("Wet body — clothing", [
            ("Naked","0.75","0.70","y","g"),("1 light layer","0.90–1.00","0.70","r","g"),
            ("2 light layers","1.00–1.10","0.70","r","g"),("3 light layers","1.00–1.10","0.70–0.90","r","r"),
            ("4 light layers","1.05–1.10","0.70–0.90","r","r"),("1 heavy layer","1.00–1.05","0.70–0.90","r","r"),
            ("2 heavy layers","1.10","0.90","g","g"),("More than 2 heavy layers","1.20","0.90","g","g"),
            ("1 heavy + 1 light layer","1.00–1.10","0.70–0.90","r","r"),
            ("1 heavy + 2 light layers","1.05–1.10","0.70–0.90","r","r"),
            ("Substantial multilayer clothing","1.20–1.30","—","r",""),
        ]),
    ],
}
def _fc_guide_cell(value, category):
    return f'<td class="guide-fc guide-{category}">{escape(value)}</td>'

def _render_fc_guide(language):
    is_it = language == "it"
    title = "Guida alla scelta del FC di base" if is_it else "Guide to choosing the base FC"
    legend = (
        "Verde: tabella originale di Henssge · Giallo: dati sperimentali/casi pubblicati · Rosso-bruno: intervalli proposti per analogia dall’app."
        if is_it else
        "Green: original Henssge table · Yellow: experimental/published cases · Reddish brown: intervals proposed by analogy."
    )
    st.markdown(f'<div class="henssge-table-title">{title}</div>', unsafe_allow_html=True)
    st.caption(legend)
    st.markdown("""
    <style>
    .guide-fc{font-weight:650;white-space:nowrap}
    .guide-g{color:#237a48}.guide-y{color:#a27600}.guide-r{color:#ad4640}
    .fc-guide-table{width:100%;border-collapse:collapse;font-size:.76rem;line-height:1.2}
    .fc-guide-table th,.fc-guide-table td{border:1px solid rgba(128,128,128,.3);padding:.23rem .32rem}
    .fc-guide-table th{background:rgba(128,128,128,.08);text-align:left}
    .fc-guide-table td:not(:first-child),.fc-guide-table th:not(:first-child){text-align:center}
    </style>
    """,unsafe_allow_html=True)
    for heading, rows in _GUIDE_ROWS[language]:
        body = "".join(
            "<tr><td>"+escape(label)+"</td>"+_fc_guide_cell(still,cs)+_fc_guide_cell(wind,cw)+"</tr>"
            for label,still,wind,cs,cw in rows
        )
        st.markdown(
            '<div class="henssge-table-title">'+escape(heading)+'</div>'
            '<div class="mallach-table-wrap"><table class="fc-guide-table"><thead><tr>'
            + ('<th>Indumenti</th><th>Aria ferma</th><th>Correnti d’aria</th>' if is_it
               else '<th>Clothing</th><th>Still air</th><th>Moving air</th>')
            + '</tr></thead><tbody>'+body+'</tbody></table></div>',
            unsafe_allow_html=True,
        )
    covering = [
        ("1 coperta spessa, senza indumenti","1.80","g"),
        ("1 coperta spessa + indumenti","1.80–2.40","r"),
        ("1 coperta molto pesante, senza indumenti","1.80–2.20","r"),
        ("1 coperta molto pesante + indumenti","1.80–2.40","r"),
        ("Più coperte non molto voluminose","1.80–2.40","r"),
        ("Più coperte molto voluminose, senza indumenti","1.80–2.80","r"),
        ("Più coperte molto voluminose + indumenti","2.00–2.80","r"),
        ("Piumone di piume molto voluminoso e avvolgente","2.80–3.00","r"),
    ]
    covering_en = [
        ("1 thick blanket, no clothing","1.80","g"),("1 thick blanket + clothing","1.80–2.40","r"),
        ("1 very heavy blanket, no clothing","1.80–2.20","r"),("1 very heavy blanket + clothing","1.80–2.40","r"),
        ("Multiple blankets, not very bulky","1.80–2.40","r"),("Multiple bulky blankets, no clothing","1.80–2.80","r"),
        ("Multiple bulky blankets + clothing","2.00–2.80","r"),("Very bulky enveloping feather duvet","2.80–3.00","r"),
    ]
    groups = [
        ("Coperte e piumoni" if is_it else "Blankets and duvets",covering if is_it else covering_en),
        ("Corpo immerso" if is_it else "Immersed body", [
            ("Acqua corrente" if is_it else "Flowing water","0.35","g"),
            ("Acqua stagnante" if is_it else "Still water","0.50","g"),
            ("Acqua stagnante prossima a 0 °C" if is_it else "Still water near 0 °C","0.50–1.00","r"),
        ]),
    ]
    for title, rows in groups:
        body="".join("<tr><td>"+escape(label)+"</td>"+_fc_guide_cell(value,category)+"</tr>" for label,value,category in rows)
        st.markdown('<div class="henssge-table-title">'+escape(title)+'</div>'
                    '<div class="mallach-table-wrap"><table class="fc-guide-table"><thead><tr>'
                    + ('<th>Condizione</th><th>FC</th>' if is_it else '<th>Condition</th><th>FC</th>')
                    + '</tr></thead><tbody>'+body+'</tbody></table></div>',unsafe_allow_html=True)
    st.caption(
        "Valori per superfici termicamente indifferenti, prima degli adattamenti per appoggio e peso. "
        "Gli intervalli per analogia non sono intervalli statistici di confidenza."
        if is_it else
        "Values for thermally indifferent surfaces, before support and weight adjustments. "
        "Analogical ranges are not statistical confidence intervals."
    )
    _reference_caption("Henssge, 1988; Henssge e Brinkmann, 1984; Henssge et al., 2000.")

_render_fc_guide(table_language)

_render_henssge_base_table(table_language)

st.markdown(
    "<div class='henssge-table-title'>"
    + ("Situazioni speciali" if table_language == "it" else "Special situations")
    + "</div>",
    unsafe_allow_html=True,
)
_render_henssge_special_table(table_language)

st.markdown(
    "<div class='henssge-table-title'>"
    + ("Adattamento per peso corporeo" if table_language == "it" else "Body-weight adjustment")
    + "</div>",
    unsafe_allow_html=True,
)
_render_henssge_weight_table(table_language)

# --- Altri criteri tanatologici utilizzati nel metodo combinato ---
st.markdown(
    "<div class='method-section-title'>Altri criteri tanatologici</div>"
    if table_language == "it" else
    "<div class='method-section-title'>Other postmortem criteria</div>"
    , unsafe_allow_html=True
)
st.caption(
    "Ipostasi, rigidità ed eccitabilità residua forniscono limiti temporali "
    "minimi e/o massimi, combinabili fra loro e con il raffreddamento."
    if table_language == "it" else
    "Lividity, rigor and residual excitability provide minimum and/or maximum "
    "time limits, which can be combined with each other and with body cooling."
)
st.markdown(
    f"<div class='henssge-table-title'>{_COMBINED_TABLE_TEXT[table_language]['caption']}</div>",
    unsafe_allow_html=True,
)
_render_combined_table(table_language)

render_back_button(TABLES_PAGE, key="back_home")

st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: transparent !important;
        color: #1e90ff !important;
        font-size: 10px !important;
        border: none !important;
        padding: 0 !important;
        text-align: left !important;
    }
    div.stButton > button:first-child:hover {
        text-decoration: underline !important;
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Use Streamlit navigation instead of trying to navigate the Cloud host iframe.
if st.button("Apri riferimenti bibliografici", key="tables_reference_nav"):
    st.session_state.pop("__fc_reference", None)
    st.switch_page("pages/9_Reference.py")

st.markdown("""<style>
.st-key-tables_reference_nav, .st-key-tables_navigation_bridge {display:none;}
</style>""", unsafe_allow_html=True)
_scroll_to_fc = st.session_state.pop("__fc_tables_scroll", False)
with st.container(key="tables_navigation_bridge"):
    # Run the static link bridge in this page's document, not in an iframe.
    # This keeps citation clicks consistent on desktop and mobile.
    st.html(
        """<script>
        (() => {
            const host = window;
            const doc = host.document;
            if (host.mortemReferenceClick) {
                doc.removeEventListener('click', host.mortemReferenceClick, true);
            }
            host.mortemReferenceClick = event => {
                const link = event.target.closest('a.mortem-reference-link');
                if (!link) return;
                const button = doc.querySelector('.st-key-tables_reference_nav button');
                if (!button) return;
                event.preventDefault();
                event.stopPropagation();
                button.click();
            };
            doc.addEventListener('click', host.mortemReferenceClick, true);
            if (SCROLL_TO_FC) {
                let attempts = 0;
                const scroll = () => {
                    const heading = doc.getElementById('fattore-di-correzione-fc')
                        || doc.getElementById('correction-factor-fc');
                    if (heading) heading.scrollIntoView({block:'start'});
                    else if (++attempts < 30) host.requestAnimationFrame(scroll);
                };
                host.requestAnimationFrame(scroll);
            }
        })();
        </script>""".replace("SCROLL_TO_FC", "true" if _scroll_to_fc else "false"),
        unsafe_allow_javascript=True,
    )

render_language_selector()
