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
def _is_num(x): 
    return x is not None and not (isinstance(x, float) and np.isnan(x))

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
    skip_warnings: bool = False,   # <-- nuovo flag per silenziare avvisi base
    **kwargs,
):
    # Back-compat: accetta skip_warnings anche via **kwargs
    if "skip_warnings" in kwargs and not skip_warnings:
        skip_warnings = bool(kwargs.pop("skip_warnings"))

    avvisi: List[str] = []
    dettagli: List[str] = []
    frase_finale_html: str = ""

    # --- anti-duplicati per i paragrafi ---
    _dettagli_seen: set[str] = set()
    def _add_det(blocco: str | None):
        if isinstance(blocco, str):
            key = blocco.strip()
            if key and key not in _dettagli_seen:
                dettagli.append(key)
                _dettagli_seen.add(key)
    henssge_detail_added = False

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

    # --- validazioni base (configurabili) ---
    if not skip_warnings:
        if input_w is None or input_w <= 0:
            st.error("⚠️ Peso non valido. Inserire un valore > 0 kg.")
            return
        if fattore_correzione is None or fattore_correzione <= 0:
            st.error("⚠️ Fattore di correzione non valido. Inserire un valore > 0.")
            return
        if any(v is None for v in [input_rt, input_ta, input_tm]):
            st.error("⚠️ Temperature mancanti.")
            return

    # --- normalizza locali; modalità silenziosa disattiva Henssge se mancano input ---
    Tr_val, Ta_val, T0_val, W_val, CF_val = input_rt, input_ta, input_tm, input_w, fattore_correzione

    # placeholder valori calcolati
    t_min_raff_henssge = np.nan
    t_max_raff_henssge = np.nan
    t_med_raff_henssge_rounded_raw = np.nan
    t_med_raff_henssge_rounded = np.nan
    Qd_val_check = np.nan
    raffreddamento_calcolabile = True

    if skip_warnings and (
        W_val is None or W_val <= 0 or any(v is None for v in [Tr_val, Ta_val, T0_val])
    ):
        Tr_val = Ta_val = T0_val = W_val = CF_val = np.nan
        raffreddamento_calcolabile = False

    # soglia Qd
    qd_threshold = 0.2 if (_is_num(Ta_val) and Ta_val <= 23) else 0.5

    # =========================
    # Henssge standard / Cautelativa
    # =========================
    if st.session_state.get("stima_cautelativa_beta", False):
        if raffreddamento_calcolabile:
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
            elenco_html += "</ul>"
            _add_det(elenco_html)

            t_min_vis = t_min_raff_henssge
            t_max_vis = t_max_raff_henssge
            par_h_caut = paragrafo_raffreddamento_dettaglio(
                t_min_visual=t_min_vis,
                t_max_visual=t_max_vis,
                t_med_round=t_med_raff_henssge_rounded,
                qd_val=Qd_val_check,
                ta_val=Ta_val,
            )
            if par_h_caut:
                _add_det(par_h_caut)
                henssge_detail_added = True
        else:
            # Henssge escluso
            st.session_state["parentetica_extra"] = ""
    else:
        if raffreddamento_calcolabile:
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
        else:
            st.session_state["parentetica_extra"] = ""

    # --- differenza piccola Tr-Ta ---
    temp_difference_small = (_is_num(Tr_val) and _is_num(Ta_val) and (Tr_val - Ta_val) >= 0 and (Tr_val - Ta_val) < 2.0)

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

    def _round_half_hour(x: float) -> float:
        return float(np.round(x * 2.0) / 2.0)

    # Potente minimo
    mt_ore = None
    mt_giorni = None

    # Ta da usare per Potente
    Ta_for_pot = (float(st.session_state.get("Ta_max_beta", Ta_val))
                  if st.session_state.get("stima_cautelativa_beta", False) else float(Ta_val)) if _is_num(Ta_val) else np.nan

    if (_is_num(Qd_val_check) and Qd_val_check < qd_threshold
        and all(_is_num(v) for v in [Tr_val, Ta_for_pot, CF_val, W_val])
        and Tr_val > Ta_for_pot + 1e-6):
        B = -1.2815 * (CF_val * W_val) ** (-5/8) + 0.0284
        ln_term = np.log(0.16) if _is_num(Ta_for_pot) and Ta_for_pot <= 23 else np.log(0.45)
        mt_ore_raw = ln_term / B
        mt_ore = _round_half_hour(float(mt_ore_raw))
        mt_giorni = round(mt_ore / 24.0, 1)

    usa_potente = (_is_num(Qd_val_check) and Qd_val_check < qd_threshold and (mt_ore is not None) and (not np.isnan(mt_ore)))

    # extra da parametri aggiuntivi
    for p in parametri_aggiuntivi_da_considerare:
        lo, hi = p["range_traslato"]
        if _is_num(lo):
            inizio.append(lo)
            fine.append(hi if (_is_num(hi) and hi < INF_HOURS) else np.nan)
            nomi_usati.append(p["nome"])

    # Henssge/Potente nell’intersezione
    if raffreddamento_calcolabile:
        if usa_potente:
            if mt_ore is not None and not np.isnan(mt_ore):
                inizio.append(mt_ore)
                fine.append(np.nan)
                nomi_usati.append("raffreddamento cadaverico (intervallo minimo secondo Potente et al.)")
        else:
            inizio.append(t_min_raff_henssge)
            fine.append(t_max_raff_henssge if _is_num(t_max_raff_henssge) else np.nan)
            nomi_usati.append(
                "raffreddamento cadaverico (cautelativo: limite superiore aperto)"
                if np.isnan(t_max_raff_henssge) else
                "raffreddamento cadaverico"
            )

    # intersezione finale
    starts_clean = [s for s in inizio if _is_num(s)]
    if not starts_clean:
        comune_inizio, comune_fine, overlap = np.nan, np.nan, False
    else:
        comune_inizio = max(starts_clean)
        superiori_finiti = [v for v in fine if _is_num(v) and v < INF_HOURS]
        comune_fine = min(superiori_finiti) if superiori_finiti else np.nan
        if st.session_state.get("stima_cautelativa_beta", False) and np.isnan(t_max_raff_henssge) and not superiori_finiti:
            comune_fine = np.nan
        if usa_potente and not superiori_finiti:
            comune_fine = np.nan
        overlap = np.isnan(comune_fine) or (comune_inizio <= comune_fine)

    # --- extra per grafico ---
    extra_params_for_plot = []
    for idx, p in enumerate(parametri_aggiuntivi_da_considerare):
        lo, hi = p["range_traslato"]
        if _is_num(lo):
            label = nomi_brevi.get(p["nome"], p["nome"])
            if p.get("adattato"):
                label += "*"
            extra_params_for_plot.append({
                "label": label,
                "start": float(lo),
                "end": float(hi) if _is_num(hi) else np.inf,
                "order": idx,
                "adattato": bool(p.get("adattato", False)),
            })

    # --- grafico ---
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if raffreddamento_calcolabile: num_params_grafico += 1
    num_params_grafico += len(extra_params_for_plot)

    if num_params_grafico > 0:
        try:
            plot_data = compute_plot_data(
                macchie_range=macchie_range if macchie_range_valido else (np.nan, np.nan),
                macchie_medi_range=macchie_medi_range if macchie_range_valido else None,
                rigidita_range=rigidita_range if rigidita_range_valido else (np.nan, np.nan),
                rigidita_medi_range=rigidita_medi_range if rigidita_range_valido else None,
                raffreddamento_calcolabile=raffreddamento_calcolabile,
                t_min_raff_henssge=t_min_raff_henssge if raffreddamento_calcolabile else np.nan,
                t_max_raff_henssge=t_max_raff_henssge if raffreddamento_calcolabile else np.nan,
                t_med_raff_henssge_rounded_raw=t_med_raff_henssge_rounded_raw if raffreddamento_calcolabile else np.nan,
                Qd_val_check=Qd_val_check if raffreddamento_calcolabile else np.nan,
                mt_ore=mt_ore,
                INF_HOURS=INF_HOURS,
                qd_threshold=qd_threshold,
                extra_params=extra_params_for_plot,
            )
        except TypeError:
            plot_data = compute_plot_data(
                macchie_range=macchie_range if macchie_range_valido else (np.nan, np.nan),
                macchie_medi_range=macchie_medi_range if macchie_range_valido else None,
                rigidita_range=rigidita_range if rigidita_range_valido else (np.nan, np.nan),
                rigidita_medi_range=rigidita_medi_range if rigidita_range_valido else None,
                raffreddamento_calcolabile=raffreddamento_calcolabile,
                t_min_raff_henssge=t_min_raff_henssge if raffreddamento_calcolabile else np.nan,
                t_max_raff_henssge=t_max_raff_henssge if raffreddamento_calcolabile else np.nan,
                t_med_raff_henssge_rounded_raw=t_med_raff_henssge_rounded_raw if raffreddamento_calcolabile else np.nan,
                Qd_val_check=Qd_val_check if raffreddamento_calcolabile else np.nan,
                mt_ore=mt_ore,
                INF_HOURS=INF_HOURS,
                qd_threshold=qd_threshold,
            )

        if isinstance(plot_data, dict):
            plot_data["extra_params"] = extra_params_for_plot
            tail = plot_data.get("tail_end", 72.0)
        else:
            tail = 72.0

        for e in extra_params_for_plot:
            if (not np.isfinite(e["end"])) or (e["end"] > tail):
                e["end"] = tail

        try:
            fig_or_none = render_ranges_plot(plot_data, extra_params=extra_params_for_plot)
        except TypeError:
            fig_or_none = render_ranges_plot(plot_data)

        import matplotlib.figure as _mplfig
        if isinstance(fig_or_none, _mplfig.Figure):
            fig = fig_or_none
            if overlap and (np.isnan(comune_fine) or comune_fine > 0):
                ax = fig.axes[0]
                if comune_inizio < tail:
                    ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
                if not np.isnan(comune_fine) and comune_fine > 0:
                    ax.axvline(min(tail, comune_fine), color='red', linestyle='--')
            st.pyplot(fig)

        # frase sotto al grafico
        if overlap:
            if usa_orario_custom:
                frase_semplice = build_simple_sentence(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    isp_dt=data_ora_ispezione,
                    inf_hours=INF_HOURS,
                )
                if frase_semplice:
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    st.markdown(_wrap_final(frase_semplice), unsafe_allow_html=True)
            else:
                frase_semplice_no_dt = build_simple_sentence_no_dt(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    inf_hours=INF_HOURS,
                )
                if frase_semplice_no_dt:
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    st.markdown(_wrap_final(frase_semplice_no_dt), unsafe_allow_html=True)

    # --- avvisi ---
    if nota_globale_range_adattato:
        avvisi.append("Alcuni parametri sono stati rilevati in orari diversi; i range sono stati traslati per renderli confrontabili.")
    if usa_orario_custom and minuti_isp not in [0, 15, 30, 45]:
        avvisi.append("NB: l’orario dei rilievi è stato arrotondato al quarto d’ora più vicino.")

    if all(_is_num(v) for v in [Tr_val, Ta_val, T0_val, W_val, CF_val]):
        if Ta_val > 25:
            avvisi.append("Per temperature ambientali &gt; 25 °C, variazioni del fattore di correzione possono influenzare notevolmente i risultati.")
        if Ta_val < 18:
            avvisi.append("Per temperature ambientali &lt; 18 °C, la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati.")
        if temp_difference_small:
            avvisi.append("Essendo minima la differenza tra temperatura rettale e ambientale, è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione.")
        if abs(Tr_val - T0_val) <= 1.0:
            avvisi.append("Considerato che la T rettale è molto simile alla T ante-mortem stimata, è verosimile che il raffreddamento corporeo non fosse ancora iniziato e/o si trovasse nella fase di plateau. In tale fase, la precisione del metodo è ridotta.")
        if not raffreddamento_calcolabile:
            avvisi.append("Non è stato possibile applicare il metodo di Henssge (temperature incoerenti o fuori range).")
        avvisi.extend(avvisi_raffreddamento_henssge(t_med_round=t_med_raff_henssge_rounded, qd_val=Qd_val_check))
        if not st.session_state.get("stima_cautelativa_beta", False):
            cf_descr = build_cf_description(
                cf_value=st.session_state.get("fattore_correzione", 1.0),
                riassunto=st.session_state.get("fc_riassunto_contatori"),
                fallback_text=st.session_state.get("fattori_condizioni_testo"),
            )
            _add_det(paragrafo_raffreddamento_input(
                isp_dt=data_ora_ispezione if usa_orario_custom else None,
                ta_val=Ta_val, tr_val=Tr_val, w_val=W_val, t0_val=T0_val, cf_descr=cf_descr
            ))

        t_min_vis = t_min_raff_visualizzato if np.isfinite(t_min_raff_visualizzato) else np.nan
        t_max_vis = t_max_raff_visualizzato if np.isfinite(t_max_raff_visualizzato) else np.nan
        par_h = paragrafo_raffreddamento_dettaglio(
            t_min_visual=t_min_vis,
            t_max_visual=t_max_vis,
            t_med_round=t_med_raff_henssge_rounded,
            qd_val=Qd_val_check,
            ta_val=Ta_val,
        )
        if par_h:
            _add_det(par_h)

        par_p = paragrafo_potente(
            mt_ore=mt_ore, mt_giorni=mt_giorni, qd_val=Qd_val_check, ta_val=Ta_val, qd_threshold=qd_threshold,
        )
        _add_det(par_p)

        for blocco in paragrafi_descrizioni_base(
            testo_macchie=testi_macchie[selettore_macchie],
            testo_rigidita=rigidita_descrizioni[selettore_rigidita],
        ):
            _add_det(blocco)
        for blocco in paragrafi_parametri_aggiuntivi(parametri=parametri_aggiuntivi_da_considerare):
            _add_det(blocco)
        _add_det(paragrafo_putrefattive(alterazioni_putrefattive))

        # --- frase finale complessiva ---
        frase_finale_html: str = ""
        if usa_orario_custom:
            _tmp = build_final_sentence(
                comune_inizio, comune_fine, data_ora_ispezione,
                qd_val=Qd_val_check, mt_ore=mt_ore, ta_val=Ta_val, inf_hours=INF_HOURS
            )
        else:
            _tmp = build_final_sentence_simple(
                comune_inizio=comune_inizio,
                comune_fine=comune_fine,
                inf_hours=INF_HOURS,
            )
        if isinstance(_tmp, str):
            frase_finale_html = _tmp

    # ⛔️ Niente parentetica extra accodata alla frase finale
    st.session_state["parentetica_extra"] = ""

    # toggle avvisi
    if avvisi:
        mostra = st.toggle(f"⚠️ Mostra avvisi ({len(avvisi)})", key="mostra_avvisi")
        if mostra:
            for m in avvisi:
                _warn_box(m)

    # ---     # --- discordanze ---
    def _finite(x):
        return isinstance(x, (int, float)) and np.isfinite(x)

    labeled_pairs = [(s, e, l) for s, e, l in zip(inizio, fine, nomi_usati)
                     if _finite(s) and (_finite(e) or np.isnan(e))]

    def _family(label: str) -> str:
        return label.lower().split("(")[0].strip()

    fam_best = {}
    for s, e, l in labeled_pairs:
        f = _family(l)
        cur = fam_best.get(f)
        if cur is None:
            fam_best[f] = (s, e, l)
        else:
            s0, e0, _ = cur
            if np.isnan(e0) and _finite(e):
                fam_best[f] = (s, e, l)
            elif _finite(e0) and _finite(e) and (e - s) < (e0 - s0):
                fam_best[f] = (s, e, l)

    compact = list(fam_best.values())
    if len(compact) >= 2:
        v_inizio = [s for s, _, _ in compact]
        v_fine   = [(e if _finite(e) else INF_HOURS) for _, e, _ in compact]
        discordanti = ((not overlap) or ranges_in_disaccordo_completa(v_inizio, v_fine))
    else:
        discordanti = False

    if discordanti:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>", unsafe_allow_html=True)

    # expander dettagli
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    with st.expander("Descrizioni dettagliate"):
        for blocco in dettagli:
            st.markdown(_wrap_final(blocco), unsafe_allow_html=True)

        if discordanti:
            st.markdown(
                _wrap_final("<ul><li><b>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</b></li></ul>"),
                unsafe_allow_html=True
            )
        elif overlap and frase_finale_html:
            st.markdown(
                _wrap_final(f"<ul><li>{frase_finale_html}</li></ul>"),
                unsafe_allow_html=True
            )

        if overlap and len(nomi_usati) > 0:
            nomi_finali = []
            for nome in nomi_usati:
                if ("raffreddamento cadaverico" in nome.lower()
                    and "potente" not in nome.lower()
                    and mt_ore is not None and not np.isnan(mt_ore)
                    and abs(comune_inizio - mt_ore) < 0.25):
                    continue
                nomi_finali.append(nome)
            small_html = frase_riepilogo_parametri_usati(nomi_finali)
            if small_html:
                st.markdown(_wrap_final(small_html), unsafe_allow_html=True)

        frase_qd_html = frase_qd(Qd_val_check, Ta_val)
        if frase_qd_html:
            st.markdown(_wrap_final(frase_qd_html), unsafe_allow_html=True)
        # --- Testi base ipostasi/rigidità (sempre nello stesso expander) ---
        try:
            no_macchie = str(selettore_macchie).strip() in {"Non valutata", "Non valutate", "/"}
            no_rigidita = str(selettore_rigidita).strip() in {"Non valutata", "Non valutate", "/"}
            if not no_macchie or not no_rigidita:
                from app.textgen import paragrafi_descrizioni_base
                st.markdown(
                    _wrap_final(
                        paragrafi_descrizioni_base(
                            selettore_macchie=selettore_macchie,
                            selettore_rigidita=selettore_rigidita
                        )
                    ),
                    unsafe_allow_html=True
                )
        except Exception:
            pass
