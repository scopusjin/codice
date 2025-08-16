# pages/02_Fattore_correzione_beta.py
import unicodedata
import pandas as pd
import streamlit as st

# =========================
# Config pagina
# =========================
st.set_page_config(
    page_title="Fattore di correzione (beta)",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Fattore di correzione — Pagina beta autonoma")
st.caption("Questa pagina è indipendente da quella principale. Puoi fare esperimenti qui senza toccare la logica della pagina ufficiale.")

# =========================
# Help / descrizioni (come da tuo testo)
# =========================
HELP_COPERTE = (
    "**Tenerne conto solo se coprono la parte bassa di torace/addome**.   "
    "**Lenzuolo +** = telo sottile/1-2 lenzuola;   "
    "**Lenzuolo ++** = lenzuolo invernale/copriletto leggero;   "
    "**Coperta** = coperta mezza stagione/ sacco mortuario;   "
    "**Coperta +** = coperta pesante/ mantellina termica;   "
    "**Coperta ++** = coperta molto pesante/ più coperte medie;   "
    "**Coperta +++** = coperta imbottita pesante (es piumino invernale);   "
    "**Coperta ++++** = molti strati di coperte;   "
    "**Foglie ++** = strato medio di foglie su corpo/vestiti;   "
    "**Foglie +++** = strato spesso di foglie."
)

HELP_VESTITI = (
    "**Tenere conto solo degli indumenti che coprono la parte bassa di torace/addome**.   "
    "**Strati sottili** = t-shirt, camicia, maglia leggera;    "
    "**Strati spessi** = maglione, felpa in pile, giubbino;   "
    "**˃ strati** = ˃4 sottili o ˃2 spessi;   "
    "**˃˃ strati** = molti strati pesanti,"
)

HELP_SUPERFICIE = (
    "**Indifferente** = pavimento di casa/parquet, prato o terreno asciutto, asfalto;   "
    "**Isolante** = materasso, tappeto spesso;   "
    "**Molto isolante** = polistirolo, sacco a pelo tecnico, divano imbottito;   "
    "**Conduttivo** = cemento, pietra, pavimento in PVC, pavimentazione esterna;   "
    "**Molto conduttivo** = superficie metallica spessa all’esterno;   "
    "**Foglie umide/secche (≥2 cm)** = adagiato su strato di foglie"
)

HELP_CORRENTI_ARIA = (
    "**Sì** = all'aria aperta, finestra aperta con aria corrente, ventilatore;   "
    "**No** = ambiente chiuso/nessuna corrente percepibile"
)

# =========================
# Utility cache per Excel
# =========================
@st.cache_data
def load_tabelle_correzione():
    """
    Carica e normalizza le tabelle usate da calcola_fattore.
    Restituisce (tabella1, tabella2) o solleva eccezione con messaggio chiaro.
    """
    try:
        t1 = pd.read_excel("tabella rielaborata.xlsx", engine="openpyxl")
        t2 = pd.read_excel("tabella secondaria.xlsx", engine="openpyxl")
    except FileNotFoundError:
        raise
    except ImportError as e:
        raise RuntimeError("Il pacchetto 'openpyxl' è richiesto per leggere i file Excel.") from e

    t1['Fattore'] = pd.to_numeric(t1['Fattore'], errors='coerce')
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    return t1, t2

# =========================
# Funzioni di supporto (normalizzazione & alias)
# =========================
def _norm(s):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return s
    s = unicodedata.normalize("NFKC", str(s)).strip()
    # uniforma tutte le varianti del maggiore
    s = (s.replace(">>", "˃˃")
           .replace("››", "˃˃")
           .replace("»»", "˃˃")
           .replace(">", "˃")
           .replace("›", "˃")
           .replace("»", "˃"))
    return " ".join(s.split())

OLD_TO_NEW_UI = {
    # Coperte
    "Coperta spessa (es copriletto)": "Coperta +",
    "Coperte più spesse (es coperte di lana)": "Coperta ++",
    "Coperta pesante (es piumino imbottito)": "Coperta +++",
    "Molte coperte pesanti": "Coperta ++++",
    "Lenzuolo +": "Lenzuolo +",
    "Lenzuolo ++": "Lenzuolo ++",
    "Nessuna coperta": "Nessuna coperta",
    # Alias coerenti con HELP
    "Coperta": "Coperta",
    "Sacco mortuario": "Coperta",

    # Superficie
    "Materasso o tappeto spesso": "Isolante",
    "Imbottitura pesante (es sacco a pelo isolante, polistirolo, divano imbottito)": "Molto isolante",
    "Pavimento di casa, terreno o prato asciutto, asfalto": "Indifferente",
    "Cemento, pietra, pavimento in PVC, pavimentazione esterna": "Conduttivo",
    "Conduttivo": "Conduttivo",
    "Superficie metallica spessa, all'esterno.": "Molto conduttivo",
}
NEW_TO_OLD = {}
for k, v in OLD_TO_NEW_UI.items():
    NEW_TO_OLD.setdefault(v, set()).add(k)

VESTITI_ALIASES = {
    "˃ strati": {"˃ strati", "> strati", "› strati"},
    "˃˃ strati": {"˃˃ strati", ">> strati", "›› strati"},
    "˃4 strati sottili o ˃2 spessi": {"˃4 strati sottili o ˃2 spessi", "˃ strati", "> strati", "› strati"},
    "Moltissimi strati": {"Moltissimi strati", "˃˃ strati", ">> strati", "›› strati"},
}

def _aliases(val: str, colname: str):
    """Restituisce un set di etichette equivalenti per la ricerca in tabella."""
    if val is None or val == "/":
        return {val}
    v = _norm(val)
    s = {v}
    if colname == "Vestiti":
        for key, alset in VESTITI_ALIASES.items():
            if v == key or v in alset:
                s |= {key}
                s |= set(alset)
    else:
        if v in OLD_TO_NEW_UI:
            s.add(OLD_TO_NEW_UI[v])
        if v in NEW_TO_OLD:
            s |= NEW_TO_OLD[v]
    return {_norm(x) for x in s}

LABEL_VESTITI = {
    "Nudo": "Nudo",
    "1-2 strati sottili": "1–2 sottili",
    "2-3 strati sottili": "2–3 sottili",
    "3-4 strati sottili": "3–4 sottili",
    "1-2 strati spessi": "1–2 spessi",
    "˃4 strati sottili o ˃2 spessi": "˃ strati",
    "Moltissimi strati": "˃˃ strati",
}
LABEL_COPERTE = {
    "Nessuna coperta": "Nessuna",
    "Lenzuolo +": "Lenzuolo +",
    "Lenzuolo ++": "Lenzuolo ++",
    "Coperta": "Coperta",
    "Coperta spessa (es copriletto)": "Coperta +",
    "Coperte più spesse (es coperte di lana)": "Coperta ++",
    "Coperta pesante (es piumino imbottito)": "Coperta +++",
    "Molte coperte pesanti": "Coperta ++++",
    "Coperta +": "Coperta +",
    "Coperta ++": "Coperta ++",
    "Coperta +++": "Coperta +++",
    "Coperta ++++": "Coperta ++++",
    "Strato di foglie di medio spessore": "Foglie ++",
    "Spesso strato di foglie": "Foglie +++",
}
LABEL_CORRENTI_ARIA = {"Esposto a corrente d'aria": "Sì", "Nessuna corrente": "No"}
LABEL_CORRENTI_ACQUA = {"In acqua corrente": "Acqua corrente", "In acqua stagnante": "Acqua stagnante"}
LABEL_SUPERFICIE = {
    "Pavimento di casa, terreno o prato asciutto, asfalto": "Indifferente",
    "Imbottitura pesante (es sacco a pelo isolante, polistirolo, divano imbottito)": "Molto isolante",
    "Materasso o tappeto spesso": "Isolante",
    "Cemento, pietra, pavimento in PVC, pavimentazione esterna": "Conduttivo",
    "Superficie metallica spessa, all'esterno.": "Molto conduttivo",
    "Foglie umide (≥2 cm)": "Foglie umide (≥2 cm)",
    "Foglie secche (≥2 cm)": "Foglie secche (≥2 cm)",
}

# =========================
# UI laterale: peso + caricamento opzionale tabelle
# =========================
with st.sidebar:
    st.header("Impostazioni")
    peso = st.number_input("Peso (kg)", min_value=10.0, max_value=250.0, value=70.0, step=0.5)

    st.markdown("---")
    st.caption("Opzionale: carica qui le tabelle per testare varianti (se omesso, uso i file nella cartella).")
    up1 = st.file_uploader("Tabella 1 (rielaborata)", type=["xlsx"], key="up_t1")
    up2 = st.file_uploader("Tabella 2 (secondaria)", type=["xlsx"], key="up_t2")

# Se l'utente carica file, sostituiamo il loader cache
if up1 and up2:
    try:
        t1 = pd.read_excel(up1, engine="openpyxl")
        t2 = pd.read_excel(up2, engine="openpyxl")
        t1['Fattore'] = pd.to_numeric(t1['Fattore'], errors='coerce')
        for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
            t1[col] = t1[col].astype(str).str.strip()
        tabella1, tabella2 = t1, t2
        st.sidebar.success("Tabelle caricate dalla sidebar.")
    except Exception as e:
        st.sidebar.error(f"Errore nel caricamento delle tabelle: {e}")
        tabella1, tabella2 = None, None
else:
    try:
        tabella1, tabella2 = load_tabelle_correzione()
    except FileNotFoundError:
        tabella1, tabella2 = None, None
        st.error("Impossibile caricare i file Excel per il calcolo del fattore di correzione. "
                 "Verifica che 'tabella rielaborata.xlsx' e 'tabella secondaria.xlsx' siano presenti "
                 "oppure caricale dalla sidebar.")
    except Exception as e:
        tabella1, tabella2 = None, None
        st.error(f"Errore nel caricamento delle tabelle: {e}")

# =========================
# UI principale (autonoma)
# =========================
col1, col2, col3 = st.columns([1, 1, 1.6], gap="small")

# --- COL 1: CONDIZIONE CORPO ---
with col1:
    stato_corpo = st.radio(
        "**Condizioni del corpo**",
        ["Asciutto", "Bagnato", "Immerso"],
        key="radio_stato_corpo_beta",
        horizontal=True
    )
    corpo_immerso = (stato_corpo == "Immerso")
    corpo_bagnato = (stato_corpo == "Bagnato")
    corpo_asciutto = (stato_corpo == "Asciutto")

copertura_speciale = False
scelta_vestiti = "/"
scelta_coperte = "/"
superficie = "/"
corrente = "/"

# --- COL 2: COPERTE ---
with col2:
    if not (corpo_immerso or corpo_bagnato):
        opzioni_coperte = [
            "Nessuna coperta","Lenzuolo +","Lenzuolo ++","Coperta",
            "Coperta spessa (es copriletto)",
            "Coperte più spesse (es coperte di lana)",
            "Coperta pesante (es piumino imbottito)",
            "Molte coperte pesanti"
        ]
        if corpo_asciutto:
            opzioni_coperte += ["Strato di foglie di medio spessore", "Spesso strato di foglie"]

        def _is_moltissimi(v):
            v = _norm(v or "")
            return v in {"Moltissimi strati", "˃˃ strati"}

        vestiti_state = st.session_state.get("radio_vestiti_beta")
        if _is_moltissimi(vestiti_state):
            opzioni_coperte = ["Molte coperte pesanti"]

        scelta_coperte = st.radio("**Coperte?**", opzioni_coperte, key="scelta_coperte_radio_beta",
                                  help=HELP_COPERTE,
                                  horizontal=True,
                                  format_func=lambda v: LABEL_COPERTE.get(v, v))
    else:
        scelta_coperte = "/"

copertura_speciale = scelta_coperte in ["Strato di foglie di medio spessore", "Spesso strato di foglie"]

# --- COL 1: VESTITI ---
if (corpo_asciutto or corpo_bagnato) and not corpo_immerso and not copertura_speciale:
    with col1:
        scelta_vestiti = st.radio(
            "**Strati di indumenti**",
            [
                "Nudo",
                "1-2 strati sottili",
                "2-3 strati sottili",
                "3-4 strati sottili",
                "1-2 strati spessi",
                "˃4 strati sottili o ˃2 spessi",
                "Moltissimi strati"
            ],
            key="radio_vestiti_beta",
            horizontal=True,
            help=HELP_VESTITI,
            format_func=lambda v: LABEL_VESTITI.get(v, v)
        )
else:
    scelta_vestiti = "/"

# --- COL 2: CORRENTI (solo ACQUA se Immerso) ---
with col2:
    if not copertura_speciale and corpo_immerso:
        corrente = st.radio("**Correnti d'acqua?**",
                            ["In acqua corrente", "In acqua stagnante"],
                            index=1, key="radio_acqua_beta", horizontal=True,
                            format_func=lambda v: LABEL_CORRENTI_ACQUA.get(v, v))
    else:
        corrente = "/"

# --- COL 3: SUPERFICIE + (spostata) CORRENTI D'ARIA ---
with col3:
    # Correnti d'aria visibili qui (NON quando Immerso, e solo se non copertura speciale)
    if not (corpo_immerso or copertura_speciale):
        mostra_corrente = False
        if corpo_bagnato:
            mostra_corrente = True
        elif corpo_asciutto:
            if scelta_vestiti in ["Nudo", "1-2 strati sottili"] and scelta_coperte in ["Nessuna coperta", "Lenzuolo +"]:
                mostra_corrente = True

        def _is_moltissimi(v):  # riuso locale
            v = _norm(v or "")
            return v in {"Moltissimi strati", "˃˃ strati"}

        if _is_moltissimi(scelta_vestiti):
            mostra_corrente = False

        if mostra_corrente:
            corrente = st.radio("**Correnti d'aria?**",
                                ["Esposto a corrente d'aria", "Nessuna corrente"],
                                index=1, key="radio_corrente_beta", horizontal=True,
                                help=HELP_CORRENTI_ARIA,
                                format_func=lambda v: LABEL_CORRENTI_ARIA.get(v, v))

    # Appoggio: solo se non immerso, non bagnato, non copertura speciale
    if not (corpo_immerso or corpo_bagnato or copertura_speciale):
        mostra_foglie = scelta_vestiti == "Nudo" and scelta_coperte == "Nessuna coperta"
        opzioni_superficie = [
            "Pavimento di casa, terreno o prato asciutto, asfalto",
            "Imbottitura pesante (es sacco a pelo isolante, polistirolo, divano imbottito)",
            "Materasso o tappeto spesso",
            "Cemento, pietra, pavimento in PVC, pavimentazione esterna"
        ]
        if scelta_vestiti == "Nudo" and scelta_coperte == "Nessuna coperta":
            opzioni_superficie.append("Superficie metallica spessa, all'esterno.")
        if mostra_foglie:
            opzioni_superficie += ["Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)"]

        superficie = st.radio("**Appoggio**", opzioni_superficie, key="radio_superficie_beta",
                              help=HELP_SUPERFICIE, horizontal=True,
                              format_func=lambda v: LABEL_SUPERFICIE.get(v, v))

# =========================
# Calcolo (autonomo)
# =========================
if tabella1 is None or tabella2 is None:
    st.stop()

valori = {
    "Ambiente": _norm(stato_corpo),
    "Vestiti": _norm(scelta_vestiti),
    "Coperte": _norm(scelta_coperte),
    "Superficie d'appoggio": _norm(superficie),
    "Correnti": _norm(corrente)
}

mask = (
    tabella1["Ambiente"].isin(_aliases(valori["Ambiente"], "Ambiente")) &
    tabella1["Vestiti"].isin(_aliases(valori["Vestiti"], "Vestiti")) &
    tabella1["Coperte"].isin(_aliases(valori["Coperte"], "Coperte")) &
    tabella1["Superficie d'appoggio"].isin(_aliases(valori["Superficie d'appoggio"], "Superficie d'appoggio")) &
    tabella1["Correnti"].isin(_aliases(valori["Correnti"], "Correnti"))
)
riga = tabella1[mask]

if riga.empty:
    st.warning("Nessuna combinazione valida trovata nella tabella.")
    st.stop()

if len(riga) > 1:
    st.info("Più combinazioni valide trovate nella tabella: viene utilizzata la prima corrispondenza.")

# Robustezza su NaN
fattore_series = pd.to_numeric(riga["Fattore"], errors='coerce').dropna()
if fattore_series.empty:
    st.warning("Il valore di 'Fattore' nella/e riga/righe trovate non è numerico. Impossibile proseguire.")
    st.stop()

fattore_base = float(fattore_series.iloc[0])
fattore_finale = fattore_base

# Applica Tabella 2 quando serve
if fattore_base >= 1.4 and peso != 70:
    try:
        t2 = tabella2.copy()

        def parse_peso(col):
            s = str(col).strip().lower().replace('kg', '').replace('w', '')
            num = ''.join(ch for ch in s if (ch.isdigit() or ch in '.,'))
            num = num.replace(',', '.')
            return float(num) if num not in ("", ".", ",") else None

        pesi_col = {col: parse_peso(col) for col in t2.columns}
        pesi_col = {col: w for col, w in pesi_col.items() if w is not None}
        if not pesi_col:
            raise ValueError("Nessuna colonna peso valida in Tabella 2.")

        col_70 = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - 70.0))
        serie70 = pd.to_numeric(t2[col_70], errors='coerce')
        idx_match = (serie70 - fattore_base).abs().idxmin()
        col_user = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - float(peso)))
        val_user = pd.to_numeric(t2.loc[idx_match, col_user], errors='coerce')
        if pd.notna(val_user):
            fattore_finale = float(val_user)
    except Exception as e:
        st.warning(f"Impossibile applicare la correzione per il peso (riporto il valore per 70 kg): {e}")

# =========================
# Output (nessun bottone, pagina autonoma)
# =========================
left, right = st.columns([2, 1])
with left:
    if abs(fattore_finale - fattore_base) > 1e-9:
        st.markdown(
            f'<div style="background-color:#e6f4ea; padding:12px; border-radius:6px; font-size:1.05rem;">'
            f'Fattore di correzione <b>adattato</b> (peso {peso:.1f} kg): <b>{fattore_finale:.2f}</b>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="background-color:#e6f4ea; padding:12px; border-radius:6px; font-size:1.05rem;">'
            f'Fattore di correzione suggerito: <b>{fattore_finale:.2f}</b>'
            f'</div>',
            unsafe_allow_html=True
        )
with right:
    st.markdown(
        f'<div style="color:gray; padding:12px;">Valore per 70 kg: {fattore_base:.2f}</div>',
        unsafe_allow_html=True
    )

with st.expander("📋 Riepilogo selezioni", expanded=False):
    st.write(
        {
            "Ambiente": valori["Ambiente"],
            "Vestiti": valori["Vestiti"],
            "Coperte": valori["Coperte"],
            "Superficie d'appoggio": valori["Superficie d'appoggio"],
            "Correnti": valori["Correnti"],
            "Peso (kg)": f"{peso:.1f}",
        }
    )

st.info("Pagina **beta**: i cambi alla logica qui non toccano la pagina principale.")

