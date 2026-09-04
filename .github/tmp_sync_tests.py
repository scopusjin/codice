from pathlib import Path

# 1) Rigidità: il test deve distinguere label UI corrente e valore legacy interno.
path = Path("tests/test_full_tanatology.py")
text = path.read_text(encoding="utf-8")
old = '''    def test_full_rigor_ui_matches_current_parameter_options(self):
        current_labels = tuple(opzioni_rigidita.keys())
        self.assertEqual(
            tuple(FULL_RIGOR_STATE_BY_LABEL.keys()),
            current_labels,
        )
        self.assertEqual(full_rigor_labels(), current_labels)
        self.assertEqual(full_rigor_labels("it"), current_labels)
        for ui_label in opzioni_rigidita:
            self.assertEqual(
                full_rigor_state_id(ui_label),
                FULL_RIGOR_STATE_BY_LABEL[ui_label],
            )
            self.assertEqual(full_rigor_legacy_value(ui_label), ui_label)
'''
new = '''    def test_full_rigor_ui_matches_current_labels_and_legacy_values(self):
        current_labels = (
            "Non valutata",
            "Non ancora apprezzabile",
            "Presente, in aumento",
            "Presente, intensa e generalizzata",
            "In via di risoluzione",
            "Risolta",
            "Non valutabile/Non attendibile",
        )
        self.assertEqual(
            tuple(FULL_RIGOR_STATE_BY_LABEL.keys()),
            current_labels,
        )
        self.assertEqual(full_rigor_labels(), current_labels)
        self.assertEqual(full_rigor_labels("it"), current_labels)
        for ui_label in current_labels:
            self.assertEqual(
                full_rigor_state_id(ui_label),
                FULL_RIGOR_STATE_BY_LABEL[ui_label],
            )
            expected_legacy = (
                "Presente e in via di intensificazione e generalizzazione"
                if ui_label == "Presente, in aumento"
                else ui_label
            )
            self.assertEqual(full_rigor_legacy_value(ui_label), expected_legacy)
'''
if text.count(old) != 1:
    raise SystemExit(f"Rigidita block count: {text.count(old)}")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

# 2) Potente: durata non più in grassetto.
path = Path("tests/test_textgen_presentational_i18n.py")
text = path.read_text(encoding="utf-8")
old = '            "almeno <b>26 ore 30 minuti</b> (≈ 1.1 giorni) dal decesso.</li></ul>"\n'
new = '            "almeno 26 ore 30 minuti (≈ 1.1 giorni) dal decesso.</li></ul>"\n'
if text.count(old) != 1:
    raise SystemExit(f"Potente expectation count: {text.count(old)}")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

# 3) Pulsante: testo corrente della UI completa.
path = Path("tests/test_ui_i18n.py")
text = path.read_text(encoding="utf-8")
old = '            "full.estimate_button": "STIMA EPOCA DECESSO",\n'
new = '            "full.estimate_button": "Procedi con la stima",\n'
if text.count(old) != 1:
    raise SystemExit(f"Estimate button expectation count: {text.count(old)}")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
