# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.transforms import offset_copy

from app.language import presentation_i18n as i18n


# Formatter numerico: "7.0" -> "7", "7.5" -> "7.5"
def _fmt(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def _hours_range(lo: float, hi: float, inf_hours: float) -> str:
    if not np.isfinite(lo):
        return i18n.ui_text("plot.no_estimate")
    if not np.isfinite(hi) or hi >= inf_hours:
        return f"≥ {_fmt(lo)} h"
    return f"{_fmt(lo)}–{_fmt(hi)} h"


def compute_plot_data(
    *,
    macchie_range: Tuple[float, float],
    macchie_medi_range: Optional[Tuple[float, float]],
    rigidita_range: Tuple[float, float],
    rigidita_medi_range: Optional[Tuple[float, float]],
    raffreddamento_calcolabile: bool,
    t_min_raff_henssge: float,
    t_max_raff_henssge: float,
    t_med_raff_henssge_rounded_raw: float,
    Qd_val_check: float,
    mt_ore: Optional[float],
    INF_HOURS: float,
    qd_threshold: float,
    extra_params: Optional[List[Dict[str, Any]]] = None,  # può contenere: label,start,end,adattato,is_potente
    scenario_ranges: tuple[tuple[float, float] | None, ...] = (),
) -> Dict[str, Any]:
    """
    Prepara i dati per il grafico. Nessun side-effect. Nessuna dipendenza da Streamlit.
    Restituisce un dict consumato da `render_ranges_plot`.
    """
    # Contenitori paralleli
    labels: List[str] = []
    starts: List[float] = []
    ends: List[float] = []
    livor_label = i18n.ui_text("plot.livor")
    rigor_label = i18n.ui_text("plot.rigor")
    cooling_label = i18n.ui_text("plot.cooling")
    scenario_row = None

    # Etichette + range: IPOSTASI
    if macchie_range is not None and not np.isnan(macchie_range[0]):
        if macchie_range[1] < INF_HOURS:
            label_macchie = f"{livor_label}\n({_fmt(macchie_range[0])}–{_fmt(macchie_range[1])} h)"
            end_val = macchie_range[1]
        else:
            label_macchie = f"{livor_label}\n(≥ {_fmt(macchie_range[0])} h)"
            end_val = INF_HOURS
        labels.append(label_macchie)
        starts.append(macchie_range[0])
        ends.append(end_val)

    # Etichette + range: RIGIDITÀ
    if rigidita_range is not None and not np.isnan(rigidita_range[0]):
        if rigidita_range[1] < INF_HOURS:
            label_rigidita = f"{rigor_label}\n({_fmt(rigidita_range[0])}–{_fmt(rigidita_range[1])} h)"
            end_val = rigidita_range[1]
        else:
            label_rigidita = f"{rigor_label}\n(≥ {_fmt(rigidita_range[0])} h)"
            end_val = INF_HOURS
        labels.append(label_rigidita)
        starts.append(rigidita_range[0])
        ends.append(end_val)

    # Parametri extra (altri range orari da mostrare come barre)
    _extra = list(extra_params) if extra_params else []
    extra_rows = [None] * len(_extra)
    if _extra:
        for pos, e in enumerate(_extra):
            try:
                lab = str(e.get("label", i18n.ui_text("plot.generic_parameter")))
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
            extra_rows[pos] = len(labels)
            if e.get("is_potente") and scenario_ranges:
                scenario_row = len(labels)
            labels.append(lbl)
            starts.append(float(s))
            ends.append(end_val)

    # Gate: Potente presente se è stato aggiunto come extra con flag is_potente
    potente_present = any(bool(e.get("is_potente")) for e in _extra)

    # Etichette + range: RAFFREDDAMENTO (Henssge) solo se Potente assente
    raffreddamento_idx: Optional[int] = None
    t_min_raff_visualizzato = np.nan
    t_max_raff_visualizzato = np.nan

    raff_only_lower = False
    raff_only_lower_start = None
    if raffreddamento_calcolabile and not potente_present and scenario_ranges:
        scenario_row = len(labels)
        lo = t_min_raff_henssge if any(r is not None for r in scenario_ranges) else np.nan
        labels.append(f"{cooling_label}\n({_hours_range(lo, t_max_raff_henssge, INF_HOURS)})")
        starts.append(lo)
        ends.append(t_max_raff_henssge)
    elif raffreddamento_calcolabile and not potente_present:
        t_min_raff_visualizzato = t_min_raff_henssge
        t_max_raff_visualizzato = t_max_raff_henssge

        # Flag condizioni speciali
        raff_only_lower = (not np.isnan(Qd_val_check)) and (Qd_val_check < qd_threshold)

        if raff_only_lower:
            maggiore_di_valore = (
                float(mt_ore) if (mt_ore is not None and not np.isnan(mt_ore))
                else float(t_min_raff_henssge)
            )
            label_h = f"{cooling_label}\n(> {_fmt(maggiore_di_valore)} h)"
            raff_only_lower_start = maggiore_di_valore
        else:
            label_h = f"{cooling_label}\n({_fmt(t_min_raff_henssge)}–{_fmt(t_max_raff_henssge)} h)"
            raff_only_lower_start = None

        labels.append(label_h)
        starts.append(raff_only_lower_start if raff_only_lower else t_min_raff_henssge)
        ends.append(np.inf if raff_only_lower else t_max_raff_henssge)
        raffreddamento_idx = len(labels) - 1

    # Calcolo cap e coda
    LINE_W = 6
    DASH_LS = (0, (2, 1))
    TAIL_FACTOR = 1.20
    DEFAULT_CAP_IF_NO_FINITE = 72.0

    plotted_intervals = list(zip(starts, ends))
    if scenario_row is not None:
        plotted_intervals.extend(interval for interval in scenario_ranges if interval is not None)
    finite_ends_all = [e for _, e in plotted_intervals if not np.isnan(e) and e < INF_HOURS]
    cap_base = max(finite_ends_all) if finite_ends_all else DEFAULT_CAP_IF_NO_FINITE

    # Inizi dei segmenti infiniti blu
    infinite_starts_blue = [
        s for s, e in plotted_intervals
        if not np.isnan(s) and (np.isnan(e) or e >= INF_HOURS)
    ]

    tail_base = max([cap_base, *infinite_starts_blue])
    tail_end = tail_base * (TAIL_FACTOR if infinite_starts_blue else 1.05)
    if tail_end <= 0:
        tail_end = 1.0

    # Mappatura y in ordine (coincidente con labels)
    y_map = {lbl.split("\n", 1)[0]: idx for idx, lbl in enumerate(labels)}

    style_flags = dict(
        raff_only_lower=raff_only_lower,
        raff_only_lower_start=raff_only_lower_start,
        line_w=LINE_W,
        dash_ls=DASH_LS,
    )

    return dict(
        labels=labels,
        starts=starts,
        ends=ends,
        raffreddamento_idx=raffreddamento_idx,
        tail_end=tail_end,
        cap_base=cap_base,
        style_flags=style_flags,
        y_map=y_map,
        t_min_raff_visualizzato=t_min_raff_visualizzato,
        t_max_raff_visualizzato=t_max_raff_visualizzato,
        INF_HOURS=INF_HOURS,
        extra_params=_extra,
        extra_rows=extra_rows,
        scenario_row=scenario_row,
        scenario_ranges=scenario_ranges,
    )



def _scenario_labels(scenarios):
    """Keep the applied order so each key describes its own thin line."""
    if len(scenarios) != 2:
        return [i18n.ui_text("plot.scenario", number=i) for i in (1, 2)]
    different_temperatures = scenarios[0]["temperature"] != scenarios[1]["temperature"]
    labels = []
    for scenario in scenarios:
        lo, hi = scenario["range"]
        fc = f"{lo:.2f}" if lo == hi else f"{lo:.2f}–{hi:.2f}"
        label = i18n.ui_text("plot.cooling_factor", fc=fc)
        if different_temperatures:
            temperature = float(scenario["temperature"])
            # Fields accept hundredths as well as tenths.
            value = str(temperature)
            label += i18n.ui_text("plot.ambient_suffix", temperature=value)
        labels.append(label)
    return labels


def render_ranges_plot(data: Dict[str, Any], *, mobile: bool = False, scenarios=(),
                       common_range=None) -> plt.Figure:
    labels = data["labels"]
    scenario_row = data["scenario_row"]
    tail, cap = data["tail_end"], data["cap_base"]
    inf_hours = data["INF_HOURS"]
    width = data["style_flags"]["line_w"]
    dashed = data["style_flags"]["dash_ls"]
    blue, red = "#497da8", "#ad5352"
    nrows = len(labels)
    height = 1.55 + .52 * nrows + (.54 if scenario_row is not None else 0)
    fig, ax = plt.subplots(figsize=(5.6 if mobile else 8.0, height), layout="constrained")

    for row, (lo, hi) in enumerate(zip(data["starts"], data["ends"])):
        if not np.isfinite(lo):
            continue
        if np.isfinite(hi) and hi < inf_hours:
            ax.hlines(row, lo, hi, color=blue, linewidth=width, zorder=2)
        else:
            # Draw the open end beyond the last finite bound with a dashed line.
            split = max(lo, cap)
            if lo < split:
                ax.hlines(row, lo, split, color=blue, linewidth=width, zorder=2)
            ax.hlines(row, split, tail, color=blue, linewidth=width, linestyle=dashed, zorder=2)

    handles = []
    if scenario_row is not None:
        for interval, name, color, offset in zip(
            data["scenario_ranges"], _scenario_labels(scenarios),
            ("#244e72", "#a15a26"), (-6.0, -10.5), strict=True
        ):
            if interval is None:
                separator = "\n" if mobile else " "
                name += f"{separator}({i18n.ui_text('plot.no_estimate')})"
                line, = ax.plot([], [], linestyle="none", label=name)
            else:
                lo, hi = interval
                open_end = not np.isfinite(hi) or hi >= inf_hours
                transform = offset_copy(ax.transData, fig=fig, y=offset, units="points")
                line, = ax.plot([lo, tail if open_end else hi], [scenario_row, scenario_row],
                                color=color, linewidth=2.4, linestyle=dashed if open_end else "solid",
                                solid_capstyle="butt", transform=transform, label=name)
            handles.append(line)

    ax.set_xlim(0, tail)
    ax.set_ylim(nrows - .43, -.60)
    names_and_hours = [label.rsplit("\n", 1) for label in labels]
    ax.set_yticks(range(nrows), [hours for _, hours in names_and_hours],
                  fontsize=10 if mobile else 11, va="top")
    ax.tick_params(axis="y", length=0, pad=5, colors="#526471")
    for row, (name, _) in enumerate(names_and_hours):
        ax.annotate(name, (0, row), xycoords=ax.get_yaxis_transform(), xytext=(-5, 1),
                    textcoords="offset points", ha="right", va="bottom", fontweight="bold",
                    color="#182a37", fontsize=11.5 if mobile else 13)
    ax.tick_params(axis="x", length=0, pad=4, labelsize=10 if mobile else 11, colors="#526471")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6 if mobile else 7, min_n_ticks=4, steps=[1, 2, 2.5, 5, 10]))
    ax.ticklabel_format(axis="x", useLocale=False)
    ax.set_xlabel(i18n.ui_text("plot.hours_since_death"), fontsize=11 if mobile else 12, color="#182a37")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#a2afb7")
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#dce3e7", linewidth=.65)

    if common_range is not None:
        lo, hi = common_range
        ax.axvline(lo, color=red, linestyle=(0, (3, 3)), linewidth=1, zorder=1)
        center = lo
        if np.isfinite(hi) and hi > lo:
            ax.axvline(hi, color=red, linestyle=(0, (3, 3)), linewidth=1, zorder=1)
            ax.plot([lo, hi], [1, 1], transform=ax.get_xaxis_transform(), color=red,
                    linewidth=1, solid_capstyle="butt", clip_on=False)
            center = (lo + hi) / 2
        # Keep the caption inside the graph when both limits are near one edge.
        ax.text(np.clip(center / tail, .23, .77), 1.025, i18n.ui_text("plot.common_interval"),
                ha="center", va="bottom", transform=ax.transAxes, color=red, fontsize=11)
    if handles:
        fig.legend(handles=handles, loc="outside lower center", frameon=False, alignment="left",
                   fontsize=10.5 if mobile else 11.5, handlelength=2, handletextpad=.6,
                   labelspacing=.35, borderaxespad=.15)
    return fig
