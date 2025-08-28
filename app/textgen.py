# -*- coding: utf-8 -*-
# textgen.py — Generazione testi finali e paragrafi descrittivi

from __future__ import annotations
import datetime
from typing import List, Optional, Tuple, Iterable, Dict, Any
import numpy as np

from app.utils_time import split_hours_minutes

# ------------------------------------------------------------
# Utilità testuali
# ------------------------------------------------------------

def _fmt_ore_min(ore_float: float) -> Tuple[int, int, str]:
    """Converte ore decimali in (ore, minuti, label_ora|ore)."""
    h, m = split_hours_minutes(ore_float) or (0, 0)
    return h, m, ("ora" if h == 1 and m == 0 else "ore")

def _fmt_dt(dt: datetime.datetime) -> Tuple[str, str]:
    """Ritorna (HH:MM, dd.mm.YYYY)."""
    return dt.strftime('%H:%M'), dt.strftime('%d.%m.%Y')

def _safe_is_nan(x: Optional[float]) -> bool:
    return x is None or np.isnan(x)

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
    """
    Restituisce la frase conclusiva principale in HTML con intestazione in grassetto.
    Replica la logica: >48 h, limite superiore infinito, 0–X, A–B.
    """
    if _safe_is_nan(comune_inizio) and _safe_is_nan(comune_fine):
        return None

    limite_sup_inf = _safe_is_nan(comune_fine) or comune_fine == inf_hours

    # Caso: Qd basso + inizio > 30h + superiore infinito → “oltre”
    if (
        qd_val is not None and not np.isnan(qd_val) and qd_val < 0.3
        and not _safe_is_nan(comune_inizio) and comune_inizio > 30
        and limite_sup_inf
    ):
        h, m, lbl = _fmt_ore_min(comune_inizio)
        da = isp_dt - datetime.timedelta(hours=comune_inizio)
        hh, dd = _fmt_dt(da)
        if qd_val <= 0.2 and mt_ore is not None and not np.isnan(mt_ore) and mt_ore > 30:
            testo = (
                f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                f"<b>oltre</b> {h} {lbl}{'' if m == 0 else f' {m} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {hh} del {dd}."
            )
        else:
            testo = (
                f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                f"<b>oltre</b> {h} {lbl}{'' if m == 0 else f' {m} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {hh} del {dd}. "
                f"Occorre tener conto che l'affidabilità del metodo di Henssge diminuisce significativamente "
                f"per intervalli superiori a 30 ore dal decesso."
            )
        return f"<p><b>EPOCA DEL DECESSO STIMATA</b><br>{testo}</p>"

    # Caso: limite superiore infinito → “oltre X”
    if limite_sup_inf and not _safe_is_nan(comune_inizio):
        if mt_ore is not None and not np.isnan(mt_ore) and abs(comune_inizio - mt_ore) < 0.25:
            comune_inizio = round(mt_ore)
        h, m, lbl = _fmt_ore_min(comune_inizio)
        da = isp_dt - datetime.timedelta(hours=comune_inizio)
        hh, dd = _fmt_dt(da)
        testo = (
            f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
            f"<b>oltre</b> {h} {lbl}{'' if m == 0 else f' {m} minuti'} "
            f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {hh} del {dd}."
        )
        return f"<p><b>EPOCA DEL DECESSO STIMATA</b><br>{testo}</p>"

    # Caso: 0–X → “non oltre X”
    if not _safe_is_nan(comune_fine) and comune_inizio == 0:
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        da = isp_dt - datetime.timedelta(hours=comune_fine)
        hh2, dd2 = _fmt_dt(da)
        testo = (
            f"La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
            f"consente di stimare che la morte sia avvenuta <b>non oltre</b> "
            f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
            f"prima dei rilievi effettuati durante l’ispezione legale, ovvero successivamente alle ore {hh2} del {dd2}."
        )
        return f"<p><b>EPOCA DEL DECESSO STIMATA</b><br>{testo}</p>"

    # Caso: A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1, lbl1 = _fmt_ore_min(comune_inizio)
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        da = isp_dt - datetime.timedelta(hours=comune_fine)
        aa = isp_dt - datetime.timedelta(hours=comune_inizio)
        hh_da, dd_da = _fmt_dt(da)
        hh_aa, dd_aa = _fmt_dt(aa)
        if da.date() == aa.date():
            testo = (
                f"La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
                f"consente di stimare che la morte sia avvenuta tra circa "
                f"{h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
                f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {hh_da} e le ore {hh_aa} del {dd_da}."
            )
        else:
            testo = (
                f"La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
                f"consente di stimare che la morte sia avvenuta tra circa "
                f"{h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
                f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {hh_da} del {dd_da} e le ore {hh_aa} del {dd_aa}."
            )
        return f"<p><b>EPOCA DEL DECESSO STIMATA</b><br>{testo}</p>"

    return None

def build_secondary_sentence_senza_potente(
    *,
    isp_dt: datetime.datetime,
    inizio_senza_potente: Optional[float],
    fine_senza_potente: Optional[float]
) -> Optional[str]:
    """Frase “Senza considerare Potente…”. HTML semplice."""
    if _safe_is_nan(inizio_senza_potente) or _safe_is_nan(fine_senza_potente):
        return None

    h1, m1, lbl1 = _fmt_ore_min(inizio_senza_potente)
    h2, m2, lbl2 = _fmt_ore_min(fine_senza_potente)

    dt_inizio = isp_dt - datetime.timedelta(hours=fine_senza_potente)
    dt_fine = isp_dt - datetime.timedelta(hours=inizio_senza_potente)
    hh_i, dd_i = _fmt_dt(dt_inizio)
    hh_f, dd_f = _fmt_dt(dt_fine)

    return (
        "Senza considerare lo studio di Potente, la valutazione complessiva consente di stimare che la morte sia avvenuta tra circa "
        f"{h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
        f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
        f"prima dei rilievi, ovvero tra le ore {hh_i} del {dd_i} e le ore {hh_f} del {dd_f}."
    )

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
        hh, dd = _fmt_dt(dt)
        return hh, dd

    # 0–X
    if not _safe_is_nan(comune_fine) and (comune_inizio == 0 or _safe_is_nan(comune_inizio)):
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        hh2, dd2 = _ora_data(comune_fine)
        return (f"<p><b>EPOCA DEL DECESSO STIMATA</b>: "
                f"non oltre {h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
                "prima dei rilievi effettuati durante l’ispezione legale, "
                f"ovvero successivamente alle ore {hh2} del {dd2}.</p>")

    # oltre X
    if limite_sup_inf and not _safe_is_nan(comune_inizio):
        h1, m1, lbl1 = _fmt_ore_min(comune_inizio)
        hh1, dd1 = _ora_data(comune_inizio)
        return (f"<p><b>EPOCA DEL DECESSO STIMATA</b>: "
                f"oltre {h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} "
                "prima dei rilievi effettuati durante l’ispezione legale, "
                f"ovvero prima delle ore {hh1} del {dd1}.</p>")

    # A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1, lbl1 = _fmt_ore_min(comune_inizio)
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        hh_da, dd_da = _ora_data(comune_fine)
        hh_aa, dd_aa = _ora_data(comune_inizio)
        if (isp_dt - datetime.timedelta(hours=comune_fine)).date() == (isp_dt - datetime.timedelta(hours=comune_inizio)).date():
            return (f"<p><b>EPOCA DEL DECESSO STIMATA</b>: "
                    f"tra circa {h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
                    f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
                    "prima dei rilievi effettuati durante l’ispezione legale, "
                    f"ovvero circa tra le ore {hh_da} e le ore {hh_aa} del {dd_da}.</p>")
        else:
            return (f"<p><b>EPOCA DEL DECESSO STIMATA</b>: "
                    f"tra circa {h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
                    f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
                    "prima dei rilievi effettuati durante l’ispezione legale, "
                    f"ovvero circa tra le ore {hh_da} del {dd_da} e le ore {hh_aa} del {dd_aa}.</p>")
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
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        return (f"<p><b>EPOCA DEL DECESSO STIMATA</b>: "
                f"non oltre {h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
                "prima dei rilievi dei dati tanatologici.</p>")

    # oltre X
    if limite_sup_inf and not _safe_is_nan(comune_inizio):
        h1, m1, lbl1 = _fmt_ore_min(comune_inizio)
        return (f"<p><b>EPOCA DEL DECESSO STIMATA</b>: "
                f"oltre {h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} "
                "prima dei rilievi dei dati tanatologici.</p>")

    # A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1, lbl1 = _fmt_ore_min(comune_inizio)
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        return (f"<p><b>EPOCA DEL DECESSO STIMATA</b>: "
                f"tra circa {h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
                f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
                "prima dei rilievi dei dati tanatologici.</p>")
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
        h1, m1, lbl1 = _fmt_ore_min(comune_inizio)
        testo = (
            "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
            f"consente di stimare che la morte sia avvenuta: oltre "
            f"{h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} "
            "prima dei rilievi dei dati tanatologici."
        )
        return f"<p><b>EPOCA DEL DECESSO STIMATA</b><br>{testo}</p>"

    # 0–X
    if not _safe_is_nan(comune_fine) and (comune_inizio == 0 or _safe_is_nan(comune_inizio)):
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        testo = (
            "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
            f"consente di stimare che la morte sia avvenuta: non oltre "
            f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
            "prima dei rilievi dei dati tanatologici."
        )
        return f"<p><b>EPOCA DEL DECESSO STIMATA</b><br>{testo}</p>"

    # A–B
    if not _safe_is_nan(comune_inizio) and not _safe_is_nan(comune_fine):
        h1, m1, lbl1 = _fmt_ore_min(comune_inizio)
        h2, m2, lbl2 = _fmt_ore_min(comune_fine)
        testo = (
            "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
            f"consente di stimare che la morte sia avvenuta: tra circa "
            f"{h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
            f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
            "prima dei rilievi dei dati tanatologici."
        )
        return f"<p><b>EPOCA DEL DECESSO STIMATA</b><br>{testo}</p>"

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
    ta_val: Optional[float]
) -> Optional[str]:
    """
    Paragrafo Henssge con note su Qd e >30h. Ritorna HTML <ul><li>...</li></ul>.
    """
    if _safe_is_nan(t_min_visual) or _safe_is_nan(t_max_visual):
        return None

    h1, m1, lbl1 = _fmt_ore_min(t_min_visual)
    h2, m2, lbl2 = _fmt_ore_min(t_max_visual)

    testo_base = (
        f"Applicando l'equazione di Henssge, è possibile stimare che il decesso sia avvenuto tra circa "
        f"{h1} {lbl1}{'' if m1 == 0 else f' {m1} minuti'} e "
        f"{h2} {lbl2}{'' if m2 == 0 else f' {m2} minuti'} "
        f"prima dei rilievi effettuati al momento dell’ispezione legale."
    )

    extra = []

    if (qd_val is not None and not np.isnan(qd_val) and qd_val < 0.2 and
        t_med_round is not None and not np.isnan(t_med_round)):
        extra.append(
            "<li>"
            f"I valori ottenuti, tuttavia, sono in parte o totalmente fuori dai range ottimali delle equazioni applicabili. "
            f"Il range temporale indicato è stato calcolato, grossolanamente, come pari al ±20% del valore medio ottenuto dalla stima del raffreddamento cadaverico ({t_med_round:.1f} ore), ma tale range è privo di una solida base statistica ed è da ritenersi del tutto indicativo. "
            f"In mancanza di ulteriori dati o interpretazioni, si può presumere che il cadavere fosse ormai in equilibrio termico con l'ambiente. "
            f"Per tale motivo, per la stima dell'epoca del decesso è consigliabile far riferimento principalmente ad altri dati tanatologici."
            "</li>"
        )

    if (qd_val is not None and not np.isnan(qd_val) and qd_val > 0.2 and
        t_med_round is not None and not np.isnan(t_med_round) and t_med_round > 30):
        extra.append(
            "<li>"
            f"La stima media ottenuta dal raffreddamento cadaverico ({t_med_round:.1f} h) è superiore alle 30 ore. "
            f"L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
            "</li>"
        )

    par = f"<ul><li>{testo_base}"
    if extra:
        par += "<ul>" + "".join(extra) + "</ul>"
    par += "</li></ul>"
    return par

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
    if not (qd_val < qd_threshold):
        return None

    return (
        f"<ul><li>Lo studio di Potente et al. permette di stimare grossolanamente l’intervallo minimo post-mortem quando i dati non consentono di ottenere risultati attendibili con il metodo di Henssge. "
        f"Applicandolo al caso specifico, si può ipotizzare che, al momento dell’ispezione legale, fossero trascorse almeno <b>{mt_ore:.0f}</b> ore (≈ {mt_giorni:.1f} giorni) dal decesso.</li></ul>"
    )

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
        # versione senza orario/data
        titolo_temp = "Temperature misurate nel corso dell’ispezione legale:"
    else:
        orario_isp, data_isp = _fmt_dt(isp_dt)
        titolo_temp = f"Temperature misurate nel corso dell’ispezione legale verso le ore {orario_isp} del {data_isp}:"

    ta_txt = f"{ta_val:.1f}" if ta_val is not None else "—"
    tr_txt = f"{tr_val:.1f}" if tr_val is not None else "—"
    w_txt  = f"{w_val:.1f}"  if w_val  is not None else "—"
    t0_txt = f"{t0_val:.1f}" if t0_val is not None else "—"

    return (
        "<ul><li>Per quanto attiene la valutazione del raffreddamento cadaverico, sono stati considerati gli elementi di seguito indicati."
        "<ul>"
        f"<li>{titolo_temp}"
        "<ul>"
        f"<li>Temperatura ambientale: {ta_txt} °C.</li>"
        f"<li>Temperatura rettale: {tr_txt} °C.</li>"
        "</ul>"
        "</li>"
        f"<li>Peso del cadavere misurato: {w_txt} kg.</li>"
        f"<li>Temperatura corporea ipotizzata al momento della morte: {t0_txt} °C.</li>"
        f"<li>Fattore di correzione ipotizzato in base alle condizioni ambientali (per quanto noto): {cf_descr}.</li>"
        "</ul>"
        "</li></ul>"
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
        stato = p.get("stato", "")
        desc = p.get("descrizione")
        if desc and stato not in ("Non valutata", "Non valutabile/non attendibile"):
            out.append(f"<ul><li>{desc}</li></ul>")
    return out

def paragrafo_putrefattive(segnalate: bool) -> Optional[str]:
    """
    Paragrafo standard sui processi putrefattivi. HTML <ul><li>...</li></ul>.
    """
    if not segnalate:
        return None
    return (
        "<ul><li>Per quanto riguarda i processi trasformativi post-mortali (compresi quelli putrefattivi), "
        "la loro insorgenza è influenzata da numerosi fattori, esogeni (ad esempio temperatura ambientale, "
        "esposizione ai fenomeni meteorologici…) ed endogeni (temperatura corporea, infezioni prima del decesso, "
        "presenza di ferite…). Poiché tali processi possono manifestarsi in un intervallo temporale estremamente "
        "variabile, da poche ore a diverse settimane dopo il decesso, la loro valutazione non permette di formulare "
        "ulteriori precisazioni sull’epoca della morte.</li></ul>"
    )

def avvisi_raffreddamento_henssge(*, t_med_round: Optional[float], qd_val: Optional[float]) -> List[str]:
    """
    Ritorna eventuali avvisi testuali (plain text) relativi al raffreddamento cadaverico.
    - Avviso >30h sempre, indipendentemente dalla soglia di Qd.
    """
    out: List[str] = []
    if t_med_round is not None and not np.isnan(t_med_round) and t_med_round > 30:
        out.append(
            f"La stima media ottenuta dal raffreddamento cadaverico ({t_med_round:.1f} h) "
            "è superiore alle 30 ore. L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
        )
    return out

# ------------------------------------------------------------
# Riepilogo parametri usati
# ------------------------------------------------------------

def frase_riepilogo_parametri_usati(labels: List[str]) -> Optional[str]:
    """
    Testo arancione piccolo: “La stima complessiva si basa su…”.
    Fornisci già i label filtrati (niente duplicati Henssge vs Potente).
    """
    n = len(labels)
    if n == 0:
        return None
    if n == 1:
        p = labels[0]
        return f"<p style='color:orange;font-size:small;'>La stima complessiva si basa sul seguente parametro: {p[0].lower() + p[1:]}.</p>"
    join = ', '.join(x[0].lower() + x[1:] for x in labels[:-1])
    join += f" e {labels[-1][0].lower() + labels[-1][1:]}"
    return f"<p style='color:orange;font-size:small;'>La stima complessiva si basa sui seguenti parametri: {join}.</p>"

def frase_qd(qd_val: Optional[float], ta_val: Optional[float]) -> Optional[str]:
    """
    Restituisce una frase con Qd e il confronto con la soglia (0.2 o 0.5 a seconda della T ambiente).
    """
    if qd_val is None or np.isnan(qd_val) or ta_val is None or np.isnan(ta_val):
        return None

    soglia = 0.2 if ta_val <= 23 else 0.5
    condizione_temp = "T. amb ≤ 23 °C" if ta_val <= 23 else "T. amb > 23 °C"

    if qd_val < soglia:
        return (f"<p style='color:orange;font-size:small;'> Nel caso in esame, l'equazione di Henssge per il raffreddamento cadaverico ha Qd = {qd_val:.3f}. "
                f"Tale parametro è inferiore ai limiti ottimali per applicare l'equazione (per {condizione_temp}, Qd deve esser superiore a {soglia}).</p>")
    else:
        return (f"<p style='color:orange;font-size:small;'> Nel caso in esame, l'equazione di Henssge per il raffreddamento cadaverico ha Qd = {qd_val:.3f}. "
                f"Tale parametro rientra nei limiti ottimali per applicare l'equazione (per {condizione_temp}, Qd deve esser superiore a {soglia}).</p>")
