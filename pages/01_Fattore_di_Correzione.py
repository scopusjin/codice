import streamlit as st
import pandas as pd

# --- CARICAMENTO DATI ---
# --- CARICAMENTO DATI ---
tabella1 = pd.read_excel("tabella rielaborata.xlsx")
tabella1['Fattore'] = pd.to_numeric(tabella1['Fattore'], errors='coerce')  # Forza i valori numerici

# --- SEGNALAZIONE RIGHE CON ERRORI ---
righe_non_valide = tabella1[tabella1['Fattore'].isna()]
if not righe_non_valide.empty:
    st.warning(f"⚠️ Attenzione: {len(righe_non_valide)} riga/e nella tabella 'Fattore' non contengono valori numerici validi.")
    st.dataframe(righe_non_valide)

tabella2 = pd.read_excel("tabella secondaria.xlsx")

# --- FUNZIONE PRINCIPALE ---
def calcola_fattore(peso):
    st.header("Calcolo del Fattore di Correzione")

    # --- LAYOUT A 3 COLONNE ---
    col1, col2, col3 = st.columns(3)

    # COLONNA 1: Stato del corpo e vestiti
    with col1:
        st.subheader("Condizioni del corpo")
        stato_corpo = st.radio("Stato del corpo:", [
            "Asciutto", "Bagnato", "Immerso"
        ])
        corpo_immerso = (stato_corpo in ["Bagnato", "Immerso"])

        st.subheader("Abbigliamento")
        if not corpo_immerso:
            scelta_vestiti = st.radio("Vestiti:", [
                "Nudo",
                "1-2 strati sottili",
                "2-3 strati sottili",
                "3-4 strati sottili",
                "1-2 strati spessi",
                "˃4 strati sottili o ˃2 strati spessi",
                "Moltissimi strati"
            ])
        else:
            scelta_vestiti = "/"

    # COLONNA 2: Correnti e coperte
    with col2:
        st.subheader("Presenza di correnti")
        if not corpo_immerso:
            corrente = st.radio("Correnti presenti:", [
                "Esposto a corrente d'aria",
                "Nessuna corrente"
            ])
        else:
            corrente = st.radio("Correnti presenti:", [
                "In acqua corrente",
                "In acqua stagnante"
            ])

        st.subheader("Copertura")
        if not corpo_immerso:
            scelta_coperte = st.radio("Coperte:", [
                "Nessuna coperta",
                "Coperta leggera (es lenzuuolo)",
                "Coperta di medio spessore (es copriletto)",
                "Coperta pesante (es piuminino invernale)",
                "Più coperte pesanti"
            ])
        else:
            scelta_coperte = "/"

    # COLONNA 3: Superficie e pulsante
    with col3:
        st.subheader("Superficie di appoggio")
        if not corpo_immerso:
            superficie = st.radio("Superficie:", [
                "Pavimento di casa, terreno o prato asciutto, asfalto",
                "Imbottitura pesante (es sacco a pelo isolante)",
                "Materasso o tappeto spesso",
                "Foglie umide (≥2 cm)",
                "Foglie secche (≥2 cm)"
            ])
        else:
            superficie = "/"

        # PULSANTE
        calcola = st.button("Aggiorna fattore di correzione")

    # --- LOGICA DI CALCOLO ---
    if calcola:
        ambiente = {
            "Asciutto": "Asciutto",
            "Bagnato": "Bagnato",
            "Immerso": "In acqua"
        }[stato_corpo]
    # --- LOGICA DI CALCOLO ---
    if calcola:
        ambiente = {
            "Asciutto": "Asciutto",
            "Bagnato": "Bagnato",
            "Immerso": "In acqua"
        }[stato_corpo]

        # FILTRO DATI
        riga = tabella1[
            ((tabella1['Ambiente'] == ambiente) | (tabella1['Ambiente'] == '/')) &
            ((tabella1['Vestiti'] == scelta_vestiti) | (tabella1['Vestiti'] == '/')) &
            ((tabella1['Coperte'] == scelta_coperte) | (tabella1['Coperte'] == '/')) &
            ((tabella1['Correnti'] == corrente) | (tabella1['Correnti'] == '/')) &
            ((tabella1["Superficie d'appoggio"] == superficie) | (tabella1["Superficie d'appoggio"] == '/'))
        ]

        if riga.empty:
            st.error("Nessuna combinazione trovata.")
            return

        # DESCRIZIONE
        descrizione = f"{stato_corpo.lower()}"
        if not corpo_immerso:
            if scelta_vestiti.lower() == "nudo":
                descrizione += ", nudo"
            else:
                descrizione += f", con {scelta_vestiti.lower()}"
            descrizione += f", sotto {scelta_coperte.lower()}"
            descrizione += f", appoggiato su {superficie.lower()}"
        descrizione += f", {'esposto a corrente' if 'corrente' in corrente else 'non esposto a correnti'}"

        # RISULTATO
        try:
            peso_colonne = [int(c) for c in tabella2.columns]
            peso_usato = min(peso_colonne, key=lambda x: abs(x - peso))
            indice_tab2 = tabella1.index.get_loc(riga.index[0])

            if indice_tab2 < len(tabella2):
                fattore_peso = tabella2.iloc[indice_tab2][str(peso_usato)]
                st.success(f"Fattore di correzione stimato: {fattore_peso:.2f} ({descrizione})")
            else:
                st.warning("Combinazione trovata, ma non presente nella tabella secondaria.")
        except Exception as e:
            st.error(f"Errore nel calcolo con tabella secondaria: {e}")

            
            st.success(f"Fattore di correzione stimato: {float(fattore):.2f} ({descrizione})")

        else:
            try:
                peso_colonne = [int(c) for c in tabella2.columns]
                peso_usato = min(peso_colonne, key=lambda x: abs(x - peso))
                indice_tab2 = tabella1.index.get_loc(riga.index[0])

                if indice_tab2 < len(tabella2):
                    fattore_peso = tabella2.iloc[indice_tab2][str(peso_usato)]
                    st.info(f"Fattore corretto per {peso} kg: {fattore_peso:.2f} ({descrizione})")
                else:
                    st.warning("Combinazione trovata, ma non presente nella tabella secondaria.")
            except Exception as e:
                st.error(f"Errore nel calcolo con tabella secondaria: {e}")
peso_input = st.slider("Peso del corpo (kg)", min_value=30, max_value=150, value=70, step=1)
calcola_fattore(peso=peso_input)
