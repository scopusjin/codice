import streamlit as st

from app import i18n


_MALLACH_REFERENCE = (
    "Handbook of Forensic Medicine. Editor: Burkhard Madea, 2022 — "
    "Chapter 7: Post-mortem changes and time since death; dati da: "
    "Mallach HJ. Zur Frage der Todeszeitbestimmung. Berl Med. 1964;18:577–582."
)


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
    .mallach-note {
        font-size: 0.78rem;
        line-height: 1.3;
        margin-top: 0.35rem;
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
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Rigor%20(Mallach).jpeg",
    caption="Rigor (Mallach)",
    use_container_width=True
)

st.markdown("## Metodi combinati")
st.image(
    "https://raw.githubusercontent.com/scopusjin/codice/Fattore-di-correzione/immagini/Metodi%20combinati.jpeg",
    caption="Metodi combinati",
    use_container_width=True
)

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
