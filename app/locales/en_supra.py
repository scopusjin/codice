"""English details for the supraciliary grid; interval notation is shared."""

from app import special_tanatology_states as ss
from app.locales.it_supra import SUPRA_GRID_DETAIL_BY_ID as _IT_DETAILS


_LABELS = {
    ss.SUPRA_PHASE_VI: "Forehead + orbit + cheek",
    ss.SUPRA_PHASE_V: "Forehead + orbit",
    ss.SUPRA_PHASE_IV: "Upper + lower orbicularis oculi",
    ss.SUPRA_PHASE_III: "Entire upper eyelid",
    ss.SUPRA_PHASE_II: "< 2/3 of upper eyelid",
    ss.SUPRA_PHASE_I: "< 1/3 of upper eyelid",
    ss.OPTION_NO_REACTION: "",
    ss.OPTION_UNRELIABLE: "",
    ss.OPTION_NOT_ASSESSED: "",
}
SUPRA_GRID_DETAIL_BY_ID = {
    option: (label, _IT_DETAILS[option][1]) for option, label in _LABELS.items()
}
