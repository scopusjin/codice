"""Subpage headings consistent with the home page and shared mobile header."""
from html import escape

import streamlit as st


_PAGE_HEADING_CSS = """
<style>
.mortem-subpage-title {
    margin: 0 0 0.25rem !important;
    padding: 0 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    font-size: clamp(1.2rem, 1.25vw, 1.5rem) !important;
    font-weight: 650 !important;
    line-height: 1.25 !important;
    text-align: left !important;
    text-transform: uppercase !important;
}
@media (max-width: 768px) {
    .mortem-subpage-title {
        margin-bottom: 0 !important;
        font-size: 1.15rem !important;
        line-height: 1.05 !important;
    }
}
</style>
"""


def render_page_heading(text: str) -> None:
    """Render a single title; the existing mobile shell displays it in its header."""
    # A single element avoids a second, visually empty mobile layout slot.
    st.html(_PAGE_HEADING_CSS + f'<h1 class="mortem-full-title mortem-subpage-title">{escape(text)}</h1>')
