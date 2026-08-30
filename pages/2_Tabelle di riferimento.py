import streamlit as st

from app import i18n


_MALLACH_REFERENCE = (
    "Handbook of Forensic Medicine. Editor: Burkhard Madea, 2022 — "
    "Chapter 7: Post-mortem changes and time since death; dati da: "
    "Mallach HJ. Zur Frage der Todeszeitbestimmung. Berl Med. 1964;18:577–582."
)

_RIGOR_REFERENCE = (
    "Henßge C, Madea B. Estimation of the time since death. "
    "Forensic Sci Int. 2004;144:167–175. doi:10.1016/j.forsciint.2004.04.051, Table 1; "
    "dati da Mallach H. Zur Frage der Todeszeitbestimmung. Berl Med. 1964;18:577–582."
)

_COMBINED_REFERENCE = (
    "Henssge C, Althaus L, Bolt J, Freislederer A, Haffner H-T, Henssge CA, "
    "Hoppe B, Schneider V. Experiences with a compound method for estimating "
    "the time since death. II. Integration of non-temperature-based methods. "
    "Int J Legal Med. 2000;113(6):320–331. doi:10.1007/s004149900090, Table 1."
)

_HENSSGE_BASE_REFERENCE = (
    "Henssge C. Death time estimation in case work. I. The rectal temperature time of death nomogram. "
    "Forensic Sci Int. 1988;38(3–4):209–236. doi:10.1016/0379-0738(88)90168-5."
)

_HENSSGE_SPECIAL_REFERENCE = (
    "Henßge C. Todeszeitbestimmung an Leichen. "
    "Rechtsmedizin. 2002;12(2):112–131. doi:10.1007/s00194-002-0136-8."
)

_HENSSGE_WEIGHT_REFERENCE = (
    "Henssge C. Rectal temperature time of death nomogram: dependence of corrective factors "
    "on the body weight under stronger thermic insulation conditions. "
    "Forensic Sci Int. 1992;54(1):51–66. doi:10.1016/0379-0738(92)90080-G; "
    "Madea B. Methods for determining time of death. "
    "Forensic Sci Med Pathol. 2016;12(4):451–485. doi:10.1007/s12024-016-9776-y, Table 10."
)

_MALLACH_TABLE_TEXT = {
    "it": {
        "caption": (
            "Decorso temporale dei diversi criteri delle ipostasi: calcoli statistici "
            "di Mallach basati su dati riportati nei testi*"
        ),
        "criterion": "Criterio",
        "sd": "DS",
        "range": "Range di dispersione",
        "references": "N. citazioni",
        "lower": "Limite inferiore",
        "upper": "Limite superiore",
        "development": "Sviluppo",
        "confluence": "Confluenza",
        "maximum": "Massima distensione e intensità",
        "disappearance": "Scomparsa",
        "thumb": "1. Completa alla pressione con il pollice",
        "point": "2. Incompleta alla pressione puntiforme (pinza)",
        "shifting": "Spostamento dopo rotazione del corpo",
        "complete": "1. Completo",
        "incomplete": "2. Incompleto",
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
        "caption": "Tabella 1 — Decorso temporale della rigidità cadaverica",
        "phase": "Fase della rigidità",
        "mean": "Media con deviazione standard",
        "hours": "Ore post-mortem",
        "probability": "Limiti di probabilità del 95.5% (2 s)",
        "variations": "Variazioni",
        "lower": "Limite inferiore",
        "upper": "Limite superiore",
        "publications": "Numero di pubblicazioni valutate",
        "delay": "Periodo di latenza",
        "reestablishment": "Ripristino possibile",
        "up_to_5": "Fino a 5",
        "complete": "Rigidità completa",
        "persistence": "Persistenza",
        "resolution": "Risoluzione",
        "note": (
            "Media e deviazione standard calcolate sui dati della letteratura di 150 anni "
            "(1811–1960) da Mallach 1964 [43] (Schleyer [44], leggermente modificata)."
        ),
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Table 1 — Time course of cadavric rigidity",
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
            "(1811–1960) by Mallach 1964 [43] (Schleyer [44] slightly modified)."
        ),
        "adapted": "Adapted from",
    },
}

_COMBINED_TABLE_TEXT = {
    "it": {
        "caption": "Tabella 1 — Limiti temporali dei metodi/criteri non basati sulla temperatura",
        "method": "Metodo/criterio",
        "result": "Risultato dell'esame",
        "minimum": "Limite minimo del periodo dalla morte (ore post-mortem)",
        "maximum": "Limite massimo del periodo dalla morte (ore post-mortem)",
        "statistics": "Statistica (limiti)",
        "reference": "Riferimento",
        "lividity": "Ipostasi",
        "beginning": "Inizio",
        "confluence": "Confluenza",
        "thumb_pressure": "Pressione con il pollice",
        "complete_shifting": "Spostamento completo",
        "maximum_row": "Massimo",
        "incomplete_shifting": "Spostamento incompleto",
        "rigor": "Rigidità",
        "reestablishment": "Ripristino",
        "mechanical": "Eccitabilità meccanica muscolare",
        "tendon": "Reazione tendinea",
        "idiomuscular": "Contrazione idiomuscolare",
        "electrical": "Eccitabilità elettrica muscolare",
        "eyebrow": "Elettrodi nel sopracciglio",
        "grade": "Grado",
        "mouth": "Elettrodi all'angolo della bocca",
        "chemical": "Eccitabilità chimica dell'iride",
        "atropin": "Atropina",
        "tropicamide": "Tropicamide",
        "acetylcholine": "Acetilcolina",
        "positive": "Positivo",
        "negative": "Negativo",
        "variation": "Variazione",
        "confidence": "Confidenza 95%",
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Table 1 — Time limits used of the non-temperature-based methods/criteria",
        "method": "Method/criterion",
        "result": "Result of examination",
        "minimum": "Minimum limit of the period since death (hours postmortem)",
        "maximum": "Maximum limit of the period since death (hours postmortem)",
        "statistics": "Statistics (limits)",
        "reference": "Reference",
        "lividity": "Lividity",
        "beginning": "Beginning",
        "confluence": "Confluence",
        "thumb_pressure": "Thumb pressure",
        "complete_shifting": "Complete shifting",
        "maximum_row": "Maximum",
        "incomplete_shifting": "Incomplete shifting",
        "rigor": "Rigor",
        "reestablishment": "Re-establishment",
        "mechanical": "Mechanical excitability muscle",
        "tendon": "Tendon reaction",
        "idiomuscular": "Idiomuscular contraction",
        "electrical": "Electrical excitability muscle",
        "eyebrow": "Electrodes in eyebrow",
        "grade": "Grade",
        "mouth": "Electrodes in corner of mouth",
        "chemical": "Chemical excitability iris",
        "atropin": "Atropin",
        "tropicamide": "Tropicamide",
        "acetylcholine": "Acetylcholine",
        "positive": "Positive",
        "negative": "Negative",
        "variation": "Variation",
        "confidence": "95% confidence",
        "adapted": "Adapted from",
    },
}

_HENSSGE_BASE_TABLE_TEXT = {
    "it": {
        "caption": "Fattori di correzione empirici del peso corporeo",
        "dry": "Abbigliamento/copertura asciutti",
        "in_air": "In aria",
        "factor": "Fattore di correzione",
        "wet": "Abbigliamento/copertura bagnati, superficie corporea bagnata",
        "in_water": "In acqua",
        "naked": "Nudo",
        "moving": "In movimento",
        "still": "Ferma",
        "flowing": "Corrente",
        "thin_1_2": "1–2 strati sottili",
        "thicker_2_plus": "2 o più strati più spessi",
        "more_than_2_thicker": "Più di 2 strati più spessi",
        "thicker_2": "2 strati più spessi",
        "thin_2_3": "2–3 strati sottili",
        "thicker_1_2": "1–2 strati più spessi",
        "thin_3_4": "3–4 strati sottili",
        "more_layers": "Più strati sottili/spessi",
        "moving_or_still": "In movimento o ferma",
        "without_influence": "Senza influenza",
        "thick_bedspread": "Coperta spessa",
        "clothing_combined": "+ abbigliamento combinato",
        "note": (
            "* I valori indicati si riferiscono a corpi di peso medio (riferimento: 70 kg), "
            "in posizione distesa su una base termicamente indifferente."
        ),
        "lower_trunk": (
            "Per la scelta del fattore di correzione è rilevante solo l'abbigliamento "
            "o la copertura del tronco inferiore."
        ),
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Empiric corrective factors of the body weight",
        "dry": "Dry clothing/covering",
        "in_air": "In air",
        "factor": "Corrective factor",
        "wet": "Wet-through clothing/covering, wet body surface",
        "in_water": "In water",
        "naked": "Naked",
        "moving": "Moving",
        "still": "Still",
        "flowing": "Flowing",
        "thin_1_2": "1–2 thin layers",
        "thicker_2_plus": "2 or more thicker layers",
        "more_than_2_thicker": "More than 2 thicker layers",
        "thicker_2": "2 thicker layers",
        "thin_2_3": "2–3 thin layers",
        "thicker_1_2": "1–2 thicker layers",
        "thin_3_4": "3–4 thin layers",
        "more_layers": "More thin/thicker layers",
        "moving_or_still": "Moving or still",
        "without_influence": "Without influence",
        "thick_bedspread": "Thick bedspread",
        "clothing_combined": "+ clothing combined",
        "note": (
            "* The listed values apply to bodies of average weight (reference: 70 kg), "
            "in an extended position on a thermally indifferent base."
        ),
        "lower_trunk": (
            "For the selection of the corrective factor of any case, only the clothing "
            "or covering of the lower trunk is relevant."
        ),
        "adapted": "Adapted from",
    },
}


_HENSSGE_SPECIAL_TABLE_TEXT = {
    "it": {
        "caption": "Adattamento dei fattori di correzione (f, vedi Tabella 1) alla superficie di appoggio",
        "ground": "Superficie di appoggio",
        "clothing": "Abbigliamento",
        "factor": "Fattore di correzione f",
        "indifferent": "Termicamente indifferente",
        "indifferent_ground": "Pavimento di casa/appartamento, prato, terreno asciutto, asfalto",
        "isolating": "Isolante",
        "heavy_padding": "Forte imbottitura",
        "mattress": "Materasso, tappeto spesso",
        "conducting": "Termoconduttiva",
        "concrete": "Cemento, pietra, piastrelle",
        "yes": "Sì",
        "no": "No",
        "thick": "Spesso",
        "thin": "Sottile",
        "very_thin": "Molto sottile",
        "see_table_1": "vedi Tabella 1",
        "adapted": "Adattato da",
    },
    "en": {
        "caption": "Adaptation of corrective factors (f, see Table 1) to ground under body",
        "ground": "Ground under body",
        "clothing": "Clothing",
        "factor": "Corrective factor f",
        "indifferent": "Indifferent",
        "indifferent_ground": "House or apartment flooring, lawn, dry earth, asphalt",
        "isolating": "Isolating",
        "heavy_padding": "Heavy padding",
        "mattress": "Mattress, thick carpet",
        "conducting": "Conducting heat",
        "concrete": "Concrete, stone, tiles",
        "yes": "Yes",
        "no": "No",
        "thick": "Thick",
        "thin": "Thin",
        "very_thin": "Very thin",
        "see_table_1": "see Table 1",
        "adapted": "Adapted from",
    },
}

_HENSSGE_WEIGHT_TABLE_TEXT = {
    "it": {
        "weight": "Peso corporeo reale (kg)",
        "cooling": "Condizioni di raffreddamento",
        "clothing": "Abbigliamento, più strati",
        "bedspread": "Coperta",
        "clothing_bedspread": "Abbigliamento + coperta",
        "feather_bed": "Piumone",
        "note": (
            "Il riferimento dei fattori empirici è 70 kg (valori in grassetto). "
            "Per un peso corporeo diverso, il fattore scelto per 70 kg va adattato leggendo "
            "il valore sulla stessa riga. Per fattori inferiori a 1.4 (fino a 0.75), "
            "la dipendenza dal peso corporeo può essere trascurata. "
            "Le celle vuote corrispondono a valori non riportati nella tabella originale."
        ),
        "adapted": "Adattato da",
    },
    "en": {
        "weight": "Real body weight (kg)",
        "cooling": "Cooling conditions",
        "clothing": "Clothing, more layers",
        "bedspread": "Bedspread",
        "clothing_bedspread": "Clothing + bedspread",
        "feather_bed": "Feather bed",
        "note": (
            "The empirical corrective factors use 70 kg as the reference body weight "
            "(values in bold). For a different body weight, the factor selected for 70 kg "
            "is adjusted by reading the value on the same row. For corrective factors below "
            "1.4 (down to 0.75), dependence on body weight may be neglected. "
            "Blank cells correspond to values not reported in the original table."
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
            <caption style="caption-side:top;text-align:left;font-weight:650;padding-bottom:.45rem;">
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
            <caption style="caption-side:top;text-align:left;font-weight:650;padding-bottom:.45rem;">
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
    p = text["positive"]
    n = text["negative"]
    v = text["variation"]
    c = text["confidence"]
    st.markdown(
        f"""
        <div class="mallach-table-wrap">
          <table class="mallach-table combined-table">
            <caption style="caption-side:top;text-align:left;font-weight:650;padding-bottom:.45rem;">
              {text['caption']}
            </caption>
            <thead>
              <tr>
                <th>{text['method']}</th>
                <th>{text['result']}</th>
                <th>{text['minimum']}</th>
                <th>{text['result']}</th>
                <th>{text['maximum']}</th>
                <th>{text['statistics']}</th>
                <th>{text['reference']}</th>
              </tr>
            </thead>
            <tbody>
              <tr class="group-row"><td>{text['lividity']}</td><td></td><td></td><td></td><td></td><td></td><td>[8]</td></tr>
              <tr><td class="subcriterion">{text['beginning']}</td><td>{p}</td><td>0.0</td><td>{n}</td><td>3.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['confluence']}</td><td>{p}</td><td>1.0</td><td>{n}</td><td>4.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['thumb_pressure']}</td><td>{n}</td><td>1.0</td><td>{p}</td><td>20.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['complete_shifting']}</td><td>{n}</td><td>2.0</td><td>{p}</td><td>6.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['maximum_row']}</td><td>{p}</td><td>3.0</td><td>{n}</td><td>16.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['incomplete_shifting']}</td><td>{n}</td><td>4.0</td><td>{p}</td><td>24.0</td><td></td><td></td></tr>
              <tr class="group-row"><td>{text['rigor']}</td><td></td><td></td><td></td><td></td><td></td><td>[8]</td></tr>
              <tr><td class="subcriterion">{text['beginning']}</td><td>{p}</td><td>0.5</td><td>{n}</td><td>7.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['reestablishment']}</td><td>{n}</td><td>2.0</td><td>{p}</td><td>8.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['maximum_row']}</td><td>{p}</td><td>2.0</td><td>{n}</td><td>20.0</td><td>{v}</td><td></td></tr>
              <tr class="group-row"><td>{text['mechanical']}</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
              <tr><td class="subcriterion">{text['tendon']}</td><td>{n}</td><td>0.0</td><td>{p}</td><td>2.5</td><td>{v}</td><td>[9, 10]</td></tr>
              <tr><td class="subcriterion">{text['idiomuscular']}</td><td>{n}</td><td>1.5</td><td>{p}</td><td>13.0</td><td>{v}</td><td>[10, 11]</td></tr>
              <tr class="group-row"><td>{text['electrical']}</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
              <tr><td class="subcriterion">{text['eyebrow']}</td><td></td><td></td><td></td><td></td><td></td><td>[4, 7]</td></tr>
              <tr><td class="subcriterion nested">{text['grade']} VI</td><td>{n}</td><td>1.0</td><td>{p}</td><td>6.0</td><td>{c}</td><td></td></tr>
              <tr><td class="subcriterion nested">{text['grade']} V</td><td>{n}</td><td>2.0</td><td>{p}</td><td>7.0</td><td>{c}</td><td></td></tr>
              <tr><td class="subcriterion nested">{text['grade']} IV</td><td>{n}</td><td>3.0</td><td>{p}</td><td>8.0</td><td>{c}</td><td></td></tr>
              <tr><td class="subcriterion nested">{text['grade']} III</td><td>{n}</td><td>3.5</td><td>{p}</td><td>13.0</td><td>{c}</td><td></td></tr>
              <tr><td class="subcriterion nested">{text['grade']} II</td><td>{n}</td><td>5.0</td><td>{p}</td><td>26.0</td><td>{c}</td><td></td></tr>
              <tr><td class="subcriterion nested">{text['grade']} I</td><td>{n}</td><td>5.0</td><td>{p}</td><td>22.0</td><td>{c}</td><td></td></tr>
              <tr><td class="subcriterion">{text['mouth']}</td><td>{n}</td><td>3.0</td><td>{p}</td><td>11.0</td><td>{v}</td><td>[4]</td></tr>
              <tr class="group-row"><td>{text['chemical']}</td><td></td><td></td><td></td><td></td><td></td><td>[4]</td></tr>
              <tr><td class="subcriterion">{text['atropin']}</td><td>{n}</td><td>3.0</td><td>{p}</td><td>10.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['tropicamide']}</td><td>{n}</td><td>5.0</td><td>{p}</td><td>30.0</td><td>{v}</td><td></td></tr>
              <tr><td class="subcriterion">{text['acetylcholine']}</td><td>{n}</td><td>14.0</td><td>{p}</td><td>46.0</td><td>{v}</td><td></td></tr>
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['adapted']}: {_COMBINED_REFERENCE}")


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
              <tr><td></td><td></td><td>0.50</td><td>{text['naked']}</td><td></td><td>{text['still']}</td></tr>
              <tr><td></td><td></td><td>0.70</td><td>{text['naked']}</td><td>{text['moving']}</td><td></td></tr>
              <tr><td></td><td></td><td>0.70</td><td>{text['thin_1_2']}</td><td>{text['moving']}</td><td></td></tr>
              <tr><td>{text['naked']}</td><td>{text['moving']}</td><td>0.75</td><td></td><td></td><td></td></tr>
              <tr><td>{text['thin_1_2']}</td><td>{text['moving']}</td><td>0.90</td><td>{text['thicker_2_plus']}</td><td>{text['moving']}</td><td></td></tr>
              <tr><td>{text['naked']}</td><td>{text['still']}</td><td>1.00</td><td></td><td></td><td></td></tr>
              <tr><td>{text['thin_1_2']}</td><td>{text['still']}</td><td>1.10</td><td>{text['thicker_2']}</td><td>{text['still']}</td><td></td></tr>
              <tr><td>{text['thin_2_3']}</td><td></td><td>1.20</td><td>{text['more_than_2_thicker']}</td><td>{text['still']}</td><td></td></tr>
              <tr><td>{text['thicker_1_2']}</td><td>{text['moving_or_still']}</td><td>1.20</td><td></td><td></td><td></td></tr>
              <tr><td>{text['thin_3_4']}</td><td></td><td>1.30</td><td></td><td></td><td></td></tr>
              <tr><td>{text['more_layers']}</td><td>{text['without_influence']}</td><td>1.40</td><td></td><td></td><td></td></tr>
              <tr><td>{text['thick_bedspread']}</td><td></td><td>1.80</td><td></td><td></td><td></td></tr>
              <tr><td>{text['clothing_combined']}</td><td></td><td>2.40</td><td></td><td></td><td></td></tr>
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
              <tr><td>{text['no']}</td><td>1.3</td></tr>
              <tr>
                <td rowspan="2">{text['mattress']}</td>
                <td>{text['yes']}</td><td>+0.1</td>
              </tr>
              <tr><td>{text['no']}</td><td>1.1–1.2</td></tr>
              <tr>
                <td rowspan="3"><strong>{text['conducting']}</strong><br>{text['concrete']}</td>
                <td>{text['thick']}</td><td>−0.1</td>
              </tr>
              <tr><td>{text['very_thin']}</td><td>−0.2</td></tr>
              <tr><td>{text['no']}</td><td>0.75</td></tr>
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{text['adapted']}: {_HENSSGE_SPECIAL_REFERENCE}")


def _render_henssge_weight_table(language: str) -> None:
    text = _HENSSGE_WEIGHT_TABLE_TEXT[language]
    blank = "<td></td>"
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
                <td>1.6</td><td>1.6</td><td>1.6</td><td>1.6</td><td>1.5</td><td>1.4</td>
                <td>1.3</td><td>1.2</td><td>1.2</td><td class="weight-reference">1.2</td>{blank * 8}
              </tr>
              <tr>
                <td>2.1</td><td>2.1</td><td>2.0</td><td>2.0</td><td>1.9</td><td>1.8</td>
                <td>1.6</td><td>1.4</td><td>1.4</td><td class="weight-reference">1.4</td><td>1.3</td><td>1.3</td>{blank * 6}
              </tr>
              <tr>
                <td rowspan="3">{text['bedspread']}</td>
                <td>2.7</td><td>2.7</td><td>2.6</td><td>2.5</td><td>2.3</td><td>2.2</td>
                <td>2.1</td><td>2.0</td><td>1.8</td><td class="weight-reference">1.6</td><td>1.6</td><td>1.6</td>
                <td>1.5</td><td>1.4</td><td>1.4</td>{blank * 3}
              </tr>
              <tr>
                <td>3.5</td><td>3.4</td><td>3.3</td><td>3.2</td><td>2.8</td><td>2.6</td>
                <td>2.4</td><td>2.3</td><td>2.0</td><td class="weight-reference">1.8</td><td>1.8</td><td>1.7</td>
                <td>1.6</td><td>1.6</td><td>1.5</td><td>1.5</td>{blank * 2}
              </tr>
              <tr>
                <td>4.5</td><td>4.3</td><td>4.1</td><td>3.9</td><td>3.4</td><td>3.0</td>
                <td>2.8</td><td>2.6</td><td>2.4</td><td class="weight-reference">2.2</td><td>2.1</td><td>2.0</td>
                <td>1.9</td><td>1.8</td><td>1.7</td><td>1.7</td><td>1.6</td><td>1.6</td>
              </tr>
              <tr>
                <td rowspan="2">{text['clothing_bedspread']}</td>
                <td>5.7</td><td>5.3</td><td>5.0</td><td>4.8</td><td>4.0</td><td>3.5</td>
                <td>3.2</td><td>2.9</td><td>2.7</td><td class="weight-reference">2.4</td><td>2.3</td><td>2.2</td>
                <td>2.1</td><td>1.9</td><td>1.9</td><td>1.8</td><td>1.7</td><td>1.6</td>
              </tr>
              <tr>
                <td>7.1</td><td>6.6</td><td>6.2</td><td>5.8</td><td>4.7</td><td>4.0</td>
                <td>3.6</td><td>3.2</td><td>2.9</td><td class="weight-reference">2.6</td><td>2.5</td><td>2.3</td>
                <td>2.2</td><td>2.1</td><td>2.0</td><td>1.9</td><td>1.8</td><td>1.7</td>
              </tr>
              <tr>
                <td rowspan="2">{text['feather_bed']}</td>
                <td>8.8</td><td>8.1</td><td>7.5</td><td>7.0</td><td>5.5</td><td>4.6</td>
                <td>3.9</td><td>3.5</td><td>3.2</td><td class="weight-reference">2.8</td><td>2.7</td><td>2.5</td>
                <td>2.3</td><td>2.2</td><td>2.0</td><td>1.9</td><td>1.8</td><td>1.7</td>
              </tr>
              <tr>
                <td>10.9</td><td>9.8</td><td>8.9</td><td>8.3</td><td>6.2</td><td>5.1</td>
                <td>4.3</td><td>3.8</td><td>3.4</td><td class="weight-reference">3.0</td><td>2.8</td><td>2.6</td>
                <td>2.4</td><td>2.3</td><td>2.1</td><td>2.0</td><td>1.9</td><td>1.8</td>
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

st.markdown(
    """
    <style>
    .mallach-table-wrap {
        width: 100%;
        overflow-x: auto;
        margin: 0.08rem 0 0.16rem 0;
    }
    table.mallach-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.70rem;
        line-height: 1.05;
    }
    table.mallach-table caption {
        font-size: 0.73rem;
        line-height: 1.08;
        padding-bottom: 0.14rem !important;
    }
    .mallach-table th,
    .mallach-table td {
        border: 1px solid rgba(128,128,128,.35);
        padding: 0.13rem 0.20rem;
        vertical-align: middle;
    }
    .mallach-table thead th {
        text-align: center;
        font-weight: 650;
        background: rgba(128,128,128,.08);
        line-height: 1.05;
    }
    .mallach-table td:first-child {
        text-align: left;
        min-width: 9.8rem;
    }
    .mallach-table td:not(:first-child) {
        text-align: center;
        white-space: nowrap;
    }
    .mallach-table .group-row td {
        font-weight: 650;
        background: rgba(128,128,128,.05);
    }
    .mallach-table .subcriterion {
        padding-left: 0.50rem;
    }
    .mallach-table .subcriterion.nested {
        padding-left: 1rem;
    }
    .mallach-note {
        font-size: 0.64rem;
        line-height: 1.10;
        margin-top: 0.14rem;
    }
    .combined-table td:first-child {
        min-width: 9rem;
    }
    .combined-table th:nth-child(2),
    .combined-table th:nth-child(4) {
        min-width: 5.2rem;
    }
    .combined-table th:nth-child(3),
    .combined-table th:nth-child(5) {
        min-width: 6.2rem;
    }
    .henssge-base-table td:first-child,
    .henssge-base-table td:nth-child(4) {
        min-width: 8.5rem;
    }
    .henssge-base-table td:nth-child(4) {
        white-space: normal;
    }
    .henssge-base-table th:nth-child(2),
    .henssge-base-table th:nth-child(5),
    .henssge-base-table th:nth-child(6) {
        min-width: 4.5rem;
    }
    .henssge-base-table th:nth-child(3) {
        min-width: 5rem;
    }
    .henssge-special-table td:first-child {
        min-width: 10rem;
        white-space: normal;
    }
    .henssge-special-table th:nth-child(2) {
        min-width: 5rem;
    }
    .henssge-special-table th:nth-child(3) {
        min-width: 6rem;
    }
    .henssge-weight-table {
        font-size: 0.64rem !important;
    }
    .henssge-weight-table td:first-child {
        min-width: 8.2rem;
        white-space: normal;
    }
    .henssge-weight-table th:not(:first-child),
    .henssge-weight-table td:not(:first-child) {
        min-width: 2.25rem;
        padding-left: 0.12rem;
        padding-right: 0.12rem;
    }
    .henssge-weight-table .weight-reference {
        font-weight: 700;
        background: rgba(128,128,128,.10);
    }
    .henssge-table-title {
        font-size: 0.78rem;
        font-weight: 650;
        line-height: 1.05;
        margin: 0.20rem 0 0.02rem 0;
    }
    div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
        margin-top: -0.16rem !important;
        margin-bottom: -0.28rem !important;
    }
    div[data-testid="stRadio"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.08rem !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] > label {
        margin: 0 !important;
        padding: 0 0.04rem 0 0 !important;
    }
    div[data-testid="stRadio"] label p {
        font-size: 0.68rem !important;
        line-height: 1 !important;
    }
    div[data-testid="stCaptionContainer"] p {
        font-size: 0.62rem !important;
        line-height: 1.10 !important;
    }
    div[data-testid="stMarkdownContainer"] h2 {
        font-size: 1.15rem !important;
        margin-top: 0.70rem !important;
        margin-bottom: 0.05rem !important;
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

st.markdown("## Metodi combinati")
combined_language = st.radio(
    "Lingua tabella metodi combinati",
    ["Italiano", "English"],
    horizontal=True,
    key="combined_table_language",
    label_visibility="collapsed",
)
_render_combined_table("it" if combined_language == "Italiano" else "en")

# --- Sezione 2: Tabelle Henssge ---
st.markdown("## Fattori di correzione")

_base_language_before = st.session_state.get("henssge_base_table_language", "Italiano")
st.markdown(
    "<div class='henssge-table-title'>"
    + (
        "Tabella 1 — Fattori di correzione base"
        if _base_language_before == "Italiano"
        else "Table 1 — Basic correction factors"
    )
    + "</div>",
    unsafe_allow_html=True,
)
henssge_base_language = st.radio(
    "Lingua tabella fattori di correzione base",
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
        "Tabella 2 — Situazioni speciali"
        if _special_language_before == "Italiano"
        else "Table 2 — Special situations"
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
        "Tabella 3 — Adattamento per peso corporeo"
        if _weight_language_before == "Italiano"
        else "Table 3 — Body-weight adjustment"
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

if st.button("⬅️ Torna alla pagina principale", key="back_home"):
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
