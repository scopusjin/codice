# app/graphing.py
from __future__ import annotations
import datetime
import re
import textwrap
from typing import Dict, List, Any
from numbers import Real
from app.theme import warn_box
from app.fc_scenarios import manual_fc_note
from app.theme import frase_breve_box
import numpy as np
import streamlit as st

from app.language import presentation_i18n as i18n, current_language
from app.presentation_translation import translate
from app.report_formatting import underline_findings
from app.fc_description import build_cf_description
from app.henssge import ranges_in_disaccordo_completa
from app.parameters import INF_HOURS, nomi_brevi, peribuccale_popwassilew_palm_ranges
from app.livor_digitopressione import PRESSURE_NOT_ASSESSED
from app.rigor_reformation import REFORMATION_NOT_ASSESSED, REFORMATION_YES
from app.graphing_tanatology import (
    FAMILY_LIVOR,
    FAMILY_RIGOR,
    FAMILY_COOLING,
    special_family_id,
    resolve_base_tanatology_ranges,
    resolve_special_tanatology_value,
)
from app.special_tanatology_states import PARAM_ELECTRICAL_PERIORAL
from app.graphing_cooling import compute_cooling_state, _potente_limit_for_combination
from app.cooling_inputs import missing_cooling_inputs
from app.fc_scenarios import temperature_description
from app.utils_time import round_display_hours
from app.tanatology_times import format_tanatology_measurement_datetime
from app.plotting import compute_plot_data, render_ranges_plot
from app.textgen import (
    nota_limiti_stima, nota_arrotondamento_orari,
    build_final_sentence, paragrafo_raffreddamento_dettaglio, paragrafo_potente,
    paragrafo_raffreddamento_misto, nota_potente_condizioni_critiche,
    paragrafo_raffreddamento_input, paragrafi_descrizioni_base,
    paragrafi_parametri_aggiuntivi, paragrafo_putrefattive,
    frase_riepilogo_parametri_usati, avvisi_raffreddamento_henssge,
    frase_qd, build_simple_sentence, build_final_sentence_simple, build_simple_sentence_no_dt,
)


# --------- helpers ----------
def _is_num(x):
    return x is not None and not (isinstance(x, float) and np.isnan(x))

def _wrap_final(s: str | None) -> str | None:
    if not s:
        return s

    s = underline_findings(s)

    # Detailed descriptions use regular text, including when pasted into Word.
    # Shared sentence templates retain their emphasis in the separate summary.
    s = re.sub(r"</?(?:b|strong)\b[^>]*>", "", s, flags=re.IGNORECASE)
    s = re.sub(
        r"(\bstyle\s*=\s*)([\"'])(.*?)\2",
        lambda match: match.group(1) + match.group(2) + re.sub(
            r"(?<![\w-])(?:mso-bidi-)?font-weight\s*:[^;]+",
            "font-weight:normal", match.group(3), flags=re.IGNORECASE,
        ) + match.group(2),
        s, flags=re.IGNORECASE | re.DOTALL,
    )

    def style_block(match: re.Match) -> str:
        tag, attrs = match.group(1), match.group(2)
        # Repeat paragraph formatting on each block for copying into Word.
        style = "font-weight:normal;line-height:14pt;mso-line-height-rule:at-least;" if tag in {"p", "li"} else ""
        if tag in {"ul", "li"}:
            # Keep real HTML lists, with ordinary round bullets at every level.
            style += "list-style-type:disc;"
        existing = re.search(r"\bstyle\s*=\s*([\"'])(.*?)\1", attrs, flags=re.DOTALL)
        if existing:
            quote, value = existing.group(1), existing.group(2)
            attrs = (
                attrs[:existing.start()]
                + f"style={quote}{value.rstrip(';')};{style}{quote}"
                + attrs[existing.end():]
            )
        else:
            attrs += f' style="{style}"'
        return f"<{tag}{attrs}>"

    # Preserve text, colours, font sizes and list nesting in these app fragments.
    s = re.sub(r"<(p|li|ul)\b([^>]*)>", style_block, s)
    return f'<div class="final-text" style="font-family:Arial,sans-serif;font-size:10pt;font-weight:normal;line-height:14pt;mso-line-height-rule:at-least;">{s}</div>'

def _rigor_temperature_warning_keys(rigor_range, input_ta, options):
    """Restituisce gli avvisi termici del rigor senza modificare i range."""
    if not isinstance(rigor_range, tuple):
        return []

    if bool(options.get("stima_cautelativa_beta", False)):
        candidates = [options.get("Ta_min_beta"), options.get("Ta_max_beta")]
    else:
        candidates = [input_ta]

    values = []
    for value in candidates:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if np.isfinite(numeric):
            values.append(numeric)

    if not values:
        return []

    keys = []
    if min(values) <= 10.0:
        keys.append("graph.rigor_low_temperature_warning")
    if max(values) >= 30.0:
        keys.append("graph.rigor_high_temperature_warning")
    return keys


def render_frase_breve(html: str, key: str = "fb_top"):
    contenuto = html.strip()
    if contenuto.startswith("<p>") and contenuto.endswith("</p>"):
        contenuto = contenuto[3:-4]
    st.markdown(
        '<div style="background:#E6F1EF; border:1px solid #7FA8A0; border-radius:8px; '
        'padding:12px 20px; margin:4px 0; color:#123C34; line-height:1.4; '
        'text-align:justify; text-justify:inter-word; box-sizing:border-box; width:100%;">'
        f'{contenuto}</div>',
        unsafe_allow_html=True,
    )


def _cooling_unavailable_note(error: str) -> str:
    """Compact presentation only; preserve the underlying validation rules."""
    from html import escape
    missing = re.match(r"^Manc(?:a|ano) (.+)\.$", error)
    if missing:
        fields = re.sub(r"(^|, | e )(?:la |il )", r"\1", missing.group(1))
        if current_language() == "en":
            replacements = {
                "tutte le temperature (rettale, ambientale e ante-mortem)": "all temperatures (rectal, ambient and ante-mortem)",
                "uno dei due valori del ": "one of the two values for ",
                "uno dei due valori di ": "one of the two values for ",
                "temperatura rettale": "rectal temperature",
                "temperatura ambientale": "ambient temperature",
                "temperatura ante-mortem": "ante-mortem temperature",
                "peso corporeo": "body weight",
                "fattore di correzione": "corrective factor",
            }
            for source, target in replacements.items():
                fields = fields.replace(source, target)
            fields = fields.replace(" e ", " and ")
            text = "Body cooling not calculated (missing: " + fields + ")."
        else:
            text = "Raffreddamento non calcolato (non compilati " + fields + ")."
    else:
        prefix = "Body cooling not calculated" if current_language() == "en" else "Raffreddamento non calcolato"
        text = prefix + " (" + translate(error).rstrip(".") + ")."
    return "<p style='color:#a66b00;font-size:8pt;line-height:1.35;margin:4px 0;'>" + escape(text) + "</p>"

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
    cooling_options=None,
    late_report=None,
    livor_digitopressione: str = PRESSURE_NOT_ASSESSED,
    rigor_reformation: str = REFORMATION_NOT_ASSESSED,
    **kwargs,
):
    # Back-compat: accetta skip_warnings anche via **kwargs
    if "skip_warnings" in kwargs and not skip_warnings:
        skip_warnings = bool(kwargs.pop("skip_warnings"))

    st.session_state.pop("__word_report_blocks", None)
    st.session_state["__word_footnotes"] = []
    st.session_state["__desc_dettagliate_html"] = ""
    word_cooling = []
    testo_macchie = testo_rigidita = ""
    avvisi: List[str] = []
    dettagli: List[str] = []
    frase_finale_html: str = ""

    # --- anti-duplicati per i paragrafi ---
    _dettagli_seen: set[str] = set()
    def _add_det(blocco: str | None):
        if isinstance(blocco, str):
            key = translate(blocco.strip())
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
        data_ora_ispezione_raw = datetime.datetime.combine(input_data_rilievo, ora_isp_obj.time())
        data_ora_ispezione = data_ora_ispezione_raw
    else:
        data_ora_ispezione_raw = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        data_ora_ispezione = data_ora_ispezione_raw

    # --- validazioni base (configurabili) ---
    if not skip_warnings:
        missing = missing_cooling_inputs(input_rt=input_rt, input_ta=input_ta,
            input_tm=input_tm, input_w=input_w, fattore_correzione=fattore_correzione,
            options=st.session_state if cooling_options is None else cooling_options)
        if missing:
            st.error(missing)
            return
        if input_w is None or input_w <= 0:
            st.error(i18n.ui_text("graph.invalid_weight"))
            return
        if fattore_correzione is None or fattore_correzione <= 0:
            st.error(i18n.ui_text("graph.invalid_factor"))
            return
        if any(v is None for v in [input_rt, input_ta, input_tm]):
            st.error(i18n.ui_text("graph.missing_temperatures"))
            return

    raffreddamento_richiesto = any(
        v is not None for v in (input_rt, input_ta, input_tm, input_w)
    )

    cooling = compute_cooling_state(
        input_rt=input_rt,
        input_ta=input_ta,
        input_tm=input_tm,
        input_w=input_w,
        fattore_correzione=fattore_correzione,
        data_ora_ispezione=data_ora_ispezione,
        skip_warnings=skip_warnings,
        cooling_options=cooling_options,
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
    swisswuff_mode = cooling.swisswuff_mode
    raffreddamento_calcolabile = cooling.raffreddamento_calcolabile
    Ta_for_pot = cooling.Ta_for_pot
    qd_threshold = cooling.qd_threshold
    gate_fail = cooling.gate_fail
    options = st.session_state if cooling_options is None else cooling_options
    round_minutes = int(options.get("henssge_round_minutes", 15))
    condizioni_variabili = bool(options.get("stima_cautelativa_beta", False))
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
    base_tanatology = resolve_base_tanatology_ranges(
        selettore_macchie, selettore_rigidita, livor_digitopressione, rigor_reformation
    )
    macchie_range = base_tanatology.livor_range
    macchie_range_valido = isinstance(macchie_range, tuple)
    macchie_medi_range = base_tanatology.livor_typical_range if macchie_range_valido else None

    rigidita_range = base_tanatology.rigor_range
    rigidita_range_valido = isinstance(rigidita_range, tuple)
    rigidita_medi_range = base_tanatology.rigor_typical_range if rigidita_range_valido else None

    macchie_non_valutate = str(selettore_macchie).strip() in {"Non valutata", "Non valutate", "/"}
    rigidita_non_valutata = str(selettore_rigidita).strip() in {"Non valutata", "Non valutate", "/"}

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
            ora_rilievo_time = data_ora_ispezione_raw.time()
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
            data_rilievo_param = data_ora_ispezione_raw.date()

        range_valori = parametro_risolto.range_value
        if range_valori:
            descrizione = (
                i18n.special_description(parametro_risolto.parameter_id, parametro_risolto.option_id)
                if current_language() == "en" and parametro_risolto.parameter_id and parametro_risolto.option_id else
                parametro_risolto.description
                if parametro_risolto.description is not None
                else i18n.ui_text("graph.missing_special_description", state=stato_selezionato)
            )
            data_ora_param = datetime.datetime.combine(data_rilievo_param, ora_rilievo_time)
            diff_h = (data_ora_param - data_ora_ispezione_raw).total_seconds() / 3600.0

            if diff_h != 0:
                measurement_when = format_tanatology_measurement_datetime(data_ora_param)
                reference_when = format_tanatology_measurement_datetime(data_ora_ispezione_raw)

                plural = "valutazioni del dato tanatologico"
                singular = "valutazione del dato tanatologico"
                if plural in descrizione:
                    descrizione = descrizione.replace(
                        plural,
                        i18n.ui_text(
                            "graph.special_time_context_plural",
                            measurement_when=measurement_when,
                            reference_when=reference_when,
                        ),
                        1,
                    )
                elif singular in descrizione:
                    descrizione = descrizione.replace(
                        singular,
                        i18n.ui_text(
                            "graph.special_time_context_singular",
                            measurement_when=measurement_when,
                            reference_when=reference_when,
                        ),
                        1,
                    )
                else:
                    descrizione = (
                        f"{descrizione.rstrip()} "
                        + i18n.ui_text(
                            "graph.special_time_context_fallback",
                            measurement_when=measurement_when,
                            reference_when=reference_when,
                        )
                    )
                descrizione = descrizione.replace(
                    f" (rilievi termometrici {reference_when})",
                    "",
                )

            if range_valori[1] >= INF_HOURS:
                range_trasl = (range_valori[0] - diff_h, INF_HOURS)
            else:
                range_trasl = (range_valori[0] - diff_h, range_valori[1] - diff_h)
            lo, hi = range_trasl
            lo = max(0, lo)

            green_range_traslato = None
            if parametro_risolto.parameter_id == PARAM_ELECTRICAL_PERIORAL:
                pp_range = peribuccale_popwassilew_palm_ranges.get(stato_selezionato)
                if pp_range is not None:
                    pp_lo = max(0, pp_range[0] - diff_h)
                    pp_hi = max(0, pp_range[1] - diff_h)
                    if pp_hi >= pp_lo:
                        green_range_traslato = (pp_lo, pp_hi)

            parametri_aggiuntivi_da_considerare.append(dict(
                nome=nome_parametro, label=parametro_label,
                parameter_id=parametro_risolto.parameter_id,
                stato=stato_selezionato,
                range_traslato=(lo, hi), descrizione=descrizione,
                differenza_ore=diff_h, adattato=(diff_h != 0),
                green_range_traslato=green_range_traslato,
            ))
            diffs = {p["differenza_ore"] for p in parametri_aggiuntivi_da_considerare if p.get("adattato")}
            nota_globale_range_adattato = len(diffs) == 1
        else:
            descrizione = (
                i18n.special_description(parametro_risolto.parameter_id, parametro_risolto.option_id)
                if current_language() == "en" and parametro_risolto.parameter_id and parametro_risolto.option_id else
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
                range_traslato=(np.nan, np.nan), descrizione=descrizione,
                green_range_traslato=None,
            ))

    orari_parametri_differenti = any(
        bool(p.get("adattato")) for p in parametri_aggiuntivi_da_considerare
    )

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
        mt_ore = _potente_limit_for_combination(Ta_for_pot, CF_val, W_val)
        if mt_ore is not None:
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

    from app.late_changes import late_hours_conflict
    late_warning = late_hours_conflict(late_report, zip(nomi_usati, fine), current_language())
    if late_warning:
        from html import escape
        late_report = dict(late_report)
        late_report['html'] = late_report.get('conflict_html', late_report['html']) + '<p style="color:#9C2F16;">' + escape(late_warning) + '</p>'
        avvisi.append(late_warning)

    # Più scenari o metodi del raffreddamento restano un solo parametro.
    single_parameter = len(set(famiglie_usate)) == 1

    # intersezione finale
    starts_clean = [s for s in inizio if _is_num(s)]
    if not starts_clean:
        comune_inizio, comune_fine, overlap = np.nan, np.nan, False
    else:
        comune_inizio = max(starts_clean)
        superiori_finiti = [v for v in fine if _is_num(v) and v < INF_HOURS]
        comune_fine = min(superiori_finiti) if superiori_finiti else np.nan
        if condizioni_variabili and np.isnan(t_max_raff_henssge) and not superiori_finiti:
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
            extra_param = {
                "label": label,
                "start": float(lo),
                "end": float(hi) if _is_num(hi) else np.inf,
                "order": idx,
                "adattato": bool(p.get("adattato", False)),
            }
            green_range = p.get("green_range_traslato")
            if isinstance(green_range, tuple) and len(green_range) == 2:
                extra_param["green_start"] = float(green_range[0])
                extra_param["green_end"] = float(green_range[1])
            extra_params_for_plot.append(extra_param)

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
    # Su mobile il grafico viene conservato temporaneamente e mostrato dopo
    # il riepilogo sintetico, dentro una sezione richiudibile. In questo modo
    # l'esito medico-legale è la prima informazione visibile dopo il calcolo.
    mobile_result_figure = None
    mobile_results = bool(st.session_state.get("__full_device_mobile", False))
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if raff_for_plot: num_params_grafico += 1
    num_params_grafico += len(extra_params_for_plot)

    st.session_state["frase_breve"] = None

    if num_params_grafico == 0 and not cooling.validation_error and not late_report:
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
            ax = fig.axes[0]

            # Sottorange Popwassilew–Palm: informativo soltanto, non entra nell'intersezione.
            extra_base_y = int(macchie_range_valido) + int(rigidita_range_valido)
            for pos, e in enumerate(extra_params_for_plot):
                green_start = e.get("green_start")
                green_end = e.get("green_end")
                if _is_num(green_start) and _is_num(green_end) and float(green_end) > float(green_start):
                    ax.hlines(
                        extra_base_y + pos,
                        max(0.0, float(green_start)),
                        min(float(tail), float(green_end)),
                        color='mediumseagreen',
                        linewidth=6,
                        alpha=1.0,
                        zorder=3,
                    )

            if overlap and (np.isnan(comune_fine) or comune_fine > 0):
                if comune_inizio < tail:
                    ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
                if not np.isnan(comune_fine) and comune_fine > 0:
                    ax.axvline(min(tail, comune_fine), color='red', linestyle='--')
            if mobile_results:
                mobile_result_figure = fig
            else:
                st.pyplot(fig)

        # La frase breve viene calcolata qui e mostrata prima dei comandi di dettaglio.
        if overlap:
            if usa_orario_custom:
                frase_semplice = build_simple_sentence(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    isp_dt=data_ora_ispezione,
                    inf_hours=INF_HOURS,
                    round_minutes=round_minutes,
                )
                if frase_semplice:
                    st.session_state["frase_breve"] = frase_semplice
            else:
                frase_semplice_no_dt = build_simple_sentence_no_dt(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    inf_hours=INF_HOURS,
                    round_minutes=round_minutes,
                )
                if frase_semplice_no_dt:
                    st.session_state["frase_breve"] = frase_semplice_no_dt

    # --- avvisi ---
    if nota_globale_range_adattato:
        avvisi.append(i18n.ui_text("graph.shifted_ranges_note"))

    missing_or_invalid = (
        not _is_num(Tr_val) or not _is_num(Ta_val) or not _is_num(T0_val) or
        not _is_num(W_val) or not _is_num(CF_val) or
        (_is_num(W_val) and W_val <= 0) or (_is_num(CF_val) and CF_val <= 0)
    )
    if raffreddamento_richiesto and not raffreddamento_calcolabile and not cooling.validation_error:
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
        if not condizioni_variabili:
            cf_descr = build_cf_description(
                cf_value=st.session_state.get("fattore_correzione", 1.0),
                riassunto=st.session_state.get("fc_riassunto_contatori"),
                fallback_text=st.session_state.get("fattori_condizioni_testo"),
            )
            _add_det(paragrafo_raffreddamento_input(
                isp_dt=data_ora_ispezione if usa_orario_custom else None,
                ta_val=Ta_val, tr_val=Tr_val, w_val=W_val, t0_val=T0_val, cf_descr=cf_descr,
                ambient_temperature_text=temperature_description(
                    st.session_state if cooling_options is None else cooling_options,
                    (CF_val, CF_val), W_val, (Ta_val, Ta_val)),
            ))

        word_cooling_start = len(dettagli)
        if temperatures_equal and not usa_potente:
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
        raffreddamento_misto = condizioni_variabili and qd_range_status == "mixed" and usa_potente
        if raffreddamento_misto:
            _add_det(paragrafo_raffreddamento_misto(minimum_hours=raff_plot_start, round_minutes=round_minutes))
        elif henssge_non_applicabile_singolo:
            _add_det("<ul><li>Nel caso in esame, il grado di raffreddamento corporeo, calcolabile sulla base della temperatura rettale e ambientale, ricade al di fuori dei range nei quali il metodo di Henssge consente una stima sufficientemente attendibile del tempo post-mortale; la sua applicazione porterebbe pertanto a formulare stime tendenzialmente inaffidabili.</li></ul>")
        else:
            par_h = paragrafo_raffreddamento_dettaglio(
                t_min_visual=t_min_vis,
                t_max_visual=t_max_vis,
                t_med_round=t_med_raff_henssge_rounded,
                qd_val=Qd_val_check,
                ta_val=Ta_val,
                qd_range_status=qd_range_status,
                round_minutes=round_minutes,
            )
            if par_h:
                if usa_orario_custom:
                    if current_language() == "en":
                        par_h = par_h.replace(
                            "before temperature measurement.",
                            f"before temperature measurement at {data_ora_ispezione_raw:%H:%M} on {data_ora_ispezione_raw:%d.%m.%Y}.",
                            1,
                        )
                    par_h = par_h.replace(
                        "prima dei rilievi effettuati nel corso dell’ispezione legale.",
                        f"prima dei rilievi effettuati nel corso dell’ispezione legale, alle ore {data_ora_ispezione_raw:%H:%M} del {data_ora_ispezione_raw:%d.%m.%Y}.",
                        1,
                    )
                _add_det(par_h)

        if not raffreddamento_misto:
            qd_for_potente = 0.0 if temperatures_equal else Qd_val_check
            par_p = paragrafo_potente(
                mt_ore=mt_ore, mt_giorni=mt_giorni, qd_val=qd_for_potente, ta_val=Ta_val, qd_threshold=qd_threshold,
                round_minutes=round_minutes,
            )
            if temperatures_equal and par_p and current_language() == "it":
                # Link thermal equilibrium directly to the minimum-time method.
                continuation = par_p.split("In tali condizioni,", 1)
                if len(continuation) == 2:
                    equilibrium = i18n.ui_text("graph.henssge_equal_temperature_detail", temperature=f"{float(Tr_val):.1f}")
                    equilibrium = equilibrium.removeprefix("<ul><li>").removesuffix("</li></ul>")
                    equilibrium = equilibrium.replace("In merito al <u>raffreddamento corporeo</u>, è valutabile", "È valutabile", 1)
                    body = (equilibrium + " In tali condizioni," + continuation[1]).removesuffix("</li></ul>")
                    par_p = '<p style="margin-left:40px;">' + body + '</p>'
            elif temperatures_equal and par_p:
                _add_det(i18n.ui_text("graph.henssge_equal_temperature_detail", temperature=f"{float(Tr_val):.1f}"))
            _add_det(par_p)

        word_cooling = dettagli[word_cooling_start:]

        # --- frase finale complessiva ---
        frase_finale_html: str = ""
        if usa_orario_custom:
            _tmp = build_final_sentence(
                comune_inizio, comune_fine, data_ora_ispezione,
                qd_val=Qd_val_check, mt_ore=mt_ore, ta_val=Ta_val, inf_hours=INF_HOURS,
                single_parameter=single_parameter,
                round_minutes=round_minutes,
            )
        else:
            _tmp = build_final_sentence_simple(
                comune_inizio=comune_inizio,
                comune_fine=comune_fine,
                inf_hours=INF_HOURS,
                single_parameter=single_parameter,
                round_minutes=round_minutes,
            )
        if isinstance(_tmp, str):
            frase_finale_html = _tmp

    # Fallback: genera il riepilogo anche quando la stima non usa il raffreddamento.
    if overlap and not frase_finale_html:
        if usa_orario_custom:
            _tmp = build_final_sentence(
                comune_inizio, comune_fine, data_ora_ispezione,
                qd_val=Qd_val_check, mt_ore=mt_ore, ta_val=Ta_val, inf_hours=INF_HOURS,
                single_parameter=single_parameter,
                round_minutes=round_minutes,
            )
        else:
            _tmp = build_final_sentence_simple(
                comune_inizio=comune_inizio,
                comune_fine=comune_fine,
                inf_hours=INF_HOURS,
                single_parameter=single_parameter,
                round_minutes=round_minutes,
            )
        if isinstance(_tmp, str):
            frase_finale_html = _tmp

    if orari_parametri_differenti and frase_finale_html:
        intro_orari_diversi = (
            "La valutazione combinata dei dati tanatologici, integrando i loro limiti temporali minimi e massimi "
            "e tenendo conto dei diversi orari di misurazione dei vari parametri,"
        )
        intro_min_max = (
            "La valutazione combinata dei dati tanatologici, integrando i loro limiti temporali minimi e massimi,"
        )
        intro_generico = "La valutazione combinata dei dati tanatologici consente"
        intro_semplice = "La valutazione combinata dei dati tanatologici, integrando i loro limiti temporali,"
        if intro_min_max in frase_finale_html:
            frase_finale_html = frase_finale_html.replace(intro_min_max, intro_orari_diversi, 1)
        elif intro_generico in frase_finale_html:
            frase_finale_html = frase_finale_html.replace(
                intro_generico,
                f"{intro_orari_diversi} consente",
                1,
            )
        elif intro_semplice in frase_finale_html:
            frase_finale_html = frase_finale_html.replace(intro_semplice, intro_orari_diversi, 1)

    if current_language() == "en" and orari_parametri_differenti and frase_finale_html:
        for prefix in ("Combined assessment of the postmortem findings, integrating their minimum and maximum time limits,",
                       "Combined assessment of the postmortem findings, integrating their time limits,",
                       "Combined assessment of the postmortem findings"):
            if prefix in frase_finale_html:
                frase_finale_html = frase_finale_html.replace(prefix,
                    "Combined assessment of the postmortem findings, accounting for their different observation times,", 1)
                break

    # Descrizioni tanatologiche: includi solo rilievi effettivamente valutati.
    # Gli stati "Non valutata/e" non vengono più riportati nel testo dettagliato.
    if not macchie_non_valutate and not (late_report and base_tanatology.livor_id == "livor_unreliable"):
        testo_macchie = i18n.livor_description(base_tanatology.livor_id)
        if (
            base_tanatology.livor_id == "livor_partially_migratable"
            and livor_digitopressione == "complete_fading"
            and macchie_range == (4, 20)
        ):
            testo_macchie = (
                "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, "
                "si trovassero in una fase di migrabilità parziale e fossero improntabili. "
                "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, "
                "questo suggerisce che fossero trascorse tra 4 e 20 ore dal decesso."
            )
        elif macchie_range_valido and livor_digitopressione != PRESSURE_NOT_ASSESSED and testo_macchie:
            # Una sola descrizione e un solo intervallo, già intersecato dal motore.
            descrizione_reperto = testo_macchie.split(". ", 1)[0].rstrip(".")
            improntabilita = (
                "improntabili"
                if livor_digitopressione == "complete_fading"
                else "non completamente improntabili"
            )
            minimo, massimo = macchie_range
            if massimo >= INF_HOURS:
                limite = (
                    f"fossero trascorse più di {minimo:g} ore dal decesso"
                    if base_tanatology.livor_id == "livor_fixed"
                    else f"fosse trascorsa almeno {minimo:g} ora dal decesso"
                    if minimo == 1 else f"fossero trascorse almeno {minimo:g} ore dal decesso"
                )
            elif minimo <= 0:
                limite = f"fossero trascorse meno di {massimo:g} ore dal decesso"
            else:
                limite = f"fossero trascorse tra {minimo:g} e {massimo:g} ore dal decesso"
            testo_macchie = (
                f"{descrizione_reperto} e fossero {improntabilita}. "
                f"Secondo i limiti segnalati in letteratura scientifica, "
                f"questo suggerisce che {limite}."
            )
        if current_language() == "en" and macchie_range_valido and livor_digitopressione != PRESSURE_NOT_ASSESSED:
            from app.locales.en_combined_findings import livor_with_pressure
            testo_macchie = livor_with_pressure(base_tanatology.livor_id, livor_digitopressione,
                                               *macchie_range, macchie_range[1] >= INF_HOURS)
        if testo_macchie:
            _add_det(f"<ul><li>{testo_macchie.strip()}</li></ul>")
    if not rigidita_non_valutata and not (late_report and base_tanatology.rigor_id == "rigor_unreliable"):
        testo_rigidita = i18n.rigor_description(base_tanatology.rigor_id)
        if (
            rigor_reformation == REFORMATION_YES
            and isinstance(rigidita_range, tuple)
            and base_tanatology.rigor_id in ("rigor_developing", "rigor_full")
        ):
            minimo, massimo = rigidita_range
            reperto = (
                "fosse in via di formazione, intensificazione e generalizzazione"
                if base_tanatology.rigor_id == "rigor_developing"
                else "fosse presente e generalizzata"
            )
            minimo_testo = "30 minuti" if minimo == 0.5 else f"{minimo:g} ore"
            testo_rigidita = (
                "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, "
                f"{reperto} e che, dopo essere stata vinta mediante mobilizzazione forzata, "
                "si fosse nuovamente formata. Secondo i limiti minimi e massimi segnalati "
                "in letteratura scientifica, questo suggerisce che fossero trascorsi "
                f"tra {minimo_testo} e {massimo:g} ore dal decesso."
            )
        if (current_language() == "en" and rigor_reformation == REFORMATION_YES
                and isinstance(rigidita_range, tuple)
                and base_tanatology.rigor_id in ("rigor_developing", "rigor_full")):
            from app.locales.en_combined_findings import rigor_with_reformation
            testo_rigidita = rigor_with_reformation(base_tanatology.rigor_id, *rigidita_range)
        if testo_rigidita:
            _add_det(f"<ul><li>{testo_rigidita}</li></ul>")
    word_additional = paragrafi_parametri_aggiuntivi(parametri=parametri_aggiuntivi_da_considerare)
    word_putrefaction = late_report["html"] if late_report else paragrafo_putrefattive(alterazioni_putrefattive)
    for blocco in word_additional:
        _add_det(blocco)
    _add_det(word_putrefaction)

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

    # 1) descrizioni dettagliate dei dati/metodi effettivamente valutati
    for blocco in dettagli:
        chunks.append(_wrap_final(blocco))

    # Prepara la frase Qd; verrà aggiunta come ultimo elemento delle descrizioni.
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
        swiss_min_txt = i18n.prudent_hours_text(round_display_hours(swisswuff_min_ore, round_minutes))
        swiss_max_txt = i18n.prudent_hours_text(round_display_hours(swisswuff_max_ore, round_minutes, upper=True))

        if swisswuff_mode == "high_temp":
            swiss_note = (
                "A titolo esclusivamente orientativo, secondo l’impostazione utilizzata da Swisswuff, "
                f"il tempo trascorso dal decesso al momento dei rilievi sarebbe stimabile tra {swiss_min_txt} e {swiss_max_txt}. "
                "Tale risultato non viene utilizzato nella stima principale poiché, per temperature ambientali &gt;23 °C e Q ≤0.5, "
                "Potente et al. considerano non adeguatamente validati i limiti di confidenza dell’intervallo calcolato mediante il metodo di Henssge "
                "e propongono, in via prudenziale, di fare riferimento al solo tempo minimo trascorso dal decesso."
            )
        elif swisswuff_mode == "mixed":
            swiss_note = (
                "A titolo esclusivamente orientativo, secondo l’impostazione utilizzata da Swisswuff, "
                f"il tempo trascorso dal decesso al momento dei rilievi ricadrebbe complessivamente tra {swiss_min_txt} e {swiss_max_txt}. "
                "Tale risultato non viene utilizzato nella stima principale: per le condizioni con temperatura ambientale &gt;23 °C e Q ≤0.5 "
                "Potente et al. considerano non adeguatamente validati i limiti di confidenza dell’intervallo calcolato mediante il metodo di Henssge; "
                "per le condizioni con Q ≤0.2, l’intervallo Swisswuff è inoltre ottenuto applicando una variazione di ±20% alla stima centrale "
                "ed è privo di uno specifico fondamento statistico."
            )
        else:
            swiss_scope = (
                "Per le condizioni con Qd ≤ 0.2, a titolo esclusivamente orientativo, "
                if condizioni_variabili
                else "A titolo esclusivamente orientativo, "
            )
            swiss_note = (
                f"{swiss_scope}secondo l’impostazione utilizzata da Swisswuff, "
                f"il tempo trascorso dal decesso al momento dei rilievi sarebbe stimabile tra {swiss_min_txt} e {swiss_max_txt}; tale intervallo è da intendersi "
                "come del tutto approssimativo, essendo calcolato applicando una variazione di ±20% alla stima centrale "
                "e privo di uno specifico fondamento statistico."
            )

        frase_qd_html = frase_qd_html.replace("</p>", f" {swiss_note}</p>")

    # 2) stima complessiva / eventuale discordanza
    if discordanti:
        chunks.append(_wrap_final(i18n.ui_text("graph.discordant_detail_html")))
    elif overlap and frase_finale_html and (not single_parameter or usa_orario_custom):
        # Con un solo parametro, senza data/ora la conclusione ripete il dettaglio.
        chunks.append(_wrap_final(frase_finale_html))

    if overlap and not discordanti:
        chunks.append(_wrap_final(nota_limiti_stima()))
        chunks.append(_wrap_final(nota_arrotondamento_orari(round_minutes)))

    # 3) frase blu di riepilogo dei parametri usati.
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

    if raffreddamento_calcolabile:
        note_bounds = ([options.get("FC_min_beta"), options.get("FC_max_beta")]
                       if condizioni_variabili else [CF_val, CF_val])
        if fc_note := manual_fc_note(options, note_bounds, W_val):
            chunks.append(_wrap_final("<p style='color:blue;font-size:8pt;'>" + fc_note + "</p>"))

    # 4) nota blu Qd, seguita dalla precisazione Potente per il caso in esame.
    if frase_qd_html:
        chunks.append(_wrap_final(frase_qd_html))

    if condizioni_variabili and qd_range_status == "mixed" and usa_potente and _is_num(mt_ore):
        chunks.append(_wrap_final(nota_potente_condizioni_critiche(minimum_hours=float(mt_ore), round_minutes=round_minutes)))

    # Separate Word fields: use the same generated prose, without the blue notes.
    from app.case_report import build_word_blocks
    st.session_state["__word_report_blocks"] = build_word_blocks(
        input_html="\n".join(dettagli), cooling_html="\n".join(word_cooling),
        livor=testo_macchie, rigor=testo_rigidita,
        additional_html="\n".join(word_additional), putrefaction_html=word_putrefaction,
        conclusion=((frase_finale_html + nota_limiti_stima()) if overlap and not discordanti and frase_finale_html else ""),
    )

    st.session_state["__word_footnotes"] = late_report.get("word_footnotes", []) if late_report else []

    # salva per popover
    st.session_state["__desc_dettagliate_html"] = translate("\n".join([c for c in chunks if c]))

    # Riepilogo verde prima dei comandi di dettaglio.
    frase_breve_html = st.session_state.get("frase_breve")
    if late_warning:
        st.warning(late_warning)
    if late_report and not late_warning:
        from html import escape
        late_brief = "<p>" + escape(late_report["brief"]).replace("\n", "</p><p>") + "</p>"
        frase_breve_html = (frase_breve_html or "") + late_brief
        st.session_state["frase_breve"] = frase_breve_html
    if frase_breve_html:
        render_frase_breve(frase_breve_html, key="fb_before_details")
        if overlap and not discordanti:
            brief_note = nota_limiti_stima().replace("<i>", "").replace("</i>", "").replace(
                "<p>", "<p style='color:blue;font-size:8pt;line-height:1.35;margin:4px 0;'>"
            )
            st.markdown(brief_note, unsafe_allow_html=True)

    if cooling.validation_error:
        st.markdown(_cooling_unavailable_note(cooling.validation_error), unsafe_allow_html=True)

    if mobile_result_figure is not None:
        with st.expander(i18n.ui_text("graph.plot_expander"), expanded=False):
            st.pyplot(mobile_result_figure, width="stretch")

    # Margine contenuto prima dei comandi secondari.
    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

    # --- ROW: Descrizioni dettagliate + Avvisi, con ritorno a capo se necessario ---
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
                text-align:justify!important;
                text-justify:inter-word!important;
            }
            </style>
            """),
            unsafe_allow_html=True
        )
        st.session_state["_pop_css_row_applied"] = True

    row_has_any = bool(avvisi) or bool(st.session_state.get("__desc_dettagliate_html"))
    if row_has_any:
        with st.container(
            horizontal=True,
            wrap=True,
            horizontal_alignment="left",
            vertical_alignment="center",
            gap="small",
            key="result_secondary_actions",
        ):
            if st.session_state.get("__desc_dettagliate_html"):
                with st.container(width="content", key="result_descriptions_action"):
                    with st.popover(i18n.ui_text("graph.descriptions_popover")):
                        st.markdown(
                            st.session_state["__desc_dettagliate_html"],
                            unsafe_allow_html=True
                        )
                        from app.case_report import capture_report
                        from app.case_ui import render_case_download
                        capture_report(st.session_state, "full")
                        render_case_download("full", key="case_download_details", word_hint=True)

            if avvisi:
                with st.container(width="content", key="result_warnings_action"):
                    with st.popover(i18n.ui_text("graph.warnings_popover")):
                        for m in avvisi:
                            warn_box(m)  # usa l'helper locale
