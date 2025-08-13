# -*- coding: utf-8 -*-
import streamlit as st

# Titolo grande e in grassetto
st.markdown("# **Riferimenti bibliografici**")

# Testo in markdown: corsivo solo per i titoli di libri/articoli
REFERENCES_MD = """
- *Handbook of Forensic Medicine*. Editor: Burkhard Madea, 2022 — Chapter 7: Post-mortem changes and time since death.
- PHP-code written and implemented 2005 by Wolf Schweitzer, MD, Institute of Legal Medicine, University of Zurich, Switzerland — method described by Henssge C (2002). [Swisswuff – Time of Death Calculator](https://www.swisswuff.ch/calculators/todeszeit.php)
- Otatsume M, Shinkawa N, Tachibana M, Kuroki H, Ro A, Sonoda A, Kakizaki E, Yukawa N. *Technical note: Excel spreadsheet calculation of the Henssge equation as an aid to estimating postmortem interval*. J Forensic Leg Med. 2024.
- Mallach HJ. *Zur Frage der Todeszeitbestimmung*. Berl Med. 1964;18:577–582.
- Potente S, Kettner M, Verhoff MA, Ishikawa T. *Minimum time since death when the body has either reached or closely approximated equilibrium with ambient temperature*. Forensic Sci Int. 2017;281:63–66. doi: 10.1016/j.forsciint.2017.09.012. PMID: 29102846.
- Henssge C, Madea B. *Estimation of the time since death in the early post-mortem period*. Forensic Science International. 2004;144(2):167–175.
- Henssge C. *Todeszeitschätzungen durch die mathematische Beschreibung der rektalen Leichenabkühlung unter verschiedenen Abkühlbedingungen*. Z Rechtsmed. 1981;187:147–178.
- Henssge C. *Todeszeitbestimmung an Leichen*. Rechtsmedizin. 2002;12:112–131.
"""

st.markdown(REFERENCES_MD)
