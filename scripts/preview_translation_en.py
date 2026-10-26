"""Build a static bilingual review directly from the locale resources.

Run from the repository root: python scripts/preview_translation_en.py
No case data, application state or external requests are used.
"""

from html import escape
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import i18n, special_tanatology_states as ss  # noqa: E402
from app.locales import en, it, en_ui, it_ui, en_msil, it_msil  # noqa: E402


def card(label, italian, english):
    return (
        f"\n<article><h3>{escape(label)}</h3><div class='pair'>\n"
        f"<section lang='it'><span class='lang'>Italiano</span>{italian or '<p>—</p>'}</section>\n"
        f"<section lang='en'><span class='lang'>English</span>{english or '<p>—</p>'}</section></div></article>\n"
    )


def paragraph(text):
    return f"<p>{escape(text)}</p>" if text else ""


def build():
    cooling = []
    def example(label, render):
        cooling.append(card(label, render("it"), render("en")))

    example("Henssge — intervallo", lambda lang: i18n.henssge_detail_paragraph(
        i18n.format_hours_range(8, 0, 12, 30, lang), language=lang))
    for status in ("optimal", "intermediate", "outside"):
        example("Qd — " + status, lambda lang, status=status: i18n.qd_summary(
            qd_text={"optimal": "0.50", "intermediate": "0.25", "outside": "0.18"}[status],
            ambient_at_most_23=True, threshold_text="0.2", within_limits=status != "outside",
            status=status, language=lang))
    example("Qd — combinazioni miste", lambda lang: i18n.qd_range_summary(
        qd_min_text="0.18", qd_max_text="0.32", status="mixed", single_value=False, language=lang))
    example("Potente — minimo, temperatura ambientale >23 °C", lambda lang: i18n.potente_paragraph(
        i18n.format_hours_minutes(43, 0, lang), "1.8", high_temperature=True, language=lang))
    example("Riepilogo dei range di temperatura e FC", lambda lang: i18n.prudent_graphing_detail_list(
        header=i18n.prudent_header(lang), ta_text="11–15 °C", cf_text="0.70–1.40", weight_text="85 kg", language=lang))
    example("Dati termometrici", lambda lang: i18n.cooling_input_paragraph(
        inspection_time="14:25", inspection_date="21.10.2026", ta_text="15", tr_text="28.1",
        weight_text="85", t0_text="37.2", correction_description="1.20", language=lang))
    example("Conclusione — intervallo con data", lambda lang: i18n.final_sentence_dt_range(
        i18n.format_hours_range(2, 0, 4, 0, lang), "10:25", "21.10.2026", "12:25", "21.10.2026", True, lang))
    example("Conclusione — solo limite minimo", lambda lang: i18n.final_sentence_simple_over(
        i18n.format_hours_minutes(16, 30, lang), language=lang))
    example("Riepilogo breve — durata senza data", lambda lang: i18n.simple_sentence_no_dt_range(
        i18n.format_hours_range(2, 0, 4, 0, lang), language=lang))
    example("Riepilogo breve — durata con solo limite minimo", lambda lang: i18n.simple_sentence_no_dt_over(
        i18n.format_hours_minutes(16, 30, lang), language=lang))
    example("Riepilogo breve — durata con solo limite massimo", lambda lang: i18n.simple_sentence_no_dt_not_over(
        i18n.format_hours_minutes(6, 0, lang), language=lang))
    example("Riepilogo breve — data e ora", lambda lang: i18n.simple_sentence_dt_range(
        i18n.format_hours_range(2, 0, 4, 0, lang), "10:25", "21.10.2026", "12:25", "21.10.2026", True, lang))
    example("Alterazioni putrefattive", lambda lang: i18n.putrefactive_paragraph(lang))

    findings = []
    for label, source, translated in (
        ("Ipostasi", it.LIVOR_DESCRIPTION_IT_BY_ID, en.LIVOR_DESCRIPTION_BY_ID),
        ("Digitopressione", it.LIVOR_PRESSURE_DESCRIPTION_IT_BY_ID, en.LIVOR_PRESSURE_DESCRIPTION_BY_ID),
        ("Rigor mortis", it.RIGOR_DESCRIPTION_IT_BY_ID, en.RIGOR_DESCRIPTION_BY_ID),
    ):
        for key, text in source.items():
            findings.append(card(label + " · " + key, paragraph(text), paragraph(translated[key])))
    for param in ss.SPECIAL_PARAM_LABEL_IT:
        for option in ss.special_option_ids(param):
            if option == ss.OPTION_NOT_ASSESSED:
                continue
            findings.append(card(ss.SPECIAL_PARAM_LABEL_IT[param] + " · " + option,
                paragraph(ss.special_description(param, option)),
                paragraph(i18n.special_description(param, option, "en"))))

    labels = []
    for source, translated in (
        (it.LIVOR_LABEL_BY_ID, en.LIVOR_LABEL_BY_ID),
        (it.RIGOR_LABEL_IT, en.RIGOR_LABEL_BY_ID),
        (ss.SPECIAL_PARAM_LABEL_IT, en.SPECIAL_PARAM_LABEL_BY_ID),
    ):
        for key, text in source.items():
            labels.append(card(key, paragraph(text), paragraph(translated[key])))
    for key, text in it_msil.MSIL_LIVOR_LABEL_BY_ID.items():
        labels.append(card("MSIL · " + key, paragraph(text), paragraph(en_msil.MSIL_LIVOR_LABEL_BY_ID[key])))
    ui = [card(key, it_ui.UI_TEXT[key], en_ui.UI_TEXT[key]) for key in it_ui.UI_TEXT]

    return """<!doctype html><html lang="it"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mor-tem — revisione traduzione inglese, blocco 1</title>
<style>
body{font:16px/1.55 system-ui,sans-serif;color:#172b36;background:#f4f6f8;margin:0}
main{max-width:1200px;margin:auto;padding:32px 22px 72px}h1{font-size:30px;line-height:1.2}
h2{font-size:22px}h3{font-size:14px;margin:0 0 14px;color:#425767;overflow-wrap:anywhere}
.intro{max-width:850px}.note{padding:16px 20px;background:#e6eff3;border-left:4px solid #376b80}
article{background:white;border:1px solid #d5dfe4;border-radius:10px;padding:20px;margin:16px 0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:32px}.lang{display:block;font-size:12px;
font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#376b80;margin-bottom:10px}
p{margin:0 0 12px}li{margin:6px 0}ul{padding-left:22px}summary{font-size:20px;cursor:pointer;padding:16px 0}
details{border-top:1px solid #c8d4dc;margin-top:30px}a{color:#235c72}
@media(max-width:700px){.pair{grid-template-columns:1fr;gap:22px}main{padding:24px 14px}h1{font-size:25px}}
@media print{body{background:white}article{break-inside:avoid}.pair{gap:20px}}
</style><main>
<h1>Mor-tem · Traduzione inglese</h1>
<div class="intro"><p><b>Blocco 1 — confronto dei testi scientifici e delle risorse linguistiche.</b></p>
<p class="note">L’inglese non è ancora attivato nell’app. Questa anteprima serve a verificare la traduzione
prima del collegamento alle schermate, al pannello FC e alle esportazioni. I valori negli esempi
sono dimostrativi e non costituiscono una valutazione di un caso.</p>
<p>Terminologia del raffreddamento confrontata con il capitolo di Henssge in Madea,
<i>Estimation of the Time Since Death</i>, 3ª edizione, presente sul Drive. Le descrizioni
degli altri reperti traducono i testi attualmente implementati. Limiti numerici e disuguaglianze
sono conservati; questa revisione non introduce una nuova validazione scientifica.</p></div>
<h2>Raffreddamento e conclusioni — esempi di resa</h2>
""" + "".join(cooling) + (
        f"<details><summary>Descrizioni dei reperti ({len(findings)})</summary>{''.join(findings)}</details>"
        f"<details><summary>Etichette principali ({len(labels)})</summary>{''.join(labels)}</details>"
        f"<details><summary>Catalogo interfaccia ({len(ui)} chiavi)</summary>"
        "<p>I segnaposto tra parentesi graffe vengono sostituiti dai dati soltanto durante l’uso dell’app.</p>"
        f"{''.join(ui)}</details>"
        "<p style='margin-top:32px'>Generato dalle risorse del repository con scripts/preview_translation_en.py.</p>"
        "</main></html>"
    )


if __name__ == "__main__":
    destination = ROOT / "docs" / "translation_review_en.html"
    destination.write_text("\n".join(line.rstrip() for line in build().splitlines()) + "\n", encoding="utf-8")
    print(destination)
