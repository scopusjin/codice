# pages/02_Fattore_correzione_beta.py
# -*- coding: utf-8 -*-
import math
import pandas as pd
import streamlit as st

# =========================
# Config pagina
# =========================
st.set_page_config(
    page_title="Fattore di correzione (beta)",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Fattore di correzione — beta")

# =========================
# Help compatti
# =========================
HELP_CONDIZIONE = "Se il corpo è immerso in acqua, abbigliamento e coperte non sono rilevanti."
HELP_CORRENTI_ARIA = "Se ci sono finestre aperte, ventole o correnti naturali, seleziona 'con correnti d'aria'."
HELP_COPERTE = "Considera solo se coprono la parte inferiore del tronco"
HELP_SUPERFICIE = (
    "Indifferente = Pavimento/terreno/prato asciutto/asfalto · "
    "Isolante = Materasso/tappeto spesso · "
    "Molto isolante = Imbottitura pesante (sacco a pelo, polistirolo, divano imbottito) · "
    "Conduttivo = Cemento/pietra/PVC/esterno · "
    "Molto conduttivo = Superficie metallica spessa all'esterno (solo nudo asciutto) · "
    "Foglie umide/secche = strato ≥ 2 cm (solo se corpo asciutto)"
)

# Etichette brevi -> descrizioni estese
APP_APPOGGIO_MAP = {
    "Indifferente": "Pavimento di casa, terreno o prato asciutto, asfalto",
    "Isolante": "Materasso o tappeto spesso",
    "Molto isolante": "Imbottitura pesante (sacco a pelo tecnico, polistirolo, divano imbottito)",
    "Conduttivo": "Cemento, pietra, pavimentazione esterna, pavimento in PVC.",
    "Molto conduttivo": "Superficie metallica spessa, in ambiente esterno.",
    "Foglie umide (>= 2 cm)": "Adagiato su strato di foglie umide ≥ 2 cm",
    "Foglie secche (>= 2 cm)": "Adagiato su strato di foglie secche ≥ 2 cm",
}

# =========================
# Utility
# =========================
def clamp(x, lo=0.35, hi=3.0):
    return max(lo, min(hi, x))

# =========================
# 1) Peso su riga isolata
# =========================
peso = st.number_input(
    "Peso corporeo (kg)",
    min_value=10.0, max_value=200.0, value=70.0, step=0.5,
)

# =========================
# 2) Condizioni iniziali (no colonne, opzioni orizzontali)
# =========================
stato = st.radio(
    "**Condizioni del corpo**",
    ["asciutto", "bagnato", "in acqua"],
    index=0,
    horizontal=True,
    help=HELP_CONDIZIONE,
)

scelta_vestizione = st.radio(
    "**Vestizione**",
    ["nudo e scoperto", "vestito e/o coperto"],
    index=0,  # default richiesto
    horizontal=True,
)

# Caso: immerso -> UI minima e stop (niente tabella vestiti)
if stato == "in acqua":
    acqua_tipo = st.radio(
        "**Condizioni dell'acqua**",
        ["acqua stagnante", "acqua corrente"],
        index=0,
        horizontal=True,
    )
    fattore_finale = 0.35 if acqua_tipo == "acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# =========================
# 3) Tabella VESTITI/COPERTE subito sotto la riga “Vestizione”
# =========================
# Contatori di default (anche se nudo restano 0)
n_sottili = n_spessi = n_lenz_plus = n_cop_medie = n_cop_pesanti = 0
has_lenz_pp = False

fattore_vestiti_coperte = 1.0  # serve sia per calcolo sia per regole correnti/bagnato

if scelta_vestizione == "vestito e/o coperto":
    # DataFrame a 1 riga con dtype espliciti
    df = pd.DataFrame(
        {
            "Sottili": pd.Series([0], dtype="int"),
            "Spessi": pd.Series([0], dtype="int"),
            "Lenz.+": pd.Series([0], dtype="int"),
            "Cop. medie": pd.Series([0], dtype="int"),
            "Cop. pesanti": pd.Series([0], dtype="int"),
            "Lenz.++": pd.Series([False], dtype="bool"),
        }
    )

    edited = st.data_editor(
        df,
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        key="editor_vestiti",
        column_config={
            "Sottili": st.column_config.NumberColumn(min_value=0, step=1, format="%d", help="+0.075 per strato"),
            "Spessi": st.column_config.NumberColumn(min_value=0, step=1, format="%d", help="+0.15 per strato"),
            "Lenz.+": st.column_config.NumberColumn(min_value=0, step=1, format="%d", help="+0.075 per lenzuolo"),
            "Cop. medie": st.column_config.NumberColumn(min_value=0, step=1, format="%d", help="base 1.8 (voluta); +0.2 extra"),
            "Cop. pesanti": st.column_config.NumberColumn(min_value=0, step=1, format="%d", help="base 2.0 (voluta); +0.3 extra"),
            "Lenz.++": st.column_config.CheckboxColumn(help="+0.15 (lenzuolo spesso)"),
        },
    )

    r = edited.iloc[0]
    # Valori dai contatori
    n_sottili     = int(r["Sottili"])
    n_spessi      = int(r["Spessi"])
    n_lenz_plus   = int(r["Lenz.+"])
    has_lenz_pp   = bool(r["Lenz.++"])
    n_cop_medie   = int(r["Cop. medie"])
    n_cop_pesanti = int(r["Cop. pesanti"])

    # -----------------------------
    # Calcolo base con regole VOLUTE per le coperte:
    # - Se presente >=1 coperta pesante: BASE = 2.0 (voluta)
    # - altrimenti se presente >=1 coperta media: BASE = 1.8 (voluta)
    # - altrimenti: BASE = 1.0
    # Extra coperte:
    #   * pesante aggiuntiva: +0.3 ciascuna
    #   * media aggiuntiva (o medie quando base è pesante): +0.2 ciascuna
    # Strati / lenzuola:
    #   * sottile: +0.075 ciascuno
    #   * spesso: +0.15 ciascuno
    #   * lenzuolo+: +0.075 ciascuno
    #   * lenzuolo++: +0.15 (checkbox)
    # -----------------------------
    if n_cop_pesanti > 0:
        fattore_vestiti_coperte = 2.0 + max(0, n_cop_pesanti - 1) * 0.3 + n_cop_medie * 0.2
    elif n_cop_medie > 0:
        fattore_vestiti_coperte = 1.8 + max(0, n_cop_medie - 1) * 0.2
    else:
        fattore_vestiti_coperte = 1.0

    fattore_vestiti_coperte += n_sottili * 0.075
    fattore_vestiti_coperte += n_spessi * 0.15
    fattore_vestiti_coperte += n_lenz_plus * 0.075
    if has_lenz_pp:
        fattore_vestiti_coperte += 0.15

    # ⛔️ NIENTE cap qui: il clamp resta SOLO alla fine della pipeline

# =========================
# 4) Correnti d’aria (VISIBILITÀ dipende SOLO da vestiti/lenzuola)
#    - Se, sulla base di vestiti/lenzuola, il fattore >= 1.2 -> correnti irrilevanti e widget nascosto
# =========================
correnti_aria = "/"
if fattore_vestiti_coperte < 1.2:
    correnti_aria = st.radio(
        "**Correnti d'aria?**",
        ["senza correnti", "con correnti d'aria"],
        index=0,
        horizontal=True,
        help=HELP_CORRENTI_ARIA,
    )
# Se nascosto rimane "/" = neutro; in caso di "Molto conduttivo" assumeremo default "senza correnti".

# =========================
# 5) Appoggio (senza colonne, orizzontali)
# =========================
opts_appoggio = ["Indifferente", "Isolante", "Molto isolante", "Conduttivo"]
# "Molto conduttivo" solo se nudo + asciutto
if stato == "asciutto" and scelta_vestizione == "nudo e scoperto":
    opts_appoggio.append("Molto conduttivo")
# Foglie solo se corpo asciutto
if stato == "asciutto":
    opts_appoggio += ["Foglie umide (>= 2 cm)", "Foglie secche (>= 2 cm)"]

superficie_short = st.radio(
    "**Appoggio**",
    opts_appoggio,
    index=0,  # default: Indifferente
    horizontal=True,
    help=HELP_SUPERFICIE,
)
superficie_full = APP_APPOGGIO_MAP.get(superficie_short, superficie_short)

# =========================
# 6) Regole Appoggio (dopo vestiti/coperte)
# =========================
def applica_regole_superficie(
    fatt, superficie_short, stato, correnti_aria, vestizione,
    n_sottili, n_spessi, n_lenz_plus, has_lenz_pp, n_cop_medie, n_cop_pesanti
):
    """Applica le regole dell'appoggio.
       NOTA: 'Molto conduttivo' ha precedenza assoluta e usa le correnti (se nascoste -> default 'senza correnti')."""
    tot_items = (
        n_sottili + n_spessi + n_lenz_plus
        + (1 if has_lenz_pp else 0) + n_cop_medie + n_cop_pesanti
    )

    def only_thin_1():
        return (n_sottili == 1 and tot_items == 1)

    def only_sheet_1():
        return (n_lenz_plus == 1 and tot_items == 1)

    def only_thin_1_2():
        return (
            n_sottili in (1, 2)
            and n_spessi == 0 and n_lenz_plus == 0 and not has_lenz_pp
            and n_cop_medie == 0 and n_cop_pesanti == 0
            and tot_items == n_sottili
        )

    def only_sheet_1_2():
        return (
            n_lenz_plus in (1, 2)
            and n_sottili == 0 and n_spessi == 0 and not has_lenz_pp
            and n_cop_medie == 0 and n_cop_pesanti == 0
            and tot_items == n_lenz_plus
        )

    # 0) Indifferente → nessuna modifica
    if superficie_short == "Indifferente":
        return fatt

    # 1) Isolante
    if superficie_short == "Isolante":
        if tot_items == 0:
            return 1.20
        elif only_thin_1() or only_sheet_1():
            return 1.10
        else:
            return fatt + 0.10

    # 2) Molto isolante
    if superficie_short == "Molto isolante":
        if tot_items == 0:
            return 1.30
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.10

    # 3) Conduttivo
    if superficie_short == "Conduttivo":
        if tot_items == 0:
            return 0.75
        elif only_thin_1() or only_sheet_1():
            return fatt - 0.20
        else:
            return fatt - 0.10

    # 4) Molto conduttivo (solo nudo + asciutto): override con correnti (precedenza assoluta)
    if superficie_short == "Molto conduttivo":
        if not (stato == "asciutto" and vestizione == "nudo e scoperto"):
            return fatt  # guard-rail
        # Se correnti erano nascoste, di default consideriamo "senza correnti"
        if correnti_aria == "con correnti d'aria":
            return 0.50
        else:
            return 0.55

    # 5) Foglie umide (>= 2 cm)
    if superficie_short == "Foglie umide (>= 2 cm)":
        if tot_items == 0:
            return 1.20
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.20
        else:
            return fatt + 0.10

    # 6) Foglie secche (>= 2 cm)
    if superficie_short == "Foglie secche (>= 2 cm)":
        if tot_items == 0:
            return 1.50
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.20

    return fatt

# Applica regole Appoggio
fattore_post_appoggio = applica_regole_superficie(
    fattore_vestiti_coperte,
    superficie_short=superficie_short,
    stato=stato,
    correnti_aria=correnti_aria,
    vestizione=scelta_vestizione,
    n_sottili=n_sottili,
    n_spessi=n_spessi,
    n_lenz_plus=n_lenz_plus,
    has_lenz_pp=has_lenz_pp,
    n_cop_medie=n_cop_medie,
    n_cop_pesanti=n_cop_pesanti,
)

# =========================
# 7) Regole CORRENTI D'ARIA (fuori da "Molto conduttivo")
# =========================
def applica_correnti(
    fatt, stato, vestizione, superficie_short, correnti_aria,
    n_sottili, n_spessi, n_lenz_plus, has_lenz_pp
):
    """
    Applica le regole sulle correnti d’aria con la seguente precedenza:

    0) Se correnti invisibili (vestiti/lenzuola >= 1.2) -> nessun effetto (correnti_aria = "/").
    1) 'Molto conduttivo' già gestito in applica_regole_superficie (precedenza assoluta) -> qui non si tocca.
    2) Bagnato + correnti: override a 0.7 / 0.8 / 0.9 in base agli strati.
    3) Nudo + asciutto (fattore < 1.2, non 'Molto conduttivo'): 1.00 senza correnti, 0.75 con correnti.
    4) Vestizione minima + correnti: fatt - 0.10.
    """
    # 0) correnti non visibili -> nessun effetto
    if correnti_aria == "/":
        return fatt, False  # False = non è stato applicato un override "forte"

    # 1) 'Molto conduttivo' già trattato sopra
    if superficie_short == "Molto conduttivo":
        return fatt, True  # è un override gestito a monte

    # Prepara contatori "spessi equivalenti": indumento spesso + lenzuolo spesso
    spessi_equiv = n_spessi + (1 if has_lenz_pp else 0)

    # 2) Corpo bagnato + correnti: override diretto
    if stato == "bagnato" and correnti_aria == "con correnti d'aria":
        # nudo o 1 sottile -> 0.7
        if (vestizione == "nudo e scoperto") or (n_sottili == 1 and n_spessi == 0 and n_lenz_plus == 0 and not has_lenz_pp):
            return 0.70, True
        # 2 sottili oppure 1 spesso (indumento o lenzuolo) -> 0.8
        if (n_sottili == 2 and spessi_equiv == 0) or (spessi_equiv == 1 and n_sottili == 0):
            return 0.80, True
        # 2 strati spessi (somma tra indumenti e lenzuolo spesso) -> 0.9
        if spessi_equiv >= 2:
            return 0.90, True
        # Altri casi bagnato+correnti non esplicitati: non applichiamo override
        return fatt, False

    # 3) Nudo + asciutto (fattore < 1.2, non molto conduttivo)
    if stato == "asciutto" and vestizione == "nudo e scoperto":
        if correnti_aria == "con correnti d'aria":
            return 0.75, True
        else:
            return 1.00, True

    # 4) Vestizione minima + correnti: -0.10
    # condizioni: 1-2 sottili o 1-2 lenzuola sottili o 1 spesso o 1 lenzuolo spesso
    vestizione_minima = (
        (n_sottili in (1, 2) and n_spessi == 0 and n_lenz_plus == 0 and not has_lenz_pp) or
        (n_lenz_plus in (1, 2) and n_sottili == 0 and n_spessi == 0 and not has_lenz_pp) or
        (n_spessi == 1 and n_sottili == 0 and n_lenz_plus == 0 and not has_lenz_pp) or
        (has_lenz_pp and n_sottili == 0 and n_spessi == 0 and n_lenz_plus == 0)
    )
    if vestizione_minima and correnti_aria == "con correnti d'aria":
        return fatt - 0.10, False

    # Nessuna regola applicata
    return fatt, False

fattore_post_correnti, correnti_override = applica_correnti(
    fatt=fattore_post_appoggio,
    stato=stato,
    vestizione=scelta_vestizione,
    superficie_short=superficie_short,
    correnti_aria=correnti_aria,
    n_sottili=n_sottili,
    n_spessi=n_spessi,
    n_lenz_plus=n_lenz_plus,
    has_lenz_pp=has_lenz_pp,
)

# =========================
# 8) Regola generale BAGNATO (-0.3 se <1.2 in base a vestiti/lenzuola)
#    - si applica al fattore finale (post appoggio / correnti), salvo override forte (0.7/0.8/0.9)
# =========================
fattore_pre_correzione_peso = float(fattore_post_correnti)
if stato == "bagnato" and fattore_vestiti_coperte < 1.2 and not correnti_override:
    fattore_pre_correzione_peso -= 0.30

# Sanity check e clamp
if math.isnan(fattore_pre_correzione_peso):
    fattore_pre_correzione_peso = 1.0
fattore_pre_correzione_peso = clamp(fattore_pre_correzione_peso)

# =========================
# 9) Correzione peso (Tabella 2 - stub pronto)
# =========================
def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    """
    Se f_base >= 1.4:
      1) trova nella colonna 70 kg il valore più vicino a f_base
      2) prendi la riga corrispondente
      3) restituisci l'incrocio con la colonna del peso effettivo
    Fallback provvisorio finché non colleghi la tabella reale.
    """
    if f_base < 1.4:
        return f_base
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

fattore_finale = correzione_peso_tabella2(fattore_pre_correzione_peso, float(peso))

# =========================
# 10) Output
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    
