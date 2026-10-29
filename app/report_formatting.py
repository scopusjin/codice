"""Presentation-only emphasis shared by the displayed and exported report."""
import re

_TERMS = re.compile(
    r"raffreddamento (?:cadaverico|corporeo)|macchie ipostatiche|rigidità cadaverica|"
    r"eccitabilità (?:muscolare (?:elettrica|meccanica)(?: residua)?|pupillare chimica(?: residua)?|chimica pupillare)|"
    r"stimolo elettrico|stimolo meccanico|percussione del muscolo del braccio|"
    r"postmortem body cooling|postmortem lividity|rigor mortis|"
    r"(?:supraciliary|perioral) electrical stimulation|"
    r"(?:electrical|mechanical) (?:muscle )?excitability|"
    r"pharmacological (?:iris )?excitability|percussion of (?:the biceps brachii|the arm muscle)",
    re.IGNORECASE,
)


def underline_findings(html):
    """Underline existing terms in text nodes without nesting existing underlines."""
    depth = 0
    parts = []
    for token in re.split(r"(<[^>]+>)", html):
        if token.startswith('<'):
            if re.match(r'<u(?:\s|>)', token, re.I):
                depth += 1
            elif re.match(r'</u\s*>', token, re.I):
                depth = max(0, depth - 1)
            parts.append(token)
        else:
            parts.append(token if depth else _TERMS.sub(lambda m: '<u>' + m[0] + '</u>', token))
    return ''.join(parts)
