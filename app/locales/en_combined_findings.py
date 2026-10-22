"""English prose for existing combined findings; accepts already calculated bounds."""

from app.locales.en import LIVOR_DESCRIPTION_BY_ID


def livor_with_pressure(state_id, pressure, lower, upper, open_upper):
    finding = LIVOR_DESCRIPTION_BY_ID[state_id].split('. ', 1)[0].rstrip('.')
    blanching = "blanched completely" if pressure == "complete_fading" else "did not blanch completely"
    if open_upper:
        qualifier = "more than" if state_id == "livor_fixed" else "at least"
        limit = f"{qualifier} {lower:g} {'hour' if lower == 1 else 'hours'}"
    elif lower <= 0:
        limit = f"less than {upper:g} hours"
    else:
        limit = f"between {lower:g} and {upper:g} hours"
    return (f"{finding}; it {blanching} under finger pressure. "
            "According to the time limits reported in the scientific literature, "
            f"this suggests that {limit} had elapsed since death.")


def rigor_with_reformation(state_id, lower, upper):
    finding = "developing, increasing in intensity and becoming generalised" if state_id == "rigor_developing" else "present and generalised"
    minimum = "30 minutes" if lower == 0.5 else f"{lower:g} hours"
    return (f"Rigor mortis is considered to have been {finding} at the time of the medico-legal examination, "
            "and to have re-established after being broken by forced manipulation. "
            "According to the minimum and maximum time limits reported in the scientific literature, "
            f"this suggests that between {minimum} and {upper:g} hours had elapsed since death.")
