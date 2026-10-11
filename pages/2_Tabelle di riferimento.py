import streamlit as st

from app import i18n
from app.mobile_shell import install_minimal_mobile_shell


install_minimal_mobile_shell()


_MALLACH_REFERENCE = (
    "Handbook of Forensic Medicine. Editor: Burkhard Madea, 2022 — "
    "Chapter 7: Post-mortem changes and time since death; dati da: "
    "Mallach HJ. Zur Frage der Todeszeitbestimmung. Berl Med. 1964;18:577–582."
)

_RIGOR_REFERENCE = (
    "Henssge C, Madea B. Estimation of the time since death in the early post-mortem period. "
    "Forensic Sci Int. 2004;144(2–3):167–175. doi:10.1016/j.forsciint.2004.04.051, Table 1; "
    "dati da Mallach H. Zur Frage der Todeszeitbestimmung. Berl Med. 1964;18:577–582."
)

_COMBINED_REFERENCE = (
    "Henssge C, Althaus L, Bolt J, Freislederer A, Haffner H-T, Henssge CA, "
    "Hoppe B, Schneider V. Experiences with a compound method for estimating "
    "the time since death. II. Integration of non-temperature-based methods. "
    "Int J Legal Med. 2000;113(6):320–331. doi:10.1007/s004149900090, Table 1."
)

# Local numbering for the scientific synthesis, independent of the source bibliography.
_COMBINED_BIBLIOGRAPHY = (
    f"[1] {_COMBINED_REFERENCE}",
    "[2] Henssge C, Madea B. Estimation of the time since death in the early post-mortem period. "
    "Forensic Sci Int. 2004;144(2–3):167–175. doi:10.1016/j.forsciint.2004.04.051, "
    "Fig. 4; Tables 1–2.",
)

_HENSSGE_BASE_REFERENCE = (
    "Henssge C. Death time estimation in case work. I. The rectal temperature time of death nomogram. "
    "Forensic Sci Int. 1988;38(3–4):209–236. doi:10.1016/0379-0738(88)90168-5."
    " Ripreso in: Henssge C. Basics and application of the nomogram method at the scene. In: Madea B, ed. Estimation of the Time Since Death. 3rd ed. CRC Press; 2016. Chapter 6.1, Table 6.18."
)

_HENSSGE_SPECIAL_REFERENCE = (
    "Henßge C. Todeszeitbestimmung an Leichen. "
    "Rechtsmedizin. 2002;12(2):112–131. doi:10.1007/s00194-002-0136-8."
    " Ripreso in: Henssge C. Basics and application of the nomogram method at the scene. In: Madea B, ed. Estimation of the Time Since Death. 3rd ed. CRC Press; 2016. Chapter 6.1, Table 6.19."
)

_HENSSGE_WEIGHT_REFERENCE = (
    "Henssge C. Rectal temperature time of death nomogram: dependence of corrective factors "
    "on the body weight under stronger thermic insulation conditions. "
    "Forensic Sci Int. 1992;54(1):51–66. doi:10.1016/0379-0738(92)90080-G; "
    "Madea B. Methods for determining time of death. "
    "Forensic Sci Med Pathol. 2016;12(4):451–485. doi:10.1007/s12024-016-9776-y, Table 10."
    " Ripreso in: Henssge C. Basics and application of the nomogram method at the scene. In: Madea B, ed. Estimation of the Time Since Death. 3rd ed. CRC Press; 2016. Chapter 6.1, Table 6.20."
)

_MALLACH_TABLE_TEXT = {
    "it": {
        "caption": "Decorso temporale di diverse caratteristiche delle macchie ipostatiche*",
        "criterion": "Criterio",
        "sd": "DS",
        "range": "Range di dispersione",
        "references": "Numero di pubblicazioni valutate",
        "lower": "Limite inferiore",
        "upper": "Limite superiore",
        "development": "In via di comparsa",
        "confluence": "Confluenza",
        "maximum": "Massima estensione e intensità",
        "disappearance": "Improntabilità",
        "thumb": "1. Completa alla pressione con il pollice",
        "point": "2. Incompleta alla pressione focale e intensa (pinza)",
        "shifting": "Migrabilità dopo aver spostato il corpo",
        "complete": "1. Completa",
        "incomplete": "2. Incompleta",
        "slight": "3. Solo lieve impallidimento",
        "note": (
            "* I calcoli statistici non sono basati su studi trasversali o longitudinali, "
            "ma su conoscenze empiriche riportate nei testi.<br>"
            "x̄ = valore medio; DS = deviazione standard. "
            "Tutti i tempi sono espressi in ore post-mortem."
        ),
        "adapted": "Adattato da",
    },
    "en": {
        "caption": (
            "Time course of the different criteria of lividity: Mallach's statistical "
            "calculations based on data reported in textbooks*"
        ),
        "criterion": "Criterion",
        "sd": "SD",
        "range": "Range of variation",
        "references": "No. references",
        "lower": "Lower limit",
        "upper": "Upper limit",
        "development": "Development",
        "confluence": "Confluence",
        "maximum": "Maximum extension and intensity",
        "disappearance": "Disappearance",
        "thumb": "1. Complete on thumb pressure",
        "point": "2. Incomplete on point pressure (forceps)",
        "shifting": "Shifting after rotation of the body",
        "complete": "1. Complete",
        "incomplete": "2. Incomplete",
        "slight": "3. Slight blanching only",
        "note": (
            "* The statistical calculations are not based on cross-sectional or longitudinal "
            "studies, but on empirical knowledge reported in textbooks.<br>"
            "x̄ = mean; SD = standard deviation. All times are expressed in hours postmortem."
        ),
        "adapted": "Adapted from",
    },
}

_RIGOR_TABLE_TEXT = {
    "it": {
        "caption": "Decorso temporale della rigidità cadaverica",
        "phase": "Fase della rigidità",
        "mean": "Media con deviazione standard",
        "hours": "Ore post-mortem",
        "probability": "Limiti di probabilità del 95.5% (2 s)",
        "variations": "Variazioni",
        "lower": "Limite inferiore",
        "upper": "Limite superiore",
        "publications": "Numero di pubblicazioni valutate",
        "delay": "Latenza prima della comparsa",
        "reestablishment": "Si riforma dopo esser stato vinto",
        "up_to_5": "Fino a 5",
        "complete": "Rigidità estesa a tutto il corpo e massima",
        "persistence": "Persistenza",
        "resolution": "Risoluzione",
        "note": (
            "Media e deviazione standard calcolate sui dati della letteratura di 150 anni "
            "(1811–1960) da Mallach (1964), nella versione riportata da Henssge e Madea (2004)."
        ),
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Time course of cadaveric rigidity",
        "phase": "Rigor phase",
        "mean": "Mean with standard deviation(s)",
        "hours": "Hours postmortem",
        "probability": "Limits of 95.5% probability (2 s)",
        "variations": "Variations",
        "lower": "Lower limit",
        "upper": "Upper limit",
        "publications": "Number of publications evaluated",
        "delay": "Delay period",
        "reestablishment": "Re-establishment possible",
        "up_to_5": "Up to 5",
        "complete": "Complete rigidity",
        "persistence": "Persistence",
        "resolution": "Resolution",
        "note": (
            "Mean and standard deviation calculated from the literature data of 150 years "
            "(1811–1960) by Mallach (1964), as reported by Henssge and Madea (2004)."
        ),
        "adapted": "Adapted from",
    },
}

_COMBINED_TABLE_TEXT = {
    "it": {
        "caption": "Criteri tanatologici non termici",
        "intro": (
            "Sintesi riorganizzata dei limiti temporali impiegati nel metodo combinato proposto "
            "da Henssge et al. [1], con riferimento alla successiva trattazione di Henssge e Madea [2]. "
            "Tutti i tempi sono espressi in ore post-mortem."
        ),
        "parameter": "Parametro",
        "criterion": "Criterio",
        "present": "Presente",
        "absent": "Assente",
        "lividity": "Ipostasi",
        "beginning": "Comparsa",
        "confluence": "Confluenza",
        "thumb_pressure": "Scomparsa alla pressione del pollice",
        "complete_shifting": "Migrabilità completa",
        "maximum_row": "Massima estensione e intensità",
        "incomplete_shifting": "Migrabilità almeno parziale",
        "rigor": "Rigidità",
        "rigor_complete": "Completa instaurazione",
        "reestablishment": "Ricomparsa dopo essere stata vinta",
        "mechanical": "Eccitabilità meccanica",
        "tendon": "Reazione alla percussione tendinea",
        "idiomuscular": "Contrazione idiomuscolare",
        "eyebrow": "Eccitabilità elettrica sopraciliare",
        "grade": "Grado",
        "interval": "Intervallo (h)",
        "no_response": "Nessuna reazione: ≥ 5 h [1].",
        "mouth": "Eccitabilità elettrica peribuccale",
        "muscle_response": "Risposta muscolare",
        "mouth_note": "* Il limite di 11 ore riguarda qualsiasi risposta peribuccale positiva, indipendentemente dalla sua estensione.",
        "chemical": "Eccitabilità chimica pupillare",
        "atropin": "Dilatazione con atropina",
        "tropicamide": "Dilatazione con tropicamide",
        "acetylcholine": "Costrizione con acetilcolina",
        "variation_note": (
            "Limiti di variazione: estremi temporali riportati in letteratura e adottati da Henssge "
            "per la stima combinata; non corrispondono automaticamente a intervalli statistici al 95% "
            "né a soglie biologiche assolute."
        ),
        "confidence_note": "Gli intervalli dei gradi sopraciliari sono indicati dalla fonte [2] come limiti di confidenza al 95%.",
        "reading_note": (
            "«—» indica che il criterio non fornisce un limite temporale utile. Per comparsa e completo "
            "sviluppo, «assente» significa non ancora raggiunto; per la migrabilità significa non più conservata."
        ),
    },
    "en": {
        "caption": "Non-temperature-based postmortem criteria",
        "intro": (
            "Reorganized synthesis of the time limits used in the compound method proposed by "
            "Henssge et al. [1], with reference to the subsequent account by Henssge and Madea [2]. "
            "All times are expressed in hours postmortem."
        ),
        "parameter": "Parameter",
        "criterion": "Criterion",
        "present": "Present",
        "absent": "Absent",
        "lividity": "Lividity",
        "beginning": "Onset",
        "confluence": "Confluence",
        "thumb_pressure": "Disappearance under thumb pressure",
        "complete_shifting": "Complete shifting",
        "maximum_row": "Maximum extent and intensity",
        "incomplete_shifting": "At least partial shifting",
        "rigor": "Rigor",
        "rigor_complete": "Full development",
        "reestablishment": "Re-establishment after breaking",
        "mechanical": "Mechanical excitability",
        "tendon": "Reaction to tendon percussion",
        "idiomuscular": "Idiomuscular contraction",
        "eyebrow": "Supraciliary electrical excitability",
        "grade": "Grade",
        "interval": "Interval (h)",
        "no_response": "No response: ≥ 5 h [1].",
        "mouth": "Perioral electrical excitability",
        "muscle_response": "Muscular response",
        "mouth_note": "* The 11-hour limit applies to any positive perioral response, regardless of its extent.",
        "chemical": "Chemical excitability of the pupil",
        "atropin": "Dilatation with atropine",
        "tropicamide": "Dilatation with tropicamide",
        "acetylcholine": "Constriction with acetylcholine",
        "variation_note": (
            "Limits of variation: extreme time limits reported in the literature and adopted by Henssge "
            "for the compound estimate; they do not automatically represent 95% statistical intervals "
            "or absolute biological thresholds."
        ),
        "confidence_note": "The source [2] describes the intervals for the supraciliary grades as 95% confidence limits.",
        "reading_note": (
            "“—” means that the criterion provides no useful time limit. For onset and full development, "
            "“absent” means not yet reached; for shifting, it means no longer possible."
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
            "* I valori indicati si riferiscono a corpi di peso medio (riferimento: 70 kg), "
            "in posizione distesa su una base termicamente indifferente."
        ),
        "lower_trunk": (
            "Per la scelta del FC contano solo i vestiti/teli "
            "e le coperte sul tronco inferiore. Indifferente = stesso FC con o senza correnti d’aria."
        ),
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
            "* The listed values apply to bodies of average weight (reference: 70 kg), "
            "in an extended position on a thermally indifferent base."
        ),
        "lower_trunk": (
            "For the selection of the FC, only the clothing "
            "or covering of the lower trunk is relevant. No influence = same FC with or without air currents."
        ),
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
        "indifferent_ground": "Pavimento di casa, prato, terreno asciutto, asfalto",
        "isolating": "Isolante",
        "heavy_padding": "Forte imbottitura",
        "mattress": "Materasso, tappeto spesso",
        "leaves": "Foglie (appoggio di circa 2 cm)",
        "leaves_factors": "1.0 (bagnate)<br>1.3 (umide)<br>1.5 (secche)<br>1.8–2.7 (anche copertura di circa 10 cm)",
        "leaves_reference": "Althaus et al., 2007 · prove su simulatori con foglie.",
        "naked_note": "* Per il corpo nudo, i valori con +/− nell’originale sono interpretati come FC complessivi, non come incrementi o decrementi, in accordo con gli esempi di Henssge.",
        "conducting": "Termoconduttiva",
        "concrete": "Cemento, pietra, piastrelle",
        "yes": "Sì",
        "no": "No",
        "thick": "Spesso",
        "thin": "Sottile",
        "very_thin": "Molto sottile",
        "see_table_1": "vedi FC di base",
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Adaptation of the FC to the supporting surface",
        "ground": "Ground under body",
        "clothing": "Clothing",
        "factor": "FC",
        "indifferent": "Indifferent",
        "indifferent_ground": "House flooring, lawn, dry earth, asphalt",
        "isolating": "Isolating",
        "heavy_padding": "Heavy padding",
        "mattress": "Mattress, thick carpet",
        "leaves": "Leaves (about 2 cm underneath)",
        "leaves_factors": "1.0 (wet)<br>1.3 (partly dry)<br>1.5 (dry)<br>1.8–2.7 (also covered by about 10 cm of leaves)",
        "leaves_reference": "Althaus et al., 2007 · cooling experiments using dummies and leaves.",
        "naked_note": "* For naked bodies, values marked +/− in the original are interpreted as the overall FC, not increases or decreases, consistently with Henssge’s examples.",
        "conducting": "Conducting heat",
        "concrete": "Concrete, stone, tiles",
        "yes": "Yes",
        "no": "No",
        "thick": "Thick",
        "thin": "Thin",
        "very_thin": "Very thin",
        "see_table_1": "see Basic FC",
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
            "Il FC empirico si riferisce a 70 kg (valori in grassetto). "
            "Per un peso corporeo diverso, il FC scelto per 70 kg va adattato leggendo "
            "il valore sulla stessa riga. Per un FC inferiore a 1.4 (fino a 0.75), "
            "la dipendenza dal peso corporeo può essere trascurata. "
            "I valori delle aree accorpate nell’originale sono ripetuti nelle colonne corrispondenti."
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
            "The empirical FC uses 70 kg as the reference body weight "
            "(values in bold). For a different body weight, the FC selected for 70 kg "
            "is adjusted by reading the value on the same row. For an FC below "
            "1.4 (down to 0.75), dependence on body weight may be neglected. "
            "Values spanning merged areas in the original are repeated in the corresponding columns."
        ),
        "adapted": "Adapted from",
    },
}


def _render_livor_table(language: str) -> None:
    text = _MALLACH_TABLE_TEXT[language]
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table">
            <caption style="caption-side:top;text-align:left;font-weight:650;padding-bottom:.20rem;">
              {text['caption']}
            </caption>
            <thead>
              <tr>
                <th rowspan="2">{text['criterion']}</th>
                <th rowspan="2">x̄</th>
                <th rowspan="2">{text['sd']}</th>
                <th colspan="2">2 {text['sd']}</th>
                <th colspan="2">{text['range']}</th>
                <th rowspan="2">{text['references']}</th>
              </tr>
              <tr>
                <th>{text['lower']}</th>
                <th>{text['upper']}</th>
                <th>{text['lower']}</th>
                <th>{text['upper']}</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>{text['development']}</td><td>¾</td><td>½</td><td>—</td><td>2</td><td>¼</td><td>3</td><td>17</td></tr>
              <tr><td>{text['confluence']}</td><td>2½</td><td>1</td><td>¾</td><td>4¼</td><td>1</td><td>4</td><td>5</td></tr>
              <tr><td>{text['maximum']}</td><td>9½</td><td>4½</td><td>½</td><td>18¼</td><td>3</td><td>16</td><td>7</td></tr>
              <tr class="group-row"><td colspan="8">{text['disappearance']}</td></tr>
              <tr><td class="subcriterion">{text['thumb']}</td><td>5½</td><td>6</td><td>—</td><td>17½</td><td>1</td><td>20</td><td>5</td></tr>
              <tr><td class="subcriterion">{text['point']}</td><td>17</td><td>10½</td><td>—</td><td>37½</td><td>10</td><td>36</td><td>4</td></tr>
              <tr class="group-row"><td colspan="8">{text['shifting']}</td></tr>
              <tr><td class="subcriterion">{text['complete']}</td><td>3¾</td><td>1</td><td>2</td><td>5½</td><td>2</td><td>6</td><td>11</td></tr>
              <tr><td class="subcriterion">{text['incomplete']}</td><td>11</td><td>4½</td><td>2¼</td><td>20</td><td>4</td><td>24</td><td>11</td></tr>
              <tr><td class="subcriterion">{text['slight']}</td><td>18½</td><td>8</td><td>2½</td><td>34½</td><td>10</td><td>30</td><td>7</td></tr>
            </tbody>
          </table>
        </div>
        <div class="mallach-note">{text['note']}</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['adapted']}: {_MALLACH_REFERENCE}")


def _render_rigor_table(language: str) -> None:
    text = _RIGOR_TABLE_TEXT[language]
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table">
            <caption style="caption-side:top;text-align:left;font-weight:650;padding-bottom:.20rem;">
              {text['caption']}
            </caption>
            <thead>
              <tr>
                <th rowspan="3">{text['phase']}</th>
                <th rowspan="3">{text['mean']}</th>
                <th colspan="4">{text['hours']}</th>
                <th rowspan="3">{text['publications']}</th>
              </tr>
              <tr>
                <th colspan="2">{text['probability']}</th>
                <th colspan="2">{text['variations']}</th>
              </tr>
              <tr>
                <th>{text['lower']}</th>
                <th>{text['upper']}</th>
                <th>{text['lower']}</th>
                <th>{text['upper']}</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>{text['delay']}</td><td>3 ± 2</td><td>–</td><td>7</td><td>&lt;1/2</td><td>7</td><td>26</td></tr>
              <tr><td>{text['reestablishment']}</td><td>{text['up_to_5']}</td><td>–</td><td>–</td><td>2</td><td>8</td><td>–</td></tr>
              <tr><td>{text['complete']}</td><td>8 ± 1</td><td>6</td><td>10</td><td>2</td><td>20</td><td>28</td></tr>
              <tr><td>{text['persistence']}</td><td>57 ± 14</td><td>29</td><td>85</td><td>24</td><td>96</td><td>27</td></tr>
              <tr><td>{text['resolution']}</td><td>76 ± 32</td><td>12</td><td>140</td><td>24</td><td>192</td><td>27</td></tr>
            </tbody>
          </table>
        </div>
        <div class="mallach-note">{text['note']}</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['adapted']}: {_RIGOR_REFERENCE}")


def _render_combined_table(language: str) -> None:
    text = _COMBINED_TABLE_TEXT[language]
    sep = "," if language == "it" else "."
    # Scientific reference data: these limits are not read from application ranges.
    # A missing useful bound is shown as a dash, not as an artificial zero.
    groups = (
        ("lividity", "[1, 2]", (
            ("beginning", "—", "≤ 3"),
            ("confluence", "≥ 1", "≤ 4"),
            ("maximum_row", "≥ 3", "≤ 16"),
            ("thumb_pressure", "≤ 20", "≥ 1"),
            ("complete_shifting", "≤ 6", "≥ 2"),
            ("incomplete_shifting", "≤ 24", "≥ 4"),
        )),
        ("rigor", "[1]", (
            ("beginning", f"≥ 0{sep}5", "≤ 7"),
            ("rigor_complete", "≥ 2", "≤ 20"),
            ("reestablishment", "≤ 8", "≥ 2"),
        )),
        ("mechanical", "[1]", (
            ("tendon", f"≤ 2{sep}5", "—"),
            ("idiomuscular", "≤ 13", f"≥ 1{sep}5"),
        )),
        ("mouth", "[1]", (("muscle_response", "≤ 11*", "≥ 3"),)),
        ("chemical", "[1]", (
            ("atropin", "≤ 10", "≥ 3"),
            ("tropicamide", "≤ 30", "≥ 5"),
            ("acetylcholine", "≤ 46", "≥ 14"),
        )),
    )
    rows = []
    for parameter, reference, criteria in groups:
        for index, (criterion, present, absent) in enumerate(criteria):
            group_cell = (
                f'<th scope="rowgroup" rowspan="{len(criteria)}" class="combined-group">'
                f'{text[parameter]} {reference}</th>' if index == 0 else ""
            )
            rows.append(
                f'<tr>{group_cell}<td class="combined-criterion">{text[criterion]}</td>'
                f'<td class="combined-limit">{present}</td>'
                f'<td class="combined-limit">{absent}</td></tr>'
            )
    st.caption(text["intro"])
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table combined-table">
            <caption>{text['caption']}</caption>
            <colgroup><col style="width:24%"><col style="width:46%"><col style="width:15%"><col style="width:15%"></colgroup>
            <thead>
              <tr><th scope="col">{text['parameter']}</th><th scope="col">{text['criterion']}</th>
              <th scope="col">{text['present']}</th><th scope="col">{text['absent']}</th></tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(text["reading_note"])
    st.caption(text["mouth_note"])
    st.caption(text["variation_note"])
    # Fig. 4 of Henssge & Madea (2004), checked visually: grade II is 3.5–16 h.
    # Its limits describe an observed grade, not absence of that same grade.
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table combined-supra-table">
            <caption>{text['eyebrow']} [2]</caption>
            <thead>
              <tr><th scope="col">{text['grade']}</th><th scope="col">{text['interval']}</th>
              <th scope="col">{text['grade']}</th><th scope="col">{text['interval']}</th></tr>
            </thead>
            <tbody>
              <tr><td>VI</td><td>≤ 6</td><td>III</td><td>3–13</td></tr>
              <tr><td>V</td><td>1–7</td><td>II</td><td>3{sep}5–16</td></tr>
              <tr><td>IV</td><td>2–8</td><td>I</td><td>5–22</td></tr>
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['no_response']} {text['confidence_note']}")
    for reference in _COMBINED_BIBLIOGRAPHY:
        st.caption(reference)


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
              <tr><td>{text['naked']}</td><td>{text['moving']}</td><td>0.75</td><td></td><td></td><td></td></tr>
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
        <div class="mallach-note">{text['note']}<br>{text['lower_trunk']}</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['adapted']}: {_HENSSGE_BASE_REFERENCE}")


def _render_henssge_special_table(language: str) -> None:
    text = _HENSSGE_SPECIAL_TABLE_TEXT[language]
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table henssge-special-table">
            <thead>
              <tr>
                <th>{text['ground']}</th>
                <th>{text['clothing']}</th>
                <th>{text['factor']}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td rowspan="2"><strong>{text['indifferent']}</strong><br>{text['indifferent_ground']}</td>
                <td>{text['yes']}</td><td>{text['see_table_1']}</td>
              </tr>
              <tr><td>{text['no']}</td><td>{text['see_table_1']}</td></tr>
              <tr>
                <td rowspan="3"><strong>{text['isolating']}</strong><br>{text['heavy_padding']}</td>
                <td>{text['thick']}</td><td>+0.1</td>
              </tr>
              <tr><td>{text['thin']}</td><td>+0.3</td></tr>
              <tr><td>{text['no']}</td><td>1.3*</td></tr>
              <tr>
                <td rowspan="2">{text['mattress']}</td>
                <td>{text['yes']}</td><td>+0.1</td>
              </tr>
              <tr><td>{text['no']}</td><td>1.1–1.2*</td></tr>
              <tr>
                <td>{text['leaves']}</td><td>{text['no']}</td><td>{text['leaves_factors']}</td>
              </tr>
              <tr>
                <td rowspan="3"><strong>{text['conducting']}</strong><br>{text['concrete']}</td>
                <td>{text['thick']}</td><td>−0.1</td>
              </tr>
              <tr><td>{text['very_thin']}</td><td>−0.2</td></tr>
              <tr><td>{text['no']}</td><td>0.75*</td></tr>
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['adapted']}: {_HENSSGE_SPECIAL_REFERENCE}")
    st.caption(text['naked_note'])
    st.caption(f"{text['leaves_reference']} [doi:10.1007/s00414-006-0108-8](https://doi.org/10.1007/s00414-006-0108-8)")


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
        <div class="mallach-note">{text['note']}</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['adapted']}: {_HENSSGE_WEIGHT_REFERENCE}")


st.title("Tabelle di riferimento")
if st.session_state.get("__fc_tables_return"):
    if st.button("← Indietro al FC", key="back_to_fc_top"):
        from app.fc_page import FULL_PAGE
        st.switch_page(st.session_state.get("__fc_home", FULL_PAGE))
    from app.fc_reference_cases import render_fc_cases
    render_fc_cases()

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
    .mallach-table .subcriterion {
        padding-left: 0.10rem;
    }
    .mallach-table .subcriterion.nested {
        padding-left: 0.15rem;
    }
    .mallach-note {
        font-size: 0.64rem;
        line-height: 1.08;
        margin-top: 0.08rem;
    }
    table.combined-table,
    table.combined-supra-table {
        width: 100%;
        max-width: 48rem;
        table-layout: fixed;
    }
    .combined-table td,
    .combined-table th,
    .combined-supra-table td,
    .combined-supra-table th {
        padding: 0.20rem 0.25rem;
    }
    .combined-table td:first-child,
    .combined-supra-table td:first-child {
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
    table.combined-supra-table {
        max-width: 30rem;
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
    .henssge-special-table td:first-child {
        min-width: 7.5rem;
        max-width: 9rem;
        white-space: normal;
    }
    .henssge-special-table th:nth-child(2) {
        min-width: 4rem;
    }
    .henssge-special-table th:nth-child(3) {
        min-width: 4.5rem;
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
        font-size: 0.62rem !important;
        line-height: 1.08 !important;
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
        .mallach-note {
            font-size: 0.70rem;
            line-height: 1.12;
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

# --- Sezione 1: Mallach ---
st.markdown(f"## {i18n.ui_text('full.livor_heading')}")
livor_language = st.radio(
    "Lingua tabella ipostasi",
    ["Italiano", "English"],
    horizontal=True,
    key="livor_table_language",
    label_visibility="collapsed",
)
_render_livor_table("it" if livor_language == "Italiano" else "en")

st.markdown("## Rigidità cadaverica")
rigor_language = st.radio(
    "Lingua tabella rigidità",
    ["Italiano", "English"],
    horizontal=True,
    key="rigor_table_language",
    label_visibility="collapsed",
)
_render_rigor_table("it" if rigor_language == "Italiano" else "en")

_combined_language_before = st.session_state.get("combined_table_language", "Italiano")
st.markdown("## Metodo combinato di Henssge" if _combined_language_before == "Italiano" else "## Henssge’s compound method")
combined_language = st.radio(
    "Lingua tabella metodi combinati",
    ["Italiano", "English"],
    horizontal=True,
    key="combined_table_language",
    label_visibility="collapsed",
)
_render_combined_table("it" if combined_language == "Italiano" else "en")

# --- Sezione 2: Tabelle Henssge ---
_base_language_before = st.session_state.get("henssge_base_table_language", "Italiano")
st.markdown("## Fattore di correzione (FC)" if _base_language_before == "Italiano" else "## Correction factor (FC)")

st.markdown(
    "<div class='henssge-table-title'>"
    + (
        "FC di base"
        if _base_language_before == "Italiano"
        else "Basic FC"
    )
    + "</div>",
    unsafe_allow_html=True,
)
henssge_base_language = st.radio(
    "Lingua tabella FC di base",
    ["Italiano", "English"],
    horizontal=True,
    key="henssge_base_table_language",
    label_visibility="collapsed",
)
_render_henssge_base_table("it" if henssge_base_language == "Italiano" else "en")

_special_language_before = st.session_state.get("henssge_special_table_language", "Italiano")
st.markdown(
    "<div class='henssge-table-title'>"
    + (
        "Situazioni speciali"
        if _special_language_before == "Italiano"
        else "Special situations"
    )
    + "</div>",
    unsafe_allow_html=True,
)
henssge_special_language = st.radio(
    "Lingua tabella situazioni speciali",
    ["Italiano", "English"],
    horizontal=True,
    key="henssge_special_table_language",
    label_visibility="collapsed",
)
_render_henssge_special_table("it" if henssge_special_language == "Italiano" else "en")

_weight_language_before = st.session_state.get("henssge_weight_table_language", "Italiano")
st.markdown(
    "<div class='henssge-table-title'>"
    + (
        "Adattamento per peso corporeo"
        if _weight_language_before == "Italiano"
        else "Body-weight adjustment"
    )
    + "</div>",
    unsafe_allow_html=True,
)
henssge_weight_language = st.radio(
    "Lingua tabella adattamento per peso corporeo",
    ["Italiano", "English"],
    horizontal=True,
    key="henssge_weight_table_language",
    label_visibility="collapsed",
)
_render_henssge_weight_table("it" if henssge_weight_language == "Italiano" else "en")

if not st.session_state.get("__fc_tables_return"):
    from app.fc_reference_cases import render_fc_cases
    render_fc_cases()

if st.button("← Indietro al FC" if st.session_state.get("__fc_tables_return") else "⬅️ Torna alla pagina principale", key="back_home"):
    if st.session_state.get("__fc_tables_return"):
        st.switch_page(st.session_state.get("__fc_home", "Stima_epoca_decesso.py"))
    st.switch_page("Stima_epoca_decesso.py")

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
