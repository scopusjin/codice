"""Human-readable date and time of separate tanatological observations."""

from datetime import datetime


def format_tanatology_measurement_datetime(moment: datetime) -> str:
    """Report the date even when the measurement and inspection share a day."""
    return f"alle ore {moment:%H:%M} del {moment:%d.%m.%Y}"
