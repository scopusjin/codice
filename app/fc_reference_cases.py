"""Documentary cases displayed on the app's existing reference page."""

import streamlit as st

from app.fc_catalog import load_examples


def case_rows(case_types=None):
    examples = load_examples()
    rows = []
    for example in examples:
        if case_types is not None and example["type"] not in case_types:
            continue
        if example.get("observations"):
            fc = example["observations"]
        elif example.get("weightNote"):
            fc = f"FC iniziale: {example['fc']}; a {example['weight']:.1f} kg: {example['adjustedFc']}."
        else:
            fc = example["fc"]
        weights = example.get("weights", [example.get("weight")])
        rows.append({
            "Caso": example["title"],
            "Peso (kg)": " / ".join(f"{weight:g}".replace(".", ",") for weight in weights if weight is not None),
            "Condizioni": example["conditions"].replace("aria mobile", "correnti d’aria").replace("aria ferma", "assenza di correnti d’aria"),
            "FC": fc,
            "Significato e limiti": example["notes"],
            "Fonte": example["sourceText"],
        })
    return rows


def render_fc_cases():
    st.subheader("Casi documentati da Henssge")
    st.caption("Sono riportati 13 casi sperimentali e 4 casi della pratica medico-legale, in 16 schede. L’elenco non comprende l’intera casistica pubblicata. Pesi e fattori conservano la precisione della fonte.")
    st.markdown("**Esperimenti su cadaveri**")
    st.write("Il raffreddamento è osservato in condizioni controllate e il fattore di correzione è ricavato dai dati. Ogni valore si riferisce al peso e alle condizioni descritti: non costituisce un incremento fisso da attribuire a un singolo indumento.")
    st.dataframe(case_rows(("Esperimento", "Esperimenti")), hide_index=True, width="stretch")
    st.markdown("**Casi della pratica medico-legale**")
    st.write("Sono casi reali esaminati durante accertamenti medico-legali. Il medico sceglie il FC, o un intervallo di FC, in base alle condizioni della scena per stimare l’epoca del decesso. Quando l’indagine consente di conoscere il tempo di morte, si può verificare la concordanza con la stima; questo riscontro non è disponibile per tutti i casi.")
    st.dataframe(case_rows(("Caso operativo",)), hide_index=True, width="stretch")
    st.caption("Le prove su simulatore, citate per alcuni appoggi e per le foglie, riguardano invece corpi artificiali con un peso virtuale: non sono casi su cadaveri. Le proposte interpretative dell’app sono indicate separatamente dalle osservazioni pubblicate.")

