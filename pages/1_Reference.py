# -*- coding: utf-8 -*-
import streamlit as st
from references import REFERENCES_MD

st.title("References")
st.markdown(REFERENCES_MD)


"""
Riferimenti bibliografici per la stima dell'epoca della morte
"""

REFERENCES_MD = """
**References**

- Handbook of Forensic Medicine - Editor: Burkhard Madea, 2022 – Chapter 7 – *Post-mortem changes and time since death*.
- [Swisswuff - Time of Death Calculator](https://www.swisswuff.ch/calculators/todeszeit.php)
- Mallach HJ (1964) Zur Frage der Todeszeitbestimmung. *Berl Med* 18:577–582.
- Potente S, Kettner M, Verhoff MA, Ishikawa T. Minimum time since death when the body has either reached or closely approximated equilibrium with ambient temperature. *Forensic Sci Int*. 2017 Dec;281:63-66. doi: 10.1016/j.forsciint.2017.09.012. Epub 2017 Oct 28. PMID: 29102846.
- Henssge, C., and B. Madea. *Estimation of the time since death in the early post-mortem period*. *Forensic Science International* 144.2 (2004): 167-175.
- Henssge C. *Todeszeitschatzungen durch die mathematische Beschreibung der rektalen Leichenabkuhlung unter verschiedenen Abkuhlbedingungen*. *Z Rechtsmed*. 1981;187:147-178.
- Henssge C (2002) *Todeszeitbestimmung an Leichen*. *Rechtsmedizin* 12:112-131.
- PHP-code written and implemented 2005 by Wolf Schweitzer, MD, Institute of Legal Medicine, University of Zurich, Switzerland – method described by Henssge C (2002).
"""
