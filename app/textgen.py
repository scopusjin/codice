# -*- coding: utf-8 -*-
# textgen.py — Generazione testi finali e paragrafi descrittivi

from __future__ import annotations
import datetime
from typing import List, Optional, Tuple, Iterable, Dict, Any
import numpy as np

from app import i18n
from app.utils_time import split_hours_minutes
from app.textgen_tanatology import special_description_is_reportable

# ------------------------------------------------------------
# Utilità testuali
# ------------------------------------------------------------

def _fmt_dt(dt: datetime.datetime) -> Tuple[str, str]:
    """Ritorna (HH:MM, dd.mm.YYYY)."""
    return dt.strftime('%H:%M'), dt.strftime('%d.%m.%Y')

def _safe_is_nan(x: Optional[float]) -> bool:
    return x is None or np.isnan(x)

# --- Helper formattazione ore/minuti ---

def _hm_from_hours(ore_float: float) -> tuple[int, int]:
    """Converte ore decimali in (ore, minuti) interi non negativi."""
    h, m = split_hours_minutes(ore_float) or (0, 0)
    return int(h), int(m)

def _fmt_hm_full(h: int, m: int) -> str:
    """'1 ora e 30 minuti' / '2 ore' / '45 minuti' / '1 minuto'."""
    return i18n.format_hours_minutes(h, m)

def _fmt_range_hm(h1: int, m1: int, h2: int, m2: int) -> str:
    """
    Intervallo naturale:
    - 'tra 2 e 3 ore'                (2:00–3:00)
    - 'tra 2 ore e 3 ore 30 minuti'  (2:00–3:30)
    Fallback:
    - 'tra 1 ora e 30 minuti e 3 ore'
    """
    return i18n.format_hours_range(h1, m1, h2, m2)

# ------------------------------------------------------------
# Frasi conclusive (HTML pronto)
# ------------------------------------------------------------

def build_final_sentence(
    comune_inizio: float,
    comune_fine: float,
    isp_dt: datetime.datetime,
    *,
    qd_val: Optional[float] = None,
    mt_ore: Optional[float] = None,
    ta_val: Optional[float] = None,
    inf_hours: float = np.inf
) -> Optional[str]:
    if _safe_is_nan(comune_inizio) and _safe_is_nan(comune_fine):
        return None

    limite_sup_inf = _safe_is_nan(comune_fine) or comune_fine == inf_hours

    # Caso: limite superiore infinito → “oltre X”
    if limite_sup_inf and not _safe_is_nan(comune_inizio):
        start = mt_ore if (mt_ore is not None and not np.isnan(mt_ore) and abs(comune_inizio - mt_ore) < 0.25) else comune_inizio
        h1, m1 = _hm_from_hours(start)
        decesso_dt = isp_dt - datetime.timedelta(hours=start)
        hh_d, dd_d = _fmt_dt(decesso_dt)
        return i18n.final_sentence_dt_over(_fmt_hm_full(h1, m1), hh_d, dd_d)

    # Caso: 0–X → “non oltre X”
    if not _safe_is_nan(comune_fine) and (comune_inizio == 0 or _safe_is_nan(comune_inizio)):
        h2, m2 = _hm_from_hours(comune_fine)
        lim_inf_dt = isp_dt - datetime.timedelta(hours=comune_fine)
        hh_lo, dd_lo = _fmt_dt(lim_inf_dt)
        hh_isp, dd_isp = _fmt_dt(isp_dt)
        return i18n.final_sentence_dt_not_over(
            _fmt_hm_full(h2, m2),
            hh_lo,
            dd_lo,
            hh_isp,
            dd_isp,
        )

    # Caso: A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1 = _hm_from_hours(comune_inizio)
        h2, m2 = _hm_from_hours(comune_fine)
        dt_da = isp_dt - datetime.timedelta(hours=comune_fine)
        dt_aa = isp_dt - datetime.timedelta(hours=comune_inizio)
        hh_da, dd_da = _fmt_dt(dt_da)
        hh_aa, dd_aa = _fmt_dt(dt_aa)
        intervallo_txt = _fmt_range_hm(h1, m1, h2, m2)
        return i18n.final_sentence_dt_range(
            intervallo_txt,
            hh_da,
            dd_da,
            hh_aa,
            dd_aa,
            dt_da.date() == dt_aa.date(),
        )

    return None

# ------------------------------------------------------------
# Frasi brevi per la sezione sotto al grafico
# ------------------------------------------------------------

def build_simple_sentence(
    comune_inizio: Optional[float],
    comune_fine: Optional[float],
    isp_dt: datetime.datetime,
    *,
    inf_hours: float = np.inf
) -> Optional[str]:
    """Versione breve con data/ora. HTML con intestazione in grassetto."""
    if _safe_is_nan(comune_inizio) and _safe_is_nan(comune_fine):
        return None
    limite_sup_inf = _safe_is_nan(comune_fine) or comune_fine == inf_hours

    def _ora_data(h_dec):
        dt = isp_dt - datetime.timedelta(hours=h_dec)
        return _fmt_dt(dt)

    # 0–X
    if not _safe_is_nan(comune_fine) and (comune_inizio == 0 or _safe_is_nan(comune_inizio)):
        h2, m2 = _hm_from_hours(comune_fine)
        hh_lo, dd_lo = _ora_data(comune_fine)
        hh_isp, dd_isp = _fmt_dt(isp_dt)
        return i18n.simple_sentence_dt_not_over(
            _fmt_hm_full(h2, m2),
            hh_lo,
            dd_lo,
            hh_isp,
            dd_isp,
        )

    # oltre X
    if limite_sup_inf and not _safe_is_nan(comune_inizio):
        h1, m1 = _hm_from_hours(comune_inizio)
        hh_d, dd_d = _ora_data(comune_inizio)
        return i18n.simple_sentence_dt_over(_fmt_hm_full(h1, m1), hh_d, dd_d)

    # A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1 = _hm_from_hours(comune_inizio)
        h2, m2 = _hm_from_hours(comune_fine)
        hh_da, dd_da = _ora_data(comune_fine)
        hh_aa, dd_aa = _ora_data(comune_inizio)
        intervallo_txt = _fmt_range_hm(h1, m1, h2, m2)
        return i18n.simple_sentence_dt_range(
            intervallo_txt,
            hh_da,
            dd_da,
            hh_aa,
            dd_aa,
            (isp_dt - datetime.timedelta(hours=comune_fine)).date()
            == (isp_dt - datetime.timedelta(hours=comune_inizio)).date(),
        )
    return None

def build_simple_sentence_no_dt(
    comune_inizio: Optional[float],
    comune_fine: Optional[float],
    *,
    inf_hours: float = np.inf
) -> Optional[str]:
    """
    Versione breve senza data/ora. HTML con intestazione in grassetto.
    """
    if _safe_is_nan(comune_inizio) and _safe_is_nan(comune_fine):
        return None
    limite_sup_inf = _safe_is_nan(comune_fine) or comune_fine == inf_hours

    # 0–X
    if not _safe_is_nan(comune_fine) and (comune_inizio == 0 or _safe_is_nan(comune_inizio)):
        h2, m2 = _hm_from_hours(comune_fine)
        return i18n.simple_sentence_no_dt_not_over(_fmt_hm_full(h2, m2))

    # oltre X
    if limite_sup_inf and not _safe_is_nan(comune_inizio):
        h1, m1 = _hm_from_hours(comune_inizio)
        return i18n.simple_sentence_no_dt_over(_fmt_hm_full(h1, m1))

    # A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1 = _hm_from_hours(comune_inizio)
        h2, m2 = _hm_from_hours(comune_fine)
        intervallo_txt = _fmt_range_hm(h1, m1, h2, m2)
        return i18n.simple_sentence_no_dt_range(intervallo_txt)
    return None

def build_final_sentence_simple(
    comune_inizio: float,
    comune_fine: float,
    *,
    inf_hours: float = np.inf
) -> Optional[str]:
    """
    Versione semplificata per l’expander. HTML con intestazione in grassetto.
    """
    if _safe_is_nan(comune_inizio) and _safe_is_nan(comune_fine):
        return None

    limite_sup_inf = _safe_is_nan(comune_fine) or comune_fine == inf_hours

    # oltre X
    if limite_sup_inf and not _safe_is_nan(comune_inizio):
        h1, m1 = _hm_from_hours(comune_inizio)
        return i18n.final_sentence_simple_over(_fmt_hm_full(h1, m1))

    # 0–X
    if not _safe_is_nan(comune_fine) and (comune_inizio == 0 or _safe_is_nan(comune_inizio)):
        h2, m2 = _hm_from_hours(comune_fine)
        return i18n.final_sentence_simple_not_over(_fmt_hm_full(h2, m2))

    # A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1 = _hm_from_hours(comune_inizio)
        h2, m2 = _hm_from_hours(comune_fine)
        intervallo_txt = _fmt_range_hm(h1, m1, h2, m2)
        return i18n.final_sentence_simple_range(intervallo_txt)

    return None

# ------------------------------------------------------------
# Paragrafi descrittivi per l’expander “Descrizioni dettagliate”
# ------------------------------------------------------------

def paragrafo_raffreddamento_dettaglio(
    *,
    t_min_visual: Optional[float],
    t_max_visual: Optional[float],
    t_med_round: Optional[float],
    qd_val: Optional[float],
    ta_val: Optional[float],
    qd_range_status: Optional[str] = None,
) -> Optional[str]:
    """
    Paragrafo Henssge con note su Qd e >30h.
    Ritorna HTML <ul><li>...</li></ul>.
    """
    if _safe_is_nan(t_min_visual) or _safe_is_nan(t_max_visual):
        return None

    h1, m1 = _hm_from_hours(t_min_visual)
    h2, m2 = _hm_from_hours(t_max_visual)

    # Se il limite inferiore è 0 → “non oltre X”
    intervallo_txt = (
        i18n.prudent_result_text(
            minimum_text="",
            maximum_text=_fmt_hm_full(h2, m2),
            beyond=False,
            not_over=True,
        )
        if (h1 == 0 and m1 == 0)
        else _fmt_range_hm(h1, m1, h2, m2)
    )

    extra = ""

    if qd_range_status == "mixed":
        extra = i18n.henssge_qd_range_mixed_warning()
    elif qd_range_status == "no_optimal_intermediate":
        extra = i18n.henssge_qd_range_intermediate_warning()
    elif qd_range_status == "all_outside":
        extra = i18n.henssge_qd_outside_warning()
    elif qd_range_status == "all_optimal":
        extra = ""
    elif (
        qd_val is not None and not np.isnan(qd_val)
        and ta_val is not None and not np.isnan(ta_val)
        and t_med_round is not None and not np.isnan(t_med_round)
    ):
        qd_threshold = 0.2 if ta_val <= 23 else 0.5
        if qd_val <= qd_threshold:
            extra = i18n.henssge_qd_outside_warning()
        elif ta_val <= 23 and qd_val < 0.3:
            extra = i18n.henssge_qd_partial_warning()

    return i18n.henssge_detail_paragraph(intervallo_txt, extra)


def paragrafo_potente(
    *,
    mt_ore: Optional[float],
    mt_giorni: Optional[float],
    qd_val: Optional[float],
    ta_val: Optional[float],
    qd_threshold: float
) -> Optional[str]:
    """
    Paragrafo Potente et al. se applicabile. HTML <ul><li>...</li></ul>.
    """
    if (
        mt_ore is None or np.isnan(mt_ore) or
        qd_val is None or np.isnan(qd_val) or
        ta_val is None or np.isnan(ta_val)
    ):
        return None
    if not (qd_val <= qd_threshold):
        return None

    h, m = _hm_from_hours(mt_ore)
    return i18n.potente_paragraph(_fmt_hm_full(h, m), f"{mt_giorni:.1f}")

def paragrafo_raffreddamento_input(
    *,
    isp_dt: Optional[datetime.datetime],
    ta_val: Optional[float],
    tr_val: Optional[float],
    w_val: Optional[float],
    t0_val: Optional[float],
    cf_descr: str
) -> str:
    """
    Paragrafo con riepilogo input Henssge. HTML <ul> nidificata.
    """
    if isp_dt is None:
        orario_isp = None
        data_isp = None
    else:
        orario_isp, data_isp = _fmt_dt(isp_dt)

    ta_txt = f"{ta_val:.1f}" if ta_val is not None else "—"
    tr_txt = f"{tr_val:.1f}" if tr_val is not None else "—"
    w_txt  = f"{w_val:.1f}"  if w_val  is not None else "—"
    t0_txt = f"{t0_val:.1f}" if t0_val is not None else "—"

    return i18n.cooling_input_paragraph(
        inspection_time=orario_isp,
        inspection_date=data_isp,
        ta_text=ta_txt,
        tr_text=tr_txt,
        weight_text=w_txt,
        t0_text=t0_txt,
        correction_description=cf_descr,
    )

def paragrafi_descrizioni_base(
    *,
    testo_macchie: str,
    testo_rigidita: str
) -> List[str]:
    """Ritorna due paragrafi HTML <ul><li>...</li></ul> per macchie e rigidità."""
    return [
        f"<ul><li>{testo_macchie}</li></ul>",
        f"<ul><li>{testo_rigidita}</li></ul>",
    ]

def paragrafi_parametri_aggiuntivi(
    *,
    parametri: Iterable[Dict[str, Any]]
) -> List[str]:
    """
    Per ogni parametro aggiuntivo considerato con 'descrizione' e stato valido,
    produce <ul><li>descrizione</li></ul>.
    """
    out: List[str] = []
    for p in parametri:
        desc = p.get("descrizione")
        if desc and special_description_is_reportable(p):
            out.append(f"<ul><li>{desc}</li></ul>")
    return out

def paragrafo_putrefattive(segnalate: bool) -> Optional[str]:
    """
    Paragrafo standard sui processi putrefattivi. HTML <ul><li>...</li></ul>.
    """
    if not segnalate:
        return None
    return i18n.putrefactive_paragraph()

def avvisi_raffreddamento_henssge(*, t_med_round: Optional[float], qd_val: Optional[float]) -> List[str]:
    """Avvisi testuali relativi al raffreddamento cadaverico."""
    return []

# ------------------------------------------------------------
# Riepilogo parametri usati
# ------------------------------------------------------------

def frase_riepilogo_parametri_usati(labels: List[str]) -> Optional[str]:
    """
    Testo arancione piccolo: “La stima complessiva si basa su…”.
    Fornisci già i label filtrati (niente duplicati Henssge vs Potente).
    """
    if len(labels) == 0:
        return None
    return i18n.parameter_summary(labels)

def frase_qd(
    qd_val: Optional[float],
    ta_val: Optional[float],
    *,
    qd_min: Optional[float] = None,
    qd_max: Optional[float] = None,
    qd_range_status: Optional[str] = None,
) -> Optional[str]:
    """Frase Qd per caso singolo o per l'insieme delle condizioni variabili."""
    if (
        qd_range_status is not None
        and qd_min is not None and not np.isnan(qd_min)
        and qd_max is not None and not np.isnan(qd_max)
    ):
        return i18n.qd_range_summary(
            qd_min_text=f"{qd_min:.3f}",
            qd_max_text=f"{qd_max:.3f}",
            status=qd_range_status,
            single_value=abs(float(qd_max) - float(qd_min)) < 1e-9,
        )

    if qd_val is None or np.isnan(qd_val) or ta_val is None or np.isnan(ta_val):
        return None

    soglia = 0.2 if ta_val <= 23 else 0.5
    if ta_val <= 23:
        if qd_val <= 0.2:
            status = "outside"
        elif qd_val < 0.3:
            status = "intermediate"
        else:
            status = "optimal"
    else:
        status = "outside" if qd_val <= 0.5 else "optimal"

    return i18n.qd_summary(
        qd_text=f"{qd_val:.3f}",
        ambient_at_most_23=ta_val <= 23,
        threshold_text=str(soglia),
        within_limits=status == "optimal",
        status=status,
    )
