import streamlit as st

from app.mobile_shell import install_minimal_mobile_shell


install_minimal_mobile_shell()


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
    "Tables 1–2.",
    "[3] Henssge C, Madea B. Integration of different methods in casework. "
    "In: Madea B, ed. Estimation of the Time Since Death. 3rd ed. CRC Press; 2016. "
    "Chapter 10.1, Table 10.4; Figure 10.7.",
    "[4] Anders S, Kunz M, Gehl A, Sehner S, Raupach T, Beck-Bornholdt H-P. "
    "Estimation of the time since death—reconsidering the re-establishment of rigor mortis. "
    "Int J Legal Med. 2013;127(1):127–130. "
    "[doi:10.1007/s00414-011-0632-z](https://doi.org/10.1007/s00414-011-0632-z).",
    "[5] Madea B. Supravitality in tissues. In: Madea B, ed. Estimation of the Time Since Death. "
    "3rd ed. CRC Press; 2016. Chapter 3, Tables 3.1–3.2, 3.5.",
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
        "confluence": "Sono confluenti?",
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
        "whole_muscle": "La percussione del muscolo provoca la contrazione dell’intero muscolo?",
        "reversible_swelling": "La percussione del muscolo provoca una tumefazione reversibile?",
        "mechanical_response": "È presente una risposta alla percussione del muscolo (contrazione dell’intero muscolo, tumefazione reversibile o piccola tumefazione persistente)?",
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
            "I limiti temporali indicati non corrispondono tutti a intervalli statistici al 95% "
            "e non costituiscono soglie biologiche assolute."
        ),
        "supra_note": (
            "Per l’eccitabilità sopraciliare, «Sì» comprende anche una contrazione più estesa: "
            "il limite minimo deriva dalla risposta immediatamente più estesa non ottenibile, quello massimo "
            "dalla risposta conservata [1, 3]."
        ),
        "reading_note": (
            "«—»: nessun limite utile. Nelle domande sul decorso, «No» significa «non ancora»; "
            "per migrabilità ed eccitabilità, indica una risposta non ottenibile. "
            "I reperti non valutati o non attendibili non equivalgono a «No»."
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
        "whole_muscle": "Does percussion of the muscle cause contraction of the whole muscle?",
        "reversible_swelling": "Does percussion of the muscle cause a reversible swelling?",
        "mechanical_response": "Is a response to muscle percussion present (whole-muscle contraction, reversible swelling or a small persistent swelling)?",
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
            "The stated time limits do not all represent 95% statistical intervals "
            "and are not absolute biological thresholds."
        ),
        "supra_note": (
            "For supraciliary excitability, “Yes” also includes a more extensive contraction: "
            "the lower limit comes from the next more extensive response that cannot be elicited, "
            "and the upper limit from the preserved response [1, 3]."
        ),
        "reading_note": (
            "“—”: no useful limit. For questions on progression, “No” means “not yet”; "
            "for shifting and excitability, it means that the response cannot be elicited. "
            "Unassessed or unreliable findings do not count as “No”."
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


def _render_combined_table(language: str) -> None:
    text = _COMBINED_TABLE_TEXT[language]
    # Scientific reference data: these limits are not read from application ranges.
    # A missing useful bound is shown as a dash, not as an artificial zero.
    groups = (
        ("lividity", "[1, 2]", (
            ("lividity_beginning", "—", "≤ 3"),
            ("confluence", "≥ 1", "≤ 4"),
            ("maximum_row", "≥ 3", "≤ 16"),
            ("thumb_pressure", "≤ 20", "≥ 1"),
            ("complete_shifting", "≤ 6", "≥ 2"),
            ("incomplete_shifting", "≤ 24", "≥ 4"),
        )),
        ("rigor", "[1–4]", (
            ("rigor_beginning", "≥ 0.5", "≤ 7"),
            ("rigor_complete", "≥ 2", "≤ 20"),
            # Observed upper extreme in Anders et al. (2013), not a universal cutoff.
            ("reestablishment", "≤ 19 [4]", "≥ 2"),
            # Agreed adaptation of the descriptive course limits in [2].
            ("rigor_persistence", "≥ 24", "≤ 96"),
            ("rigor_resolution", "≥ 24", "≤ 192"),
        )),
        ("mechanical", "[1, 5]", (
            ("whole_muscle", "≤ 2.5", "—"),
            ("reversible_swelling", "≤ 5", "—"),
            # The negative bound applies only when no mechanical response is obtained.
            # The 13-hour compound-method limit remains distinct from Table 3.5's 8–12 h.
            ("mechanical_response", "≤ 13", "≥ 1.5"),
        )),
        # Table 10.4 and Figure 10.7 in [3]: each question is cumulative.
        # A negative response concerns this extent, not absence of all contraction.
        ("eyebrow", "[1, 3]", (
            ("supra_cheek", "≤ 6", "≥ 1"),
            ("supra_forehead", "≤ 7", "≥ 2"),
            ("supra_lower_lid", "≤ 8", "≥ 3"),
            ("supra_whole_upper_lid", "≤ 13", "≥ 3.5"),
            ("supra_partial_upper_lid", "≤ 16", "≥ 5"),
            ("supra_nasal", "≤ 22", "≥ 5"),
        )),
        ("mouth", "[1]", (("muscle_response", "≤ 11", "≥ 3"),)),
        ("chemical", "[1, 5]", (
            ("atropin", "≤ 10", "≥ 3"),
            ("tropicamide", "≤ 30", "≥ 5"),
            ("acetylcholine", "≤ 46", "≥ 14"),
        )),
    )
    rows = []
    for parameter, reference, criteria in groups:
        for index, (criterion, yes, no) in enumerate(criteria):
            group_cell = (
                f'<th scope="rowgroup" rowspan="{len(criteria)}" class="combined-group">'
                f'{text[parameter]} {reference}</th>' if index == 0 else ""
            )
            rows.append(
                f'<tr>{group_cell}<td class="combined-criterion">{text[criterion]}</td>'
                f'<td class="combined-limit">{yes}</td><td class="combined-limit">{no}</td></tr>'
            )
    st.markdown(
        f"""
        <p class="combined-intro" style="font-size:1.0625rem;line-height:1.55;font-weight:400;color:inherit;margin:0 0 1rem;">{text['intro']}</p>
        <div class="mallach-table-wrap">
          <table class="mallach-table combined-table">
            <caption>{text['caption']}</caption>
            <colgroup><col style="width:24%"><col style="width:46%"><col style="width:15%"><col style="width:15%"></colgroup>
            <thead>
              <tr><th scope="col">{text['parameter']}</th><th scope="col">{text['criterion']}</th>
              <th scope="col">{text['yes']}</th><th scope="col">{text['no']}</th></tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(text["reading_note"])
    st.caption(text["supra_note"])
    st.caption(text["variation_note"])
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

# Scientific synthesis of the compound method.
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
