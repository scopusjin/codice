"""Versioned, portable case data. Never serialize arbitrary session objects."""

from copy import deepcopy
from datetime import date, datetime
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from app.full_tanatology import FULL_LIVOR_STATE_BY_LABEL, FULL_RIGOR_STATE_BY_LABEL
from app.msil_tanatology import MSIL_LIVOR_STATE_BY_LABEL, MSIL_RIGOR_STATE_BY_LABEL
from app.special_tanatology_states import SPECIAL_PARAM_LABEL_IT, SPECIAL_OPTION_LABEL_IT

FORMAT = "mortem-case"
SCHEMA_VERSION = 1
MAX_BYTES = 1024 * 1024
PAGES = {"full": "Stima_epoca_decesso.py", "msil": "pages/App_MSIL.py"}
NUMBER_KEYS = set("""rt_val tm_val peso ta_base_val ta_other_val fattore_correzione
fc_min_val fc_other_val Ta_min_beta Ta_max_beta FC_min_beta FC_max_beta
__full_standard_ta_base_val __full_standard_fattore_correzione
__full_interval_ta_base_val __full_interval_ta_other_val
__full_interval_fc_min_val __full_interval_fc_other_val __fc_reviewed_weight""".split())
BOOL_KEYS = set("""usa_orario_custom henssge_non_applicabile stima_cautelativa_beta
range_unico_beta peso_stimato_beta mostra_parametri_aggiuntivi alterazioni_putrefattive
__prudent_explicit_ranges_initialized ta_range_toggle_beta fc_manual_range_beta""".split())
TEXT_KEYS = {"input_ora_rilievo", "fattori_condizioni_testo", "fattori_condizioni_parentetica"}
DATE_KEYS = {"input_data_rilievo"}
LIST_KEYS = {"fc_suggested_vals", "__msil_fc_chosen_range"}
SELECTORS = {}
for param, label in SPECIAL_PARAM_LABEL_IT.items():
    SELECTORS[label + "_selector"] = set(SPECIAL_OPTION_LABEL_IT[param].values())
    BOOL_KEYS.update({label + "_diversa", label + "_ora__manual"})
    TEXT_KEYS.update({label + "_ora", label + "_ora__last_main"})
    DATE_KEYS.add(label + "_data")
STATE_KEYS = NUMBER_KEYS | BOOL_KEYS | TEXT_KEYS | DATE_KEYS | LIST_KEYS | SELECTORS.keys() | {"henssge_round_minutes"}
CHOICE_KEYS = set("""range weight base_range manual manual_weight_adjusted weight_adjusted
manual_center conditions description rule explanation sources draft scenarios temperature""".split())
DRAFT_FIELDS = set("""thin thick medium heavy surface metal-type leaf leaf-cover feather air water
isolation blanket-volume support-soaked""".split())
DRAFT_BOOLS = set("""waterNearZero wetCase manual manualWeightAdjusted weightAdjusted
rangeExpanded sourceOpen multiple scenarioWeightAdjusted temperatureEdited""".split())
DRAFT_KEYS = DRAFT_BOOLS | {"state", "fields", "lo", "hi", "weight", "manualBase", "selectedBase",
                            "temperature", "activeScenario", "scenarios"}


class CaseFileError(ValueError):
    pass


def _require(condition, message="File del caso non valido."):
    if not condition:
        raise CaseFileError(message)


def _number(value):
    return type(value) in (int, float) and isfinite(value)


def _text(value, limit=8000):
    return isinstance(value, str) and len(value) <= limit and not any(ord(c) < 32 and c not in "\n\t" for c in value)


def _json_tree(value, depth=0):
    _require(depth <= 16, "File del caso troppo complesso.")
    if isinstance(value, dict):
        _require(len(value) <= 200)
        for key, item in value.items():
            _require(_text(key, 160))
            _json_tree(item, depth + 1)
    elif isinstance(value, list):
        _require(len(value) <= 100)
        for item in value:
            _json_tree(item, depth + 1)
    else:
        _require(value is None or type(value) is bool or _number(value) or _text(value))


def _pair(value, *, nullable=False):
    return isinstance(value, list) and len(value) == 2 and all(_number(v) or (nullable and v is None) for v in value)


def _validate_draft(draft, *, nested=False):
    _require(isinstance(draft, dict) and draft.keys() <= DRAFT_KEYS)
    for key, value in draft.items():
        if key in DRAFT_BOOLS:
            _require(type(value) is bool)
        elif key == "fields":
            _require(isinstance(value, dict) and value.keys() <= DRAFT_FIELDS)
            _require(all(_text(v, 100) for v in value.values()))
        elif key == "state":
            _require(value in {"Asciutto", "Bagnato", "Immerso"})
        elif key in {"lo", "hi"}:
            _require(_text(value, 100))
        elif key in {"manualBase", "selectedBase"}:
            _require(value is None or _pair(value, nullable=True))
        elif key in {"temperature", "weight"}:
            _require(value is None or _number(value) or (key == "temperature" and _text(value, 100)))
        elif key == "activeScenario":
            _require(type(value) is int and 0 <= value < 100)
        elif key == "scenarios":
            _require(isinstance(value, list) and len(value) <= (0 if nested else 100))
            for item in value:
                _validate_draft(item, nested=True)


def _clean_choice(choice):
    if choice is None:
        return None
    cleaned = {k: deepcopy(v) for k, v in choice.items() if k in CHOICE_KEYS}
    if "scenarios" in cleaned:
        cleaned["scenarios"] = [_clean_choice(item) for item in cleaned["scenarios"]]
    return cleaned


def _validate_choice(choice):
    if choice is None:
        return
    _require(isinstance(choice, dict) and choice.keys() <= CHOICE_KEYS)
    for key, value in choice.items():
        if key in {"range", "base_range"}:
            _require((key == "base_range" and value is None) or _pair(value, nullable=True))
        elif key in {"weight", "temperature"}:
            _require(value is None or _number(value))
        elif key in {"manual", "manual_weight_adjusted", "weight_adjusted", "manual_center"}:
            _require(type(value) is bool)
        elif key == "draft":
            _validate_draft(value)
        elif key == "conditions":
            _require(isinstance(value, dict))
        elif key == "sources":
            _require(isinstance(value, list) and all(_text(v, 100) for v in value))
        elif key == "scenarios":
            _require(isinstance(value, list) and 2 <= len(value) <= 100)
            for item in value:
                _require(isinstance(item, dict) and "scenarios" not in item)
                _validate_choice(item)
        else:
            _require(_text(value) and "<" not in value and ">" not in value)
    if choice.get("scenarios"):
        from app.fc_selection import validate_choice
        try:
            validate_choice(choice)
        except (TypeError, ValueError, OverflowError, KeyError) as exc:
            raise CaseFileError("Scenari del caso non validi.") from exc


def app_version():
    """Content fingerprint, also available on deployments without git metadata."""
    root = Path(__file__).resolve().parents[1]
    files = [root / "Stima_epoca_decesso.py", *sorted((root / "app").rglob("*")),
             *sorted((root / "pages").glob("*.py")), *sorted((root / "data").glob("*.json"))]
    digest = sha256()
    for path in files:
        if path.is_file() and path.suffix in {".py", ".js", ".html", ".json"}:
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def snapshot_case(state, view, *, now=None):
    _require(view in PAGES)
    current = dict(state)
    editor_open = bool(current.get("__fc_active"))
    if editor_open:
        current.update(state.get("__fc_form", {}))
    values = {k: deepcopy(current[k]) for k in STATE_KEYS if k in current}
    values.setdefault("henssge_round_minutes", 30)
    for key in DATE_KEYS & values.keys():
        if isinstance(values[key], date):
            values[key] = values[key].isoformat()
    maps = ((MSIL_LIVOR_STATE_BY_LABEL, MSIL_RIGOR_STATE_BY_LABEL) if view == "msil"
            else (FULL_LIVOR_STATE_BY_LABEL, FULL_RIGOR_STATE_BY_LABEL))
    signs = {}
    for name, mapping, legacy in zip(("livor", "rigor"), maps, ("selettore_macchie", "selettore_rigidita")):
        ui_key = legacy + ("_mobile" if view == "msil" else "_ui")
        label = current.get(ui_key)
        signs[name] = mapping.get(label, current.get(legacy + "_id", next(iter(mapping.values()))))
    case = {"format": FORMAT, "schema_version": SCHEMA_VERSION,
            "app_version": app_version(), "saved_at": (now or datetime.now(ZoneInfo("Europe/Zurich"))).isoformat(),
            "case_code": str(state.get("case_code", "")).strip(), "view": view,
            "inputs": values, "signs": signs, "fc_choice": _clean_choice(current.get("__fc_applied_choice")),
            "fc_draft": deepcopy(state.get("__fc_draft")), "editor_open": editor_open}
    validate_case(case)
    return case


def validate_case(case):
    _json_tree(case)
    _require(isinstance(case, dict) and case.get("format") == FORMAT, "Il file non è un caso Mor-tem.")
    _require(type(case.get("schema_version")) is int and case["schema_version"] == SCHEMA_VERSION,
             "Versione del file non supportata. Nessun dato è stato modificato.")
    required = {"format", "schema_version", "app_version", "saved_at", "case_code", "view", "inputs",
                "signs", "fc_choice", "fc_draft", "editor_open"}
    _require(case.keys() == required)
    _require(_text(case["case_code"], 80) and "\n" not in case["case_code"] and "\t" not in case["case_code"])
    _require(_text(case["app_version"], 100) and _text(case["saved_at"], 100))
    try:
        datetime.fromisoformat(case["saved_at"])
    except ValueError as exc:
        raise CaseFileError("Data del salvataggio non valida.") from exc
    _require(case["view"] in PAGES and type(case["editor_open"]) is bool)
    values = case["inputs"]
    _require(isinstance(values, dict) and values.keys() <= STATE_KEYS)
    for key, value in values.items():
        if key in NUMBER_KEYS:
            _require(value is None or _number(value))
        elif key in BOOL_KEYS:
            _require(type(value) is bool)
        elif key in TEXT_KEYS:
            _require(value is None or (_text(value) and "<" not in value and ">" not in value))
        elif key in DATE_KEYS:
            try:
                if value is not None:
                    date.fromisoformat(value)
            except (TypeError, ValueError) as exc:
                raise CaseFileError("Data dei rilievi non valida.") from exc
        elif key in LIST_KEYS:
            _require(value is None or (isinstance(value, list) and all(_number(v) for v in value)))
            if key == "__msil_fc_chosen_range" and value:
                _require(_pair(value))
        elif key in SELECTORS:
            _require(isinstance(value, str) and value in SELECTORS[key])
        elif key == "henssge_round_minutes":
            _require(type(value) is int and value in {6, 15, 30})
    maps = ((MSIL_LIVOR_STATE_BY_LABEL, MSIL_RIGOR_STATE_BY_LABEL) if case["view"] == "msil"
            else (FULL_LIVOR_STATE_BY_LABEL, FULL_RIGOR_STATE_BY_LABEL))
    _require(isinstance(case["signs"], dict) and case["signs"].keys() == {"livor", "rigor"})
    for name, mapping in zip(("livor", "rigor"), maps):
        _require(isinstance(case["signs"][name], str) and case["signs"][name] in mapping.values())
    _validate_choice(case["fc_choice"])
    if case["fc_draft"] is not None:
        _validate_draft(case["fc_draft"])
    _require(not case["editor_open"] or isinstance(case["fc_draft"], dict))
    return case


def encode_case(case):
    validate_case(case)
    raw = json.dumps(case, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8")
    _require(len(raw) <= MAX_BYTES, "Il caso supera la dimensione massima di 1 MB.")
    return raw


def decode_case(raw):
    _require(isinstance(raw, bytes) and len(raw) <= MAX_BYTES, "Dimensione massima del file: 1 MB.")
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            _require(key not in result, "Il file contiene campi duplicati.")
            result[key] = value
        return result
    try:
        data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_pairs)
        return validate_case(data)
    except (UnicodeError, ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        if isinstance(exc, CaseFileError):
            raise
        raise CaseFileError("File del caso non valido. Nessun dato è stato modificato.") from exc


def case_filename(case):
    code = re.sub(r"[^\w.-]+", "_", case["case_code"], flags=re.UNICODE).strip("._-")
    suffix = code or datetime.fromisoformat(case["saved_at"]).strftime("%Y-%m-%d_%H%M")
    return f"mortem_{suffix}.json"


def restored_inputs(case):
    """Validate the entire file before returning any state to apply."""
    validate_case(case)
    values = deepcopy(case["inputs"])
    for key in DATE_KEYS & values.keys():
        if values[key] is not None:
            values[key] = date.fromisoformat(values[key])
    maps = ((MSIL_LIVOR_STATE_BY_LABEL, MSIL_RIGOR_STATE_BY_LABEL) if case["view"] == "msil"
            else (FULL_LIVOR_STATE_BY_LABEL, FULL_RIGOR_STATE_BY_LABEL))
    from app.tanatology_states import livor_legacy_label, rigor_legacy_label
    for name, mapping, key, legacy in zip(("livor", "rigor"), maps,
            ("selettore_macchie", "selettore_rigidita"), (livor_legacy_label, rigor_legacy_label)):
        state_id = case["signs"][name]
        values[key] = legacy(state_id)
        values[key + "_id"] = state_id
        values[key + ("_mobile" if case["view"] == "msil" else "_ui")] = next(k for k, v in mapping.items() if v == state_id)
    values.update(case_code=case["case_code"], __fc_applied_choice=deepcopy(case["fc_choice"]),
                  __fc_draft=deepcopy(case["fc_draft"]), show_results=False, run_stima_mobile=False)
    return values
