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
            f"The combined findings suggest {limit} since death, based on published time limits.")


def rigor_with_reformation(state_id, lower, upper):
    finding = "developing, with increasing intensity and extent" if state_id == "rigor_developing" else "fully developed and generalised"
    minimum = "30 minutes" if lower == 0.5 else f"{lower:g} hours"
    return (f"Rigor mortis was {finding}. It re-established after being broken by forced manipulation. "
            f"Published limits suggest a postmortem interval between {minimum} and {upper:g} hours.")
