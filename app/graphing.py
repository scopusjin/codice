# app/graphing.py
from __future__ import annotations
import datetime
import textwrap
from typing import Dict, List, Any
from numbers import Real
from app.theme import warn_box
from app.theme import frase_breve_box
import numpy as np
import streamlit as st

from app import i18n
from app.factor_calc import build_cf_description
from app.henssge import ranges_in_disaccordo_completa
from app.parameters import INF_HOURS, nomi_brevi
from app.graphing_tanatology import (
    FAMILY_LIVOR,
    FAMILY_RIGOR,
    FAMILY_COOLING,
    special_family_id,
    resolve_base_tanatology_ranges,
    resolve_special_tanatology_value,
)
from app.graphing_cooling import compute_cooling_state
from app.utils_time import arrotonda_quarto_dora, round_quarter_hour
from app.plotting import compute_plot_data, render_ranges_plot
from app.textgen import (
    build_final_sentence, paragrafo_raffreddamento_dettaglio, paragrafo_potente,
    paragrafo_raffreddamento_input, paragrafi_descrizioni_base,
    paragrafi_parametri_aggiuntivi, paragrafo_putrefattive,
    frase_riepilogo_parametri_usati, avvisi_raffreddamento_henssge,
    frase_qd, build_simple_sentence, build_final_sentence_simple, build_simple_sentence_no_dt,
)


# --------- helpers ----------
def _is_num(x):
    return x is not None and not (isinstance(x, float) and np.isnan(x))

def _wrap_final(s: str | None) -> str | None:
    return (
        f'<div class="final-text" style="font-family:Arial,sans-serif;font-size:10pt;line-height:14pt;mso-line-height-rule:at-least;">{s}</div>'
        if s else s
    )

def render_frase_breve(html: str, key: str = "fb_top"):
    with frase_breve_box(key):
        st.markdown(f'<div class="fb-compact">{html}</div>', unsafe_allow_html=True)

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

    # --- data/ora ispezione ---
    if usa_orario_custom:
        if not input_data_rilievo or not input_ora_rilievo:
            st.markdown(i18n.ui_text("graph.missing_inspection_datetime_html"), unsafe_allow_html=True)
            return
        try:
            ora_isp_obj = datetime.datetime.strptime(input_ora_rilievo, "%H:%M")
        except ValueError:
            st.markdown(i18n.ui_text("graph.invalid_inspection_time_html"), unsafe_allow_html=True)
            return
        data_ora_ispezione = arrotonda_quarto_dora(datetime.datetime.combine(input_data_rilievo, ora_isp_obj.time()))
    else:
        data_ora_ispezione = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))

    # --- validazioni base (configurabili) ---
    if not skip_warnings:
        if input_w is None or input_w <= 0:
            st.error(i18n.ui_text("graph.invalid_weight"))
            return
        if fattore_correzione is None or fattore_correzione <= 0:
            st.error(i18n.ui_text("graph.invalid_factor"))
            return
        if any(v is None for v in [input_rt, input_ta, input_tm]):
            st.error(i18n.ui_text("graph.missing_temperatures"))
            return

    cooling = compute_cooling_state(
        input_rt=input_rt,
        input_ta=input_ta,
        input_tm=input_tm,
        input_w=input_w,
        fattore_correzione=fattore_correzione,
        data_ora_ispezione=data_ora_ispezione,
        skip_warnings=skip_warnings,
    )
    Tr_val = cooling.Tr_val
    Ta_val = cooling.Ta_val
    T0_val = cooling.T0_val
    W_val = cooling.W_val
    CF_val = cooling.CF_val
    t_min_raff_henssge = cooling.t_min_raff_henssge
    t_max_raff_henssge = cooling.t_max_raff_henssge
    t_med_raff_henssge_rounded_raw = cooling.t_med_raff_henssge_rounded_raw
    t_med_raff_henssge_rounded = cooling.t_med_raff_henssge_rounded
    Qd_val_check = cooling.Qd_val_check
    Qd_min = cooling.Qd_min
    Qd_max = cooling.Qd_max
    qd_range_status = cooling.qd_range_status
    potente_min_ore = cooling.potente_min_ore
    swisswuff_min_ore = cooling.swisswuff_min_ore
    swisswuff_max_ore = cooling.swisswuff_max_ore
    raffreddamento_calcolabile = cooling.raffreddamento_calcolabile
    Ta_for_pot = cooling.Ta_for_pot
    qd_threshold = cooling.qd_threshold
    gate_fail = cooling.gate_fail
    condizioni_variabili = bool(st.session_state.get("stima_cautelativa_beta", False))
    for blocco in cooling.detail_blocks:
        _add_det(blocco)

    # --- differenza piccola Tr-Ta ---
    temperatures_equal = (
        _is_num(Tr_val) and _is_num(Ta_val) and float(Tr_val) == float(Ta_val)
    )
    temperature_below_ambient = (
        _is_num(Tr_val) and _is_num(Ta_val) and float(Tr_val) < float(Ta_val)
    )
    temp_difference_small = (_is_num(Tr_val) and _is_num(Ta_val) and (Tr_val - Ta_val) >= 0 and (Tr_val - Ta_val) < 2.0)

    # --- macchie/rigidità ---
    base_tanatology = resolve_base_tanatology_ranges(selettore_macchie, selettore_rigidita)
    macchie_range = base_tanatology.livor_range
    macchie_range_valido = isinstance(macchie_range, tuple)
    macchie_medi_range = base_tanatology.livor_typical_range if macchie_range_valido else None

    rigidita_range = base_tanatology.rigor_range
    rigidita_range_valido = isinstance(rigidita_range, tuple)
    rigidita_medi_range = base_tanatology.rigor_typical_range if rigidita_range_valido else None

    # --- parametri aggiuntivi ---
    parametri_aggiuntivi_da_considerare: List[Dict[str, Any]] = []
    nota_globale_range_adattato = False

    for nome_parametro, widgets in widgets_parametri_aggiuntivi.items():
        stato_selezionato = widgets["selettore"]
        parametro_risolto = resolve_special_tanatology_value(nome_parametro, stato_selezionato)
        if parametro_risolto.is_not_assessed:
            continue
        parametro_label = (
            i18n.special_parameter_label(parametro_risolto.parameter_id)
            if parametro_risolto.parameter_id is not None
            else nome_parametro
        )
        data_rilievo_param = widgets["data_rilievo"]
        ora_rilievo_param_str = widgets["ora_rilievo"]

        # orario
        if not ora_rilievo_param_str or not str(ora_rilievo_param_str).strip():
            ora_rilievo_time = data_ora_ispezione.time()
        else:
            try:
                ora_rilievo_time = datetime.datetime.strptime(ora_rilievo_param_str, "%H:%M").time()
            except ValueError:
                avvisi.append(i18n.ui_text(
                    "graph.invalid_special_time",
                    parameter=parametro_label,
                    time=ora_rilievo_param_str,
                ))
                continue

        if data_rilievo_param is None:
            data_rilievo_param = data_ora_ispezione.date()

        range_valori = parametro_risolto.range_value
        if range_valori:
            descrizione = (
                parametro_risolto.description
                if parametro_risolto.description is not None
                else i18n.ui_text("graph.missing_special_description", state=stato_selezionato)
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
                nome=nome_parametro, label=parametro_label,
                parameter_id=parametro_risolto.parameter_id,
                stato=stato_selezionato,
                range_traslato=(lo, hi), descrizione=descrizione,
                differenza_ore=diff_h, adattato=(diff_h != 0)
            ))
            diffs = {p["differenza_ore"] for p in parametri_aggiuntivi_da_considerare if p.get("adattato")}
            nota_globale_range_adattato = len(diffs) == 1
        else:
            descrizione = (
                parametro_risolto.description
                if parametro_risolto.description is not None
                else i18n.ui_text(
                    "graph.special_without_range",
                    parameter=parametro_label,
                    state=stato_selezionato,
                )
            )
            parametri_aggiuntivi_da_considerare.append(dict(
                nome=nome_parametro, label=parametro_label,
                parameter_id=parametro_risolto.parameter_id,
                stato=stato_selezionato,
                range_traslato=(np.nan, np.nan), descrizione=descrizione
            ))

    # --- range Henssge per grafico ---
    t_min_raff_visualizzato = t_min_raff_henssge if raffreddamento_calcolabile else np.nan
    t_max_raff_visualizzato = t_max_raff_henssge if raffreddamento_calcolabile else np.nan

    def _append_range_safe(rng, label, family_id):
        if isinstance(rng, tuple) and len(rng) == 2:
            lo, hi = rng
            if _is_num(lo):
                inizio.append(lo)
                fine.append(hi if _is_num(hi) and hi < INF_HOURS else np.nan)
                nomi_usati.append(label)
                famiglie_usate.append(family_id)

    # --- intersezione ---
    inizio, fine = [], []
    nomi_usati = []
    famiglie_usate = []
    _append_range_safe(
        macchie_range,
        i18n.ui_text("graph.parameter_livor"),
        FAMILY_LIVOR,
    )
    _append_range_safe(
        rigidita_range,
        i18n.ui_text("graph.parameter_rigor"),
        FAMILY_RIGOR,
    )

    def _round_half_hour(x: float) -> float:
        return float(np.round(x * 2.0) / 2.0)

    # Potente minimo
    mt_ore = None
    mt_giorni = None

    # Nelle condizioni variabili usa il minimo calcolato sulle sole combinazioni
    # per cui Potente è applicabile; negli altri casi conserva la logica storica.
    if condizioni_variabili and raffreddamento_calcolabile and _is_num(potente_min_ore):
        mt_ore = float(potente_min_ore)
        mt_giorni = round(mt_ore / 24.0, 1)
    elif all(_is_num(v) for v in [Tr_val, Ta_val, Ta_for_pot, CF_val, W_val]) and (
        (Tr_val - Ta_val) >= (0.1 - 1e-9) or temperatures_equal
    ):
        B = -1.2815 * (CF_val * W_val) ** (-5/8) + 0.0284
        ln_term = np.log(0.16) if (_is_num(Ta_for_pot) and Ta_for_pot <= 23) else np.log(0.45)
        mt_ore_raw = ln_term / B
        mt_ore = _round_half_hour(float(mt_ore_raw))
        mt_giorni = round(mt_ore / 24.0, 1)

    if condizioni_variabili and raffreddamento_calcolabile:
        usa_potente = _is_num(potente_min_ore)
    else:
        # Logica storica della modalità standard e dei casi di bordo.
        qd_ok = (_is_num(Qd_val_check) and Qd_val_check <= qd_threshold) or (not _is_num(Qd_val_check))
        usa_potente = (mt_ore is not None) and (not np.isnan(mt_ore)) and qd_ok

    # Nel grafico il raffreddamento occupa sempre una sola riga.
    # Se Potente scatta, il range combinato viene rappresentato come intervallo aperto.
    raff_for_plot = raffreddamento_calcolabile and not usa_potente

    # extra da parametri aggiuntivi
    for p in parametri_aggiuntivi_da_considerare:
        lo, hi = p["range_traslato"]
        if _is_num(lo):
            inizio.append(lo)
            fine.append(hi if (_is_num(hi) and hi < INF_HOURS) else np.nan)
            nomi_usati.append(p["label"])
            famiglie_usate.append(special_family_id(p.get("parameter_id"), p["nome"]))

    # Raffreddamento nell'intersezione: in condizioni variabili Henssge e Potente
    # sono alternative della stessa famiglia, quindi se Potente scatta si usa la loro unione.
    if condizioni_variabili and raffreddamento_calcolabile:
        raff_start = float(t_min_raff_henssge)
        raff_end = t_max_raff_henssge if _is_num(t_max_raff_henssge) else np.nan
        raff_label = (
            i18n.ui_text("graph.parameter_cooling_prudent_open")
            if np.isnan(raff_end) else
            i18n.ui_text("graph.parameter_cooling")
        )
        if usa_potente and _is_num(mt_ore):
            raff_start = min(raff_start, float(mt_ore))
            raff_end = np.nan
            raff_label = i18n.ui_text("graph.parameter_cooling_prudent_open")
        inizio.append(raff_start)
        fine.append(raff_end)
        nomi_usati.append(raff_label)
        famiglie_usate.append(FAMILY_COOLING)
    elif usa_potente and (raffreddamento_calcolabile or temperatures_equal):
        if mt_ore is not None and not np.isnan(mt_ore):
            inizio.append(mt_ore)
            fine.append(np.nan)
            nomi_usati.append(i18n.ui_text("graph.parameter_cooling_potente"))
            famiglie_usate.append(FAMILY_COOLING)
    elif raffreddamento_calcolabile:
        inizio.append(t_min_raff_henssge)
        fine.append(t_max_raff_henssge if _is_num(t_max_raff_henssge) else np.nan)
        nomi_usati.append(
            i18n.ui_text("graph.parameter_cooling_prudent_open")
            if np.isnan(t_max_raff_henssge) else
            i18n.ui_text("graph.parameter_cooling")
        )
        famiglie_usate.append(FAMILY_COOLING)

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
            label = (
                i18n.special_graph_label(p["parameter_id"])
                if p.get("parameter_id") is not None
                else nomi_brevi.get(p["nome"], p["nome"])
            )
            if p.get("adattato"):
                label += "*"
            extra_params_for_plot.append({
                "label": label,
                "start": float(lo),
                "end": float(hi) if _is_num(hi) else np.inf,
                "order": idx,
                "adattato": bool(p.get("adattato", False)),
            })

    # Se Potente scatta, mostra una sola barra "Raffreddamento" che rappresenta
    # l'unione già usata per il risultato complessivo.
    if usa_potente and _is_num(mt_ore):
        raff_plot_start = float(mt_ore)
        if condizioni_variabili and raffreddamento_calcolabile and _is_num(t_min_raff_henssge):
            raff_plot_start = min(float(t_min_raff_henssge), float(mt_ore))
        extra_params_for_plot.insert(0, {
            "label": i18n.ui_text("plot.cooling"),
            "start": raff_plot_start,
            "end": np.inf,
            "order": -1,
            "adattato": False,
            "is_potente": True,
        })

    # --- grafico ---
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if raff_for_plot: num_params_grafico += 1
    num_params_grafico += len(extra_params_for_plot)
    
    if num_params_grafico == 0:
        warn_box(i18n.ui_text("graph.no_useful_data"))

    if num_params_grafico > 0:
        plot_data = compute_plot_data(
            macchie_range=macchie_range if macchie_range_valido else (np.nan, np.nan),
            macchie_medi_range=macchie_medi_range if macchie_range_valido else None,
            rigidita_range=rigidita_range if rigidita_range_valido else (np.nan, np.nan),
            rigidita_medi_range=rigidita_medi_range if rigidita_range_valido else None,
            raffreddamento_calcolabile=raff_for_plot,   # <-- usa raff_for_plot
            t_min_raff_henssge=t_min_raff_henssge if raff_for_plot else np.nan,
            t_max_raff_henssge=t_max_raff_henssge if raff_for_plot else np.nan,
            t_med_raff_henssge_rounded_raw=t_med_raff_henssge_rounded_raw if raff_for_plot else np.nan,
            Qd_val_check=Qd_val_check if raff_for_plot else np.nan,
            mt_ore=mt_ore,
            INF_HOURS=INF_HOURS,
            qd_threshold=qd_threshold,
            extra_params=extra_params_for_plot,
        )

        if isinstance(plot_data, dict):
            plot_data["extra_params"] = extra_params_for_plot
            tail = plot_data.get("tail_end", 72.0)
        else:
            tail = 72.0

        for e in extra_params_for_plot:
            if (not np.isfinite(e["end"])) or (e["end"] > tail):
                e["end"] = tail

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

        # frase breve subito dopo il grafico
        st.session_state["frase_breve"] = None
        if overlap:
            if usa_orario_custom:
                frase_semplice = build_simple_sentence(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    isp_dt=data_ora_ispezione,
                    inf_hours=INF_HOURS,
                )
                if frase_semplice:
                    st.session_state["frase_breve"] = frase_semplice
                    render_frase_breve(frase_semplice, key="fb_with_dt")
            else:
                frase_semplice_no_dt = build_simple_sentence_no_dt(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    inf_hours=INF_HOURS,
                )
                if frase_semplice_no_dt:
                    st.session_state["frase_breve"] = frase_semplice_no_dt
                    render_frase_breve(frase_semplice_no_dt, key="fb_no_dt")

    # --- avvisi ---
    if nota_globale_range_adattato:
        avvisi.append(i18n.ui_text("graph.shifted_ranges_note"))

    missing_or_invalid = (
        not _is_num(Tr_val) or not _is_num(Ta_val) or not _is_num(T0_val) or
        not _is_num(W_val) or not _is_num(CF_val) or
        (_is_num(W_val) and W_val <= 0) or (_is_num(CF_val) and CF_val <= 0)
    )
    if not raffreddamento_calcolabile:
        if missing_or_invalid:
            avvisi.append(i18n.ui_text("graph.henssge_missing_invalid"))
        elif temperatures_equal:
            avvisi.append(i18n.ui_text(
                "graph.henssge_equal_temperature_warning",
                temperature=f"{float(Tr_val):.1f}",
            ))
        elif temperature_below_ambient:
            avvisi.append(i18n.ui_text("graph.henssge_below_ambient_warning"))
        else:
            msg = i18n.ui_text("graph.henssge_incoherent")
            
            avvisi.append(msg)

    if all(_is_num(v) for v in [Tr_val, Ta_val, T0_val, W_val, CF_val]):
        if Ta_val > 25:
            avvisi.append(i18n.ui_text("graph.high_ambient_factor_warning"))
        if Ta_val < 18:
            avvisi.append(i18n.ui_text("graph.low_ambient_factor_warning"))
        if temp_difference_small and not temperatures_equal:
            avvisi.append(i18n.ui_text("graph.thermal_equilibrium_warning"))
        if abs(Tr_val - T0_val) <= 1.0:
            avvisi.append(i18n.ui_text("graph.plateau_warning"))

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

        if temperatures_equal:
            _add_det(i18n.ui_text(
                "graph.henssge_equal_temperature_detail",
                temperature=f"{float(Tr_val):.1f}",
            ))
        if temperature_below_ambient:
            _add_det(i18n.ui_text("graph.henssge_below_ambient_detail"))

        t_min_vis = t_min_raff_visualizzato if np.isfinite(t_min_raff_visualizzato) else np.nan
        t_max_vis = t_max_raff_visualizzato if np.isfinite(t_max_raff_visualizzato) else np.nan
        henssge_non_applicabile_singolo = (
            not condizioni_variabili
            and _is_num(Qd_val_check)
            and float(Qd_val_check) <= qd_threshold
        )
        if henssge_non_applicabile_singolo:
            _add_det("<ul><li>Nel caso in esame, l’equazione di Henssge non è applicabile.</li></ul>")
        else:
            par_h = paragrafo_raffreddamento_dettaglio(
                t_min_visual=t_min_vis,
                t_max_visual=t_max_vis,
                t_med_round=t_med_raff_henssge_rounded,
                qd_val=Qd_val_check,
                ta_val=Ta_val,
                qd_range_status=qd_range_status,
            )
            if par_h:
                _add_det(par_h)

        qd_for_potente = 0.0 if temperatures_equal else Qd_val_check
        par_p = paragrafo_potente(
            mt_ore=mt_ore, mt_giorni=mt_giorni, qd_val=qd_for_potente, ta_val=Ta_val, qd_threshold=qd_threshold,
        )
        _add_det(par_p)

        for blocco in paragrafi_descrizioni_base(
            testo_macchie=i18n.livor_description(base_tanatology.livor_id),
            testo_rigidita=i18n.rigor_description(base_tanatology.rigor_id),
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

    # Fallback: genera il riepilogo anche quando la stima non usa il raffreddamento.
    if overlap and not frase_finale_html:
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

    # --- discordanze ---
    def _finite(x):
        return isinstance(x, Real) and np.isfinite(x)

    labeled_pairs = [
        (s, e, family_id, label)
        for s, e, family_id, label in zip(inizio, fine, famiglie_usate, nomi_usati)
        if _finite(s) and (_finite(e) or np.isnan(e))
    ]

    fam_best = {}
    for s, e, family_id, label in labeled_pairs:
        cur = fam_best.get(family_id)
        if cur is None:
            fam_best[family_id] = (s, e, label)
        else:
            s0, e0, _ = cur
            if np.isnan(e0) and _finite(e):
                fam_best[family_id] = (s, e, label)
            elif _finite(e0) and _finite(e) and (e - s) < (e0 - s0):
                fam_best[family_id] = (s, e, label)

    compact = list(fam_best.values())
    if len(compact) >= 2:
        v_inizio = [s for s, _, _ in compact]
        v_fine   = [(e if _finite(e) else INF_HOURS) for _, e, _ in compact]
        discordanti = ((not overlap) or ranges_in_disaccordo_completa(v_inizio, v_fine))
    else:
        discordanti = False

    if discordanti:
        st.markdown(i18n.ui_text("graph.discordant_html"), unsafe_allow_html=True)

    # --- buffer per popover descrizioni ---
    st.session_state["__desc_dettagliate_html"] = ""  # reset
    chunks = []

    # blocchi principali
    for blocco in dettagli:
        chunks.append(_wrap_final(blocco))

    # discordanze o frase finale
    if discordanti:
        chunks.append(_wrap_final(i18n.ui_text("graph.discordant_detail_html")))
    elif overlap and frase_finale_html:
        chunks.append(_wrap_final(f"<ul><li>{frase_finale_html}</li></ul>"))

    # riepilogo parametri usati
    if overlap and len(nomi_usati) > 0:
        nomi_finali = []
        for nome, family_id in zip(nomi_usati, famiglie_usate):
            if (family_id == FAMILY_COOLING
                and not usa_potente
                and mt_ore is not None and not np.isnan(mt_ore)
                and abs(comune_inizio - mt_ore) < 0.25):
                continue
            nomi_finali.append(nome)
        small_html = frase_riepilogo_parametri_usati(nomi_finali)
        if small_html:
            chunks.append(_wrap_final(small_html))

    # frase Qd
    frase_qd_html = frase_qd(
        Qd_val_check,
        Ta_val,
        qd_min=Qd_min,
        qd_max=Qd_max,
        qd_range_status=qd_range_status,
    )
    if (
        frase_qd_html
        and _is_num(swisswuff_min_ore)
        and _is_num(swisswuff_max_ore)
    ):
        swiss_min_txt = i18n.prudent_hours_text(float(swisswuff_min_ore))
        swiss_max_txt = i18n.prudent_hours_text(float(swisswuff_max_ore))
        swiss_scope = "Per le condizioni con Qd ≤ 0,2, " if condizioni_variabili else ""
        swiss_note = (
            f"{swiss_scope}a titolo esclusivamente orientativo, secondo l’impostazione utilizzata da Swisswuff, "
            f"il range temporale sarebbe compreso tra {swiss_min_txt} e {swiss_max_txt}; tale range è da intendersi "
            "come del tutto approssimativo, essendo calcolato applicando una variazione di ±20% alla stima centrale "
            "e privo di uno specifico fondamento statistico."
        )
        frase_qd_html = frase_qd_html.replace("</p>", f" {swiss_note}</p>")
    if frase_qd_html:
        chunks.append(_wrap_final(frase_qd_html))

    # testi base se raffreddamento non calcolabile
    if not raffreddamento_calcolabile and missing_or_invalid:
        no_macchie = str(selettore_macchie).strip() in {"Non valutata", "Non valutate", "/"}
        no_rigidita = str(selettore_rigidita).strip() in {"Non valutata", "Non valutate", "/"}
        if not no_macchie or not no_rigidita:
            for blk in paragrafi_descrizioni_base(
                testo_macchie=i18n.livor_description(base_tanatology.livor_id),
                testo_rigidita=i18n.rigor_description(base_tanatology.rigor_id),
            ):
                chunks.append(_wrap_final(blk))

        # >>> aggiunta: testi di eccitabilità anche senza dati di temperatura <<<
        if parametri_aggiuntivi_da_considerare:
            for blocco in paragrafi_parametri_aggiuntivi(
                parametri=parametri_aggiuntivi_da_considerare
            ):
                chunks.append(_wrap_final(blocco))


    # salva per popover
    st.session_state["__desc_dettagliate_html"] = "\n".join([c for c in chunks if c])

    # margine verticale prima dei link
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # --- ROW: Descrizioni dettagliate + Avvisi affiancati (descrizioni a sinistra) ---
    if not st.session_state.get("_pop_css_row_applied"):
        st.markdown(
            textwrap.dedent("""
            <style>
            /* Trigger del popover in stile link */
            div[data-testid="stPopover"] button{
                background:transparent!important;
                border:none!important;
                box-shadow:none!important;
                outline:none!important;
                color:inherit!important;
                font-size:0.95rem!important;
                text-decoration:none!important;
                cursor:pointer;
                padding:0!important;
                margin:0!important;
            }
            /* Niente limite di altezza e sfondo bianco dentro il popover */
            div[data-testid="stPopoverContent"]{max-height:none!important;}
            div[data-testid="stPopoverContent"] .final-text{
                background:#FFFFFF!important;
                color:inherit!important;
                border:1px solid rgba(0,0,0,0.08)!important;
                border-radius:8px!important;
                padding:10px 12px!important;
            }
            </style>
            """),
            unsafe_allow_html=True
        )
        st.session_state["_pop_css_row_applied"] = True

    row_has_any = bool(avvisi) or bool(st.session_state.get("__desc_dettagliate_html"))
    if row_has_any:
        c1, c2 = st.columns(2, gap="small")

        # Prima: descrizioni
        with c1:
            if st.session_state.get("__desc_dettagliate_html"):
                with st.popover(i18n.ui_text("graph.descriptions_popover")):
                    st.markdown(
                        st.session_state["__desc_dettagliate_html"],
                        unsafe_allow_html=True
                    )

        # Poi: avvisi
        with c2:
            if avvisi:
                with st.popover(i18n.ui_text("graph.warnings_popover")):
                    for m in avvisi:
                        warn_box(m)  # usa l'helper locale
