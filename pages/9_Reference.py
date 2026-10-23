# -*- coding: utf-8 -*-
import streamlit as st

from app.mobile_shell import install_minimal_mobile_shell
from app.language import render_language_selector
from app.page_heading import render_page_heading
from app.page_navigation import (
    FC_VIEW, REFERENCES_PAGE, previous_view, record_page_visit, render_back_button,
)


install_minimal_mobile_shell()
record_page_visit(st.session_state, REFERENCES_PAGE)

# Same title typography as the main page, with mobile header integration.
render_page_heading("Riferimenti bibliografici")

if st.session_state.get("__fc_active"):
    if previous_view(st.session_state, REFERENCES_PAGE) == FC_VIEW:
        render_back_button(REFERENCES_PAGE, key="back_to_fc_top")
    selected = st.session_state.get("__fc_reference", {})
    if selected.get("full"):
        st.subheader(selected.get("short", "Riferimento selezionato"))
        st.write(selected["full"])
        url = selected.get("url", "")
        if url.startswith("https://doi.org/"):
            st.markdown(f"[DOI: {url.removeprefix('https://doi.org/')}]({url})")
        st.divider()

# Testo in markdown: corsivo solo per i titoli di libri/articoli
REFERENCES_MD = """
- *Handbook of Forensic Medicine*. Editor: Burkhard Madea, 2022 — Chapter 7: Post-mortem changes and time since death.
- PHP-code written and implemented 2005 by Wolf Schweitzer, MD, Institute of Legal Medicine, University of Zurich, Switzerland — method described by Henssge C (2002). [Swisswuff – Time of Death Calculator](https://www.swisswuff.ch/calculators/todeszeit.php)
- Schweitzer W, Thali MJ. *Computationally approximated solution for the equation for Henssge’s time of death estimation*. BMC Med Inform Decis Mak. 2019;19:201. [doi: 10.1186/s12911-019-0920-y](<https://doi.org/10.1186/s12911-019-0920-y>).
- Otatsume M, Shinkawa N, Tachibana M, Kuroki H, Ro A, Sonoda A, Kakizaki E, Yukawa N. *Technical note: Excel spreadsheet calculation of the Henssge equation as an aid to estimating postmortem interval*. J Forensic Leg Med. 2024;101:102634. [doi: 10.1016/j.jflm.2023.102634](<https://doi.org/10.1016/j.jflm.2023.102634>) (pubblicazione online: 6 dicembre 2023).
- Henssge C. *Death time estimation in case work. I. The rectal temperature time of death nomogram*. Forensic Sci Int. 1988;38(3–4):209–236. [doi: 10.1016/0379-0738(88)90168-5](<https://doi.org/10.1016/0379-0738(88)90168-5>).
- Henssge C. *Rectal temperature time of death nomogram: dependence of corrective factors on the body weight under stronger thermic insulation conditions*. Forensic Sci Int. 1992;54(1):51–66. [doi: 10.1016/0379-0738(92)90080-G](<https://doi.org/10.1016/0379-0738(92)90080-G>).
- Althaus L, Stückradt S, Henssge C, Bajanowski T. *Cooling experiments using dummies covered by leaves*. Int J Legal Med. 2007;121(2):112–114. [doi: 10.1007/s00414-006-0108-8](<https://doi.org/10.1007/s00414-006-0108-8>).
- Heinrich F, Rimkus-Ebeling F, Dietz E, Raupach T, Ondruschka B, Anders-Lohner S. *An assessment of the Henssge method for forensic death time estimation in the early post-mortem interval*. Int J Legal Med. 2025;139(1):105–117. [doi: 10.1007/s00414-024-03338-5](<https://doi.org/10.1007/s00414-024-03338-5>).
- Scendoni R, Tomassini L, Bianchini G, Baldelli L, Fedeli P, Cingolani M. *Transitioning from conventional to digital methods for estimating time since death: a multi-parameter forensic software*. J Forensic Leg Med. 2025;116:103009. [doi: 10.1016/j.jflm.2025.103009](<https://doi.org/10.1016/j.jflm.2025.103009>).
- Mallach HJ. *Zur Frage der Todeszeitbestimmung*. Berl Med. 1964;18:577–582.
- Potente S, Kettner M, Verhoff MA, Ishikawa T. *Minimum time since death when the body has either reached or closely approximated equilibrium with ambient temperature*. Forensic Sci Int. 2017;281:63–66. [doi: 10.1016/j.forsciint.2017.09.012](<https://doi.org/10.1016/j.forsciint.2017.09.012>). PMID: 29102846.
- Henssge C, Madea B. *Estimation of the time since death in the early post-mortem period*. Forensic Sci Int. 2004;144(2–3):167–175. [doi: 10.1016/j.forsciint.2004.04.051](<https://doi.org/10.1016/j.forsciint.2004.04.051>).
- Henssge C. *Todeszeitschätzungen durch die mathematische Beschreibung der rektalen Leichenabkühlung unter verschiedenen Abkühlbedingungen*. Z Rechtsmed. 1981;87(3):147–178. [doi: 10.1007/BF00204763](<https://doi.org/10.1007/BF00204763>).
- Henssge C. *Todeszeitbestimmung an Leichen*. Rechtsmedizin. 2002;12(2):112–131. [doi: 10.1007/s00194-002-0136-8](<https://doi.org/10.1007/s00194-002-0136-8>).
- Madea B, ed. *Estimation of the Time Since Death*. 3rd ed. CRC Press; 2016. Henssge C, Chapter 6.1: *Basics and application of the ‘nomogram method’ at the scene*, pp. 63–113. Edizione delle pagine consultate per tabelle e casi FC; distinta da *Handbook of Forensic Medicine* (2022).
- Henssge C, Althaus L, Bolt J, Freislederer A, Haffner H-T, Henssge CA, Hoppe B, Schneider V. *Experiences with a compound method for estimating the time since death. I. Rectal temperature nomogram for time since death*. Int J Legal Med. 2000;113(6):303–319. [doi: 10.1007/s004149900089](https://doi.org/10.1007/s004149900089). Casi consultati nella terza edizione di Madea, tabelle 6.17 e 6.21; testo integrale originale da acquisire.
- Henssge C, Althaus L, Bolt J, Freislederer A, Haffner H-T, Henssge CA, Hoppe B, Schneider V. *Experiences with a compound method for estimating the time since death. II. Integration of non-temperature-based methods*. Int J Legal Med. 2000;113(6):320–331. [doi: 10.1007/s004149900090](https://doi.org/10.1007/s004149900090).
- Henssge C, Brinkmann B. *Todeszeitbestimmung aus der Rektaltemperatur. Mathematische Analyse von empirischem Material versus thermodynamische Modellierung. Eine kritische Falldarstellung*. Arch Kriminol. 1984;174(3–4):96–112. [PMID: 6508475](https://pubmed.ncbi.nlm.nih.gov/6508475/). Dati sul bagnato citati in Madea, 3rd ed., 2016, tabella 6.8.
- Henssge C, Brinkmann B, Püschel K. *Todeszeitbestimmung durch Messung der Rektaltemperatur bei Wassersuspension der Leiche*. Z Rechtsmed. 1984;92(4):255–276. [doi: 10.1007/BF00200284](https://doi.org/10.1007/BF00200284). Dati sull’immersione citati in Madea, 3rd ed., 2016, tabella 6.7.
- Henssge C, Madea B. *Methoden zur Bestimmung der Todeszeit an der Leiche*. Lübeck: Schmidt-Römhild; 1988. Citato in Madea, 3rd ed., 2016, tabelle 6.4–6.6, per gli esperimenti con indumenti e coperture.
- Stipanits E, Henssge C. *Präzisionsvergleich von Todeszeitrückrechnungen ohne und mit Berücksichtigung von Einflussfaktoren*. Beitr Gerichtl Med. 1985;43:323–329. Citato in Madea, 3rd ed., 2016, tabella 6.4; originale non consultato.
- Knörle T. *Normierungsvarianten für die Wärmeflussmessung an einem Kunstkörper*. Cologne: University of Cologne; MD thesis; 1991. Citato in Madea, 3rd ed., 2016, tabella 6.10 e riferimento 90, per le prove su simulatore e piani di appoggio; tesi non consultata integralmente.
- Madea B. *Methods for determining time of death*. Forensic Sci Med Pathol. 2016;12(4):451–485. [doi: 10.1007/s12024-016-9776-y](https://doi.org/10.1007/s12024-016-9776-y).
- Henriksson O, Lundgren JP, Kuklane K, Holmér I, Bjornstig U. *Protection against cold in prehospital care—thermal insulation properties of blankets and rescue bags in different wind conditions*. Prehosp Disaster Med. 2009;24(5):408–415. [doi: 10.1017/S1049023X00007238](<https://doi.org/10.1017/S1049023X00007238>).
- Anders S, Kunz M, Gehl A, Sehner S, Raupach T, Beck-Bornholdt H-P. *Estimation of the time since death—reconsidering the re-establishment of rigor mortis*. Int J Legal Med. 2013;127(1):127–130. [doi: 10.1007/s00414-011-0632-z](<https://doi.org/10.1007/s00414-011-0632-z>).
- Henssge C, Madea B. *Integration of different methods in casework*. In: Madea B, ed. *Estimation of the Time Since Death*. 3rd ed. CRC Press; 2016. Chapter 10.1, Table 10.4; Figure 10.7.
- Madea B. *Supravitality in tissues*. In: Madea B, ed. *Estimation of the Time Since Death*. 3rd ed. CRC Press; 2016. Chapter 3, Tables 3.1–3.2, 3.5.
"""

st.markdown(REFERENCES_MD)

render_back_button(REFERENCES_PAGE, key="back_home")

st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: transparent !important;
        color: #1e90ff !important;
        font-size: 10px !important;  /* più piccolo del normale */
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

render_language_selector()
