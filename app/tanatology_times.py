"""Human-readable date and time of separate tanatological observations."""

from datetime import datetime


def format_tanatology_measurement_datetime(moment: datetime) -> str:
    """Report the date even when the measurement and inspection share a day."""
    from app.language import current_language
    if current_language() == "en":
        return f"at {moment:%H:%M} on {moment:%d.%m.%Y}"
    return f"alle ore {moment:%H:%M} del {moment:%d.%m.%Y}"
