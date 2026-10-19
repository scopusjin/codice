"""Export the displayed report only while its calculation inputs still match."""
from hashlib import sha256
from html.parser import HTMLParser
from copy import deepcopy
import json
import re


class _PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.parts.append("\n• ")
        elif tag in {"p", "div", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"p", "div", "li", "ul", "ol"}:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(html):
    parser = _PlainText()
    parser.feed(html)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(
        line.strip() for line in "".join(parser.parts).splitlines())).strip()


def _signature(case):
    payload = {key: case[key] for key in ("view", "inputs", "signs", "fc_choice")}
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def capture_report(state, view):
    from app.case_file import snapshot_case
    html = state.get("__desc_dettagliate_html", "")
    case = snapshot_case(state, view, include_report=False)
    state["__case_report"] = {"signature": _signature(case),
                              "detailed_html": html, "detailed_text": plain_text(html),
                              "word_blocks": deepcopy(state.get("__word_report_blocks", {}))}


def current_report(state, case):
    active_key = "show_results" if case["view"] == "full" else "run_stima_mobile"
    saved = state.get("__case_report")
    if (case["editor_open"] or not state.get(active_key) or not saved
            or saved["signature"] != _signature(case) or not saved["detailed_text"]):
        return None
    return {key: saved[key] for key in ("detailed_text", "detailed_html", "word_blocks")}


WORD_BLOCK_KEYS = {"ambient_temperature", "correction_factor", "cooling", "livor", "rigor", "putrefaction", "additional", "conclusion"}


def build_word_blocks(*, input_html, cooling_html, livor, rigor, conclusion, additional_html="", putrefaction_html=""):
    """Temperature comparison is deferred to Word, which has the original MSIL value."""
    blocks = {}

    def add(key, html, rule="always"):
        if html:
            blocks[key] = {"html": html, "text": plain_text(html), "insert_when": rule}

    # Only leaf list items: never copy the input introduction or measured data.
    for item in re.findall(r"<li[^>]*>((?:(?!<li\b|</li>).)*)</li>", input_html, re.S):
        text = plain_text(item).lower()
        if text.startswith(("range di temperature ambientali", "temperatura ambientale media", "temperatura ambientale:")):
            item = re.sub(r"^Temperatura ambientale:", "Temperatura ambientale media stimata:", item)
            add("ambient_temperature", "<ul><li>" + item + "</li></ul>", "different_from_msil")
        elif text.startswith(("range stimato per il fattore", "range dei fattori", "fattore di correzione")):
            add("correction_factor", "<ul><li>" + item + "</li></ul>")
    add("cooling", cooling_html)
    for key, text, phrase in (("livor", livor, "macchie ipostatiche"),
                              ("rigor", rigor, "rigidità cadaverica")):
        if text:
            text = text.replace(phrase, "<u>" + phrase + "</u>", 1)
            add(key, "<ul><li>" + text + "</li></ul>")
    add("putrefaction", putrefaction_html)
    add("additional", additional_html)
    if conclusion:
        add("conclusion", "<p>&nbsp;</p><p>" + conclusion + "</p>")
    return blocks
