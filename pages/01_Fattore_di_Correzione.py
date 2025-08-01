import streamlit as st
import pandas as pd

# --- CARICAMENTO DATI ---
tabella1 = pd.read_excel("tabella rielaborata.xlsx")
tabella1['Fattore'] = pd.to_numeric(tabella1['Fattore'], errors='coerce')

righe_non_valide = tabella1[tabella1['Fattore'].isna()]
if not righe_non_valide.empty:
    st.warning(f"⚠️ {len(righe_non_valide)} riga/e nella tabella 'Fattore' non contengono valori numerici validi.")
    st.dataframe(righe_non_valide)

tabella2 = pd.read_excel("tabella secondaria.xlsx")

def calcola_fattore(peso):
    st.header("Calcolo del Fattore di Correzione")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Condizioni del corpo</p>", unsafe_allow_html=True)
        stato_corpo = st.radio("", ["Asciutto", "Bagnato", "Immerso"], label_visibility="collapsed")
        corpo_immerso = (stato_corpo == "Immerso")
        corpo_bagnato = (stato_corpo == "Bagnato")

        st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Abbigliamento</p>", unsafe_allow_html=True)
        if not corpo_immerso:
            scelta_vestiti = st.radio("", [
                "Nudo",
                "1-2 strati sottili",
                "2-3 strati sottili",
                "3-4 strati sottili",
                "1-2 strati spessi",
                "˃4 strati sottili o ˃2 strati spessi",
                "Moltissimi strati"
            ], label_visibility="collapsed")
        else:
            scelta_vestiti = "/"

    with col2:
        if not (corpo_immerso or corpo_bagnato):
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Copertura</p>", unsafe_allow_html=True)
            if scelta_vestiti == "Moltissimi strati":
                opzioni_coperte = [
                    "Nessuna coperta",
                    "Più coperte pesanti"
                ]
            else:
                opzioni_coperte = [
                    "Nessuna coperta",
                    "Coperta leggera (es lenzuolo)",
                    "Coperta di medio spessore (es copriletto)",
                    "Coperta pesante (es piuminino invernale)",
                    "Più coperte pesanti"
                ]
            scelta_coperte = st.radio("", opzioni_coperte, label_visibility="collapsed")
        else:
            scelta_coperte = "/"

        mostra_corrente = not corpo_immerso and not (
            scelta_vestiti in [
                "2-3 strati sottili", "3-4 strati sottili",
                "1-2 strati spessi", "˃4 strati sottili o ˃2 strati spessi",
                "Moltissimi strati"
            ] or (not (corpo_immerso or corpo_bagnato) and scelta_coperte != "Nessuna coperta")
        )

        if mostra_corrente:
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Presenza di correnti</p>", unsafe_allow_html=True)
            corrente = st.radio("", [
                "Esposto a corrente d'aria",
                "Nessuna corrente"
            ], label_visibility="collapsed")
        elif corpo_immerso:
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Presenza di correnti</p>", unsafe_allow_html=True)
            corrente = st.radio("", [
                "In acqua corrente",
                "In acqua stagnante"
            ], label_visibility="collapsed")
        else:
            corrente = "/"

    with col3:
        if not (corpo_immerso or corpo_bagnato):
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Superficie di appoggio</p>", unsafe_allow_html=True)
            if scelta_vestiti == "Nudo":
                opzioni_superficie = [
                    "Pavimento di casa, terreno o prato asciutto, asfalto",
                    "Imbottitura pesante (es sacco a pelo isolante)",
                    "Materasso o tappeto spesso",
                    "Foglie umide (≥2 cm)",
                    "Foglie secche (≥2 cm)"
                ]
            else:
                opzioni_superficie = [
                    "Pavimento di casa, terreno o prato asciutto, asfalto",
                    "Imbottitura pesante (es sacco a pelo isolante)",
                    "Materasso o tappeto spesso"
                ]
            superficie = st.radio("", opzioni_superficie, label_visibility="collapsed")
        else:
            superficie = "/"


        try:
            fattore = riga.iloc[0]['Fattore']
            if fattore < 1.4 or peso == 70:
                st.success(f"Fattore di correzione stimato: {float(fattore):.2f} ({descrizione})")
            else:
                colonna_70 = tabella2["70"]
                indice_vicino = (colonna_70 - fattore).abs().idxmin()
                riga_tab2 = tabella2.loc[indice_vicino]

                colonna_peso = str(peso)
                if colonna_peso not in tabella2.columns:
                    # Arrotonda al valore più vicino disponibile
                    colonne_pesi = [int(c) for c in tabella2.columns if c.isnumeric()]
                    peso_vicino = min(colonne_pesi, key=lambda x: abs(x - peso))
                    colonna_peso = str(peso_vicino)
                    st.warning(f"valori di peso arrotondati.")

                fattore_corretto = riga_tab2[colonna_peso]
                st.info(f"Fattore corretto per {colonna_peso} kg: {fattore_corretto:.2f} ({descrizione})")
        except Exception as e:
            st.error(f"Errore nel calcolo: {e}")

peso_input = st.slider("Peso del corpo (kg)", min_value=30, max_value=150, value=70, step=1)
calcola_fattore(peso=peso_input)

