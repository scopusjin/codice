# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import matplotlib.pyplot as plt


def compute_plot_data(
    *,
    macchie_range: Tuple[float, float] | Tuple[float, float],
    macchie_medi_range: Optional[Tuple[float, float]],
    rigidita_range: Tuple[float, float] | Tuple[float, float],
    rigidita_medi_range: Optional[Tuple[float, float]],
    raffreddamento_calcolabile: bool,
    t_min_raff_hensge: float | float,
    t_max_raff_hensge: float | float,
    t_med_raff_hensge_rounded_raw: float | float,
    Qd_val_check: float | float,
    mt_ore: Optional[float],
    INF_HOURS: float,
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
            label_macchie = f"Ipostasi\n({macchie_range[0]:.1f}–{macchie_range[1]:.1f} h)"
            end_val = macchie_range[1]
        else:
            label_macchie = f"Ipostasi\n(≥ {macchie_range[0]:.1f} h)"
            end_val = INF_HOURS
        labels.append(label_macchie)
        starts.append(macchie_range[0])
        ends.append(end_val)

    # Etichette + range: RIGIDITÀ
    if rigidita_range is not None and not np.isnan(rigidita_range[0]):
        if rigidita_range[1] < INF_HOURS:
            label_rigidita = f"Rigor\n({rigidita_range[0]:.1f}–{rigidita_range[1]:.1f} h)"
            end_val = rigidita_range[1]
        else:
            label_rigidita = f"Rigor\n(≥ {rigidita_range[0]:.1f} h)"
            end_val = INF_HOURS
        labels.append(label_rigidita)
        starts.append(rigidita_range[0])
        ends.append(end_val)

    # Etichette + range: RAFFREDDAMENTO
    raffreddamento_idx: Optional[int] = None
    t_min_raff_visualizzato = np.nan
    t_max_raff_visualizzato = np.nan

    if raffreddamento_calcolabile:
        t_min_raff_visualizzato = t_min_raff_hensge
        t_max_raff_visualizzato = t_max_raff_hensge

        # Flag condizioni speciali (identiche alla logica del main)
        raff_only_lower = (not np.isnan(Qd_val_check)) and (Qd_val_check < 0.2)
        raff_over_30 = (
            (not np.isnan(Qd_val_check)) and
            (Qd_val_check > 0.2) and
            (t_med_raff_hensge_rounded_raw is not None) and
            (t_med_raff_hensge_rounded_raw > 30)
        )

        if raff_only_lower:
            # Mostra etichetta con “> … h” e anche il range t_min–t_max come nel main
            maggiore_di_valore = t_min_raff_hensge
            if mt_ore is not None and not np.isnan(mt_ore):
                maggiore_di_valore = float(round(mt_ore))
                label_h = f"Raffreddamento\n(> {maggiore_di_valore:.0f} h)"
            else:
                label_h = (
                    f"Raffreddamento\n(> {maggiore_di_valore:.1f} h)\n"
                    f"({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"
                )
        elif raff_over_30:
            maggiore_di_valore = 30.0
            if mt_ore is not None and not np.isnan(mt_ore):
                maggiore_di_valore = float(round(mt_ore))
                label_h = f"Raffreddamento\n(> {maggiore_di_valore:.0f} h)"
            else:
                label_h = (
                    f"Raffreddamento\n(> {maggiore_di_valore:.1f} h)\n"
                    f"({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"
                )
        else:
            label_h = f"Raffreddamento\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"

        labels.append(label_h)
        starts.append(t_min_raff_hensge)
        ends.append(t_max_raff_hensge)
        raffreddamento_idx = len(labels) - 1
    else:
        raff_only_lower = False
        raff_over_30 = False

    # Calcolo cap e coda come nel main
    LINE_W = 6
    DASH_LS = (0, (2, 1))  # per referenza; usati in render
    TAIL_FACTOR = 1.20
    DEFAULT_CAP_IF_NO_FINITE = 72.0

    finite_ends_all = [e for e in ends if not np.isnan(e) and e < INF_HOURS]
    cap_base = max(finite_ends_all) if finite_ends_all else DEFAULT_CAP_IF_NO_FINITE

    # Inizi dei segmenti infiniti blu
    infinite_starts_blue = [
        s for s, e in zip(starts, ends)
        if not np.isnan(s) and (np.isnan(e) or e >= INF_HOURS)
    ]

    # Inizi verdi speciali per raffreddamento
    special_inf_starts_green: List[float] = []
    if raffreddamento_calcolabile and raffreddamento_idx is not None:
        if mt_ore is not None and not np.isnan(mt_ore):
            special_inf_starts_green.append(float(mt_ore))
        if (not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and
                t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30):
            special_inf_starts_green.append(30.0)

    if infinite_starts_blue or special_inf_starts_green:
        tail_base = max([cap_base] + infinite_starts_blue + special_inf_starts_green)
    else:
        tail_base = cap_base
    tail_end = tail_base * TAIL_FACTOR

    # Mediane verdi per ipostasi/rigidità (copiate dal main: stessa semantica)
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

    # Dimensione figura dinamica (identica formula del main)
    num_params_grafico = len(labels)
    figsize = (10, max(2, 1.5 + 0.5 * num_params_grafico))

    style_flags = dict(
        raff_only_lower=raff_only_lower,
        raff_over_30=raff_over_30,
        potente_from=(float(mt_ore) if (mt_ore is not None and not np.isnan(mt_ore)) else None),
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
        potente_from = style.get("potente_from")
        raff_over_30 = style.get("raff_over_30", False)

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

        if potente_from is not None:
            _draw_green_segment(raff_idx, float(potente_from))
        if raff_over_30:
            _draw_green_segment(raff_idx, 30.0)

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

    # Marker corto verde del punto medio raffreddamento (solo se non segmenti speciali)
    if raff_idx is not None:
        potente_from = style.get("potente_from")
        raff_over_30 = style.get("raff_over_30", False)
        if potente_from is None and not raff_over_30:
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
    ax.set_xlabel("Ore dal decesso")
    ax.grid(True, axis='x', linestyle=':', alpha=0.6)

    plt.tight_layout()
    return fig
