# pages/02_Fattore_correzione_beta.py
import pandas as pd
import streamlit as st

# =========================
# Config pagina
# =========================
st.set_page_config(
    page_title="Fattore di correzione (beta)",
    
    layout="wide",
    initial_sidebar_state="collapsed"   # Sidebar nascosta
)

st.title("Fattore di correzione — beta")
st.caption("Struttura originale, etichette allineate alla tabella, UI verticale compatta.")

# =========================
# HELP (testi di guida) — invariate
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
# Cache caricamento tabelle (come originale)
# =========================
@st.cache_data
def load_tabelle_correzione():
    """
    Carica e normalizza le tabelle usate da calcola_fattore.
    Restituisce (tabella1, tabella2) o solleva eccezione con messaggio chiaro.
    Colonne attese in Tabella 1:
      Ambiente, Vestiti, Coperte, Correnti, Superficie d'appoggio, Fattore
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
# Funzione principale (come originale ma UI verticale e label allineate)
# =========================
def calcola_fattore(peso: float):
    # Caricamento tabelle
    try:
        tabella1, tabella2 = load_tabelle_correzione()
    except FileNotFoundError:
        st.error("Impossibile caricare i file Excel per il calcolo del fattore di correzione. "
                 "Verifica che 'tabella rielaborata.xlsx' e 'tabella secondaria.xlsx' siano presenti.")
        return
    except Exception as e:
        st.error(f"Errore nel caricamento delle tabelle: {e}")
        return

    # ========== UI verticale (senza colonne) ==========
    # 1) AMBIENTE
    stato_corpo = st.radio(
        "**Condizioni del corpo**",
        ["Asciutto", "Bagnato", "Immerso"],
        key="radio_stato_corpo_beta",
        horizontal=True
    )
    corpo_immerso = (stato_corpo == "Immerso")
    corpo_bagnato = (stato_corpo == "Bagnato")
    corpo_asciutto = (stato_corpo == "Asciutto")

    # Iniziali
    scelta_vestiti = "/"
    scelta_coperte = "/"
    superficie = "/"
    corrente = "/"

    # 2) COPERTE / VESTITI / CORRENTI / SUPERFICIE (in base ad AMBIENTE)
    if corpo_immerso:
        # Immerso → solo correnti d'acqua
        corrente = st.radio("**Correnti d'acqua?**",
                            ["In acqua corrente", "In acqua stagnante"],
                            index=1, key="radio_acqua_beta", horizontal=True)
        # altri = '/'
        scelta_vestiti = "/"
        scelta_coperte = "/"
        superficie = "/"

    elif corpo_bagnato:
        # Bagnato → vestiti + correnti aria (No/Sì) ; no coperte, no superficie
        scelta_vestiti = st.radio(
            "**Strati di indumenti**",
            ["Nudo", "1-2 strati sottili", "1-2 strati spessi", "2-3 strati sottili", "3-4 strati sottili", "˃ strati", "˃˃ strati"],
            key="radio_vestiti_beta",
            horizontal=True,
            help=HELP_VESTITI
        )
        corrente = st.radio("**Correnti d'aria?**",
                            ["Nessuna corrente", "Esposto a corrente d'aria"],
                            index=0, key="radio_corrente_beta", horizontal=True, help=HELP_CORRENTI_ARIA)
        scelta_coperte = "/"
        superficie = "/"

    else:
        # Asciutto → vestiti + coperte; correnti aria e superficie dipendono dalla coperta
        scelta_vestiti = st.radio(
            "**Strati di indumenti**",
            ["Nudo", "1-2 strati sottili", "2-3 strati sottili", "3-4 strati sottili", "1-2 strati spessi", "˃ strati", "˃˃ strati"],
            key="radio_vestiti_beta",
            horizontal=True,
            help=HELP_VESTITI
        )
        scelta_coperte = st.radio(
            "**Coperte?**",
            [
                "Nessuna coperta", "Lenzuolo +", "Lenzuolo ++",
                "Coperta", "Coperta +", "Coperta ++", "Coperta +++", "Coperta ++++",
                "Strato di foglie di medio spessore", "Spesso strato di foglie"
            ],
            key="scelta_coperte_radio_beta",
            horizontal=True,
            help=HELP_COPERTE
        )

        if scelta_coperte in ["Strato di foglie di medio spessore", "Spesso strato di foglie"]:
            # caso speciale (in tabella Correnti='/' e Superficie='/'; Vestiti='/')
            corrente = "/"
            superficie = "/"
            scelta_vestiti = "/"
        else:
            # Correnti aria presenti per tutti i casi Asciutto con coperta NON 'foglie'
            corrente = st.radio("**Correnti d'aria?**",
                                ["Nessuna corrente", "Esposto a corrente d'aria"],
                                index=0, key="radio_corrente_beta", horizontal=True, help=HELP_CORRENTI_ARIA)
            # Superficie: in tabella 'Molto conduttivo' compare solo con Nudo + Nessuna coperta
            mostra_foglie = (scelta_vestiti == "Nudo" and scelta_coperte == "Nessuna coperta")
            opzioni_superficie = ["Indifferente", "Molto isolante", "Isolante", "Conduttivo"]
            if mostra_foglie:
                opzioni_superficie = [
                    "Indifferente", "Molto isolante", "Isolante",
                    "Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)", "Molto conduttivo", "Conduttivo"
                ]
            superficie = st.radio("**Appoggio**", opzioni_superficie, key="radio_superficie_beta", horizontal=True, help=HELP_SUPERFICIE)

    # ========== CALCOLO ==========
    valori = {
        "Ambiente": stato_corpo,
        "Vestiti": scelta_vestiti,
        "Coperte": scelta_coperte,
        "Superficie d'appoggio": superficie,
        "Correnti": corrente
    }

    mask = (
        (tabella1["Ambiente"] == valori["Ambiente"]) &
        (tabella1["Vestiti"] == valori["Vestiti"]) &
        (tabella1["Coperte"] == valori["Coperte"]) &
        (tabella1["Superficie d'appoggio"] == valori["Superficie d'appoggio"]) &
        (tabella1["Correnti"] == valori["Correnti"])
    )
    riga = tabella1[mask]

    if riga.empty:
        st.warning("Nessuna combinazione valida trovata nella tabella con le diciture selezionate.")
        return
    if len(riga) > 1:
        st.info("Più combinazioni valide trovate nella tabella: viene utilizzata la prima corrispondenza.")

    # fattore base
    fattore_series = pd.to_numeric(riga["Fattore"], errors='coerce').dropna()
    if fattore_series.empty:
        st.warning("Il valore di 'Fattore' nella riga trovata non è numerico. Impossibile proseguire.")
        return

    fattore_base = float(fattore_series.iloc[0])
    fattore_finale = fattore_base

    # ========== Applicazione Tabella 2 (come originale) ==========
    applied_t2 = False
    t2_details = {}
    if fattore_base >= 1.4 and float(peso) != 70.0:
        try:
            t2 = tabella2.copy()

            def parse_peso(col_name: str):
                s = str(col_name).strip().lower().replace('kg', '').replace('w', '')
                num = ''.join(ch for ch in s if (ch.isdigit() or ch in '.,'))
                num = num.replace(',', '.')
                try:
                    return float(num)
                except Exception:
                    return None

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
                applied_t2 = True
                t2_details = {
                    "colonna_70kg": f"{col_70} (≈70 kg)",
                    "riga_match_indice": str(idx_match),
                    "colonna_peso_utente": f"{col_user} (≈{peso:.1f} kg)"
                }
        except Exception as e:
            st.warning(f"Impossibile applicare la correzione per il peso (riporto il valore per 70 kg): {e}")

    # ========== Output (nessun bottone) ==========
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

    st.markdown(
        f'<div style="color:gray; padding:8px 0 16px 0;">Valore per 70 kg: {fattore_base:.2f}</div>',
        unsafe_allow_html=True
    )

    # Badge Tabella 2
    if applied_t2:
        st.markdown(
            '<div style="background:#e8f0fe;border:1px solid #c3d3ff;padding:8px 10px;border-radius:6px;display:inline-block;">'
            'Tabella 2: <b>applicata</b>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        reason = "peso = 70 kg" if abs(float(peso) - 70.0) < 1e-9 else "fattore < 1.4"
        st.markdown(
            f'<div style="background:#f1f3f4;border:1px solid #d7dadc;padding:8px 10px;border-radius:6px;display:inline-block;">'
            f'Tabella 2: <b>non applicata</b> <span style="color:#5f6368;">({reason})</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with st.expander("📋 Riepilogo selezioni e dettagli", expanded=False):
        riepilogo = {
            "Ambiente": valori["Ambiente"],
            "Vestiti": valori["Vestiti"],
            "Coperte": valori["Coperte"],
            "Superficie d'appoggio": valori["Superficie d'appoggio"],
            "Correnti": valori["Correnti"],
            "Peso (kg)": f"{peso:.1f}",
            "Fattore base (70 kg)": f"{fattore_base:.2f}",
            "Fattore finale": f"{fattore_finale:.2f}",
            "Tabella 2 applicata": applied_t2
        }
        if applied_t2 and t2_details:
            riepilogo.update(t2_details)
        st.write(riepilogo)

# =========================
# UI: Peso + richiamo funzione (pagina autonoma)
# =========================
peso = st.number_input("Peso (kg)", min_value=10.0, max_value=250.0, value=70.0, step=0.5, key="peso_input_beta")
calcola_fattore(peso)
