"""English counterpart of every key in it_ui; values are presentation only."""

from __future__ import annotations


_TA_HELP = (
    "Consider the mean ambient temperature to which the body may have been exposed between death and "
    "examination. This is not necessarily the temperature measured at examination, particularly if the "
    "body is outdoors. If uncertain, enter a range: a wider temperature range results in a wider estimated time interval."
)

UI_TEXT = {
    "full.title": "ESTIMATION OF THE TIME SINCE DEATH",
    "full.add_datetime": "Add date/time of postmortem observations",
    "full.inspection_date": "Date of medico-legal examination:",
    "full.inspection_time": "Time of medico-legal examination (HH:MM):",
    "full.livor_heading": "Postmortem lividity",
    "full.livor_select_label": "Postmortem lividity:",
    "full.rigor_heading": "Rigor mortis",
    "full.rigor_select_label": "Rigor mortis:",
    "full.cooling_heading": "Postmortem body cooling",
    "full.prudent_toggle": "Variable conditions?",
    "full.henssge_not_applicable": "Henssge’s method not applicable",
    "full.henssge_not_applicable_help": (
        "Henssge’s method cannot be applied in the following circumstances:\n"
        "• It cannot be established that the body was found at the place of death.\n"
        "• A heat source is present close to the body, or underfloor heating is present beneath it.\n"
        "• Confirmed or suspected hypothermia (initial body temperature < 35 °C).\n"
        "• The mean ambient temperature cannot be determined.\n"
        "• The corrective factor cannot be estimated.\n"
        "• A substantial increase in ambient temperature (from low to high values)."
    ),
    "full.prudent_default_note": (
        "<div style='font-size:0.9rem; color:#444; padding:6px 8px; "
        "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
        "Use this mode when the mean ambient temperature and corrective factor may have changed over time "
        "or are uncertain. For each parameter, enter the two plausible endpoints of the range: the minimum "
        "and maximum values to be considered in the calculation. The CF panel helps identify the corrective "
        "factor to associate with each endpoint.</div>"
    ),
    "full.specify_range": "Specify a range",
    "full.ta_mean_label": f"Mean ambient temperature (°C): <span title='{_TA_HELP}'>ⓘ</span>",
    "full.ta_range_label": f"Range of mean ambient temperatures (°C): <span title='{_TA_HELP}'>ⓘ</span>",
    "full.ta_mean_help": _TA_HELP,
    "full.fc_label": "Corrective factor (CF):",
    "full.fc_range_label": "Corrective factor (CF) range:",
    "full.rectal_temp_label": "Rectal temperature (°C):",
    "full.antemortem_temp_label": "Antemortem temperature (°C):",
    "full.antemortem_temp_estimated_label": "Estimated antemortem temperature (°C):",
    "full.weight_label": "Weight (kg):",
    "full.weight_label_standard": "Weight (kg):",
    "full.weight_uncertainty": "±3 kg",
    "full.ta_input_label": "Ambient temperature (°C):",
    "full.ta_base_input": "Base Ta",
    "full.ta_other_input": "Other Ta endpoint",
    "full.fc_input_label": "Corrective factor:",
    "full.fc_min_input": "Min CF",
    "full.fc_max_input": "Max CF",
    "full.fc_input": "CF",
    "full.suggest_fc": "Suggest CF",
    "full.fc_suggested": "Suggested corrective factor: {value:.2f}",
    "full.fc_adjusted_for_weight": "Adjusted for {weight:.0f} kg (value for 70 kg: {base:.2f})",
    "full.use_this_factor": "✅ Use this factor",
    "full.add_to_fc_range": "➕ Add to CF range",
    "full.clothed_covered": "Clothed / covered?",
    "full.count_column": "Number?",
    "full.support_surface": "Supporting surface",
    "full.air_currents": "Moving air?",
    "full.add_special_data": "Additional postmortem findings",
    "full.special_datetime_hint": (
        "<div style='font-size:0.9rem; color:#666; padding:6px 8px; "
        "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
        "To specify observation times, enable <b>“Add date/time of postmortem observations”</b> above.</div>"
    ),
    "full.livor_pressure_label": "Blanching under finger pressure?",
    "full.assessed_different_time": "Assessed at a different time?",
    "full.measurement_date": "Observation date:",
    "full.measurement_time": "Observation time:",
    "full.measurement_time_input": "Observation time (HH:MM):",
    "full.putrefactive_changes": "Putrefactive changes?",
    "full.estimate_button": "Estimate time since death",
    "full.no_data_warning": "No data entered for estimation",
    "full.henssge_incoherent_warning": "Henssge’s method could not be applied (inconsistent or out-of-range temperatures).",
    "msil.page_title": "ESTIMATION OF THE TIME SINCE DEATH — MSIL",
    "msil.no_description": "<p style='opacity:.7'>No description available.</p>",
    "msil.add_datetime": "Add date/time of postmortem observations",
    "msil.inspection_date": "Date of medico-legal examination",
    "msil.inspection_time": "Time of medico-legal examination (HH:MM)",
    "msil.livor_select_label": "Postmortem lividity",
    "msil.livor_pressure_label": "Blanching under finger pressure?",
    "msil.rigor_select_label": "Rigor mortis",
    "msil.rectal_temp": "Rectal temperature (°C)",
    "msil.ta_mean": "Mean ambient temperature (°C)",
    "msil.weight": "Weight (kg)",
    "msil.fc_label": "Corrective factor (CF)",
    "msil.suggest_fc": "Suggest CF",
    "msil.clothed_covered": "Clothing / blankets over abdomen / pelvis?",
    "msil.item_column": "Item",
    "msil.count_column": "Number?",
    "msil.support_surface": "Supporting surface",
    "msil.air_currents": "Moving air?",
    "msil.estimate_button": "ESTIMATE TIME SINCE DEATH",
    "msil.recommendations_button": "ℹ️ Recommendations",
    "msil.recommendations_html": (
        '<div style="font-size:0.9rem; line-height:1.45; color:#444;">\n'
        "      <b>ASSESSMENT BASED ON POSTMORTEM BODY COOLING IS NOT APPLICABLE IF:</b><br><br>\n"
        "      • Place of examination / discovery ≠ place of death.<br>\n"
        "      • Heat sources are present close to the body.<br>\n"
        "      • Underfloor heating is present beneath the body.<br>\n"
        "      • Hypothermia is confirmed or suspected (initial temperature < 35 °C).<br>\n"
        "      • The mean ambient temperature cannot be determined, or the temperature has increased substantially since death.<br>\n"
        "      • The corrective factor cannot be estimated.<br><br>\n"
        "      <b>REMEMBER:</b><br><br>\n"
        "      • Do not simply use the measured ambient temperature. Consider how temperature changed between death and examination "
        "(did it rise during the day? was it colder at night?). Estimate the mean temperature to which the body may have been exposed. "
        "Consider any available meteorological data.<br>\n"
        "      • Shifting and blanching under finger pressure are distinct findings. Shifting is assessed after repositioning the body; "
        "finger pressure is used to assess whether lividity blanches completely.<br>\n"
        "      • When selecting the corrective factor, consider only clothing and coverings over the lower trunk. The suggested "
        "corrective factor is a guide. Try different combinations and a range of factors.<br>\n"
        "      • By default, as a precaution, the application allows for possible variations of ±1 °C in the entered ambient temperature, "
        "± 0.1 in the corrective factor and ±3 kg in the estimated body weight.<br><br>\n"
        "    </div>"
    ),
    "graph.missing_inspection_datetime_html": "<p style='color:red;font-weight:bold;'>⚠️ Enter the date and time of the medico-legal examination.</p>",
    "graph.invalid_inspection_time_html": "<p style='color:red;font-weight:bold;'>⚠️ Invalid examination time format. Use HH:MM.</p>",
    "graph.invalid_weight": "⚠️ Invalid body weight. Enter a value > 0 kg.",
    "graph.invalid_factor": "⚠️ Invalid corrective factor. Enter a value > 0.",
    "graph.missing_temperatures": "⚠️ Temperatures are missing.",
    "graph.invalid_special_time": "⚠️ {parameter}: excluded because '{time}' is not a valid time (use HH:MM).",
    "graph.missing_special_description": "No description found for '{state}'.",
    "graph.special_without_range": "{parameter} ({state}) has no defined time range.",
    "graph.no_useful_data": "Insufficient data for estimation",
    "graph.shifted_ranges_note": 'Some parameters were assessed at different times; ranges marked with "*" have been shifted to a common reference time for comparison.',
    "graph.special_time_context_singular": "assessment of the postmortem finding, performed {measurement_when} (temperature measurements {reference_when})",
    "graph.special_time_context_plural": "assessments of the postmortem finding, performed {measurement_when} (temperature measurements {reference_when})",
    "graph.special_time_context_fallback": "Observation made {measurement_when} (temperature measurements {reference_when}).",
    "graph.henssge_missing_invalid": "Henssge’s method for postmortem body cooling could not be applied: missing or invalid data.",
    "graph.henssge_incoherent": "Henssge’s method for postmortem body cooling could not be applied: inconsistent or out-of-range data",
    "graph.henssge_equal_temperature_warning": "Rectal and ambient temperatures are equal: Henssge’s method is not applicable because there is no thermal gradient.",
    "graph.henssge_equal_temperature_detail": (
        "<ul><li>Rectal and ambient temperatures are both <b>{temperature} °C</b>. This suggests that the body "
        "has reached thermal equilibrium with its surroundings, which precludes application of Henssge’s method.</li></ul>"
    ),
    "graph.henssge_below_ambient_warning": "Rectal temperature is below ambient temperature: Henssge’s method is not applicable. Check the entered data.",
    "graph.henssge_below_ambient_detail": (
        "<ul><li>The mean ambient temperature exceeds the rectal temperature; therefore, an estimate of the time "
        "of death based on postmortem body cooling cannot be made. Check that the measurements and entered data "
        "are correct; alternatively, the body may have reached thermal equilibrium with its surroundings, followed "
        "by a change in environmental conditions. Remember to use the mean ambient temperature (which may be lower "
        "than the temperature measured during the medico-legal examination).</li></ul>"
    ),
    "graph.high_ambient_factor_warning": "At ambient temperatures &gt; 25 °C, changes in the corrective factor may substantially affect the results.",
    "graph.low_ambient_factor_warning": "At ambient temperatures &lt; 18 °C, selecting a corrective factor other than 1 may substantially affect the results.",
    "graph.rigor_low_temperature_warning": "Low ambient temperature may slow the course of rigor mortis and prolong its persistence.",
    "graph.rigor_high_temperature_warning": "High ambient temperature may accelerate the onset and subsequent resolution of rigor mortis.",
    "graph.thermal_equilibrium_warning": "The difference between rectal and ambient temperatures is minimal, so the body may already have reached thermal equilibrium with its surroundings. Interpret the estimate based on postmortem body cooling with caution.",
    "graph.plateau_warning": "The rectal temperature is very close to the estimated antemortem temperature, suggesting that body cooling has not yet begun and/or is in the temperature plateau phase. The precision of the method is reduced during this phase.",
    "graph.discordant_html": "<p style='color:red;font-weight:bold;'>⚠️ Estimates based on individual postmortem findings are discordant.</p>",
    "graph.discordant_detail_html": "<ul><li><b>⚠️ Estimates based on individual postmortem findings are discordant.</b></li></ul>",
    "graph.descriptions_popover": "📖 Detailed descriptions",
    "graph.warnings_popover": "⚠️ Warnings",
    "graph.plot_expander": "Show graph",
    "graph.parameter_livor": "Postmortem lividity",
    "graph.parameter_rigor": "Rigor mortis",
    "graph.parameter_cooling": "postmortem body cooling",
    "graph.parameter_cooling_prudent_open": "postmortem body cooling (conservative estimate: no upper time limit)",
    "graph.parameter_cooling_potente": "postmortem body cooling (minimum time since death according to Potente et al.)",
    "plot.livor": "Lividity",
    "plot.rigor": "Rigor mortis",
    "plot.cooling": "Body cooling",
    "plot.generic_parameter": "Parameter",
    "plot.hours_since_death": "Hours since death",
    "data.weight_table_missing": "Body-weight correction table not found; continuing without it.",
    "data.openpyxl_missing": "Reading the .xlsx file requires 'openpyxl'. Install it with: pip install openpyxl",
    "data.weight_table_read_error": "Unable to read the body-weight table from Excel: {error}",
}


def ui_text(key: str, **values) -> str:
    text = UI_TEXT[key]
    return text.format(**values) if values else text


__all__ = ["UI_TEXT", "ui_text"]
