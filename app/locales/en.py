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
    ts.LIVOR_CONFLUENT_FULLY_MIGRATABLE: "Confluent, with complete shifting",
    ts.LIVOR_FULLY_MIGRATABLE: "Complete shifting (confluence unspecified)",
    ts.LIVOR_PARTIALLY_MIGRATABLE: "Incomplete shifting",
    ts.LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: "Shifting present (extent unspecified)",
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
        "Postmortem lividity had not yet developed. Published limits suggest less than 3 hours "
        "since death (usual onset: 15–20 minutes)."
    ),
    ts.LIVOR_CONFLUING: (
        "Postmortem lividity was becoming confluent. Published limits suggest less than 4 hours "
        "since death (this stage is usually seen between 1 hour 30 minutes and 3 hours 30 minutes)."
    ),
    ts.LIVOR_CONFLUENT: (
        "Postmortem lividity was confluent (shifting not assessed or specified). "
        "This suggests at least 1 hour since death, without an upper time limit."
    ),
    ts.LIVOR_CONFLUENT_FULLY_MIGRATABLE: (
        "Postmortem lividity was confluent and shifted completely after repositioning. "
        "Published limits suggest a postmortem interval between 1 and 6 hours."
    ),
    ts.LIVOR_FULLY_MIGRATABLE: (
        "Postmortem lividity shifted completely after repositioning (confluence unspecified). "
        "Published limits suggest less than 6 hours since death."
    ),
    ts.LIVOR_PARTIALLY_MIGRATABLE: (
        "Postmortem lividity showed incomplete shifting after repositioning. "
        "Published limits suggest a postmortem interval between 4 and 24 hours."
    ),
    ts.LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: (
        "Postmortem lividity shifted after repositioning, but whether shifting was complete "
        "or incomplete could not be determined. Published limits suggest less than 24 hours since death."
    ),
    ts.LIVOR_FIXED: (
        "Postmortem lividity was fixed. Published limits suggest more than 4 hours since death "
        "(lividity may fade without shifting after repositioning for up to 30 hours)."
    ),
    ts.LIVOR_UNRELIABLE: "Postmortem lividity was not assessed or was unreliable for time-since-death estimation.",
}

LIVOR_PRESSURE_DESCRIPTION_BY_ID = {
    PRESSURE_COMPLETE_FADING: (
        "Postmortem lividity blanched completely under finger pressure, "
        "providing an upper postmortem time limit of 20 hours."
    ),
    PRESSURE_INCOMPLETE_FADING: (
        "Postmortem lividity did not blanch completely under finger pressure, "
        "providing a lower postmortem time limit of 1 hour."
    ),
}

RIGOR_DESCRIPTION_BY_ID = {
    ts.RIGOR_NOT_ASSESSED: "Rigor mortis was not assessed.",
    ts.RIGOR_ABSENT: (
        "Rigor mortis had not yet developed. Published limits suggest less than 7 hours "
        "since death (mean onset: 2–3 hours)."
    ),
    ts.RIGOR_DEVELOPING: (
        "Rigor mortis was developing, increasing in intensity and extent. Published limits suggest "
        "at least 30 minutes but less than 20 hours since death (usually fully developed within 6–10 hours)."
    ),
    ts.RIGOR_FULL: (
        "Rigor mortis was fully developed and generalised. Published limits suggest at least 2 hours "
        "but less than 96 hours (4 days) since death. Resolution begins after 57 hours on average "
        "(approximately 2 and a half days)."
    ),
    ts.RIGOR_RESOLVING: (
        "Rigor mortis was resolving. Published limits suggest at least 24 hours but less than "
        "192 hours (8 days) since death. On average, resolution begins after 57 hours "
        "(approximately 2 and a half days) and is complete within 76 hours (just over 3 days)."
    ),
    ts.RIGOR_RESOLVED: (
        "Rigor mortis had resolved. Published limits suggest at least 24 hours since death "
        "(mean time to disappearance: 76 hours, just over 3 days)."
    ),
    ts.RIGOR_UNRELIABLE: "Rigor mortis was not assessed or was unreliable for time-since-death estimation.",
}

SPECIAL_DESCRIPTION_BY_ID = {
    ss.PARAM_ELECTRICAL_SUPRACILIARY: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.SUPRA_PHASE_I: (
            "Supraciliary electrical stimulation produced a slight contraction of less than 1/3 of "
            "the upper eyelid, consistent with a postmortem interval of more than 5 hours but less than 22 hours."
        ),
        ss.SUPRA_PHASE_II: (
            "Supraciliary electrical stimulation produced contraction of less than 2/3 of the upper eyelid, "
            "consistent with a postmortem interval of more than 3 hours 30 minutes but less than 16 hours."
        ),
        ss.SUPRA_PHASE_III: (
            "Supraciliary electrical stimulation produced contraction of the entire upper eyelid, "
            "consistent with a postmortem interval of more than 3 hours but less than 13 hours."
        ),
        ss.SUPRA_PHASE_IV: (
            "Supraciliary electrical stimulation produced generalised contraction of the upper and lower "
            "orbicularis oculi, consistent with a postmortem interval of more than 2 hours but less than 8 hours."
        ),
        ss.SUPRA_PHASE_V: (
            "Supraciliary electrical stimulation produced generalised contraction of the forehead and orbital "
            "muscles, consistent with a postmortem interval of more than 1 hour but less than 7 hours."
        ),
        ss.SUPRA_PHASE_VI: (
            "Supraciliary electrical stimulation produced generalised contraction of the forehead, orbital "
            "and cheek muscles, consistent with a postmortem interval of less than 6 hours."
        ),
        ss.OPTION_NO_REACTION: (
            "Supraciliary electrical stimulation produced no muscular contraction. "
            "This suggests only a lower time limit: more than 5 hours since death."
        ),
        ss.OPTION_UNRELIABLE: "Supraciliary electrical excitability could not be assessed or was unreliable.",
    },
    ss.PARAM_ELECTRICAL_PERIORAL: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.PERIORAL_MARKED: (
            "Perioral electrical stimulation produced generalised facial muscle contraction. "
            "In Henssge’s compound method, any perioral response suggests no more than 11 hours "
            "since death, regardless of its extent."
        ),
        ss.PERIORAL_MODERATE: (
            "Perioral electrical stimulation produced contraction confined to the perioral muscles. "
            "In Henssge’s compound method, any perioral response suggests no more than 11 hours "
            "since death, regardless of its extent."
        ),
        ss.PERIORAL_SLIGHT: (
            "Perioral electrical stimulation produced a focal response near the electrodes. "
            "In Henssge’s compound method, any perioral response suggests no more than 11 hours "
            "since death, regardless of its extent."
        ),
        ss.OPTION_NO_REACTION: (
            "Perioral electrical stimulation produced no appreciable muscular contraction. "
            "Henssge’s compound method associates this finding with more than 3 hours since death."
        ),
        ss.OPTION_UNRELIABLE: "Perioral electrical excitability could not be assessed or was unreliable for time-since-death estimation.",
    },
    ss.PARAM_MECHANICAL_MUSCLE: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.MECH_WHOLE_MUSCLE: (
            "Percussion of the biceps brachii produced contraction of the whole muscle, "
            "consistent with no more than 2 hours 30 minutes since death."
        ),
        ss.MECH_REVERSIBLE_SWELLING: (
            "Percussion of the biceps brachii produced reversible muscular swelling, "
            "consistent with no more than 5 hours since death."
        ),
        ss.MECH_SMALL_PERSISTENT_SWELLING: (
            "Percussion of the biceps brachii produced a small persistent muscular swelling, "
            "consistent with no more than 13 hours since death."
        ),
        ss.OPTION_NO_REACTION: (
            "Percussion of the arm muscle produced no appreciable response, "
            "suggesting more than 1 hour 30 minutes since death."
        ),
        ss.OPTION_UNRELIABLE: "Mechanical muscle excitability could not be assessed or was unreliable for time-since-death estimation.",
    },
    ss.PARAM_CHEMICAL_PUPILLARY: {
        ss.OPTION_NOT_ASSESSED: None,
        ss.OPTION_UNRELIABLE: "Pharmacological iris excitability could not be assessed or was unreliable for time-since-death estimation.",
        # Historical options retained for compatibility, not the current drug-specific menu.
        ss.PUPILLARY_POSITIVE: (
            "Atropine injection produced pupillary dilatation, "
            "consistent with a postmortem interval of less than 30 hours."
        ),
        ss.PUPILLARY_NEGATIVE: (
            "Atropine injection produced no increase in pupillary diameter, "
            "suggesting more than 5 hours since death."
        ),
        ss.PUPILLARY_ATROPINE_DILATION: (
            "Atropine injection produced pupillary dilatation, "
            "consistent with a postmortem interval of less than 10 hours."
        ),
        ss.PUPILLARY_ATROPINE_NO_CHANGE: (
            "Atropine injection produced no appreciable change in pupillary diameter, "
            "suggesting at least 3 hours since death."
        ),
        ss.PUPILLARY_TROPICAMIDE_DILATION: (
            "Tropicamide injection produced pupillary dilatation, "
            "consistent with a postmortem interval of less than 30 hours."
        ),
        ss.PUPILLARY_TROPICAMIDE_NO_CHANGE: (
            "Tropicamide injection produced no appreciable change in pupillary diameter, "
            "suggesting at least 5 hours since death."
        ),
        ss.PUPILLARY_ACETYLCHOLINE_REDUCTION: (
            "Acetylcholine injection produced pupillary constriction, "
            "consistent with a postmortem interval of less than 46 hours."
        ),
        ss.PUPILLARY_ACETYLCHOLINE_NO_CHANGE: (
            "Acetylcholine injection produced no appreciable change in pupillary diameter, "
            "suggesting at least 14 hours since death."
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


_EXAMINATION = "the medico-legal examination"


def simple_sentence_no_dt_not_over(duration: str) -> str:
    return f"<p><b>ESTIMATED TIME SINCE DEATH:</b> <b>no more than {duration}</b> at the time of {_EXAMINATION}.</p>"


def simple_sentence_no_dt_over(duration: str) -> str:
    return f"<p><b>ESTIMATED TIME SINCE DEATH:</b> <b>more than {duration}</b> at the time of {_EXAMINATION}.</p>"


def simple_sentence_no_dt_range(interval: str) -> str:
    return f"<p><b>ESTIMATED TIME SINCE DEATH:</b> <b>{interval}</b> at the time of {_EXAMINATION}.</p>"


def _available_data_conclusion(window: str) -> str:
    return f"<p>The available findings suggest that death occurred approximately {window}.</p>"


def _combined_conclusion(window: str) -> str:
    return (
        "<p>Combined assessment of the postmortem findings "
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
        "<p>Combined assessment of the postmortem findings "
        f"suggests that death occurred approximately <b>no more than {duration} before</b> {_EXAMINATION}, "
        f"i.e. {window}.</p>"
    )


def final_sentence_dt_range(interval: str, start_time: str, start_date: str,
                           end_time: str, end_date: str, same_date: bool, *, single_parameter: bool = False) -> str:
    window = _date_window(start_time, start_date, end_time, end_date, same_date)
    if single_parameter:
        return _available_data_conclusion(f"<b>{window}</b>")
    return (
        "<p>Combined assessment of the postmortem findings "
        f"suggests that death occurred approximately <b>{interval} before</b> {_EXAMINATION}, "
        f"i.e. <b>{window}</b>.</p>"
    )


def putrefactive_paragraph() -> str:
    return (
        "<ul><li>Putrefactive changes cannot refine this estimate: their onset varies from a few hours "
        "to several weeks after death. Relevant factors include ambient temperature, weather exposure, "
        "body temperature, infection before death and wounds.</li></ul>"
    )


def parameter_summary(labels: list[str]) -> str:
    if len(labels) == 1:
        label = labels[0]
        return f"<p style='color:blue;font-size:8pt;'>Estimate based on: {label[0].lower() + label[1:]}.</p>"
    joined = ", ".join(x[0].lower() + x[1:] for x in labels[:-1])
    joined += f" and {labels[-1][0].lower() + labels[-1][1:]}"
    return f"<p style='color:blue;font-size:8pt;'>Estimate based on: {joined}.</p>"


def potente_paragraph(duration: str, days: str, high_temperature: bool = False) -> str:
    if high_temperature:
        opening = (
            "At ambient temperatures above 23 °C, Henssge’s method is based on limited case series. "
            "The observed degree of cooling does not support a sufficiently reliable time interval. "
        )
    else:
        opening = (
            "At this degree of cooling, Henssge’s method cannot provide a sufficiently reliable time interval. "
        )
    return (
        f"<ul><li>{opening}The method of Potente et al. estimates only the minimum time since death. "
        f"Here, it suggests that at least {duration} had elapsed at examination.</li></ul>"
    )


def cooling_input_paragraph(*, inspection_time, inspection_date, ta_text: str, tr_text: str,
                            weight_text: str, t0_text: str, correction_description: str,
                            ambient_temperature_text: str | None = None) -> str:
    if inspection_time is None or inspection_date is None:
        title = "Temperatures measured at examination:"
    else:
        title = f"Temperatures measured at approximately {inspection_time} on {inspection_date}:"
    return (
        "<ul><li>Postmortem body cooling was assessed using:"
        f"<ul><li>{title}<ul>"
        f"<li>Ambient temperature: {ambient_temperature_text or ta_text + ' °C'}.</li>"
        f"<li>Rectal temperature: {tr_text} °C.</li></ul></li>"
        f"<li>Measured body weight: {weight_text} kg.</li>"
        f"<li>Assumed body temperature at death: {t0_text} °C.</li>"
        "<li>Corrective factor (assumed from the known conditions): "
        f"{correction_description.rstrip('.')}.</li></ul></li></ul>"
    )
