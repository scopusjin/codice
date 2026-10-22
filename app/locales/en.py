"""Scientific English presentation resources, keyed by existing stable IDs.

These resources do not supply calculation ranges. See docs/TRANSLATION_EN.md
for terminology, sources and the staged integration status.
"""

from __future__ import annotations

from app import tanatology_states as ts
from app import special_tanatology_states as ss
from app import factor_ui_states as fs
from app import surface_ui_states as surfaces
from app.livor_digitopressione import PRESSURE_COMPLETE_FADING, PRESSURE_INCOMPLETE_FADING
from app.locales.en_msil import MSIL_LIVOR_LABEL_BY_ID, MSIL_RIGOR_LABEL_BY_ID


LIVOR_LABEL_BY_ID = {
    ts.LIVOR_NOT_ASSESSED: "Not assessed",
    ts.LIVOR_ABSENT: "Not yet present",
    ts.LIVOR_CONFLUING: "Developing confluence",
    ts.LIVOR_CONFLUENT: "Confluent (shifting not assessed)",
    ts.LIVOR_CONFLUENT_FULLY_MIGRATABLE: "Confluent and fully shiftable",
    ts.LIVOR_FULLY_MIGRATABLE: "Fully shiftable (confluence unspecified)",
    ts.LIVOR_PARTIALLY_MIGRATABLE: "Partially shiftable",
    ts.LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: "At least partially shiftable",
    ts.LIVOR_FIXED: "Fixed",
    ts.LIVOR_UNRELIABLE: "Not assessable / unreliable",
}

RIGOR_LABEL_BY_ID = {
    ts.RIGOR_NOT_ASSESSED: "Not assessed",
    ts.RIGOR_ABSENT: "Not yet detectable",
    ts.RIGOR_DEVELOPING: "Present, increasing in intensity and extent",
    ts.RIGOR_FULL: "Fully developed and generalised",
    ts.RIGOR_RESOLVING: "Resolving",
    ts.RIGOR_RESOLVED: "Resolved",
    ts.RIGOR_UNRELIABLE: "Not assessable / unreliable",
}

SPECIAL_PARAM_LABEL_BY_ID = {
    ss.PARAM_ELECTRICAL_SUPRACILIARY: "Electrical excitability — supraciliary stimulation",
    ss.PARAM_ELECTRICAL_PERIORAL: "Electrical excitability — perioral stimulation",
    ss.PARAM_MECHANICAL_MUSCLE: "Mechanical excitability of skeletal muscle",
    ss.PARAM_CHEMICAL_PUPILLARY: "Pharmacological excitability of the iris",
}

SPECIAL_OPTION_LABEL_BY_ID = {
    ss.PARAM_ELECTRICAL_SUPRACILIARY: {
        ss.OPTION_NOT_ASSESSED: "Not assessed",
        ss.SUPRA_PHASE_I: "Contraction of less than 1/3 of the upper eyelid",
        ss.SUPRA_PHASE_II: "Contraction of less than 2/3 of the upper eyelid",
        ss.SUPRA_PHASE_III: "Contraction of the entire upper eyelid",
        ss.SUPRA_PHASE_IV: "Contraction of the upper and lower orbicularis oculi",
        ss.SUPRA_PHASE_V: "Contraction of the forehead and orbital muscles",
        ss.SUPRA_PHASE_VI: "Contraction of the forehead, orbital and cheek muscles",
        ss.OPTION_NO_REACTION: "No response",
        ss.OPTION_UNRELIABLE: "Not assessable / unreliable",
    },
    ss.PARAM_ELECTRICAL_PERIORAL: {
        ss.OPTION_NOT_ASSESSED: "Not assessed",
        ss.PERIORAL_MARKED: "Facial muscles (+++)",
        ss.PERIORAL_MODERATE: "Perioral muscles (++)",
        ss.PERIORAL_SLIGHT: "Focal response (+)",
        ss.OPTION_NO_REACTION: "No response",
        ss.OPTION_UNRELIABLE: "Not assessable / unreliable",
    },
    ss.PARAM_MECHANICAL_MUSCLE: {
        ss.OPTION_NOT_ASSESSED: "Not assessed",
        ss.MECH_WHOLE_MUSCLE: "Contraction of the whole muscle",
        ss.MECH_REVERSIBLE_SWELLING: "Reversible muscular swelling",
        ss.MECH_SMALL_PERSISTENT_SWELLING: "Small persistent muscular swelling",
        ss.OPTION_NO_REACTION: "No response",
        ss.OPTION_UNRELIABLE: "Not assessable / unreliable",
    },
    ss.PARAM_CHEMICAL_PUPILLARY: {
        ss.OPTION_NOT_ASSESSED: "Not assessed",
        ss.OPTION_UNRELIABLE: "Not assessable / unreliable",
        ss.PUPILLARY_POSITIVE: "Positive",
        ss.PUPILLARY_NEGATIVE: "Negative",
        ss.PUPILLARY_ATROPINE_DILATION: "Dilatation after atropine",
        ss.PUPILLARY_ATROPINE_NO_CHANGE: "No change after atropine",
        ss.PUPILLARY_TROPICAMIDE_DILATION: "Dilatation after tropicamide",
        ss.PUPILLARY_TROPICAMIDE_NO_CHANGE: "No change after tropicamide",
        ss.PUPILLARY_ACETYLCHOLINE_REDUCTION: "Constriction after acetylcholine",
        ss.PUPILLARY_ACETYLCHOLINE_NO_CHANGE: "No change after acetylcholine",
    },
}

BODY_LABEL_BY_ID = {
    fs.BODY_DRY: "Dry body", fs.BODY_WET: "Wet", fs.BODY_IMMERSED: "Immersed",
}
WATER_LABEL_BY_ID = {
    fs.WATER_STILL: "In still water", fs.WATER_FLOWING: "In flowing water",
}
FULL_CLOTHING_LABEL_BY_ID = {
    fs.LAYER_THIN: "Thin layers (clothing or sheets)",
    fs.LAYER_THICK: "Thicker layers (clothing or coverings)",
    fs.BLANKET_MEDIUM: "Thick blanket / bedspread",
    fs.BLANKET_HEAVY: "Duvet / very thick blanket",
}
MSIL_CLOTHING_LABEL_BY_ID = {
    fs.LAYER_THIN: "Thin layers (clothing or sheets)",
    fs.LAYER_THICK: "Thicker layers (clothing or coverings)",
    fs.BLANKET_MEDIUM: "Medium-thickness blankets",
    fs.BLANKET_HEAVY: "Thick blankets / thermal wraps",
}
SURFACE_LABEL_BY_ID = {
    surfaces.SURFACE_HOME_FLOOR_WOOD: "Indoor floor / wooden base",
    surfaces.SURFACE_DRY_ASPHALT_GROUND_GRASS: "Dry asphalt / soil / grass",
    surfaces.SURFACE_MATTRESS_THICK_CARPET: "Mattress / thick carpet",
    surfaces.SURFACE_SOFA_SLEEPING_BAG_POLYSTYRENE: "Sofa / insulated sleeping bag / polystyrene",
    surfaces.SURFACE_CONCRETE_STONE_PVC: "Concrete / stone / PVC",
    surfaces.SURFACE_COLD_FLOOR: "Cold floor (outdoors / cellar)",
    surfaces.SURFACE_METAL_INDOOR: "Metal base (indoors)",
    surfaces.SURFACE_THICK_METAL_OUTDOOR: "Thick metal base (outdoors)",
    surfaces.SURFACE_WET_LEAVES: "Layer of wet leaves (≥2 cm)",
    surfaces.SURFACE_DRY_LEAVES: "Layer of dry leaves (≥2 cm)",
}


LIVOR_DESCRIPTION_BY_ID = {
    ts.LIVOR_NOT_ASSESSED: "Postmortem lividity was not assessed.",
    ts.LIVOR_ABSENT: (
        "Postmortem lividity is considered not to have developed at the time of the medico-legal examination. "
        "According to the maximum time limits reported in the scientific literature, this suggests that "
        "less than 3 hours had elapsed since death (lividity generally appears within 15–20 minutes)."
    ),
    ts.LIVOR_CONFLUING: (
        "Postmortem lividity is considered to have been present but still developing confluence at the time of the "
        "medico-legal examination. According to the maximum time limits reported in the scientific literature, "
        "this suggests that less than 4 hours had elapsed since death (this stage is generally observed "
        "between 1 hour 30 minutes and 3 hours 30 minutes after death)."
    ),
    ts.LIVOR_CONFLUENT: (
        "Postmortem lividity is considered to have been present and confluent at the time of the medico-legal "
        "examination (shifting was not specified or assessed). This suggests only that at least 1 hour "
        "had elapsed since death."
    ),
    ts.LIVOR_CONFLUENT_FULLY_MIGRATABLE: (
        "Postmortem lividity is considered to have been present, confluent and fully shiftable at the time "
        "of the medico-legal examination. According to the minimum and maximum time limits reported in "
        "the scientific literature, this suggests that between 1 and 6 hours had elapsed since death."
    ),
    ts.LIVOR_FULLY_MIGRATABLE: (
        "Postmortem lividity is considered to have been fully shiftable at the time of the medico-legal "
        "examination (degree of confluence unspecified). According to the maximum time limits reported "
        "in the scientific literature, this suggests that less than 6 hours had elapsed since death."
    ),
    ts.LIVOR_PARTIALLY_MIGRATABLE: (
        "Postmortem lividity is considered to have been partially shiftable at the time of the medico-legal "
        "examination. According to the minimum and maximum time limits reported in the scientific literature, "
        "this suggests that between 4 and 24 hours had elapsed since death."
    ),
    ts.LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: (
        "Postmortem lividity is considered to have been at least partially shiftable at the time of the "
        "medico-legal examination (lividity changed after repositioning the body, but the extent of shifting "
        "could not be determined). According to the maximum time limits reported in the scientific literature, "
        "this suggests that less than 24 hours had elapsed since death."
    ),
    ts.LIVOR_FIXED: (
        "Postmortem lividity is considered to have been completely fixed at the time of the medico-legal "
        "examination. According to the minimum time limits reported in the scientific literature, this "
        "suggests that more than 4 hours had elapsed since death (up to 30 hours, lividity may fade in "
        "intensity without shifting after repositioning the body)."
    ),
    ts.LIVOR_UNRELIABLE: (
        "Postmortem lividity was not assessed, or the findings are not considered reliable for estimating the time of death."
    ),
}

LIVOR_PRESSURE_DESCRIPTION_BY_ID = {
    PRESSURE_COMPLETE_FADING: (
        "Postmortem lividity blanched completely under finger pressure; "
        "this finding provides an upper time limit of 20 hours after death."
    ),
    PRESSURE_INCOMPLETE_FADING: (
        "Postmortem lividity did not blanch completely under finger pressure; "
        "this finding provides a lower time limit of 1 hour after death."
    ),
}

RIGOR_DESCRIPTION_BY_ID = {
    ts.RIGOR_NOT_ASSESSED: "Rigor mortis was not assessed.",
    ts.RIGOR_ABSENT: (
        "Rigor mortis is considered not to have developed at the time of the medico-legal examination. "
        "According to the maximum time limits reported in the scientific literature, this indicates that "
        "less than 7 hours had elapsed since death (rigor mortis appears within 2–3 hours after death on average)."
    ),
    ts.RIGOR_DEVELOPING: (
        "Rigor mortis is considered to have been developing, increasing in intensity and becoming generalised "
        "at the time of the medico-legal examination. According to the minimum and maximum time limits "
        "reported in the scientific literature, this indicates that at least 30 minutes but less than 20 hours "
        "had elapsed since death (rigor mortis generally becomes fully developed within 6–10 hours)."
    ),
    ts.RIGOR_FULL: (
        "Rigor mortis is considered to have been present and generalised at the time of the medico-legal "
        "examination. According to the minimum and maximum time limits reported in the scientific literature, "
        "this indicates that at least 2 hours but less than 96 hours, i.e. less than 4 days, had elapsed "
        "since death (resolution begins after 57 hours on average, approximately 2 and a half days after death)."
    ),
    ts.RIGOR_RESOLVING: (
        "Rigor mortis is considered to have been resolving at the time of the medico-legal examination. "
        "According to the minimum and maximum time limits reported in the scientific literature, this "
        "indicates that at least 24 hours but less than 192 hours, i.e. less than 8 days, had elapsed since "
        "death (on average, resolution begins after 57 hours, approximately 2 and a half days, and rigor "
        "mortis disappears within 76 hours, just over 3 days after death)."
    ),
    ts.RIGOR_RESOLVED: (
        "Rigor mortis is considered to have resolved at the time of the medico-legal examination. According "
        "to the minimum and maximum time limits reported in the scientific literature, this indicates that "
        "at least 24 hours had elapsed since death (rigor mortis disappears within 76 hours on average, "
        "just over 3 days after death)."
    ),
    ts.RIGOR_UNRELIABLE: (
        "Rigor mortis was not assessed, or the findings are not considered reliable for estimating the time of death."
    ),
}

SPECIAL_DESCRIPTION_BY_ID = {
    ss.PARAM_ELECTRICAL_SUPRACILIARY: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.SUPRA_PHASE_I: (
            "Electrical stimulation in the supraciliary region produced a slight contraction of a small "
            "part of the upper eyelid (less than 1/3). This residual electrical excitability of skeletal "
            "muscle suggests that death occurred more than 5 hours but less than 22 hours before assessment."
        ),
        ss.SUPRA_PHASE_II: (
            "Electrical stimulation in the supraciliary region produced contraction of less than 2/3 of "
            "the upper eyelid. This residual electrical excitability of skeletal muscle suggests that "
            "death occurred more than 3 hours 30 minutes but less than 16 hours before assessment."
        ),
        ss.SUPRA_PHASE_III: (
            "Electrical stimulation in the supraciliary region produced contraction of the entire upper "
            "eyelid. This residual electrical excitability of skeletal muscle suggests that death occurred "
            "more than 3 hours but less than 13 hours before assessment."
        ),
        ss.SUPRA_PHASE_IV: (
            "Electrical stimulation in the supraciliary region produced generalised contraction of the "
            "upper and lower parts of the orbicularis oculi. This residual electrical excitability of skeletal "
            "muscle suggests that death occurred more than 2 hours but less than 8 hours before assessment."
        ),
        ss.SUPRA_PHASE_V: (
            "Electrical stimulation in the supraciliary region produced generalised contraction of the "
            "forehead and orbital muscles. This residual electrical excitability of skeletal muscle "
            "suggests that death occurred more than 1 hour but less than 7 hours before assessment."
        ),
        ss.SUPRA_PHASE_VI: (
            "Electrical stimulation in the supraciliary region produced generalised contraction of the "
            "forehead, orbital and cheek muscles. This residual electrical excitability of skeletal "
            "muscle suggests that death occurred less than 6 hours before assessment."
        ),
        ss.OPTION_NO_REACTION: (
            "Electrical stimulation in the supraciliary region produced no muscular contraction. "
            "This finding allows only the inference that more than 5 hours had elapsed since death at assessment."
        ),
        ss.OPTION_UNRELIABLE: (
            "Residual electrical excitability following supraciliary stimulation could not be assessed, "
            "or the finding is not considered reliable."
        ),
    },
    ss.PARAM_ELECTRICAL_PERIORAL: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.PERIORAL_MARKED: (
            "Electrical stimulation in the perioral region produced generalised contraction of the facial "
            "muscles. For estimating the time since death, Henssge’s compound method considers a perioral "
            "response irrespective of its extent; this finding suggests that no more than 11 hours had elapsed since death."
        ),
        ss.PERIORAL_MODERATE: (
            "Electrical stimulation in the perioral region produced contraction confined to the perioral "
            "muscles. For estimating the time since death, Henssge’s compound method considers a perioral "
            "response irrespective of its extent; this finding suggests that no more than 11 hours had elapsed since death."
        ),
        ss.PERIORAL_SLIGHT: (
            "Electrical stimulation in the perioral region produced a focal response near the electrodes. "
            "For estimating the time since death, Henssge’s compound method considers a perioral response "
            "irrespective of its extent; this finding suggests that no more than 11 hours had elapsed since death."
        ),
        ss.OPTION_NO_REACTION: (
            "Electrical stimulation in the perioral region produced no appreciable muscular contraction. "
            "According to Henssge’s compound method, this finding suggests that more than 3 hours had elapsed since death."
        ),
        ss.OPTION_UNRELIABLE: (
            "Residual electrical excitability following perioral stimulation could not be assessed, "
            "or the findings are not reliable for estimating the time of death."
        ),
    },
    ss.PARAM_MECHANICAL_MUSCLE: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.MECH_WHOLE_MUSCLE: (
            "At the medico-legal examination, residual mechanical excitability was demonstrated by "
            "contraction of the whole biceps brachii muscle in response to percussion. This finding "
            "suggests that no more than 2 hours 30 minutes had elapsed since death."
        ),
        ss.MECH_REVERSIBLE_SWELLING: (
            "At the medico-legal examination, residual mechanical excitability was demonstrated by "
            "reversible swelling of the biceps brachii muscle in response to percussion. This finding "
            "suggests that no more than 5 hours had elapsed since death."
        ),
        ss.MECH_SMALL_PERSISTENT_SWELLING: (
            "At the medico-legal examination, residual mechanical excitability was demonstrated by a "
            "small persistent swelling of the biceps brachii muscle in response to percussion. This "
            "finding suggests that no more than 13 hours had elapsed since death."
        ),
        ss.OPTION_NO_REACTION: (
            "Percussion of the arm muscle produced no appreciable muscular response. This finding "
            "suggests that more than 1 hour 30 minutes had elapsed since death."
        ),
        ss.OPTION_UNRELIABLE: (
            "Mechanical excitability of skeletal muscle could not be assessed, or the findings are "
            "not reliable for estimating the time of death."
        ),
    },
    ss.PARAM_CHEMICAL_PUPILLARY: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.OPTION_UNRELIABLE: (
            "Pharmacological excitability of the iris could not be assessed, or the findings are "
            "not considered reliable for estimating the time of death."
        ),
        # Historical options retained for compatibility, not the current drug-specific menu.
        ss.PUPILLARY_POSITIVE: (
            "At the medico-legal examination, residual pharmacological excitability of the iris was "
            "demonstrated by pupillary dilatation in response to atropine injection. This response "
            "suggests that death occurred less than 30 hours before the medico-legal assessment."
        ),
        ss.PUPILLARY_NEGATIVE: (
            "At the medico-legal examination, no residual pharmacological response of the iris was "
            "observed following atropine injection (no increase in pupillary diameter). This response "
            "suggests that death occurred more than 5 hours before the medico-legal assessment."
        ),
        ss.PUPILLARY_ATROPINE_DILATION: (
            "Atropine injection produced pupillary dilatation. This persistence of pharmacological "
            "excitability of the iris suggests that death occurred less than 10 hours before assessment."
        ),
        ss.PUPILLARY_ATROPINE_NO_CHANGE: (
            "Atropine injection produced no appreciable change in pupillary diameter. The absence of "
            "a response suggests that at least 3 hours had elapsed since death at assessment."
        ),
        ss.PUPILLARY_TROPICAMIDE_DILATION: (
            "Tropicamide injection produced pupillary dilatation. This persistence of pharmacological "
            "excitability of the iris suggests that death occurred less than 30 hours before assessment."
        ),
        ss.PUPILLARY_TROPICAMIDE_NO_CHANGE: (
            "Tropicamide injection produced no appreciable change in pupillary diameter. The absence "
            "of a response suggests that at least 5 hours had elapsed since death at assessment."
        ),
        ss.PUPILLARY_ACETYLCHOLINE_REDUCTION: (
            "Acetylcholine injection produced pupillary constriction. This persistence of pharmacological "
            "excitability of the iris suggests that death occurred less than 46 hours before assessment."
        ),
        ss.PUPILLARY_ACETYLCHOLINE_NO_CHANGE: (
            "Acetylcholine injection produced no appreciable change in pupillary diameter. The absence "
            "of a response suggests that at least 14 hours had elapsed since death at assessment."
        ),
    },
}

SPECIAL_GRAPH_LABEL_BY_ID = {
    ss.PARAM_ELECTRICAL_SUPRACILIARY: "Supraciliary electrical response",
    ss.PARAM_ELECTRICAL_PERIORAL: "Perioral electrical response",
    ss.PARAM_MECHANICAL_MUSCLE: "Mechanical muscle response",
    ss.PARAM_CHEMICAL_PUPILLARY: "Pharmacological iris response",
}


def livor_description(state_id: str):
    return LIVOR_DESCRIPTION_BY_ID.get(state_id)


def livor_pressure_description(option_id: str):
    return LIVOR_PRESSURE_DESCRIPTION_BY_ID.get(option_id)


def rigor_description(state_id: str):
    return RIGOR_DESCRIPTION_BY_ID.get(state_id)


def special_description(param_id: str, option_id: str):
    return SPECIAL_DESCRIPTION_BY_ID[param_id].get(option_id)


def special_graph_label(param_id: str):
    return SPECIAL_GRAPH_LABEL_BY_ID[param_id]


def format_hours_minutes(h: int, m: int) -> str:
    if h > 0 and m > 0:
        return f"{h} {'hour' if h == 1 else 'hours'} {m} {'minute' if m == 1 else 'minutes'}"
    if h > 0:
        return f"{h} {'hour' if h == 1 else 'hours'}"
    if m > 0:
        return f"{m} {'minute' if m == 1 else 'minutes'}"
    return "0 minutes"


def format_hours_range(h1: int, m1: int, h2: int, m2: int) -> str:
    if h1 > 0 and h2 > 0 and m1 == 0:
        unit2 = "hour" if h2 == 1 else "hours"
        if m2 == 0:
            return f"between {h1} and {h2} {unit2}"
        unit1 = "hour" if h1 == 1 else "hours"
        return f"between {h1} {unit1} and {h2} {unit2} {m2} minutes"
    return f"between {format_hours_minutes(h1, m1)} and {format_hours_minutes(h2, m2)}"


_EXAMINATION = "the observations made during the medico-legal examination"


def simple_sentence_no_dt_not_over(duration: str) -> str:
    return f"<p><b>ESTIMATED TIME OF DEATH:</b> <b>no more than {duration} before</b> {_EXAMINATION}.</p>"


def simple_sentence_no_dt_over(duration: str) -> str:
    return f"<p><b>ESTIMATED TIME OF DEATH:</b> <b>more than {duration} before</b> {_EXAMINATION}.</p>"


def simple_sentence_no_dt_range(interval: str) -> str:
    return f"<p><b>ESTIMATED TIME OF DEATH:</b> <b>{interval} before</b> {_EXAMINATION}.</p>"


def _available_data_conclusion(window: str) -> str:
    return f"<p>Assessment of the available findings suggests that death occurred approximately {window}.</p>"


def _combined_conclusion(window: str) -> str:
    return (
        "<p>Combined assessment of the postmortem findings, integrating their time limits, "
        f"suggests that death occurred approximately {window}.</p>"
    )


def final_sentence_simple_over(duration: str, *, single_parameter: bool = False) -> str:
    render = _available_data_conclusion if single_parameter else _combined_conclusion
    return render(f"<b>more than {duration} before</b> {_EXAMINATION}")


def final_sentence_simple_not_over(duration: str, *, single_parameter: bool = False) -> str:
    render = _available_data_conclusion if single_parameter else _combined_conclusion
    return render(f"<b>no more than {duration} before</b> {_EXAMINATION}")


def final_sentence_simple_range(interval: str, *, single_parameter: bool = False) -> str:
    render = _available_data_conclusion if single_parameter else _combined_conclusion
    return render(f"<b>{interval} before</b> {_EXAMINATION}")


def _date_window(start_time, start_date, end_time, end_date, same_date):
    if same_date:
        return f"between {start_time} and {end_time} on {start_date}"
    return f"between {start_time} on {start_date} and {end_time} on {end_date}"


def simple_sentence_dt_not_over(duration: str, lower_time: str, lower_date: str,
                               inspection_time: str, inspection_date: str) -> str:
    window = _date_window(lower_time, lower_date, inspection_time, inspection_date, lower_date == inspection_date)
    return (
        f"<p><b>ESTIMATED TIME OF DEATH:</b> no more than {duration} before {_EXAMINATION}, "
        f"i.e. approximately {window}.</p>"
    )


def simple_sentence_dt_over(duration: str, cutoff_time: str, cutoff_date: str) -> str:
    return (
        f"<p><b>ESTIMATED TIME OF DEATH:</b> <b>more than {duration} before</b> {_EXAMINATION}, "
        f"i.e. <b>before {cutoff_time} on {cutoff_date}</b>.</p>"
    )


def simple_sentence_dt_range(interval: str, start_time: str, start_date: str,
                            end_time: str, end_date: str, same_date: bool) -> str:
    window = _date_window(start_time, start_date, end_time, end_date, same_date)
    return (
        f"<p><b>ESTIMATED TIME OF DEATH:</b> <b>{interval} before</b> {_EXAMINATION}, "
        f"i.e. approximately <b>{window}</b>.</p>"
    )


def final_sentence_dt_over(duration: str, cutoff_time: str, cutoff_date: str, *, single_parameter: bool = False) -> str:
    window = f"<b>before {cutoff_time} on {cutoff_date}</b>"
    if single_parameter:
        return _available_data_conclusion(window)
    return (
        "<p>Combined assessment of the postmortem findings suggests that death occurred approximately "
        f"<b>more than {duration} before</b> {_EXAMINATION}, i.e. {window}.</p>"
    )


def final_sentence_dt_not_over(duration: str, lower_time: str, lower_date: str,
                              inspection_time: str, inspection_date: str, *, single_parameter: bool = False) -> str:
    window = f"<b>after {lower_time} on {lower_date} (but before {inspection_time} on {inspection_date})</b>"
    if single_parameter:
        return _available_data_conclusion(window)
    return (
        "<p>Combined assessment of the postmortem findings, integrating their minimum and maximum time limits, "
        f"suggests that death occurred approximately <b>no more than {duration} before</b> {_EXAMINATION}, "
        f"i.e. {window}.</p>"
    )


def final_sentence_dt_range(interval: str, start_time: str, start_date: str,
                           end_time: str, end_date: str, same_date: bool, *, single_parameter: bool = False) -> str:
    window = _date_window(start_time, start_date, end_time, end_date, same_date)
    if single_parameter:
        return _available_data_conclusion(f"<b>{window}</b>")
    return (
        "<p>Combined assessment of the postmortem findings, integrating their minimum and maximum time limits, "
        f"suggests that death occurred approximately <b>{interval} before</b> {_EXAMINATION}, "
        f"i.e. approximately <b>{window}</b>.</p>"
    )


def putrefactive_paragraph() -> str:
    return (
        "<ul><li>The onset of postmortem decomposition, including putrefaction, is influenced by numerous "
        "external factors (e.g. ambient temperature and exposure to weather) and internal factors "
        "(e.g. body temperature, infection before death and the presence of wounds). As these changes "
        "may appear over a highly variable period, from a few hours to several weeks after death, "
        "their assessment does not allow the estimated time of death to be further refined.</li></ul>"
    )


def parameter_summary(labels: list[str]) -> str:
    if len(labels) == 1:
        label = labels[0]
        return f"<p style='color:blue;font-size:8pt;'>The overall estimate is based on the following parameter: {label[0].lower() + label[1:]}.</p>"
    joined = ", ".join(x[0].lower() + x[1:] for x in labels[:-1])
    joined += f" and {labels[-1][0].lower() + labels[-1][1:]}"
    return f"<p style='color:blue;font-size:8pt;'>The overall estimate is based on the following parameters: {joined}.</p>"


def potente_paragraph(duration: str, days: str, high_temperature: bool = False) -> str:
    if high_temperature:
        opening = (
            "At ambient temperatures above 23 °C, Henssge’s method is based on limited case series. "
            "The observed degree of body cooling does not permit a sufficiently reliable time interval to be estimated. "
        )
    else:
        opening = (
            "The observed degree of body cooling does not permit a sufficiently reliable time interval "
            "to be estimated using Henssge’s method. "
        )
    return (
        f"<ul><li>{opening}Under these conditions, the method proposed by Potente et al. allows only "
        "the minimum time since death to be estimated. Applied to this case, it suggests that at least "
        f"{duration} had elapsed since death at the time of the medico-legal examination.</li></ul>"
    )


def cooling_input_paragraph(*, inspection_time, inspection_date, ta_text: str, tr_text: str,
                            weight_text: str, t0_text: str, correction_description: str,
                            ambient_temperature_text: str | None = None) -> str:
    if inspection_time is None or inspection_date is None:
        title = "Temperatures measured during the medico-legal examination:"
    else:
        title = f"Temperatures measured during the medico-legal examination at approximately {inspection_time} on {inspection_date}:"
    return (
        "<ul><li>The following information was considered in the assessment of postmortem body cooling."
        f"<ul><li>{title}<ul>"
        f"<li>Ambient temperature: {ambient_temperature_text or ta_text + ' °C'}.</li>"
        f"<li>Rectal temperature: {tr_text} °C.</li></ul></li>"
        f"<li>Measured body weight: {weight_text} kg.</li>"
        f"<li>Assumed body temperature at death: {t0_text} °C.</li>"
        "<li>Corrective factor assumed on the basis of the known environmental conditions: "
        f"{correction_description}.</li></ul></li></ul>"
    )
