import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit.components.v1 as components
import numpy as np
from scipy.optimize import root_scalar
import datetime


# Definiamo un valore che rappresenta "infinito" o un limite superiore molto elevato per i range aperti
INF_HOURS = 200 # Un valore sufficientemente grande per la scala del grafico e i calcoli
    # =======================
    # 1) DATA E ORA ISPEZIONE LEGALE (prima sezione, due colonne)
    # =======================
with st.container():   
    st.markdown("""
    <h5 style="margin:0; padding:0;">Data e ora ispezione legale</h5>
    <hr style="margin:0; padding:0; height:1px; border:none; background-color:#ccc;">
    <div style="margin-top:10px;"></div>
    """, unsafe_allow_html=True)

    col_data, col_ora = st.columns([1, 1], gap="large")
    with col_data:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Data ispezione legale</div>", unsafe_allow_html=True)
        input_data_rilievo = st.date_input(
            "Data ispezione legale",
            value=datetime.date.today(),
            label_visibility="collapsed"
        )
    with col_ora:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ora ispezione legale</div>", unsafe_allow_html=True)
        input_ora_rilievo = st.text_input(
            "Ora:",
            value='00:00',
            label_visibility="collapsed"
        )

    st.write("")

    # =======================
    # 2) IPOSTASI | RIGIDITÀ (stessa riga, due colonne)
    # =======================
    col_ipostasi, col_rigidita = st.columns([1, 1], gap="large")

    with col_ipostasi:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ipostasi</div>", unsafe_allow_html=True)
        selettore_macchie = st.selectbox(
            "Macchie ipostatiche:",
            options=list(opzioni_macchie.keys()),
            label_visibility="collapsed"
        )

    with col_rigidita:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Rigidità</div>", unsafe_allow_html=True)
        selettore_rigidita = st.selectbox(
            "Rigidità cadaverica:",
            options=list(opzioni_rigidita.keys()),
            label_visibility="collapsed"
        )

    st.write("")

    # =======================
    # 3) TEMPERATURE (stessa riga, tre colonne, etichette vicine ai campi)
    # =======================
    col_t_rettale, col_t_amb, col_t_ante = st.columns([1, 1, 1], gap="large")

    with col_t_rettale:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Temperatura rettale (°C)</div>", unsafe_allow_html=True)
        input_rt = st.number_input(
            "Temperatura rettale (°C):",
            value=35.0,
            step=0.1,
            format="%.1f",
            label_visibility="collapsed"
        )

    with col_t_amb:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Temperatura ambientale (°C)</div>", unsafe_allow_html=True)
        input_ta = st.number_input(
            "Temperatura ambientale (°C):",
            value=20.0,
            step=0.1,
            format="%.1f",
            label_visibility="collapsed"
        )

    with col_t_ante:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>T. ante-mortem stimata (°C)</div>", unsafe_allow_html=True)
        input_t0 = st.number_input(
            "T. ante-mortem stimata (°C):",
            value=37.2,
            step=0.1,
            format="%.1f",
            label_visibility="collapsed"
        )

    st.write("")

    # =======================
    # 4) PESO | FATTORE DI CORREZIONE (stessa riga, due colonne)
    #    Pulsante con ingranaggio + testo "suggerisci"
    # =======================
    col_peso, col_fattore = st.columns([1, 1], gap="large")

    with col_peso:
        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Peso (kg)</div>", unsafe_allow_html=True)
        input_w = st.number_input(
            "Peso corporeo (kg):",
            value=70.0,
            step=1.0,
            format="%.1f",
            label_visibility="collapsed"
        )
        st.session_state["peso"] = input_w  # mantiene coerenza con calcola_fattore

    with col_fattore:
        # Se è presente un valore calcolato altrove, lo porta nel campo visibile (come già facevi)
        if "fattore_correzione" in st.session_state:
            st.session_state["fattore_correzione_input"] = st.session_state["fattore_correzione"]
            st.session_state.pop("fattore_correzione", None)

        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Fattore di correzione</div>", unsafe_allow_html=True)
        input_cf = st.number_input(
            "Fattore di correzione:",
            min_value=0.05,
            max_value=5.5,
            step=0.1,
            value=st.session_state.get("fattore_correzione_input", 1.0),
            label_visibility="collapsed",
            key="fattore_correzione_input"
        )

        # 🔘 Pulsante: ingranaggio + testo SOLO "suggerisci"
        perfeziona_cf = st.button("⚙️ suggerisci", key="perfeziona_cf")

    # 🔽 Fuori da tutte le colonne, piena larghezza (toggle identico al tuo)
    if perfeziona_cf:
        st.session_state["mostra_modulo_fattore"] = not st.session_state.get("mostra_modulo_fattore", False)

    if st.session_state.get("mostra_modulo_fattore", False):
        with st.expander("Suggerimento fattore di correzione", expanded=True):
            st.markdown(
                "<div style='background-color:#f0f4f8; padding:12px; border-radius:10px;'>",
                unsafe_allow_html=True
            )
            # ⬇️ Chiama la tua funzione esistente (invariata)
            calcola_fattore(peso=st.session_state.get("peso", 70))
            st.markdown("</div>", unsafe_allow_html=True)
grafico_generato = False

def aggiorna_grafico():
    global grafico_generato

    # --- Validazione Input Data/Ora Ispezione Legale ---
    if not input_data_rilievo or not input_ora_rilievo:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Completare data e ora dell'ispezione legale.</p>", unsafe_allow_html=True)
        return

    try:
        ora_isp_obj = datetime.datetime.strptime(input_ora_rilievo, '%H:%M')
        minuti_isp = ora_isp_obj.minute
    except ValueError:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Errore: Formato ora ispezione legale non valido. Utilizzare il formato HH:MM (es. 14:30).</p>", unsafe_allow_html=True)
        return

     # if minuti_isp not in [0, 15, 30, 45]:
         # st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Errore: I minuti dell'ora di ispezione legale devono essere arrotondati al quarto d'ora più vicino.</p>", unsafe_allow_html=True)
         # return

        
        
    data_ora_ispezione_originale = datetime.datetime.combine(input_data_rilievo, ora_isp_obj.time())
    data_ora_ispezione = arrotonda_quarto_dora(data_ora_ispezione_originale)

    # --- Recupero Valori Input per Calcoli (Esistenti) ---
    Tr_val = input_rt
    Ta_val = input_ta
    T0_val = input_t0
    W_val = input_w
    CF_val = input_cf

    macchie_selezionata = selettore_macchie
    rigidita_selezionata = selettore_rigidita

    t_med_raff_hensge_rounded, t_min_raff_hensge, t_max_raff_hensge, t_med_raff_hensge_rounded_raw, Qd_val_check = calcola_raffreddamento(
        Tr_val, Ta_val, T0_val, W_val, CF_val
    )

    raffreddamento_calcolabile = not np.isnan(t_med_raff_hensge_rounded) and t_med_raff_hensge_rounded >= 0

    temp_difference_small = False
    if Tr_val is not None and Ta_val is not None and (Tr_val - Ta_val) is not None and (Tr_val - Ta_val) < 2.0 and (Tr_val - Ta_val) >= 0:
        temp_difference_small = True

    macchie_range_valido = macchie_selezionata != "Non valutabili/Non attendibili"
    macchie_range = opzioni_macchie.get(macchie_selezionata) if macchie_range_valido else (np.nan, np.nan)
    macchie_medi_range = macchie_medi.get(macchie_selezionata) if macchie_range_valido else None

    rigidita_range_valido = rigidita_selezionata != "Non valutabile/Non attendibile"
    rigidita_range = opzioni_rigidita.get(rigidita_selezionata) if rigidita_range_valido else (np.nan, np.nan)
    rigidita_medi_range = rigidita_medi.get(rigidita_selezionata) if rigidita_range_valido else None

    parametri_aggiuntivi_da_considerare = []
    nota_globale_range_adattato = False

    for nome_parametro, widgets_param in widgets_parametri_aggiuntivi.items():
        stato_selezionato = widgets_param["selettore"]
        data_rilievo_param = widgets_param["data_rilievo"]
        ora_rilievo_param_str = widgets_param["ora_rilievo"]

        if stato_selezionato == "Non valutata":
            continue

        
        chiave_descrizione = stato_selezionato.split(':')[0].strip()
      

        # Usa ora ispezione legale se non presente valore personalizzato
        if not ora_rilievo_param_str or ora_rilievo_param_str.strip() == "":
            ora_rilievo_param_obj = data_ora_ispezione
        else:
            try:
                ora_rilievo_param_obj = datetime.datetime.strptime(ora_rilievo_param_str, '%H:%M')
                minuti_param = ora_rilievo_param_obj.minute
                if minuti_param not in [0, 30]:
                    st.markdown(f"<p style='color:orange;font-weight:bold;'>⚠️ Avviso: L'ora di rilievo per '{nome_parametro}' ({ora_rilievo_param_str}) non è arrotondata alla mezzora. Questo parametro non sarà considerato nella stima.</p>", unsafe_allow_html=True)
                    continue
            except ValueError:
                st.markdown(f"<p style='color:orange;font-weight:bold;'>⚠️ Avviso: Formato ora di rilievo non valido per '{nome_parametro}' ({ora_rilievo_param_str}). Utilizzare il formato HH:MM (es. 14:30). Questo parametro non sarà considerato nella stima.</p>", unsafe_allow_html=True)
                continue

        # Se data personalizzata assente, usa quella dell’ispezione
        if data_rilievo_param is None:
            data_rilievo_param = data_ora_ispezione.date()

        # Determina la chiave corretta da usare per cercare nel dizionario dei range
        if nome_parametro == "Eccitabilità elettrica peribuccale":
            chiave_descrizione = stato_selezionato.split(':')[0].strip()
        else:
            chiave_descrizione = stato_selezionato.strip()

        # Forza il recupero esatto della chiave anche se ci sono spazi invisibili
        chiave_esatta = None
        for k in dati_parametri_aggiuntivi[nome_parametro]["range"].keys():
            if k.strip() == chiave_descrizione:
                chiave_esatta = k
                break

        range_valori = dati_parametri_aggiuntivi[nome_parametro]["range"].get(chiave_esatta)
        range_originale = range_valori

        if range_valori:
            descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"Descrizione non trovata per lo stato '{stato_selezionato}'.")

            # Calcolo data e ora param
            if isinstance(ora_rilievo_param_obj, datetime.datetime):
                ora_rilievo_time = ora_rilievo_param_obj.time()
            else:
                ora_rilievo_time = ora_rilievo_param_obj

            data_ora_param = datetime.datetime.combine(data_rilievo_param, ora_rilievo_time)
            differenza_ore = (data_ora_param - data_ora_ispezione).total_seconds() / 3600.0

            if range_originale[1] >= INF_HOURS:
                range_traslato = (range_originale[0] - differenza_ore, INF_HOURS)
            else:
                range_traslato = (range_originale[0] - differenza_ore, range_originale[1] - differenza_ore)

            range_traslato_rounded = (round_quarter_hour(range_traslato[0]), round_quarter_hour(range_traslato[1]))
            range_traslato_rounded = (max(0, range_traslato_rounded[0]), range_traslato_rounded[1])

            parametri_aggiuntivi_da_considerare.append({
                "nome": nome_parametro,
                "stato": stato_selezionato,
                "range_traslato": range_traslato_rounded,
                "descrizione": descrizione,
                "differenza_ore": differenza_ore,
                "adattato": differenza_ore != 0
            })


            differenze_ore_set = set(
                p["differenza_ore"]
                for p in parametri_aggiuntivi_da_considerare
                if p.get("adattato")
            )
            nota_globale_range_adattato = len(differenze_ore_set) == 1 and len(differenze_ore_set) > 0

        elif dati_parametri_aggiuntivi[nome_parametro]["range"].get(stato_selezionato) is None:
            descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"Il parametro {nome_parametro} ({stato_selezionato}) non ha un range temporale definito o descrizione specifica.")
            parametri_aggiuntivi_da_considerare.append({
                "nome": nome_parametro,
                "stato": stato_selezionato,
                "range_traslato": (np.nan, np.nan),
                "descrizione": descrizione
            })
    # --- Determinazione Range Raffreddamento per Visualizzazione nel Grafico ---
    # Il range visualizzato per Henssge > 30h sarà un range ±20% attorno a t_med_raw
    t_min_raff_visualizzato = np.nan
    t_max_raff_visualizzato = np.nan

    # --- Definisce i range USATI per l'intersezione (stima complessiva) ---
    ranges_per_intersezione_inizio = []
    ranges_per_intersezione_fine = []
    # Lista per tenere traccia dei nomi dei parametri USATI per l'intersezione
    nomi_parametri_usati_per_intersezione = []

    # Determina se visualizzare il range Henssge sul grafico
    visualizza_hensge_grafico = raffreddamento_calcolabile

    if visualizza_hensge_grafico:
        # Usa i limiti calcolati da calcola_raffreddamento per la visualizzazione
        t_min_raff_visualizzato = t_min_raff_hensge
        t_max_raff_visualizzato = t_max_raff_hensge
    else:
        # Se non visualizzabile, imposta NaN
        t_min_raff_visualizzato = np.nan
        t_max_raff_visualizzato = np.nan

    # --- Fine Determinazione Range Raffreddamento Visualizzazione ---

    # Aggiunge range macchie se valido e presente
    if macchie_range_valido and macchie_range is not None:
        ranges_per_intersezione_inizio.append(macchie_range[0])
        ranges_per_intersezione_fine.append(macchie_range[1])
        nomi_parametri_usati_per_intersezione.append("macchie ipostatiche")

    # Aggiunge range rigidità se valido e presente
    if rigidita_range_valido and rigidita_range is not None:
        ranges_per_intersezione_inizio.append(rigidita_range[0])
        ranges_per_intersezione_fine.append(rigidita_range[1])
        nomi_parametri_usati_per_intersezione.append("rigidità cadaverica")

    # --- Stima minima post mortem secondo Potente et al. (calcolato prima di costruire i range) ---
    mt_ore = None
    mt_giorni = None
    if not any(np.isnan(val) for val in [Tr_val, Ta_val, CF_val, W_val]):
        if Tr_val <= Ta_val + 1e-6:
            mt_ore = None
            mt_giorni = None
        else:
            Qd_potente = (Tr_val - Ta_val) / (37.2 - Ta_val)
            soglia_qd = 0.2 if Ta_val <= 23 else 0.5
            if Qd_potente < soglia_qd:
                B_potente = -1.2815 * (CF_val * W_val) ** (-5 / 8) + 0.0284
                ln_term = np.log(0.16) if Ta_val <= 23 else np.log(0.45)
                mt_ore = round(ln_term / B_potente, 1)
                mt_giorni = round(mt_ore / 24, 1)

    # Aggiunge range dei parametri aggiuntivi, considerando sempre il limite inferiore
    for p in parametri_aggiuntivi_da_considerare:
        if not np.isnan(p["range_traslato"][0]):
            ranges_per_intersezione_inizio.append(p["range_traslato"][0])
            if np.isnan(p["range_traslato"][1]) or p["range_traslato"][1] >= INF_HOURS:
                ranges_per_intersezione_fine.append(np.nan)
            else:
                ranges_per_intersezione_fine.append(p["range_traslato"][1])
            nomi_parametri_usati_per_intersezione.append(p["nome"])

    if raffreddamento_calcolabile:
        usa_solo_limite_inferiore_henssge = False
        if not np.isnan(Qd_val_check) and Qd_val_check < 0.2:
            usa_solo_limite_inferiore_henssge = True

        altri_parametri_con_range = any([
            macchie_range_valido and macchie_range[1] < INF_HOURS,
            rigidita_range_valido and rigidita_range[1] < INF_HOURS,
            any(
                not np.isnan(p["range_traslato"][0]) and
                not np.isnan(p["range_traslato"][1]) and
                p["range_traslato"][1] < INF_HOURS
                for p in parametri_aggiuntivi_da_considerare
            )
        ])

        if usa_solo_limite_inferiore_henssge:
            if mt_ore is not None and not np.isnan(mt_ore):
                ranges_per_intersezione_inizio.append(mt_ore)
                ranges_per_intersezione_fine.append(np.nan)
                nome_raffreddamento_intersezione = (
                    "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
                )
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
            else:
                ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                ranges_per_intersezione_fine.append(np.nan)
                nome_raffreddamento_intersezione = (
                    "raffreddamento cadaverico (\u00e8 stato considerato solo il limite inferiore, vista la limitata affidabilit\u00e0 del calcolo per i motivi sopraesposti)"
                )
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
        else:
            if t_med_raff_hensge_rounded_raw > 48:
                if altri_parametri_con_range:
                    if t_min_raff_hensge > 48:
                        ranges_per_intersezione_inizio.append(48.0)
                        ranges_per_intersezione_fine.append(np.nan)
                        nome_raffreddamento_intersezione = (
                            "raffreddamento cadaverico (che \u00e8 stato considerato genericamente > 48h, vista la limitata affidabilit\u00e0 del calcolo per i motivi sopraesposti)"
                        )
                        nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
                    else:
                        ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                        ranges_per_intersezione_fine.append(t_max_raff_hensge)
                        nome_raffreddamento_intersezione = "raffreddamento cadaverico"
                        nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
            else:
                ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                ranges_per_intersezione_fine.append(t_max_raff_hensge)
                nome_raffreddamento_intersezione = "raffreddamento cadaverico"
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)

    if 'mt_ore' in locals() and mt_ore is not None and not np.isnan(mt_ore):
        ranges_per_intersezione_inizio.append(mt_ore)
        ranges_per_intersezione_fine.append(np.nan)

    if len(ranges_per_intersezione_inizio) > 0:
        comune_inizio = max(ranges_per_intersezione_inizio)
        if mt_ore is not None and not np.isnan(mt_ore):
            altri_limiti_inferiori = [
                v for v, n in zip(ranges_per_intersezione_inizio, nomi_parametri_usati_per_intersezione)
                if "raffreddamento cadaverico" not in n.lower() or "potente" in n.lower()
            ]
            if len(altri_limiti_inferiori) > 0:
                limite_minimo_altri = max(altri_limiti_inferiori)
                if mt_ore >= limite_minimo_altri:
                    comune_inizio = round(mt_ore)

        superiori_finiti = [v for v in ranges_per_intersezione_fine if not np.isnan(v) and v < INF_HOURS]

        if len(superiori_finiti) > 0:
            comune_fine = min(superiori_finiti)
        else:
            comune_fine = np.nan

        if np.isnan(comune_fine):
            overlap = True
        else:
            overlap = comune_inizio <= comune_fine
    else:
        comune_inizio, comune_fine = np.nan, np.nan
        overlap = False


        # --- Sezione dedicata alla generazione del grafico ---

    # Determina il numero totale di parametri da mostrare nel grafico
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if visualizza_hensge_grafico: num_params_grafico += 1
    num_params_grafico += len([p for p in parametri_aggiuntivi_da_considerare if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1])])

    if num_params_grafico > 0:
        fig, ax = plt.subplots(figsize=(10, max(2, 1.5 + 0.5 * num_params_grafico)))

        y_indices_mapping = {}
        current_y_index = 0

        parametri_grafico = []
        ranges_to_plot_inizio = []
        ranges_to_plot_fine = []

        if macchie_range_valido and macchie_range is not None:
            nome_breve_macchie = "Ipostasi"
            if macchie_range[1] < INF_HOURS:
                label_macchie = f"{nome_breve_macchie}\n({macchie_range[0]:.1f}–{macchie_range[1]:.1f} h)"
            else:
                label_macchie = f"{nome_breve_macchie}\n(≥ {macchie_range[0]:.1f} h)"
            parametri_grafico.append(label_macchie)
            ranges_to_plot_inizio.append(macchie_range[0])
            ranges_to_plot_fine.append(macchie_range[1] if macchie_range[1] < INF_HOURS else INF_HOURS)

        if rigidita_range_valido and rigidita_range is not None:
            nome_breve_rigidita = "Rigor"
            if rigidita_range[1] < INF_HOURS:
                label_rigidita = f"{nome_breve_rigidita}\n({rigidita_range[0]:.1f}–{rigidita_range[1]:.1f} h)"
            else:
                label_rigidita = f"{nome_breve_rigidita}\n(≥ {rigidita_range[0]:.1f} h)"
            parametri_grafico.append(label_rigidita)
            ranges_to_plot_inizio.append(rigidita_range[0])
            ranges_to_plot_fine.append(rigidita_range[1] if rigidita_range[1] < INF_HOURS else INF_HOURS)


        if raffreddamento_calcolabile:
            nome_breve_hensge = "Hensge"
            usa_solo_limite_inferiore_henssge = not np.isnan(Qd_val_check) and Qd_val_check < 0.2

            if usa_solo_limite_inferiore_henssge:
                maggiore_di_valore = t_min_raff_hensge
                usa_potente = False
                if mt_ore is not None and not np.isnan(mt_ore):
                    maggiore_di_valore = round(mt_ore)
                    usa_potente = True

                if usa_potente:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore} h)"
                else:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore:.1f} h)\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"

                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            elif t_med_raff_hensge_rounded_raw > 30:
                maggiore_di_valore = 30.0
                usa_potente = False
                if mt_ore is not None and not np.isnan(mt_ore):
                    maggiore_di_valore = round(mt_ore)
                    usa_potente = True

                if usa_potente:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore} h)"
                else:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore:.1f} h)\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"

                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            else:
                label_hensge = f"{nome_breve_hensge}\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"
                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            parametri_grafico.append(label_hensge)


        for param in parametri_aggiuntivi_da_considerare:
            if not np.isnan(param["range_traslato"][0]) and not np.isnan(param["range_traslato"][1]):
                nome_breve = nomi_brevi.get(param['nome'], param['nome'])

                if param['range_traslato'][1] == INF_HOURS:
                    label_param_aggiuntivo = f"{nome_breve}\n(≥ {param['range_traslato'][0]:.1f} h)"
                else:
                    label_param_aggiuntivo = f"{nome_breve}\n({param['range_traslato'][0]:.1f}–{param['range_traslato'][1]:.1f} h)"

                if param.get('adattato', False):
                    label_param_aggiuntivo += " *"

                parametri_grafico.append(label_param_aggiuntivo)
                ranges_to_plot_inizio.append(param["range_traslato"][0])
                ranges_to_plot_fine.append(param["range_traslato"][1] if param["range_traslato"][1] < INF_HOURS else INF_HOURS)

                y_indices_mapping[label_param_aggiuntivo] = current_y_index
                current_y_index += 1

        for i, (s, e) in enumerate(zip(ranges_to_plot_inizio, ranges_to_plot_fine)):
            if not np.isnan(s) and not np.isnan(e):
                ax.hlines(i, s, e, color='steelblue', linewidth=6)

        if visualizza_hensge_grafico:
            idx = parametri_grafico.index(label_hensge) if label_hensge in parametri_grafico else None
            
            if idx is not None:
                if mt_ore is not None and not np.isnan(mt_ore):
                    ax.hlines(y=idx, xmin=mt_ore, xmax=INF_HOURS, color='orange', linewidth=6, alpha=0.6, zorder=1)
                if (not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and
                    t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30):
                    ax.hlines(y=idx, xmin=30.0, xmax=INF_HOURS, color='orange', linewidth=6, alpha=0.6, zorder=1)

        # Mapping asse Y statico per righe principali
        y_indices_mapping = {}
        current_y_index = 0
        if macchie_range_valido and macchie_range is not None:
            y_indices_mapping["Macchie ipostatiche"] = current_y_index
            current_y_index += 1
        if rigidita_range_valido and rigidita_range is not None:
            y_indices_mapping["Rigidità cadaverica"] = current_y_index
            current_y_index += 1
        if visualizza_hensge_grafico:
            y_indices_mapping["Raffreddamento cadaverico"] = current_y_index
            current_y_index += 1

        if macchie_range_valido and macchie_medi_range is not None:
            if "Macchie ipostatiche" in y_indices_mapping:
                ax.hlines(y_indices_mapping["Macchie ipostatiche"], macchie_medi_range[0], macchie_medi_range[1], color='orange', linewidth=6, alpha=0.6)

        if rigidita_range_valido and rigidita_medi_range is not None:
            if "Rigidità cadaverica" in y_indices_mapping:
                ax.hlines(y_indices_mapping["Rigidità cadaverica"], rigidita_medi_range[0], rigidita_medi_range[1], color='orange', linewidth=6, alpha=0.6)

        if visualizza_hensge_grafico:
            if "Raffreddamento cadaverico" in y_indices_mapping:
                y_pos_raffreddamento = y_indices_mapping["Raffreddamento cadaverico"]
                punto_medio_raffreddamento = (t_min_raff_visualizzato + t_max_raff_visualizzato) / 2
                offset = 0.1
                ax.hlines(y_pos_raffreddamento, punto_medio_raffreddamento - offset, punto_medio_raffreddamento + offset, color='orange', linewidth=6, alpha=0.8)

        ax.set_yticks(range(len(parametri_grafico)))
        ax.set_yticklabels(parametri_grafico, fontsize=9)
        ax.set_xlabel("Ore dal decesso")

        max_x_value = 10
        all_limits = ranges_to_plot_fine + ranges_to_plot_inizio
        valid_limits = [lim for lim in all_limits if not np.isnan(lim) and lim < INF_HOURS]
        if valid_limits:
            max_x_value = max(max_x_value, max(valid_limits) * 1.1)
            max_x_value = max(max_x_value, 10)

        ax.set_xlim(0, max_x_value)
        ax.grid(True, axis='x', linestyle=':', alpha=0.6)

        if overlap and comune_inizio < max_x_value and comune_fine > 0:
            ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
            ax.axvline(min(max_x_value, comune_fine), color='red', linestyle='--')

        plt.tight_layout()
        st.pyplot(fig)
        grafico_generato = True
    else:
        st.markdown((
            "<p style='color:orange;font-weight:bold;'>⚠️ Nessun parametro tanatologico con un range valido da visualizzare nel grafico.</p>"
        ), unsafe_allow_html=True)
        grafico_generato = False
    # --- Visualizza SEMPRE il testo descrittivo del raffreddamento (se i dati Henssge sono stati forniti) e relativi avvisi ---
    if nota_globale_range_adattato:
        st.markdown((
            "<p style='color:gray;font-size:small;'>"
            "* alcuni parametri sono stati valutati a orari diversi, ma il range indicato sul grafico e nelle eventuali stime è stato adattato di conseguenza, rendendo confrontabili tra loro gli intervalli."
            "</p>"
        ), unsafe_allow_html=True)

    if minuti_isp not in [0, 15, 30, 45]:
        st.markdown(
    "<p style='color:darkorange;font-size:small;'>NB: Considerati i limiti intrinseci dei metodi utilizzati, l’orario dei rilievi tanatologici è stato automaticamente arrotondato al quarto d’ora più vicino.</p>",
    unsafe_allow_html=True
        )
        
    hensge_input_forniti = (
        input_rt is not None and
        input_ta is not None and
        input_t0 is not None and
        input_w is not None and
        input_cf is not None
    )

    if hensge_input_forniti:

        if Ta_val > 25:
            st.markdown((
                "<p style='color:darkorange;font-size:small;'>"
                "Per la temperatura selezionata (&gt; 25 °C), la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati. Scegliere il fattore con cura."
                "</p>"
            ), unsafe_allow_html=True)

        if Ta_val < 18:
            st.markdown((
                "<p style='color:darkorange;font-size:small;'>"
                "Per la temperatura selezionata (&lt; 18 °C), la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati. Scegliere il fattore con cura."
                "</p>"
            ), unsafe_allow_html=True)

        if temp_difference_small:
            st.markdown((
                "<p style='color:darkorange;font-size:small;'>"
                "Essendo minima la differenza tra temperatura rettale e ambientale, "
                "è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. "
                "La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione."
                "</p>"
            ), unsafe_allow_html=True)

        if not raffreddamento_calcolabile:
            st.markdown((
                "<p style='color:orange;font-size:normal;'>⚠️ Non è stato possibile ricavare stime applicando il metodo di Henssge con i valori inseriti "
                "(possibile causa: temperature incoerenti o valori fuori range per il nomogramma).</p>"
            ), unsafe_allow_html=True)
        else:
            if visualizza_hensge_grafico:
                limite_inferiore_testo = t_min_raff_visualizzato
                limite_superiore_testo = t_max_raff_visualizzato
            else:
                limite_inferiore_testo = t_min_raff_hensge
                limite_superiore_testo = t_max_raff_hensge

            if not np.isnan(limite_inferiore_testo) and not np.isnan(limite_superiore_testo):
                min_raff_hours = int(limite_inferiore_testo)
                min_raff_minutes = int(round((limite_inferiore_testo % 1) * 60))
                max_raff_hours = int(limite_superiore_testo)
                max_raff_minutes = int(round((limite_superiore_testo % 1) * 60))

                min_raff_hour_text = "ora" if min_raff_hours == 1 and min_raff_minutes == 0 else "ore"
                max_raff_hour_text = "ora" if max_raff_hours == 1 and max_raff_minutes == 0 else "ore"

    # Testo base sempre incluso
    testo_raff_base = (
        f"Applicando il nomogramma di Henssge, è possibile stimare che il decesso sia avvenuto tra circa "
        f"{min_raff_hours} {min_raff_hour_text}{'' if min_raff_minutes == 0 else f' {min_raff_minutes} minuti'} e "
        f"{max_raff_hours} {max_raff_hour_text}{'' if max_raff_minutes == 0 else f' {max_raff_minutes} minuti'} "
        f"prima dei rilievi effettuati al momento dell’ispezione legale."
    )

    # Avvio struttura HTML
    testo_raff_completo = f"<ul><li>{testo_raff_base}"

    # Lista dinamica
    elenco_extra = []

    # Qd troppo basso
    if not np.isnan(Qd_val_check) and Qd_val_check < 0.2:
        elenco_extra.append(
            f"<li>"
            f"I valori ottenuti, tuttavia, sono in parte o totalmente fuori dai range ottimali delle equazioni applicabili "
            f"(Valore di Qd ottenuto: <b>{Qd_val_check:.5f}</b>, &lt; 0.2) "
            f"(il range temporale indicato è stato calcolato, grossolanamente, come pari al ±20% del valore medio ottenuto dalla stima del raffreddamento cadaverico - {t_med_raff_hensge_rounded:.1f} ore -, ma tale range è privo di una solida base statistica). "
            f"In mancanza di ulteriori dati o interpretazioni, si può presumere che il raffreddamento cadaverico fosse ormai concluso. "
            f"Per tale motivo, il range ottenuto è da ritenersi del tutto indicativo e per la stima dell'epoca del decesso è consigliabile far riferimento principalmente ad altri dati tanatologici."
            f"</li>"
        )

    # Qd alto e durata > 30 ore
    if not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and t_med_raff_hensge_rounded_raw > 30:
        elenco_extra.append(
            f"<li>"
            f"<span style='color:orange; font-weight:bold;'>"
            f"La stima media ottenuta dal raffreddamento cadaverico ({t_med_raff_hensge_rounded:.1f} h) è superiore alle 30 ore. "
            f"L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
            f"</span>"
            f"</li>"
        )

    # Metodo Potente et al.
    soglia_qd = 0.2 if Ta_val <= 23 else 0.5
    if mt_ore is not None and not np.isnan(mt_ore) and Qd_val_check is not None and Qd_val_check < soglia_qd:
        elenco_extra.append(
            f"<li>"
            f"Lo studio di Potente et al. permette di stimare grossolanamente l’intervallo minimo post-mortem quando i dati non consentono di ottenere risultati attendibili con il metodo di Henssge "
            f"(Qd &lt; {soglia_qd} e Ta ≤ 23 °C). "
            f"Applicandolo al caso specifico, si può ipotizzare che, al momento dell’ispezione legale, fossero trascorse almeno <b>{mt_ore:.0f}</b> ore (≈ {mt_giorni:.1f} giorni) dal decesso."
            f"<ul><li><span style='font-size:smaller;'>"
            f"Potente S, Kettner M, Verhoff MA, Ishikawa T. Minimum time since death when the body has either reached or closely approximated equilibrium with ambient temperature. "
            f"<i>Forensic Sci Int.</i> 2017;281:63–66. doi: 10.1016/j.forsciint.2017.09.012."
            f"</span></li></ul>"
            f"</li>"
        )

    # Se ci sono elementi extra, aggiungili
    if elenco_extra:
        testo_raff_completo += "<ul>" + "".join(elenco_extra) + "</ul>"

    # Chiudi blocco principale
    testo_raff_completo += "</li></ul>"

    # Visualizza
    st.markdown(testo_raff_completo, unsafe_allow_html=True)



    # --- Visualizza i testi descrittivi per macchie ipostatiche e rigidità cadaverica ---
    st.markdown((f"<ul><li>{testi_macchie[macchie_selezionata]}</li></ul>"), unsafe_allow_html=True)
    st.markdown((f"<ul><li>{rigidita_descrizioni[rigidita_selezionata]}</li></ul>"), unsafe_allow_html=True)
    for param in parametri_aggiuntivi_da_considerare:
       if param["stato"] != "Non valutata" and param["stato"] != "Non valutabile/non attendibile":
           st.markdown(f"<ul><li>{param['descrizione']}</li></ul>", unsafe_allow_html=True)

    # --- Fine Visualizzazione Testi Descrittivi Fissi ---
    # --- Fine Visualizzazione Testi Descrittivi Aggiuntivi ---
    # --- Visualizza Stima Complessiva e Messaggi di Incoerenza ---

    # Conta quanti range *potenzialmente* sono stati usati per l'intersezione (quelli con limite superiore < INF_HOURS)
    num_potential_ranges_used = int(macchie_range_valido and macchie_range is not None and macchie_range[1] < INF_HOURS) + \
                                int(rigidita_range_valido and rigidita_range is not None and rigidita_range[1] < INF_HOURS) + \
                                int(raffreddamento_calcolabile and not temp_difference_small and t_med_raff_hensge_rounded <= 30) + \
                                sum(1 for param in parametri_aggiuntivi_da_considerare if not np.isnan(param["range_traslato"][0]) and not np.isnan(param["range_traslato"][1]) and param["range_traslato"][1] < INF_HOURS)

    # Se invece overlap è True, stampiamo SEMPRE la frase di stima complessiva (anche con range aperti sopra)
    if overlap:
        try:
            isp = data_ora_ispezione
        except Exception:
            return

        limite_superiore_infinito = np.isnan(comune_fine) or comune_fine == INF_HOURS

        if (not np.isnan(Qd_val_check) and Qd_val_check < 0.3
            and comune_inizio > 30
            and (np.isnan(comune_fine) or comune_fine == INF_HOURS)):

            comune_inizio_hours = int(comune_inizio)
            comune_inizio_minutes = int(round((comune_inizio % 1) * 60))
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            if not np.isnan(Qd_val_check) and Qd_val_check <= 0.2 and not np.isnan(mt_ore) and mt_ore > 30:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                    f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                    f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                    f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                    f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}. "
                    f"Occorre tener conto che l'affidabilità del metodo di Henssge diminuisce significativamente quando sono trascorse più di 30 ore dal decesso, e tale dato è da considerarsi del tutto indicativo."
                )

        elif limite_superiore_infinito:
            # Arrotonda Potente se usato come limite minimo
            if mt_ore is not None and not np.isnan(mt_ore):
                if abs(comune_inizio - mt_ore) < 0.25:
                    comune_inizio = round(mt_ore)

            comune_inizio_hours = int(comune_inizio)
            comune_inizio_minutes = int(round((comune_inizio % 1) * 60))
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            testo = (
                f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )

        elif comune_inizio == 0:
            comune_fine_hours = int(comune_fine)
            comune_fine_minutes = int(round((comune_fine % 1) * 60))
            fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            testo = (
                f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                f"consente di stimare che la morte sia avvenuta <b>non oltre</b> "
                f"{comune_fine_hours} {fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero successivamente alle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )

        else:
            comune_inizio_hours = int(comune_inizio)
            comune_inizio_minutes = int(round((comune_inizio % 1) * 60))
            comune_fine_hours = int(comune_fine)
            comune_fine_minutes = int(round((comune_fine % 1) * 60))
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 else "ore"
            comune_fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            aa = isp - datetime.timedelta(hours=comune_inizio)

            if da.date() == aa.date():
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} e le ore {aa.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')} e le ore {aa.strftime('%H:%M')} del {aa.strftime('%d.%m.%Y')}."
                )

        st.markdown(f"<b>{testo}</b>", unsafe_allow_html=True)
    # --- Frase aggiuntiva SENZA considerare lo studio di Potente (in grigio) ---
    if any("potente" in nome.lower() for nome in nomi_parametri_usati_per_intersezione):
        range_inizio_senza_potente = []
        range_fine_senza_potente = []

        if macchie_range_valido and macchie_range is not None:
            range_inizio_senza_potente.append(macchie_range[0])
            range_fine_senza_potente.append(macchie_range[1])

        if rigidita_range_valido and rigidita_range is not None:
            range_inizio_senza_potente.append(rigidita_range[0])
            range_fine_senza_potente.append(rigidita_range[1])

        for p in parametri_aggiuntivi_da_considerare:
            if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1]):
                range_inizio_senza_potente.append(p["range_traslato"][0])
                range_fine_senza_potente.append(p["range_traslato"][1])

        if raffreddamento_calcolabile:
            range_inizio_senza_potente.append(t_min_raff_hensge)
            range_fine_senza_potente.append(t_max_raff_hensge)


        
        if len(range_inizio_senza_potente) >= 2:
            inizio_senza_potente = max(range_inizio_senza_potente)
            fine_senza_potente = min(range_fine_senza_potente)
            if inizio_senza_potente <= fine_senza_potente:
                inizio_h = int(inizio_senza_potente)
                inizio_m = int(round((inizio_senza_potente % 1) * 60))
                fine_h = int(fine_senza_potente)
                fine_m = int(round((fine_senza_potente % 1) * 60))

                inizio_text = "ora" if inizio_h == 1 and inizio_m == 0 else "ore"
                fine_text = "ora" if fine_h == 1 and fine_m == 0 else "ore"

                dt_inizio = data_ora_ispezione - datetime.timedelta(hours=fine_senza_potente)
                dt_fine = data_ora_ispezione - datetime.timedelta(hours=inizio_senza_potente)

                frase_secondaria = (
                    f"<b>Senza considerare lo studio di Potente</b>, la valutazione complessiva dei dati tanatologici, "
                    f"integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                    f"consente di stimare che la morte  sia avvenuta tra circa "
                    f"{inizio_h} {inizio_text}{'' if inizio_m == 0 else f' {inizio_m} minuti'} e "
                    f"{fine_h} {fine_text}{'' if fine_m == 0 else f' {fine_m} minuti'} "
                    f"prima dei rilievi effettuati al momento dell’ispezione legale, "
                    f"ovvero tra le ore {dt_inizio.strftime('%H:%M')} del {dt_inizio.strftime('%d.%m.%Y')} "
                    f"e le ore {dt_fine.strftime('%H:%M')} del {dt_fine.strftime('%d.%m.%Y')}."
                )

                st.markdown(
                    f"<div style='border:1px solid #ccc; padding:10px; color:gray; font-size:small;'>{frase_secondaria}</div>",
                    unsafe_allow_html=True
                )

    if overlap and len(nomi_parametri_usati_per_intersezione) > 0:
        # Filtra la lista dei nomi da mostrare nel riepilogo finale
        nomi_parametri_finali_per_riepilogo = []
        for nome in nomi_parametri_usati_per_intersezione:
            # Escludi il raffreddamento Henssge generico se non usato
            if (
                "raffreddamento cadaverico" in nome.lower()
                and "potente" not in nome.lower()
                and mt_ore is not None
                and not np.isnan(mt_ore)
                and abs(comune_inizio - mt_ore) < 0.25
            ):
                continue
            nomi_parametri_finali_per_riepilogo.append(nome)

        num_parametri_usati_intersezione = len(nomi_parametri_finali_per_riepilogo)
        if num_parametri_usati_intersezione == 1:
            p = nomi_parametri_finali_per_riepilogo[0]
            messaggio_parametri = f"La stima complessiva si basa sul seguente parametro: {p[0].lower() + p[1:]}."
        elif num_parametri_usati_intersezione > 1:
            parametri_usati_str = ', '.join(p[0].lower() + p[1:] for p in nomi_parametri_finali_per_riepilogo[:-1])
            parametri_usati_str += f" e {nomi_parametri_finali_per_riepilogo[-1][0].lower() + nomi_parametri_finali_per_riepilogo[-1][1:]}"
            messaggio_parametri = f"La stima complessiva si basa sui seguenti parametri: {parametri_usati_str}."
        else:
            messaggio_parametri = None

        if messaggio_parametri:
            st.markdown(
                f"<p style='color:orange;font-size:small;'>{messaggio_parametri}</p>",
                unsafe_allow_html=True
            )

    elif not overlap and num_potential_ranges_used >= 2:
        st.markdown(
            "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
            unsafe_allow_html=True
        )
    elif ranges_in_disaccordo_completa(ranges_per_intersezione_inizio, ranges_per_intersezione_fine):
        st.markdown(
            "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
            unsafe_allow_html=True
        )


# Al click del pulsante, esegui la funzione principale
if pulsante_genera_stima:
    aggiorna_grafico()



