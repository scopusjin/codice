"""Replay Henssge 1981 table 3, then assess our separate inverse extension.

Run from the repository root: python -m research.fc_two_phase.compare
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

from research.fc_two_phase.model import Inputs, late_phase_elapsed, reconstruct, single_phase_hours
from research.fc_two_phase.reference import SOURCE_HASHES

ROOT = Path(__file__).parent


def source_rows() -> list[dict]:
    with (ROOT / "table3_case28.csv").open(newline="") as stream:
        return [{"hours_since_death": float(r["hours_since_death"]),
                 "rectal_c": float(r["rectal_c"]),
                 "published_phase2_hours": float(r["published_phase2_hours"]),
                 "parenthesized_in_source": r["parenthesized_in_source"] == "true"}
                for r in csv.DictReader(stream)]


def published_grid(hours: float) -> float:
    """Next 0.2-hour step reproduces the printed values (not clinical rounding)."""
    return math.ceil((hours-1e-12)/0.2)*0.2


def compare() -> tuple[list[dict], dict]:
    rows = []
    for source in source_rows():
        duration = source["hours_since_death"] - 22
        inputs = Inputs(source["rectal_c"], 12.4, 65, 1, .75, duration)
        # Replay uses the measured switch temperature and printed rounded B.
        replay = late_phase_elapsed(source["rectal_c"], 20.3, 12.4, -.0845)
        # Extension uses only the later measurement, FCs and known phase duration.
        result = reconstruct(inputs)
        row = {**source, "known_phase2_hours": duration,
               "replay_phase2_raw_hours": replay,
               "replay_phase2_grid_hours": round(published_grid(replay), 1),
               "reconstruction_status": result.status,
               "transition_reconstructed_c": result.transition_c,
               "omitted_term_fraction": result.fast_term_fraction,
               "reconstructed_total_hours": result.total_hours,
               "reconstruction_error_hours": None if result.total_hours is None else result.total_hours-source["hours_since_death"],
               "constant_fc_before_hours": single_phase_hours(source["rectal_c"], inputs, 1),
               "constant_fc_after_hours": single_phase_hours(source["rectal_c"], inputs, .75)}
        row["constant_fc_before_error_hours"] = row["constant_fc_before_hours"]-source["hours_since_death"]
        row["constant_fc_after_error_hours"] = row["constant_fc_after_hours"]-source["hours_since_death"]
        rows.append(row)
    retained = [r for r in rows if not r["parenthesized_in_source"] and r["reconstructed_total_hours"] is not None]
    summaries = {}
    for label, key in [("two_phase_extension", "reconstruction_error_hours"),
                       ("constant_fc_before", "constant_fc_before_error_hours"),
                       ("constant_fc_after", "constant_fc_after_error_hours")]:
        errors = [r[key] for r in retained]
        summaries[label] = {"n_measurements": len(errors), "mean_error_hours": mean(errors),
                            "mean_absolute_error_hours": mean(abs(v) for v in errors),
                            "min_error_hours": min(errors), "max_error_hours": max(errors)}
    summary = {
        "source": "Henssge 1981, Z Rechtsmed 87:147-178, table 3 p.157; equation III pp.159-162",
        "doi": "10.1007/BF00204763", "reference_commit": "ed1780de025d6ac8eb887d97ec10cb61e64f1263",
        "reference_source_sha256": SOURCE_HASHES,
        "source_data_sha256": hashlib.sha256((ROOT / "table3_case28.csv").read_bytes()).hexdigest(),
        "independent_bodies": 1, "replayed_rows": len(rows),
        "reproduced_printed_rows": sum(abs(r["replay_phase2_grid_hours"]-r["published_phase2_hours"]) < 1e-9 for r in rows),
        "fast_term_gate": .01, "minimum_rectal_ambient_difference_c": 2,
        "comparison": summaries,
        "suppressed_rows": [{"hours_since_death": r["hours_since_death"], "reason": r["reconstruction_status"]}
                            for r in rows if r["reconstructed_total_hours"] is None],
        "limitations": ["Repeated measurements on one body, not independent validation cases.",
                        "The inverse transition-temperature reconstruction is our extension, not the paper's validated casework procedure.",
                        "The 1% fast-term gate is a selected numerical screen, not a published clinical threshold.",
                        "No confidence interval and no equivalent FC to apply in the app.",
                        "The prototype remains completely disconnected from Streamlit."]}
    return rows, summary


def main() -> None:
    rows, summary = compare()
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    with (output / "case28_comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    plot_comparison(rows, output)
    print(json.dumps(summary, indent=2, allow_nan=False))


def plot_comparison(rows: list[dict], output: Path) -> None:
    """Descriptive plot: only the same 16 observations used in the comparison."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["svg.hashsalt"] = "henssge-two-phase-case28"
    plt.rcParams["svg.fonttype"] = "none"
    retained = [r for r in rows if not r["parenthesized_in_source"] and r["reconstructed_total_hours"] is not None]
    fig, axis = plt.subplots(figsize=(9, 5))
    for label, key, color in [("Due fasi (sperimentale)", "reconstruction_error_hours", "#215fa8"),
                              ("FC iniziale 1 costante", "constant_fc_before_error_hours", "#b56116"),
                              ("FC finale 0,75 costante", "constant_fc_after_error_hours", "#70767d")]:
        axis.plot([r["known_phase2_hours"] for r in retained], [r[key] for r in retained],
                  label=label, color=color, marker="o", markersize=3)
    axis.axhline(0, color="#333333", linewidth=.8, linestyle="--")
    axis.set(xlabel="Ore trascorse dall'attivazione della ventilazione",
             ylabel="PMI stimato - PMI noto (ore)",
             title="Henssge 1981, caso 28: errore rispetto al tempo noto")
    axis.grid(alpha=.15)
    axis.legend(loc="best", frameon=False)
    fig.text(.5, .025, "16 misure sul medesimo corpo: confronto descrittivo, non validazione indipendente.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .06, 1, 1))
    svg_path = output / "error_comparison.svg"
    fig.savefig(svg_path, metadata={"Date": None})
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines())+"\n")
    fig.savefig(output / "error_comparison.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
