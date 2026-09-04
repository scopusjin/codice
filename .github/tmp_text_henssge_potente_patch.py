from pathlib import Path


graph_path = Path("app/graphing.py")
graph = graph_path.read_text(encoding="utf-8")

old_henssge = '_add_det("<ul><li>Nel caso in esame, l’equazione di Henssge non è applicabile.</li></ul>")'
new_henssge = '_add_det("<ul><li>I parametri del caso in esame ricadono al di fuori dei range di applicabilità dell’equazione di Henssge, che fornirebbe risultati non attendibili.</li></ul>")'
assert graph.count(old_henssge) == 1, graph.count(old_henssge)
graph = graph.replace(old_henssge, new_henssge, 1)

old_swiss = '''        swiss_scope = "Per le condizioni con Qd ≤ 0,2, " if condizioni_variabili else ""
        swiss_note = (
            f"{swiss_scope}a titolo esclusivamente orientativo, secondo l’impostazione utilizzata da Swisswuff, "
'''
new_swiss = '''        swiss_scope = (
            "Per le condizioni con Qd ≤ 0,2, a titolo esclusivamente orientativo, "
            if condizioni_variabili
            else "A titolo esclusivamente orientativo, "
        )
        swiss_note = (
            f"{swiss_scope}secondo l’impostazione utilizzata da Swisswuff, "
'''
assert graph.count(old_swiss) == 1, graph.count(old_swiss)
graph = graph.replace(old_swiss, new_swiss, 1)
graph_path.write_text(graph, encoding="utf-8")

it_path = Path("app/locales/it.py")
it_text = it_path.read_text(encoding="utf-8")
old_potente = 'f"Applicato al caso specifico, suggerisce che, al momento dell’ispezione legale, fossero trascorse almeno <b>{duration}</b> (≈ {days} giorni) dal decesso.</li></ul>"'
new_potente = 'f"Applicato al caso specifico, suggerisce che, al momento dell’ispezione legale, fossero trascorse almeno {duration} (≈ {days} giorni) dal decesso.</li></ul>"'
assert it_text.count(old_potente) == 1, it_text.count(old_potente)
it_text = it_text.replace(old_potente, new_potente, 1)
it_path.write_text(it_text, encoding="utf-8")
