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

_RIGOR_TABLE_TEXT = {
    "it": {
        "caption": "Tabella 1 — Decorso temporale della rigidità cadaverica",
        "phase": "Fase della rigidità",
        "mean": "Media con deviazione standard",
        "hours": "Ore post-mortem",
        "probability": "Limiti della probabilità del 95,5% (2 s)",
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
        "minimum": "Limite minimo del periodo dalla morte (hpm)",
        "maximum": "Limite massimo del periodo dalla morte (hpm)",
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
        "minimum": "Minimum limit of the period since death (hpm)",
        "maximum": "Maximum limit of the period since death (hpm)",
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


st.title("Tabelle di riferimento")

# --- Sezione 1: Mallach ---
st.markdown(f"## {i18n.ui_text('full.livor_heading')}")
st.markdown(
    """
    <style>
    .mallach-table-wrap {
        width: 100%;
        overflow-x: auto;
        margin: 0.25rem 0 0.35rem 0;
    }
    table.mallach-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        line-height: 1.2;
    }
    .mallach-table th,
    .mallach-table td {
        border: 1px solid rgba(128,128,128,.35);
        padding: 0.38rem 0.42rem;
        vertical-align: middle;
    }
    .mallach-table thead th {
        text-align: center;
        font-weight: 650;
        background: rgba(128,128,128,.08);
    }
    .mallach-table td:first-child {
        text-align: left;
        min-width: 13rem;
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
        padding-left: 1rem;
    }
    .mallach-table .subcriterion.nested {
        padding-left: 2rem;
    }
    .mallach-note {
        font-size: 0.78rem;
        line-height: 1.3;
        margin-top: 0.35rem;
    }
    .combined-table td:first-child {
        min-width: 12rem;
    }
    .combined-table th:nth-child(2),
    .combined-table th:nth-child(4) {
        min-width: 7.5rem;
    }
    .combined-table th:nth-child(3),
    .combined-table th:nth-child(5) {
        min-width: 8.5rem;
    }
    </style>

    <div class="mallach-table-wrap">
      <table class="mallach-table">
        <caption style="caption-side:top;text-align:left;font-weight:650;padding-bottom:.45rem;">
          Decorso temporale dei diversi criteri delle ipostasi: calcoli statistici di Mallach basati su dati riportati nei testi*
        </caption>
        <thead>
          <tr>
            <th rowspan="2">Criterio</th>
            <th rowspan="2">x̄</th>
            <th rowspan="2">DS</th>
            <th colspan="2">2 DS</th>
            <th colspan="2">Range di dispersione</th>
            <th rowspan="2">N. citazioni</th>
          </tr>
          <tr>
            <th>Limite inferiore</th>
            <th>Limite superiore</th>
            <th>Limite inferiore</th>
            <th>Limite superiore</th>
          </tr>
        </thead>
        <tbody>
          <tr><td>Sviluppo</td><td>¾</td><td>½</td><td>—</td><td>2</td><td>¼</td><td>3</td><td>17</td></tr>
          <tr><td>Confluenza</td><td>2½</td><td>1</td><td>¾</td><td>4¼</td><td>1</td><td>4</td><td>5</td></tr>
          <tr><td>Massima distensione e intensità</td><td>9½</td><td>4½</td><td>½</td><td>18¼</td><td>3</td><td>16</td><td>7</td></tr>
          <tr class="group-row"><td colspan="8">Scomparsa</td></tr>
          <tr><td class="subcriterion">1. Completa alla pressione con il pollice</td><td>5½</td><td>6</td><td>—</td><td>17½</td><td>1</td><td>20</td><td>5</td></tr>
          <tr><td class="subcriterion">2. Incompleta alla pressione puntiforme (pinza)</td><td>17</td><td>10½</td><td>—</td><td>37½</td><td>10</td><td>36</td><td>4</td></tr>
          <tr class="group-row"><td colspan="8">Spostamento dopo rotazione del corpo</td></tr>
          <tr><td class="subcriterion">1. Completo</td><td>3¾</td><td>1</td><td>2</td><td>5½</td><td>2</td><td>6</td><td>11</td></tr>
          <tr><td class="subcriterion">2. Incompleto</td><td>11</td><td>4½</td><td>2¼</td><td>20</td><td>4</td><td>24</td><td>11</td></tr>
          <tr><td class="subcriterion">3. Solo lieve impallidimento</td><td>18½</td><td>8</td><td>2½</td><td>34½</td><td>10</td><td>30</td><td>7</td></tr>
        </tbody>
      </table>
    </div>

    <div class="mallach-note">
      * I calcoli statistici non sono basati su studi trasversali o longitudinali, ma su conoscenze empiriche riportate nei testi.<br>
      x̄ = valore medio; DS = deviazione standard. Tutti i tempi sono espressi in ore post-mortem.
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Adattato da: {_MALLACH_REFERENCE}")

st.markdown("## Rigidità cadaverica")
rigor_it_tab, rigor_en_tab = st.tabs(["Italiano", "English"])
with rigor_it_tab:
    _render_rigor_table("it")
with rigor_en_tab:
    _render_rigor_table("en")

st.markdown("## Metodi combinati")
combined_it_tab, combined_en_tab = st.tabs(["Italiano", "English"])
with combined_it_tab:
    _render_combined_table("it")
with combined_en_tab:
    _render_combined_table("en")

# --- Sezione 2: Tabelle Henssge ---
st.markdown("## Fattori di correzione base")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Tabella%201%20henssge.png",
    caption="Tabella 1 henssge",
    use_container_width=True
)

st.markdown("Situazioni speciali")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Tabella%202%20Henssge.png",
    caption="Tabella 2 Henssge",
    use_container_width=True
)

st.markdown("Adattamento per peso corporeo")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Tabella%203%20Henssge.png",
    caption="Tabella 3 Henssge",
    use_container_width=True
)
if st.button("⬅️ Torna alla pagina principale", key="back_home"):
    st.switch_page("app.py")

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
