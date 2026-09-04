# -*- coding: utf-8 -*-
import streamlit as st

from app.mobile_shell import install_minimal_mobile_shell


install_minimal_mobile_shell()

# Titolo grande e in grassetto
st.markdown("# **Riferimenti bibliografici**")

# Testo in markdown: corsivo solo per i titoli di libri/articoli
REFERENCES_MD = """
- *Handbook of Forensic Medicine*. Editor: Burkhard Madea, 2022 — Chapter 7: Post-mortem changes and time since death.
- PHP-code written and implemented 2005 by Wolf Schweitzer, MD, Institute of Legal Medicine, University of Zurich, Switzerland — method described by Henssge C (2002). [Swisswuff – Time of Death Calculator](https://www.swisswuff.ch/calculators/todeszeit.php)
- Schweitzer W, Thali MJ. *Computationally approximated solution for the equation for Henssge’s time of death estimation*. BMC Med Inform Decis Mak. 2019;19:201. doi: 10.1186/s12911-019-0920-y.
- Otatsume M, Shinkawa N, Tachibana M, Kuroki H, Ro A, Sonoda A, Kakizaki E, Yukawa N. *Technical note: Excel spreadsheet calculation of the Henssge equation as an aid to estimating postmortem interval*. J Forensic Leg Med. 2024.
- Henssge C. *Death time estimation in case work. I. The rectal temperature time of death nomogram*. Forensic Sci Int. 1988;38(3–4):209–236. doi: 10.1016/0379-0738(88)90168-5.
- Henssge C. *Rectal temperature time of death nomogram: dependence of corrective factors on the body weight under stronger thermic insulation conditions*. Forensic Sci Int. 1992;54(1):51–66. doi: 10.1016/0379-0738(92)90080-G.
- Althaus L, Stückradt S, Henssge C, Bajanowski T. *Cooling experiments using dummies covered by leaves*. Int J Legal Med. 2007;121(2):112–114. doi: 10.1007/s00414-006-0108-8.
- Heinrich F, Rimkus-Ebeling F, Dietz E, Raupach T, Ondruschka B, Anders-Lohner S. *An assessment of the Henssge method for forensic death time estimation in the early post-mortem interval*. Int J Legal Med. 2025;139(1):105–117. doi: 10.1007/s00414-024-03338-5.
- Scendoni R, Tomassini L, Bianchini G, Baldelli L, Fedeli P, Cingolani M. *Transitioning from conventional to digital methods for estimating time since death: a multi-parameter forensic software*. J Forensic Leg Med. 2025;116:103009. doi: 10.1016/j.jflm.2025.103009.
- Mallach HJ. *Zur Frage der Todeszeitbestimmung*. Berl Med. 1964;18:577–582.
- Potente S, Kettner M, Verhoff MA, Ishikawa T. *Minimum time since death when the body has either reached or closely approximated equilibrium with ambient temperature*. Forensic Sci Int. 2017;281:63–66. doi: 10.1016/j.forsciint.2017.09.012. PMID: 29102846.
- Henssge C, Madea B. *Estimation of the time since death in the early post-mortem period*. Forensic Science International. 2004;144(2):167–175.
- Henssge C. *Todeszeitschätzungen durch die mathematische Beschreibung der rektalen Leichenabkühlung unter verschiedenen Abkühlbedingungen*. Z Rechtsmed. 1981;187:147–178.
- Henssge C. *Todeszeitbestimmung an Leichen*. Rechtsmedizin. 2002;12:112–131.
"""

st.markdown(REFERENCES_MD)

if st.button("⬅️ Torna alla pagina principale", key="back_home"):
    st.switch_page("app.py")

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
