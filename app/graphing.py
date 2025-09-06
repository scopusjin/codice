# app/graphing.py
from __future__ import annotations
import datetime
from typing import Dict, List, Any

import numpy as np
import streamlit as st

from app.factor_calc import build_cf_description
from app.henssge import calcola_raffreddamento, ranges_in_disaccordo_completa
from app.parameters import (
    INF_HOURS, opzioni_macchie, macchie_medi, testi_macchie,
    opzioni_rigidita, rigidita_medi, rigidita_descrizioni,
    dati_parametri_aggiuntivi, nomi_brevi,
)
from app.utils_time import arrotonda_quarto_dora, round_quarter_hour
from app.plotting import compute_plot_data, render_ranges_plot
from app.textgen import (
    build_final_sentence, paragrafo_raffreddamento_dettaglio, paragrafo_potente,
    paragrafo_raffreddamento_input, paragrafi_descrizioni_base,
    paragrafi_parametri_aggiuntivi, paragrafo_putrefattive,
    frase_riepilogo_parametri_usati, avvisi_raffreddamento_henssge,
    frase_qd, build_simple_sentence, build_final_sentence_simple, build_simple_sentence_no_dt,
)
from app.cautelativa import compute_raffreddamento_cautelativo


# --------- helpers ----------
def _is_num(x): return x is not None and not (isinstance(x, float) and np.isnan(x))

def _warn_box(msg: str):
    pal = dict(bg="#fff3cd", text="#664d03", border="#ffda6a")
    base = st.get_option("theme.base") or "light"
    if base.lower() == "dark":
        pal = dict(bg="#3b2a00", text="#ffe08a", border="#8a6d1a")
    st.markdown(
        f'<div style="background:{pal["bg"]};color:{pal["text"]};'
        f'border:1px solid {pal["border"]};border-radius:6px;'
        f'padding:8px 10px;margin:4px 0;font-size:0.92rem;">'
        f'⚠️ {msg}</div>', unsafe_allow_html=True
    )

def _wrap_final(s: str | None) -> str | None:
    return f'<div class="final-text">{s}</div>' if s else s


# --------- pubblico ----------
def aggiorna_grafico(
    *,
    selettore_macchie: str,
    selettore_rigidita: str,
    input_rt: float, input_ta: float, input_tm: float, input_w: float,
    fattore_correzione: float,
    widgets_parametri_aggiuntivi: Dict[str, Dict[str, Any]],
    usa_orario_custom: bool,
    input_data_rilievo: datetime.date | None,
    input_ora_rilievo: str | None,
    alterazioni_putrefattive: bool,
):
    avvisi: List[str] = []
    dettagli: List[str] = []

    # --- data/ora ispezione ---
    if usa_orario_custom:
        if not input_data_rilievo or not input_ora_rilievo:
            st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Inserisci data e ora dell'ispezione legale.</p>", unsafe_allow_html=True)
            return
        try:
            ora_isp_obj = datetime.datetime.strptime(input_ora_rilievo, "%H:%M")
            minuti_isp = ora_isp_obj.minute
        except ValueError:
            st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Errore: formato ora ispezione legale non valido. Usa HH:MM.</p>", unsafe_allow_html=True)
            return
        data_ora_ispezione = arrotonda_quarto_dora(datetime.datetime.combine(input_data_rilievo, ora_isp_obj.time()))
    else:
        minuti_isp = 0
        data_ora_ispezione = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))

    # --- validazioni base ---
    if input_w is None or input_w <= 0:
        st.error("⚠️ Peso non valido. Inserire un valore > 0 kg.")
        return
    if fattore_correzione is None or fattore_correzione <= 0:
        st.error("⚠️ Fattore di correzione non valido. Inserire un valore > 0.")
        return
    if any(v is None for v in [input_rt, input_ta, input_tm]):
        st.error("⚠️ Temperature mancanti.")
        return

    Tr_val, Ta_val, T0_val, W_val, CF_val = input_rt, input_ta, input_tm, input_w, fattore_correzione

    # =========================
    # Henssge standard / Cautelativa
    # =========================
    qd_threshold = 0.2 if Ta_val <= 23 else 0.5

    if st.session_state.get("stima_cautelativa_beta", False):
        # --- TA range ---
        Ta_range = None
        if "Ta_min_beta" in st.session_state and "Ta_max_beta" in st.session_state:
            a, b = float(st.session_state["Ta_min_beta"]), float(st.session_state["Ta_max_beta"])
            if a > b:
                a, b = b, a
            Ta_range = (a, b)

        # --- FC range (manuale → suggeritore → default) ---
        CF_range = None
        if st.session_state.get("fc_manual_range_beta", False):
            if "FC_min_beta" in st.session_state and "FC_max_beta" in st.session_state:
                a, b = float(st.session_state["FC_min_beta"]), float(st.session_state["FC_max_beta"])
                if a > b:
                    a, b = b, a
                CF_range = (max(a, 0.01), max(b, 0.01))
        else:
            vals = st.session_state.get("fc_suggested_vals", [])
            if len(vals) == 2:
                a, b = sorted([float(vals[0]), float(vals[1])])
                CF_range = (max(a, 0.01), max(b, 0.01))
            elif len(vals) == 1:
                v = float(vals[0])
                CF_range = (max(v - 0.10, 0.01), max(v + 0.10, 0.01))
            else:
                CF_range = None  # il core userà ±0.10 su CF_value

        res = compute_raffreddamento_cautelativo(
            dt_ispezione=data_ora_ispezione,
            Ta_value=float(Ta_val),
            CF_value=float(CF_val),
            peso_kg=float(W_val),
            Ta_range=Ta_range,
            CF_range=CF_range,
            peso_stimato=bool(st.session_state.get("peso_stimato_beta", False)),
            mostra_tabella=False,
            applica_regola_48_inf=True,
            solver_kwargs={
                "Tr": float(Tr_val),
                "T0": float(T0_val),
                "round_minutes": int(st.session_state.get("henssge_round_minutes", 30)),
            },
        )

        # mappa output cautelativa
        t_min_raff_henssge = float(res.ore_min)
        t_max_raff_henssge = (
            np.nan if (not np.isfinite(res.ore_max) or res.ore_max >= INF_HOURS - 1e-9)
            else float(res.ore_max)
        )
        _tmed_raw = t_min_raff_henssge if np.isnan(t_max_raff_henssge) else 0.5 * (t_min_raff_henssge + t_max_raff_henssge)
        t_med_raff_henssge_rounded_raw = float(_tmed_raw)
        t_med_raff_henssge_rounded = round_quarter_hour(_tmed_raw)
        Qd_val_check = res.qd_min if (res.qd_min is not None) else np.nan
        raffreddamento_calcolabile = True
        
        # testi cautelativa
        st.session_state["parentetica_extra"] = res.parentetica

        # Range Ta/CF sempre disponibili (default: Ta ±1 °C, CF ±0.10)
        if "Ta_min_beta" in st.session_state and "Ta_max_beta" in st.session_state:
            ta_lo = float(st.session_state["Ta_min_beta"])
            ta_hi = float(st.session_state["Ta_max_beta"])
        else:
            ta_lo = float(Ta_val) - 1.0
            ta_hi = float(Ta_val) + 1.0
        ta_txt = f"{ta_lo:.1f} – {ta_hi:.1f} °C"

        if st.session_state.get("fc_manual_range_beta", False) and \
           "FC_min_beta" in st.session_state and "FC_max_beta" in st.session_state:
            cf_lo = float(st.session_state["FC_min_beta"])
            cf_hi = float(st.session_state["FC_max_beta"])
        else:
            vals = st.session_state.get("fc_suggested_vals", [])
            if len(vals) == 2:
                a, b = sorted([float(vals[0]), float(vals[1])])
                cf_lo, cf_hi = a, b
            elif len(vals) == 1:
                v = float(vals[0])
                cf_lo, cf_hi = v - 0.10, v + 0.10
            else:
                v = float(CF_val)
                cf_lo, cf_hi = v - 0.10, v + 0.10
        cf_lo = max(cf_lo, 0.01); cf_hi = max(cf_hi, 0.01)
        cf_txt = f"{cf_lo:.2f} – {cf_hi:.2f}"

        p_txt = f"{max(W_val-3,1):.0f}–{(W_val+3):.0f} kg" if st.session_state.get("peso_stimato_beta", False) else f"{W_val:.0f} kg"

        # header / bullets / conclusione dal modulo cautelativa o fallback
        header_blk = getattr(res, "header_html", None) or getattr(res, "header", None)
        bullets_blk = getattr(res, "bullets_html", None) or getattr(res, "bullets", None)
        conclusione_blk = getattr(res, "conclusione_html", None) or getattr(res, "conclusione", None)

        if not (header_blk and bullets_blk and conclusione_blk):
            # --- formatter ore/minuti ---
            def _fmt_ore_min(h: float) -> str:
                if not np.isfinite(h):
                    return ""
                ore = int(h)
                minuti = int(round((h - ore) * 60))
                if minuti == 60:
                    ore += 1
                    minuti = 0
                if minuti == 0:
                    return f"{ore} {'ora' if ore == 1 else 'ore'}"
                return f"{ore} {'ora' if ore == 1 else 'ore'} {minuti} minuti"

            # risultato in forma testuale
            t_lo = round_quarter_hour(t_min_raff_henssge)
            if np.isnan(t_max_raff_henssge):
                risultato_txt = f"almeno {_fmt_ore_min(t_lo)}"
            else:
                t_hi = round_quarter_hour(t_max_raff_henssge)
                risultato_txt = f"tra {_fmt_ore_min(t_lo)} e {_fmt_ore_min(t_hi)}"

            header_blk = (
                "Per quanto attiene la valutazione del raffreddamento cadaverico, "
                "sono stati stimati i parametri di seguito indicati."
            )
            bullets_blk = (
                "<ul>"
                f"<li>Range di temperature ambientali medie: <b>{ta_txt}</b></li>"
                f"<li>Range per il fattore di correzione: <b>{cf_txt}</b></li>"
                f"<li>Peso corporeo: <b>{p_txt}</b></li>"
                "</ul>"
            )
            conclusione_blk = (
                "Applicando l'equazione di Henssge, è possibile stimare che il decesso "
                f"sia avvenuto {risultato_txt} prima dei rilievi effettuati al momento "
                "dell’ispezione legale."
            )

        # elenco con sottopunti
        elenco_html = "<ul>"
        if header_blk:
            elenco_html += f"<li>{header_blk}"
            elenco_html += "<ul style='list-style-type: circle; margin-left: 20px;'>"
            elenco_html += (
                f"<li>Range di temperature ambientali medie (tenendo conto delle possibili escursioni termiche verificatesi tra decesso e ispezione legale): <b>{ta_txt}</b>.</li>"
                f"<li>Range per il fattore di correzione (considerate le possibili condizioni in cui può essersi trovato il corpo): <b>{cf_txt}</b>.</li>"
                f"<li>Peso corporeo: <b>{p_txt}</b>.</li>"
            )
            elenco_html += "</ul></li>"
        if conclusione_blk:
            elenco_html += f"<li>{conclusione_blk}</li>"
        elenco_html += "</ul>"

        dettagli.append(elenco_html)

        # --- Dettaglio raffreddamento anche in cautelativa (abilita la nota ±20% in textgen) ---
        t_min_vis = t_min_raff_henssge if raffreddamento_calcolabile else np.nan
        t_max_vis = t_max_raff_henssge if raffreddamento_calcolabile else np.nan
        par_h_caut = paragrafo_raffreddamento_dettaglio(
            t_min_visual=t_min_vis,
            t_max_visual=t_max_vis,
            t_med_round=t_med_raff_henssge_rounded,
            qd_val=Qd_val_check,
            ta_val=Ta_val,
        )
        if par_h_caut:
            dettagli.append(par_h_caut)

    else:
        # Henssge standard
        round_minutes = int(st.session_state.get("henssge_round_minutes", 30))
        (
            t_med_raff_henssge_rounded,
            t_min_raff_henssge,
            t_max_raff_henssge,
            t_med_raff_henssge_rounded_raw,
            Qd_val_check,
        ) = calcola_raffreddamento(
            Tr_val, Ta_val, T0_val, W_val, CF_val, round_minutes=round_minutes
        )
        raffreddamento_calcolabile = (
            not np.isnan(t_med_raff_henssge_rounded) and t_med_raff_henssge_rounded >= 0
        )
        st.session_state["parentetica_extra"] = ""

    # --- differenza piccola Tr-Ta ---
    temp_difference_small = (Tr_val - Ta_val) >= 0 and (Tr_val - Ta_val) < 2.0

    # --- macchie/rigidità ---
    macchie_range = opzioni_macchie.get(selettore_macchie)
    macchie_range_valido = isinstance(macchie_range, tuple)
    macchie_medi_range = macchie_medi.get(selettore_macchie) if macchie_range_valido else None

    rigidita_range = opzioni_rigidita.get(selettore_rigidita)
    rigidita_range_valido = isinstance(rigidita_range, tuple)
    rigidita_medi_range = rigidita_medi.get(selettore_rigidita) if rigidita_range_valido else None

    # --- parametri aggiuntivi ---
    parametri_aggiuntivi_da_considerare: List[Dict[str, Any]] = []
    nota_globale_range_adattato = False

    for nome_parametro, widgets in widgets_parametri_aggiuntivi.items():
        stato_selezionato = widgets["selettore"]
        if stato_selezionato == "Non valutata":
            continue
        data_rilievo_param = widgets["data_rilievo"]
        ora_rilievo_param_str = widgets["ora_rilievo"]

        # orario
        if not ora_rilievo_param_str or not str(ora_rilievo_param_str).strip():
            ora_rilievo_time = data_ora_ispezione.time()
        else:
            try:
                ora_rilievo_time = datetime.datetime.strptime(ora_rilievo_param_str, "%H:%M").time()
            except ValueError:
                avvisi.append(f"⚠️ {nome_parametro}: ora '{ora_rilievo_param_str}' non valida (usa HH:MM) → escluso.")
                continue

        if data_rilievo_param is None:
            data_rilievo_param = data_ora_ispezione.date()

        chiave_descrizione = (stato_selezionato.split(':')[0].strip()
                              if nome_parametro == "Eccitabilità elettrica peribuccale"
                              else stato_selezionato.strip())

        # match chiave robusto
        chiave_esatta = None
        for k in dati_parametri_aggiuntivi[nome_parametro]["range"].keys():
            if k.strip() == chiave_descrizione:
                chiave_esatta = k
                break

        range_valori = dati_parametri_aggiuntivi[nome_parametro]["range"].get(chiave_esatta)
        if range_valori:
            descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(
                chiave_descrizione, f"Descrizione non trovata per '{stato_selezionato}'."
            )
            data_ora_param = arrotonda_quarto_dora(datetime.datetime.combine(data_rilievo_param, ora_rilievo_time))
            diff_h = (data_ora_param - data_ora_ispezione).total_seconds() / 3600.0
            if range_valori[1] >= INF_HOURS:
                range_trasl = (range_valori[0] - diff_h, INF_HOURS)
            else:
                range_trasl = (range_valori[0] - diff_h, range_valori[1] - diff_h)
            lo, hi = round_quarter_hour(range_trasl[0]), round_quarter_hour(range_trasl[1])
            lo = max(0, lo)
            parametri_aggiuntivi_da_considerare.append(dict(
                nome=nome_parametro, stato=stato_selezionato,
                range_traslato=(lo, hi), descrizione=descrizione,
                differenza_ore=diff_h, adattato=(diff_h != 0)
            ))
            diffs = {p["differenza_ore"] for p in parametri_aggiuntivi_da_considerare if p.get("adattato")}
            nota_globale_range_adattato = len(diffs) == 1 and len(diffs) > 0
        else:
            if dati_parametri_aggiuntivi[nome_parametro]["range"].get(stato_selezionato) is None:
                descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(
                    chiave_descrizione, f"{nome_parametro} ({stato_selezionato}) senza range definito."
                )
                parametri_aggiuntivi_da_considerare.append(dict(
                    nome=nome_parametro, stato=stato_selezionato,
                    range_traslato=(np.nan, np.nan), descrizione=descrizione
                ))

    # --- range Henssge per grafico ---
    t_min_raff_visualizzato = t_min_raff_henssge if raffreddamento_calcolabile else np.nan
    t_max_raff_visualizzato = t_max_raff_henssge if raffreddamento_calcolabile else np.nan

    def _append_range_safe(rng, label):
        if isinstance(rng, tuple) and len(rng) == 2:
            lo, hi = rng
            if _is_num(lo):
                inizio.append(lo)
                fine.append(hi if _is_num(hi) and hi < INF_HOURS else np.nan)
                nomi_usati.append(label)

    # --- intersezione ---
    inizio, fine = [], []
    nomi_usati = []
    _append_range_safe(macchie_range, "Macchie ipostatiche")
    _append_range_safe(rigidita_range, "Rigidità cadaverica")

    # --- helper: arrotonda al mezz'ora ---
    def _round_half_hour(x: float) -> float:
        return float(np.round(x * 2.0) / 2.0)

    # Potente minimo (prevale come limite inferiore se attivo)
    mt_ore = None
    mt_giorni = None

    # in cautelativa usa la Ta "peggiore" (Ta_max) per coerenza con qd_min
    Ta_for_pot = Ta_val
    if st.session_state.get("stima_cautelativa_beta", False):
        Ta_for_pot = float(st.session_state.get("Ta_max_beta", Ta_val))

    if not any(np.isnan(v) for v in [Tr_val, Ta_for_pot, CF_val, W_val]) and Tr_val > Ta_for_pot + 1e-6:
        Qd_pot = (Tr_val - Ta_for_pot) / (37.2 - Ta_for_pot)
        qd_threshold_pot = 0.2 if Ta_for_pot <= 23 else 0.5
        if Qd_pot < qd_threshold_pot:
            B = -1.2815 * (CF_val * W_val) ** (-5/8) + 0.0284
            ln_term = np.log(0.16) if Ta_for_pot <= 23 else np.log(0.45)
            mt_ore_raw = ln_term / B
            mt_ore = _round_half_hour(float(mt_ore_raw))   # <-- arrotonda al mezz’ora
            mt_giorni = round(mt_ore / 24.0, 1)

    usa_potente = (
        not np.isnan(Qd_val_check)
        and (Qd_val_check < qd_threshold)
        and (mt_ore is not None)
        and (not np.isnan(mt_ore))
    )

    # extra da parametri aggiuntivi
    for p in parametri_aggiuntivi_da_considerare:
        lo, hi = p["range_traslato"]
        if _is_num(lo):
            inizio.append(lo)
            fine.append(hi if (_is_num(hi) and hi < INF_HOURS) else np.nan)
            nomi_usati.append(p["nome"])

    # Henssge/Potente nell’intersezione
    if raffreddamento_calcolabile:
        # se Potente è attivo, usa mt_ore come limite inferiore del raffreddamento
        if np.isnan(t_max_raff_henssge):  # cautelativa: limite superiore aperto
            start = mt_ore if usa_potente else t_min_raff_henssge
            inizio.append(start)
            fine.append(np.nan)
            nomi_usati.append(
                "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
                if usa_potente else
                "raffreddamento cadaverico (cautelativo: limite superiore aperto)"
            )
        else:
            if usa_potente:
                # limite inferiore da Potente, superiore da Henssge
                start = min(mt_ore, t_max_raff_henssge)  # sicurezza nel caso patologico
                inizio.append(start)
                fine.append(t_max_raff_henssge)
                nomi_usati.append("raffreddamento cadaverico (limite inferiore da Potente et al.)")
            else:
                inizio.append(t_min_raff_henssge)
                fine.append(t_max_raff_henssge)
                nomi_usati.append("raffreddamento cadaverico")

    # intersezione finale
    starts_clean = [s for s in inizio if _is_num(s)]
    if not starts_clean:
        comune_inizio, comune_fine, overlap = np.nan, np.nan, False
    else:
        comune_inizio = max(starts_clean)
        superiori_finiti = [v for v in fine if _is_num(v) and v < INF_HOURS]
        comune_fine = min(superiori_finiti) if superiori_finiti else np.nan
        # se cautelativa e nessuno chiude → lascia aperto
        if st.session_state.get("stima_cautelativa_beta", False) and np.isnan(t_max_raff_henssge) and not superiori_finiti:
            comune_fine = np.nan
        overlap = np.isnan(comune_fine) or (comune_inizio <= comune_fine)

    # --- extra per grafico ---
    extra_params_for_plot = []
    for i
