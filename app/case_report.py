"""Export the displayed report only while its calculation inputs still match."""
from hashlib import sha256
from html.parser import HTMLParser
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
                              "detailed_html": html, "detailed_text": plain_text(html)}


def current_report(state, case):
    active_key = "show_results" if case["view"] == "full" else "run_stima_mobile"
    saved = state.get("__case_report")
    if (case["editor_open"] or not state.get(active_key) or not saved
            or saved["signature"] != _signature(case) or not saved["detailed_text"]):
        return None
    return {key: saved[key] for key in ("detailed_text", "detailed_html")}
