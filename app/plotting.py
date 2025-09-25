# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import matplotlib.pyplot as plt


# Formatter numerico: "7.0" -> "7", "7.5" -> "7.5"
def _fmt(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")

def compute_plot_data(
    *,
    macchie_range: Tuple[float, float] | Tuple[float, float],
    macchie_medi_range: Optional[Tuple[float, float]],
    rigidita_range: Tuple[float, float] | Tuple[float, float],
    rigidita_medi_range: Optional[Tuple[float, float]],
    raffreddamento_calcolabile: bool,
    t_min_raff_henssge: float | float,
    t_max_raff_henssge: float | float,
    t_med_raff_henssge_rounded_raw: float | float,
    Qd_val_check: float | float,
    mt_ore: Optional[float],
    INF_HOURS: float,
    qd_threshold: float,
    extra_params: Optional[List[Dict[str, Any]]] = None,  # <- può contenere "label","start","end","adattato"
) -> Dict[str, Any]:
    """
    Prepara i dati per il grafico. Nessun side-effect. Nessuna dipendenza da Streamlit.
    Restituisce un dict consumato da `render_ranges_plot`.
    """
    # Contenitori paralleli
    labels: List[str] = []
    starts: List[float] = []
    ends: List[float] = []

    # Etichette + range: IPOSTASI
    if macchie_range is not None and not np.isnan(macchie_range[0]):
        if macchie_range[1] < INF_HOURS:
            label_macchie = f"Ipostasi\n({_fmt(macchie_range[0])}–{_fmt(macchie_range[1])} h)"
            end_val = macchie_range[1]
        else:
            label_macchie = f"Ipostasi\n(≥ {_fmt(macchie_range[0])} h)"
            end_val = INF_HOURS
        labels.append(label_macchie)
        starts.append(macchie_range[0])
        ends.append(end_val)

    # Etichette + range: RIGIDITÀ
    if rigidita_range is not None and not np.isnan(rigidita_range[0]):
        if rigidita_range[1] < INF_HOURS:
            label_rigidita = f"Rigor\n({_fmt(rigidita_range[0])}–{_fmt(rigidita_range[1])} h)"
            end_val = rigidita_range[1]
        else:
            label_rigidita = f"Rigor\n(≥ {_fmt(rigidita_range[0])} h)"
            end_val = INF_HOURS
        labels.append(label_rigidita)
        starts.append(rigidita_range[0])
        ends.append(end_val)

    # Parametri extra (altri range orari da mostrare come barre)
    if extra_params:
        for e in extra_params:
            try:
                lab = str(e.get("label", "Parametro"))
                if e.get("adattato", False):
                    lab += "*"
                s = float(e.get("start", np.nan))
                ed = e.get("end", np.nan)
            except Exception:
                continue
            if np.isnan(s):
                continue
            if np.isnan(ed) or ed >= INF_HOURS:
                lbl = f"{lab}\n(≥ {_fmt(s)} h)"
                end_val = INF_HOURS
            else:
                end_val = float(ed)
                lbl = f"{lab}\n({_fmt(s)}–{_fmt(end_val)} h)"
            labels.append(lbl)
            starts.append(float(s))
            ends.append(end_val)

    # Etichette + range: RAFFREDDAMENTO
    raffreddamento_idx: Optional[int] = None
    t_min_raff_visualizzato = np.nan
    t_max_raff_visualizzato = np.nan

    # Potente attivo se Qd sotto soglia
    potente_attivo = (not np.isnan(Qd_val_check)) and (Qd_val_check < qd_threshold)
    # Mostra Henssge solo se calcolabile e Potente NON attivo
    mostra_raffreddamento = bool(raffreddamento_calcolabile) and (not potente_attivo)

    # Flag iniziali
    raff_only_lower = False
    raff_over_48 = False
    raff_only_lower_start: Optional[float] = None

    if mostra_raffreddamento:
        t_min_raff_visualizzato = t_min_raff_henssge
        t_max_raff_visualizzato = t_max_raff_henssge

        raff_only_lower = (not np.isnan(Qd_val_check)) and (Qd_val_check < qd_threshold)
        raff_over_48 = False  # mantieni se in futuro servirà il caso >48

        if raff_only_lower:
            maggiore_di_valore = (
                float(mt_ore) if (mt_ore is not None and not np.isnan(mt_ore))
                else float(t_min_raff_henssge)
            )
            label_h = f"Raffreddamento\n(> {_fmt(maggiore_di_valore)} h)"
            raff_only_lower_start = maggiore_di_valore
        else:
            label_h = f"Raffreddamento\n({_fmt(t_min_raff_henssge)}–{_fmt(t_max_raff_henssge)} h)"

        labels.append(label_h)
        starts.append(t_min_raff_henssge)
        ends.append(t_max_raff_henssge)
        raffreddamento_idx = len(labels) - 1

    # Calcolo cap e coda
    LINE_W = 6
    DASH_LS = (0, (2, 1))
    TAIL_FACTOR = 1.20
    DEFAULT_CAP_IF_NO_FINITE = 72.0

    finite_ends_all = [e for e in ends if not np.isnan(e) and e < INF_HOURS]
    cap_base = max(finite_ends_all) if finite_ends_all else DEFAULT_CAP_IF_NO_FINITE

    # Inizi dei segmenti infiniti blu
    infinite_starts_blue = [
        s for s, e in zip(starts, ends)
        if not np.isnan(s) and (np.isnan(e) or e >= INF_HOURS)
    ]

    # Inizi verdi speciali per raffreddamento (proseguono a ∞ in verde)
    special_inf_starts_green: List[float] = []
    if mostra_raffreddamento and (raffreddamento_idx is not None):
        if raff_only_lower and (raff_only_lower_start is not None):
            special_inf_starts_green.append(float(raff_only_lower_start))
        if raff_over_48:
            special_inf_starts_green.append(48.0)

    if infinite_starts_blue or special_inf_starts_green:
        tail_base = max([cap_base] + infinite_starts_blue + special_inf_starts_green)
    else:
        tail_base = cap_base
    tail_end = tail_base * TAIL_FACTOR

    # Mediane verdi per ipostasi/rigidità
    medians: Dict[str, Optional[Tuple[float, float]]] = {
        "Macchie ipostatiche": None,
        "Rigidità cadaverica": None,
    }
    if macchie_medi_range is not None:
        medians["Macchie ipostatiche"] = macchie_medi_range
    if rigidita_medi_range is not None:
        medians["Rigidità cadaverica"] = rigidita_medi_range

    # Mappatura y in ordine (coincidente con labels)
    y_map = {lbl.split("\n", 1)[0]: idx for idx, lbl in enumerate(labels)}

    # Dimensione figura dinamica
    num_params_grafico = len(labels)
    figsize = (10, max(2, 1.5 + 0.5 * num_params_grafico))

    style_flags = dict(
        raff_only_lower=raff_only_lower if mostra_raffreddamento else False,
        raff_only_lower_start=raff_only_lower_start if mostra_raffreddamento else None,
        raff_over_48=raff_over_48 if mostra_raffreddamento else False,
        line_w=LINE_W,
        dash_ls=DASH_LS,
    )

    return dict(
        labels=labels,
        starts=starts,
        ends=ends,
        medians=medians,
        raffreddamento_idx=raffreddamento_idx,
        tail_end=tail_end,
        cap_base=cap_base,
        style_flags=style_flags,
        y_map=y_map,
        figsize=figsize,
        t_min_raff_visualizzato=t_min_raff_visualizzato,
        t_max_raff_visualizzato=t_max_raff_visualizzato,
        INF_HOURS=INF_HOURS,
        extra_params=extra_params,
    )



    


def render_ranges_plot(data: Dict[str, Any]) -> plt.Figure:
    """
    Disegna il grafico dei range usando esclusivamente `data` di compute_plot_data.
    Non aggiunge linee rosse dell’intersezione: quelle restano nel main.
    """
    labels: List[str] = data["labels"]
    starts: List[float] = data["starts"]
    ends: List[float] = data["ends"]
    medians: Dict[str, Optional[Tuple[float, float]]] = data["medians"]
    raff_idx: Optional[int] = data["raffreddamento_idx"]
    tail_end: float = data["tail_end"]
    cap_base: float = data["cap_base"]
    style = data["style_flags"]
    INF_HOURS: float = data["INF_HOURS"]

    t_min_raff_visualizzato = data["t_min_raff_visualizzato"]
    t_max_raff_visualizzato = data["t_max_raff_visualizzato"]

    LINE_W = style["line_w"]
    DASH_LS = style["dash_ls"]

    fig, ax = plt.subplots(figsize=data["figsize"])

        


    # 1) Segmenti verdi speciali per RAFFREDDAMENTO (sotto)
    if raff_idx is not None:
        raff_over_48 = style.get("raff_over_48", False)
        raff_only_lower = style.get("raff_only_lower", False)
        raff_only_lower_start = style.get("raff_only_lower_start")

        def _draw_green_segment(y: int, start: float):
            solid_from = max(0.0, start)
            solid_to = max(solid_from, cap_base)
            if solid_from < tail_end and solid_to > solid_from:
                ax.hlines(y, solid_from, min(solid_to, tail_end),
                          color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1)
            dash_start = max(solid_to, solid_from)
            if tail_end > dash_start:
                ax.hlines(y, dash_start, tail_end,
                          color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1, linestyle=DASH_LS)

        if raff_only_lower and (raff_only_lower_start is not None):
            _draw_green_segment(raff_idx, float(raff_only_lower_start))
        if raff_over_48:
            _draw_green_segment(raff_idx, 48.0)

    # 2) Linee blu base (tutti i range)
    for i, (s, e) in enumerate(zip(starts, ends)):
        if np.isnan(s):
            continue
        is_infinite = (np.isnan(e) or e >= INF_HOURS)
        if not is_infinite:
            ax.hlines(i, s, e, color='steelblue', linewidth=LINE_W, zorder=2)
        else:
            solid_to = max(s, cap_base)
            if solid_to > s and s < tail_end:
                ax.hlines(i, s, min(solid_to, tail_end), color='steelblue', linewidth=LINE_W, zorder=2)
            dash_start = max(solid_to, s)
            if tail_end > dash_start:
                ax.hlines(i, dash_start, tail_end, color='steelblue', linewidth=LINE_W, zorder=2, linestyle=DASH_LS)

    # 3) Mediane verdi per ipostasi/rigidità (sopra)
    # Macchie
    if "Macchie ipostatiche" in medians and medians["Macchie ipostatiche"] is not None:
        y = next((idx for idx, lbl in enumerate(labels) if lbl.startswith("Ipostasi")), None)
        if y is not None:
            m_s, m_e = medians["Macchie ipostatiche"]
            is_inf = (m_e is None) or (np.isnan(m_e)) or (m_e >= INF_HOURS)
            if not is_inf:
                ax.hlines(y, m_s, m_e, color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=3)
            else:
                solid_to = max(m_s, cap_base)
                if solid_to > m_s and m_s < tail_end:
                    ax.hlines(y, m_s, min(solid_to, tail_end), color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=3)
                dash_start = max(solid_to, m_s)
                if tail_end > dash_start:
                    ax.plot([dash_start, tail_end], [y, y],
                            color='mediumseagreen', linewidth=LINE_W, alpha=1.0, linestyle=DASH_LS, zorder=3)

    # Rigidità
    if "Rigidità cadaverica" in medians and medians["Rigidità cadaverica"] is not None:
        y = next((idx for idx, lbl in enumerate(labels) if lbl.startswith("Rigor")), None)
        if y is not None:
            r_s, r_e = medians["Rigidità cadaverica"]
            is_inf = (r_e is None) or (np.isnan(r_e)) or (r_e >= INF_HOURS)
            if not is_inf:
                ax.hlines(y, r_s, r_e, color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=3)
            else:
                solid_to = max(r_s, cap_base)
                if solid_to > r_s and r_s < tail_end:
                    ax.hlines(y, r_s, min(solid_to, tail_end), color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=3)
                dash_start = max(solid_to, r_s)
                if tail_end > dash_start:
                    ax.plot([dash_start, tail_end], [y, y],
                            color='mediumseagreen', linewidth=LINE_W, alpha=1.0, linestyle=DASH_LS, zorder=3)

    # Marker corto verde del punto medio raffreddamento (solo se NON stiamo facendo tratteggiare all'infinito)
    if raff_idx is not None:
        raff_over_48 = style.get("raff_over_48", False)
        raff_only_lower = style.get("raff_only_lower", False)
        if (not raff_over_48) and (not raff_only_lower):
            if not (np.isnan(t_min_raff_visualizzato) or np.isnan(t_max_raff_visualizzato)):
                pm = (t_min_raff_visualizzato + t_max_raff_visualizzato) / 2.0
                off = 0.1
                if (pm - off) < tail_end:
                    ax.hlines(raff_idx, max(0, pm - off), min(tail_end, pm + off),
                              color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=3)

    # Assi, griglia, etichette
    ax.set_xlim(0, tail_end)
    ax.margins(x=0)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=15)
    ax.invert_yaxis()
    ax.set_xlabel("Ore dal decesso")
    ax.grid(True, axis='x', linestyle=':', alpha=0.6)

    plt.tight_layout()
    return fig
