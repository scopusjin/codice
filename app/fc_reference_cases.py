"""Documentary cases displayed on the app's existing reference page."""

import json
import re
from pathlib import Path

import streamlit as st


def case_rows():
    examples = json.loads((Path(__file__).resolve().parents[1] / "data/fc_examples.json").read_text())
    rows = []
    for example in examples:
        if example.get("observations"):
            fc = re.sub(r" a ([0-9.]+) kg", lambda m: "" if 60 <= float(m[1]) <= 80 else m[0], example["observations"])
        elif example.get("weightNote"):
            fc = f"FC iniziale: {example['fc']}; a {example['weight']:.1f} kg: 1.80 - 2.50."
        else:
            fc = example["fc"]
            if not 60 <= example["weight"] <= 80:
                fc += f" · {example['weight']:.1f} kg"
        rows.append({
            "Caso": ("Operativo" if example["type"] == "Caso operativo" else "Sperimentale") + " · " + example["title"],
            "Condizioni": example["conditions"].replace("aria mobile", "correnti d’aria").replace("aria ferma", "assenza di correnti d’aria"),
            "FC": fc,
            "Fonte": example["sourceText"],
        })
    return rows


def render_fc_cases():
    st.subheader("Casi sperimentali e operativi di Henssge")
    st.caption("Casi attualmente inclusi nell’app, tratti dalle pubblicazioni di Henssge. L’elenco non comprende l’intera casistica pubblicata.")
    st.dataframe(case_rows(), hide_index=True, width="stretch")

