"""Translate presentation text at the Streamlit output boundary.

Widget IDs and Python option values remain unchanged. Display labels and their
wire representations are translated after Streamlit computes widget identity.
Reports use locale renderers and this catalogue for remaining UI prose.
"""

from functools import lru_cache, wraps
from html import unescape, escape
import re

from app.language import current_language


@lru_cache(maxsize=1)
def catalogue():
    from app.locales import it, en, it_ui, en_ui, it_msil, en_msil
    from app.locales.en_runtime import TEXT
    from app.locales.en_fc_examples import TEXT as EXAMPLES
    from app.locales.en_fc_explanations import TEXT as EXPLANATIONS
    from app.locales import it_supra, en_supra
    pairs = {value: en_ui.UI_TEXT[key] for key, value in it_ui.UI_TEXT.items()}
    # Help renderers split lists and HTML into separate text nodes. Derive those
    # same segments from the paired, reviewed resources before rendering.
    for source, target in list(pairs.items()):
        for split in (lambda s: s.splitlines(), lambda s: re.split(r'</?[a-zA-Z][^>]*>', s)):
            left, right = split(source), split(target)
            if len(left) == len(right):
                for a, b in zip(left, right):
                    if any(char.isalpha() for char in a) and b.strip():
                        pairs[a.strip()] = b.strip()
                        pairs[escape(unescape(a.strip()), quote=False)] = escape(unescape(b.strip()), quote=False)
    for source, target in (
        (it.LIVOR_LABEL_BY_ID, en.LIVOR_LABEL_BY_ID),
        (it.RIGOR_LABEL_IT, en.RIGOR_LABEL_BY_ID),
        (it.LIVOR_DESCRIPTION_IT_BY_ID, en.LIVOR_DESCRIPTION_BY_ID),
        (it.RIGOR_DESCRIPTION_IT_BY_ID, en.RIGOR_DESCRIPTION_BY_ID),
        (it_msil.MSIL_LIVOR_LABEL_BY_ID, en_msil.MSIL_LIVOR_LABEL_BY_ID),
        (it_msil.MSIL_RIGOR_LABEL_BY_ID, en_msil.MSIL_RIGOR_LABEL_BY_ID),
    ):
        pairs.update((value, target[key]) for key, value in source.items())
    from app import special_tanatology_states as ss
    pairs.update((value, en.SPECIAL_PARAM_LABEL_BY_ID[key]) for key, value in ss.SPECIAL_PARAM_LABEL_IT.items())
    for param, options in ss.SPECIAL_OPTION_LABEL_IT.items():
        pairs.update((value, en.SPECIAL_OPTION_LABEL_BY_ID[param][key]) for key, value in options.items())
    pairs.update(TEXT)
    pairs.update(EXAMPLES)
    for source, target in EXAMPLES.items():
        source = re.sub(r"\s+(?:sul|del) tronco inferiore", "", source, flags=re.I)
        source = source.replace("aria mobile", "correnti d’aria").replace("aria ferma", "assenza di correnti d’aria")
        source = re.sub(r"(\d),(\d)", r"\1.\2", source)
        pairs[source] = target
    pairs.update(EXPLANATIONS)
    pairs.update((value[0], en_supra.SUPRA_GRID_DETAIL_BY_ID[key][0])
                 for key, value in it_supra.SUPRA_GRID_DETAIL_BY_ID.items())
    return {key: value for key, value in pairs.items() if key and isinstance(value, str) and key != value}


@lru_cache(maxsize=1)
def _pattern():
    return re.compile("|".join(re.escape(key) for key in sorted(catalogue(), key=len, reverse=True) if key not in {"Data", "Rigor"}))


def translate_text(text, language=None):
    if not isinstance(text, str) or (language or current_language()) != "en":
        return text
    if text in catalogue():
        return catalogue()[text]
    # Markdown destinations and bare URLs are not linguistic content.
    parts = re.split(r'(https?://[^\s<>\)]+)', text)
    return ''.join(part if index % 2 else _pattern().sub(
        lambda match, part=part: _replace_fragment(match, part), part)
        for index, part in enumerate(parts))


def _replace_fragment(match, text):
    start, end = match.span()
    key = match.group()
    if start and text[start - 1].isalnum() and key[0].isalnum():
        return key
    if end < len(text) and text[end].isalnum() and key[-1].isalnum():
        return key
    return catalogue()[key]


def translate_html(html, language=None):
    if not isinstance(html, str) or (language or current_language()) != "en":
        return html
    # Keep tags, attributes, URLs, scripts and styles byte-for-byte intact.
    parts = re.split(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|</?[a-zA-Z][^>]*>)', html, flags=re.S | re.I)
    def tag_text(tag):
        if re.match(r'<(?:script|style)\b', tag, re.I):
            return tag
        return re.sub(r'''((?:title|aria-label|placeholder)\s*=\s*)(["'])(.*?)\2''',
                      lambda m: m[1] + m[2] + escape(translate_text(unescape(m[3]), "en"), quote=True) + m[2],
                      tag, flags=re.S | re.I)
    return ''.join(tag_text(part) if index % 2 else translate_text(part, "en") for index, part in enumerate(parts))


def translate(text, language=None):
    return translate_html(text, language) if isinstance(text, str) and re.search(r'<[a-zA-Z][^>]*>', text) else translate_text(text, language)


_DISPLAY_FIELDS = frozenset({"label", "title", "help", "placeholder", "body", "caption", "text", "options", "content"})
_OPAQUE_MESSAGES = frozenset({"Arrow", "ArrowNamedDataSet", "Json", "Code", "Text", "ComponentInstance", "BidiComponent", "VegaLiteChart"})
_SELECTION_MESSAGES = frozenset({"Selectbox", "Radio", "ButtonGroup", "MultiSelect"})


def _map_wire(value, mapping):
    if isinstance(value, list):
        return [mapping.get(item, item) for item in value]
    return mapping.get(value, value) if isinstance(value, str) else value


def _selection_registration(original):
    """Streamlit 1.64 sends formatted strings, not option indices.

    Translate only wire labels. Deserialize back to original options before any
    callback/calculation, with an execution-local mapping for each widget.
    """
    @wraps(original)
    def register(*args, **kwargs):
        labels = kwargs.get("formatted_options")
        if labels:
            language = current_language()
            english = {label: translate(label, "en") for label in labels}
            visible = english if language == "en" else {label: label for label in labels}
            source = {value: key for key, value in english.items()}
            source.update({label: label for label in labels})
            serialize, deserialize = kwargs["serializer"], kwargs["deserializer"]
            kwargs["serializer"] = lambda value: _map_wire(serialize(value), visible)
            kwargs["deserializer"] = lambda value: deserialize(_map_wire(value, source))
            kwargs["formatted_options"] = list(visible.values())
        return original(*args, **kwargs)
    register._mortem_translation = True
    return register


def _prepare_selection(message):
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    from streamlit.elements.lib.utils import save_for_app_testing
    from streamlit.runtime.state.common import TESTING_KEY
    ctx = get_script_run_ctx(suppress_warning=True)
    if ctx is None:
        return
    language = current_language()
    state = ctx.session_state
    if "__mortem_selection_languages" not in state:
        state["__mortem_selection_languages"] = {}
    languages = state["__mortem_selection_languages"]
    previous = languages.get(message.id, language)
    languages[message.id] = language
    if previous != language:
        metadata = state._state._get_widget_metadata(message.id)
        if metadata is not None:
            value = metadata.serializer(state[message.id])
            if hasattr(message, "raw_values"):
                message.raw_values[:] = value or []
            elif value is not None:
                message.raw_value = value
            message.set_value = True
    if language == "en":
        if hasattr(message, "raw_value") and message.HasField("raw_value"):
            message.raw_value = translate(message.raw_value, language)
        if hasattr(message, "raw_values"):
            message.raw_values[:] = [translate(value, language) for value in message.raw_values]
        # AppTest must format options exactly as the native client displays them.
        if TESTING_KEY in state and message.id in state[TESTING_KEY]:
            formatter = state[TESTING_KEY][message.id]
            save_for_app_testing(ctx, message.id, lambda value: translate(formatter(value), language))


def translate_display_message(message):
    """Translate only presentation fields, excluding input defaults and IDs."""
    if message.DESCRIPTOR.name in _OPAQUE_MESSAGES:
        return
    if message.DESCRIPTOR.name in _SELECTION_MESSAGES:
        _prepare_selection(message)
    for field, value in message.ListFields():
        if field.type == field.TYPE_MESSAGE:
            for child in value if field.is_repeated else (value,):
                translate_display_message(child)
        elif current_language() == "en" and field.type == field.TYPE_STRING and field.name in _DISPLAY_FIELDS:
            if field.is_repeated:
                for index, item in enumerate(value):
                    value[index] = translate(item, "en")
            else:
                setattr(message, field.name, translate(value, "en"))


def install_presentation_translation():
    import streamlit.delta_generator as delta
    from app.render_context import serialized_installation

    @serialized_installation
    def install():
        from importlib import import_module
        for name in ("selectbox", "radio", "button_group", "multiselect"):
            module = import_module("streamlit.elements.widgets." + name)
            if not getattr(module.register_widget, "_mortem_translation", False):
                module.register_widget = _selection_registration(module.register_widget)
        original = delta._enqueue_message
        if getattr(original, "_mortem_translation", False):
            return
        @wraps(original)
        def enqueue(message):
            translate_display_message(message)
            return original(message)
        enqueue._mortem_translation = True
        delta._enqueue_message = enqueue
    install()
