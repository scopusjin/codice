# -*- coding: utf-8 -*-
"""Verifica dei limiti bibliografici nella tabella combinata, senza importare Streamlit."""

import ast
from pathlib import Path
import unittest

from app.parameters import dati_parametri_aggiuntivi


def _table_assignments():
    source = (Path(__file__).resolve().parents[1] / "pages" / "2_Tabelle di riferimento.py").read_text(
        encoding="utf-8"
    )
    module = ast.parse(source)
    function = next(
        item for item in module.body
        if isinstance(item, ast.FunctionDef) and item.name == "_render_combined_table"
    )
    assignments = {}
    for statement in function.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in {"groups", "headings"}:
                    assignments[target.id] = ast.literal_eval(statement.value)
    return assignments


class CombinedReferencePresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        values = _table_assignments()
        cls.groups = {group: (reference, findings) for group, reference, findings in values["groups"]}
        cls.headings = values["headings"]

    def test_other_scientific_limits_remain_intact(self):
        expected = {
            "rigor": [
                "0–7", "0,5–20", "2–96", "24–192", "≥ 24", "≤ 19 [4]",
            ],
            "mechanical": ["0–2,5", "0–5", "0–13", "≥ 1,5"],
            "mouth": ["≤ 11", "≥ 3"],
            "chemical": ["≤ 10", "≥ 3", "≤ 30", "≥ 5", "≤ 46", "≥ 14"],
        }
        for group, limits in expected.items():
            self.assertEqual([row[2] for row in self.groups[group][1]], limits)

    def test_livor_clinical_intervals_match_bibliographic_combinations(self):
        values = [row[2] for row in self.groups["lividity"][1]]
        self.assertEqual(
            values,
            ["0–3", "0–4", "≥ 1", "0–6", "1–6",
             "4–24", "0–24", "≥ 4", "0–20", "≥ 1"],
        )
        description = " ".join(row[0] for row in self.groups["lividity"][1])
        self.assertNotIn("massima estensione", description.lower())
        self.assertIn("digitopressione", description)
        self.assertIn("non ancora confluite", description)
        self.assertIn("Confluite e completamente migrabili", description)
        self.assertIn("Completamente migrabili (confluenza non specificata)", description)
        self.assertNotIn("confluenti", description.lower())

    def test_supraciliary_phase_intervals_match_engine(self):
        references, rows = self.groups["eyebrow"]
        self.assertEqual(references, "[1, 3]")
        engine = dati_parametri_aggiuntivi["Eccitabilità elettrica sopraciliare"]["range"]
        for (italian, english, displayed), phase in zip(
            rows[:6], ("VI", "V", "IV", "III", "II", "I"), strict=True
        ):
            with self.subTest(phase=phase):
                low, high = engine[f"Fase {phase}"]
                minimum = str(int(low)) if low == int(low) else str(low).replace(".", ",")
                maximum = str(int(high)) if high == int(high) else str(high).replace(".", ",")
                self.assertEqual(displayed, f"{minimum}–{maximum}")
                self.assertIn("stimolo elettrico", italian)
                self.assertIn("electrical stimulation", english)
        self.assertEqual(rows[6][2], "≥ 5")
        self.assertEqual(engine["Nessuna reazione"][0], 5)

    def test_all_sections_keep_references_and_bilingual_findings(self):
        references = {
            "lividity": "[1, 2]", "rigor": "[1–4]", "mechanical": "[1, 5]",
            "eyebrow": "[1, 3]", "mouth": "[1]", "chemical": "[1, 5]",
        }
        self.assertEqual(set(self.groups), set(references))
        for key, (reference, findings) in self.groups.items():
            self.assertEqual(reference, references[key])
            self.assertGreater(len(findings), 0)
            for italian, english, limit in findings:
                self.assertTrue(italian.strip())
                self.assertTrue(english.strip())
                self.assertTrue(limit.strip())
                self.assertNotIn("?", italian)
                self.assertNotIn("?", english)

    def test_table_has_no_yes_no_columns(self):
        self.assertEqual(
            self.headings["it"], ("Reperto osservato", "Limite/intervallo (h)")
        )
        self.assertEqual(
            self.headings["en"], ("Observed finding", "Time limit / interval (h)")
        )


if __name__ == "__main__":
    unittest.main()
