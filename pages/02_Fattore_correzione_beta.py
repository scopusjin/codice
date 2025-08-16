# pages/02_Fattore_correzione_beta.py
# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

# =========================
# Config pagina
# =========================
st.set_page_config(
    page_title="Fattore di correzione (beta)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Fattore di correzione — beta")
st.caption("Formula (senza tabella) + Tabella (confronto). Contatori in UNA SOLA RIGA con st.data_editor (step +/−). Correzione peso (Tabella 2) inclusa.")

# =========================
# HELP (testi di guida)
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
    "**Strato di foglie di medio spessore** = foglie su corpo/vestiti;   "
    "**Spesso strato di foglie** = strato spesso di foglie."
)
HELP_VESTITI = (
    "**Tenere conto solo degli indumenti che coprono la parte bassa di torace/addome**.   "
    "**Strati sottili** = t-shirt, camicia, maglia leggera;    "
    "**Strati spessi** = maglione, felpa in pile, giubbino;   "
    "**˃ strati** = ˃4 sottili o ˃2 spessi;   "
    "**˃˃ strati** = molti strati pesanti."
)
HELP_SUPERFICIE = (
    "**Indifferente** = pavimento di casa/parquet, prato o terreno asciutto, asfalto;   "
    "**Isolante** = materasso, tappeto spesso;   "
    "**Molto isolante** = polistirolo, sacco a pelo tecnico, divano imbottito;   "
    "**Conduttivo** = cemento, pietra, pavimento in PVC, pavimentazione esterna;   "
    "**Molto conduttivo** = superficie metallica spessa all’esterno;   "
    "**Foglie umide/secche (≥2 cm)** = adagiato su strato di foglie"
)

# =========================
# Cache caricamento Tabelle (per modalità Tabella e correzione peso)
# =========================
@st.cache_data
def load_tabelle_correzione():
    """
    Tabella 1 colonne attese:
      Ambiente, Vestiti, Coperte, Correnti, Superficie d'appoggio, Fattore
    Tabella 2: colonne con pesi (es. '50 kg', '70 kg', '90 kg' ...)
    """
    t1 = pd.read_excel("tabella rielaborata.xlsx", engine="openpyxl")
    t2 = pd.read_excel("tabella secondaria.xlsx", engine="openpyxl")
    t1["Fattore"] = pd.to_numeric(t1["Fattore"], errors="coerce")
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    return t1, t2

# =========================
# Correzione peso (Tabella 2)
# =========================
def applica_tabella2(fattore_base: float, peso: float, tabella2: pd.DataFrame):
    if not (fattore_base >= 1.4 and float(peso) != 70.0):
        return fattore_base, False, {}
    try:
        t2 = tabella2.copy()

        def parse_peso(col_name: str):
            s = str(col_name).strip().lower().replace("kg", "").replace("w", "")
            num = "".join(ch for ch in s if (ch.isdigit() or ch in ".,"))
            num = num.replace(",", ".")
            try:
                return float(num)
            except Exception:
                return None

        pesi_col = {col: parse_peso(col) for col in t2.columns}
        pesi_col = {col: w for col, w in pesi_col.items() if w is not None}
        if not pesi_col:
            raise ValueError("Nessuna colonna peso valida in Tabella 2.")

        col_70 = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - 70.0))
        serie70 = pd.to_numeric(t2[col_70], errors="coerce")
        idx_match = (serie70 - fattore_base).abs().idxmin()

        col_user = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - float(peso)))
        val_user = pd.to_numeric(t2.loc[idx_match, col_user], errors="coerce")

        if pd.notna(val_user):
            return float(val_user), True, {
                "colonna_70kg": f"{col_70} (≈70 kg)",
                "riga_match_indice": str(idx_match),
                "colonna_peso_utente": f"{col_user} (≈{peso:.1f} kg)"
            }
    except Exception:
        pass
    return fattore_base, False, {}

# =========================
# Editor contatori: UNA SOLA RIGA
# =========================
def contatori_editor_one_row(defaults=None, key="contatori_formula_row"):
    """
    Una riga, ogni contatore è una colonna con step +/-.
    Ritorna: dict {colonna: int(val)}
    """
    if defaults is None:
        defaults = {
            "n. Strati sottili": 0,
            "n. Strati spessi": 0,
            "n. Lenzuolo +": 0,
            "n. Lenzuolo ++": 0,
            "n. Coperte (medie)": 0,
            "n. Coperte (pesanti)": 0,
        }

    df_init = pd.DataFrame([defaults], index=["Quantità"])

    # Costruisco column_config dinamica per impostare tutte NumberColumn identiche
    col_cfg = {}
    for col in defaults.keys():
        col_cfg[col] = st.column_config.NumberColumn(
            col,
            help="Usa +/− o digita",
            min_value=0,
            max_value=50,
            step=1,
            format="%d",
        )

    edited = st.data_editor(
        df_init,
        key=key,
        hide_index=False,            # Mostra "Quantità" a sinistra
        use_container_width=True,
        num_rows="fixed",            # fissa a una riga
        column_config=col_cfg
    )

    # Ritorna come dict
    row = edited.iloc[0]
    return {k: int(row[k] or 0) for k in defaults.keys()}

# =========================
# Utility: etichette compatte con mapping verso tabella
# =========================
def u_bold(s: str) -> str:
    out = []
    for ch in s:
        if 'A' <= ch <= 'Z':
            out.append(chr(ord(ch) - ord('A') + 0x1D400))  # 𝐀..𝐙
        elif 'a' <= ch <= 'z':
            out.append(chr(ord(ch) - ord('a') + 0x1D41A))  # 𝐚..𝐳
        else:
            out.append(ch)
    return ''.join(out)

CORPO_OPZIONI_VIS = [
    f"Corpo {u_bold('asciutto')}",
    f"Corpo {u_bold('bagnato')}",
    f"Corpo {u_bold('immerso')}",
]
CORPO_MAP = {
    CORPO_OPZIONI_VIS[0]: "Asciutto",
    CORPO_OPZIONI_VIS[1]: "Bagnato",
    CORPO_OPZIONI_VIS[2]: "Immerso",
}

ARIA_OPZIONI_VIS = [
    f"{u_bold('Senza')} correnti d'aria",
    f"{u_bold('Con')} correnti d'aria",
]
ARIA_MAP = {
    ARIA_OPZIONI_VIS[0]: "Nessuna corrente",
    ARIA_OPZIONI_VIS[1]: "Esposto a corrente d'aria",
}

ACQUA_OPZIONI_VIS = [
    f"{u_bold('Senza')} correnti d'acqua",
    f"{u_bold('Con')} correnti d'acqua",
]
ACQUA_MAP = {
    ACQUA_OPZIONI_VIS[0]: "In acqua stagnante",
    ACQUA_OPZIONI_VIS[1]: "In acqua corrente",
}

# =========================
# Formula (senza tabella)
# =========================
def calcola_fattore_formula(
    n_sottili: int,
    n_spessi: int,
    n_lenzuolo_piu: int,
    n_lenzuolo_piu_piu: int,
    n_coperte_medie: int,
    n_coperte_pesanti: int,
    stato_corpo: str,
    corrente_tipo: str,      # "aria" | "acqua" | "/"
    corrente_label: str,     # "Nessuna corrente"/"Esposto a corrente d'aria"/"In acqua stagnante"/"In acqua corrente"/"/"
    superficie: str          # una delle superfici o "/"
) -> float:
    """
    Regole attuali (correnti/superficie NEUTRE per ora):
    - Ogni strato sottile: +0.075 (CAP sul valore a 1.8 durante la somma di sottili/spessi/L+)
    - Ogni strato spesso: +0.15 (stesso CAP 1.8 durante la somma)
    - Ogni Lenzuolo +: +0.075 (stesso CAP 1.8 durante la somma)
    - Lenzuolo ++: base 1.0, +0.15 per ciascun incremento, CAP contributo L++ = +1.0 (=> “fino a 2”)
    - Coperta media: se presente base>=1.5; +0.2 per ciascuna
    - Coperta pesante: se presente base>=1.5; +0.3 per ciascuna
    """
    base = 1.0
    if (n_coperte_medie > 0) or (n_coperte_pesanti > 0):
        base = max(base, 1.5)
    value = base

    def cap_18(x):  # cappo il "valore" a 1.8 durante somme sottili/spessi/L+
        return min(x, 1.8)

    # contributi cumulativi con cap 1.8
    value = cap_18(value + 0.075 * max(0, n_sottili))
    value = cap_18(value + 0.15  * max(0, n_spessi))
    value = cap_18(value + 0.075 * max(0, n_lenzuolo_piu))

    # Lenzuolo ++: contributo separato con CAP +1.0
    value += min(0.15 * max(0, n_lenzuolo_piu_piu), 1.0)

    # Coperte
    value += 0.2 * max(0, n_coperte_medie)
    value += 0.3 * max(0, n_coperte_pesanti)

    # Correnti/superficie per ora neutre (placeholder)
    _ = (stato_corpo, corrente_tipo, corrente_label, superficie)
    return float(value)

# =========================
# Modalità TABELLA (originale) per confronto
# =========================
def calcola_fattore_tabella(peso: float):
    try:
        tabella1, tabella2 = load_tabelle_correzione()
    except Exception as e:
        st.error(f"Errore nel caricamento delle tabelle: {e}")
        return

    corpo_label = st.radio("", CORPO_OPZIONI_VIS, key="corpo_tab", horizontal=True)
    stato_corpo = CORPO_MAP[corpo_label]

    scelta_vestiti = "/"
    scelta_coperte = "/"
    superficie = "/"
    corrente = "/"

    if stato_corpo == "Immerso":
        corr_acqua = st.radio("", ACQUA_OPZIONI_VIS, key="acqua_tab", horizontal=True)
        corrente = ACQUA_MAP[corr_acqua]

    elif stato_corpo == "Bagnato":
        scelta_vestiti = st.radio("**Strati di indumenti**",
                                  ["Nudo", "1-2 strati sottili", "1-2 strati spessi",
                                   "2-3 strati sottili", "3-4 strati sottili", "˃ strati", "˃˃ strati"],
                                  key="vestiti_tab", horizontal=True, help=HELP_VESTITI)
        corr_aria = st.radio("", ARIA_OPZIONI_VIS, key="aria_tab", horizontal=True)
        corrente = ARIA_MAP[corr_aria]

    else:  # Asciutto
        scelta_vestiti = st.radio("**Strati di indumenti**",
                                  ["Nudo", "1-2 strati sottili", "2-3 strati sottili",
                                   "3-4 strati sottili", "1-2 strati spessi", "˃ strati", "˃˃ strati"],
                                  key="vestiti_tab", horizontal=True, help=HELP_VESTITI)
        scelta_coperte = st.radio("**Coperte?**",
                                  ["Nessuna coperta", "Lenzuolo +", "Lenzuolo ++",
                                   "Coperta", "Coperta +", "Coperta ++", "Coperta +++", "Coperta ++++",
                                   "Strato di foglie di medio spessore", "Spesso strato di foglie"],
                                  key="coperte_tab", horizontal=True, help=HELP_COPERTE)

        if scelta_coperte in ["Strato di foglie di medio spessore", "Spesso strato di foglie"]:
            corrente = "/"
            superficie = "/"
            scelta_vestiti = "/"
        else:
            corr_aria = st.radio("", ARIA_OPZIONI_VIS, key="aria_tab", horizontal=True)
            corrente = ARIA_MAP[corr_aria]

            if (scelta_vestiti == "Nudo" and scelta_coperte == "Nessuna coperta"):
                opzioni_superficie = ["Indifferente", "Molto isolante", "Isolante",
                                      "Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)", "Molto conduttivo", "Conduttivo"]
            else:
                opzioni_superficie = ["Indifferente", "Molto isolante", "Isolante", "Conduttivo"]
            superficie = st.radio("**Appoggio**", opzioni_superficie, key="superficie_tab", horizontal=True, help=HELP_SUPERFICIE)

    # match in tabella
    tabella1, tabella2 = load_tabelle_correzione()
    mask = (
        (tabella1["Ambiente"] == stato_corpo) &
        (tabella1["Vestiti"] == scelta_vestiti) &
        (tabella1["Coperte"] == scelta_coperte) &
        (tabella1["Superficie d'appoggio"] == superficie) &
        (tabella1["Correnti"] == corrente)
    )
    riga = tabella1[mask]
    if riga.empty:
        st.warning("Nessuna combinazione valida trovata nella tabella.")
        return

    fattore_base = float(pd.to_numeric(riga["Fattore"], errors="coerce").dropna().iloc[0])
    fattore_finale, applied_t2, _ = applica_tabella2(fattore_base, peso, tabella2)

    # Output
    if abs(fattore_finale - fattore_base) > 1e-9:
        st.success(f"Fattore (tabella, adattato al peso {peso:.1f} kg): **{fattore_finale:.2f}**")
        st.caption(f"Valore per 70 kg: {fattore_base:.2f}")
    else:
        st.success(f"Fattore (tabella): **{fattore_finale:.2f}**")

# =========================
# UI: scelta modalità + Peso
# =========================
modo_formula = st.toggle("Usa **Formula (senza tabella)**", value=True, help="Se disattivo, uso la Tabella rielaborata.")
peso = st.number_input("Peso (kg)", min_value=10.0, max_value=250.0, value=70.0, step=0.5, key="peso_beta")

# =========================
# Modalità FORMULA: contatori (UNA RIGA) + calcolo
# =========================
if modo_formula:
    st.subheader("Coperture e indumenti (Formula)")

    vals = contatori_editor_one_row(
        defaults={
            "n. Strati sottili": 0,
            "n. Strati spessi": 0,
            "n. Lenzuolo +": 0,
            "n. Lenzuolo ++": 0,
            "n. Coperte (medie)": 0,
            "n. Coperte (pesanti)": 0,
        },
        key="contatori_formula_row"
    )

    n_sottili = vals["n. Strati sottili"]
    n_spessi = vals["n. Strati spessi"]
    n_lenzuolo_piu = vals["n. Lenzuolo +"]
    n_lenzuolo_piu_piu = vals["n. Lenzuolo ++"]
    n_coperte_medie = vals["n. Coperte (medie)"]
    n_coperte_pesanti = vals["n. Coperte (pesanti)"]

    # Corpo + correnti + superficie (per ora neutri nella formula; placeholder)
    corpo_label = st.radio("", CORPO_OPZIONI_VIS, key="corpo_formula", horizontal=True)
    stato_corpo = CORPO_MAP[corpo_label]

    corrente_tipo = "/"
    corrente_label = "/"
    if stato_corpo == "Immerso":
        corrente_tipo = "acqua"
        corr_lbl = st.radio("", ACQUA_OPZIONI_VIS, key="acqua_formula", horizontal=True)
        corrente_label = ACQUA_MAP[corr_lbl]
    else:
        corrente_tipo = "aria"
        corr_lbl = st.radio("", ARIA_OPZIONI_VIS, key="aria_formula", horizontal=True)
        corrente_label = ARIA_MAP[corr_lbl]

    superficie = "/"
    if stato_corpo == "Asciutto":
        base_opts = ["Indifferente", "Molto isolante", "Isolante", "Conduttivo"]
        extra_opts = ["Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)", "Molto conduttivo"]
        # consideriamo "nudo senza coperture" ≈ tutti i contatori a zero
        if (n_sottili == 0 and n_spessi == 0 and n_lenzuolo_piu == 0 and
            n_lenzuolo_piu_piu == 0 and n_coperte_medie == 0 and n_coperte_pesanti == 0):
            opzioni_superficie = base_opts + extra_opts
        else:
            opzioni_superficie = base_opts
        superficie = st.radio("**Appoggio**", opzioni_superficie, key="superficie_formula", horizontal=True, help=HELP_SUPERFICIE)

    # Calcolo formula
    fattore_base = calcola_fattore_formula(
        n_sottili=n_sottili,
        n_spessi=n_spessi,
        n_lenzuolo_piu=n_lenzuolo_piu,
        n_lenzuolo_piu_piu=n_lenzuolo_piu_piu,
        n_coperte_medie=n_coperte_medie,
        n_coperte_pesanti=n_coperte_pesanti,
        stato_corpo=stato_corpo,
        corrente_tipo=corrente_tipo,
        corrente_label=corrente_label,
        superficie=superficie
    )

    # Correzione peso (Tabella 2) se disponibile
    applied_t2 = False
    try:
        _, tabella2 = load_tabelle_correzione()
        fattore_finale, applied_t2, _ = applica_tabella2(fattore_base, peso, tabella2)
    except Exception:
        fattore_finale = fattore_base

    # Output
    if abs(fattore_finale - fattore_base) > 1e-9:
        st.success(f"Fattore (formula, adattato al peso {peso:.1f} kg): **{fattore_finale:.2f}**")
        st.caption(f"Valore formula per 70 kg: {fattore_base:.2f}")
    else:
        st.success(f"Fattore (formula): **{fattore_finale:.2f}**")

# =========================
# Modalità TABELLA (per confronto)
# =========================
else:
    calcola_fattore_tabella(peso)
            
