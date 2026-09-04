from pathlib import Path

path = Path("app/graphing.py")
text = path.read_text(encoding="utf-8")

old = '''        swiss_note = (
            f"{swiss_scope}secondo l’impostazione utilizzata da Swisswuff, "
            f"il range temporale sarebbe compreso tra {swiss_min_txt} e {swiss_max_txt}; tale range è da intendersi "
            "come del tutto approssimativo, essendo calcolato applicando una variazione di ±20% alla stima centrale "
            "e privo di uno specifico fondamento statistico."
        )'''
new = '''        swiss_note = (
            f"{swiss_scope}secondo l’impostazione utilizzata da Swisswuff, "
            f"il tempo trascorso dal decesso al momento dei rilievi sarebbe stimabile tra {swiss_min_txt} e {swiss_max_txt}; tale intervallo è da intendersi "
            "come del tutto approssimativo, essendo calcolato applicando una variazione di ±20% alla stima centrale "
            "e privo di uno specifico fondamento statistico."
        )'''

count = text.count(old)
if count != 1:
    raise SystemExit(f"Expected exactly one Swisswuff wording block, found {count}")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
