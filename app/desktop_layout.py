"""Desktop page layout based on available content width, including the sidebar."""

DESKTOP_LAYOUT_CSS = """
<style>
@media (min-width: 769px) {
  /* The ID scopes this layout to Full desktop, above older widget-level CSS. */
  html body:has(#mortem-page-title) [data-testid="stMainBlockContainer"] {
    box-sizing: border-box !important;
    container: mortem-desktop / inline-size;
    width: 100% !important;
    max-width: 100rem !important;
    margin-inline: auto !important;
    padding: 4.5rem clamp(1rem, 2vw, 2.5rem) 2rem !important;
  }
  html body:has(#mortem-page-title) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    display: grid !important;
    position: static !important;
    grid-template-columns: minmax(0, 1fr) !important;
    grid-auto-flow: row !important;
    width: 100% !important;
    max-width: 52rem !important;
    gap: 0.45rem !important;
    align-items: start !important;
  }
  html body:has(#mortem-page-title) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {
    grid-column: 1 !important;
    grid-row: auto !important;
    position: static !important;
    inset: auto !important;
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;
    margin: 0 !important;
    z-index: auto !important;
  }
  #mortem-page-title {
    margin: 0 0 0.35rem !important;
    padding: 0 !important;
    font-size: clamp(1.2rem, 1.25vw, 1.5rem) !important;
    font-weight: 650 !important;
    line-height: 1.25 !important;
  }
  @container mortem-desktop (min-width: 70rem) {
    html body:has(#mortem-page-title) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
      max-width: none !important;
      grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr) !important;
      column-gap: clamp(1rem, 2vw, 2rem) !important;
    }
    html body:has(#mortem-page-title) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:has(#mortem-page-title) {
      grid-column: 1 / -1 !important;
      grid-row: 1 !important;
    }
    html body:has(#mortem-page-title) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:has([class~="st-key-btn_stima"]) {
      grid-column: 2 !important;
      grid-row: 2 !important;
    }
    html body:has(#mortem-page-title) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :is(.st-key-mortem_result_box, *:has(.st-key-mortem_result_box), .st-key-mortem_no_data_box, *:has(.st-key-mortem_no_data_box)) {
      grid-column: 2 !important;
      grid-row: 3 / span 12 !important;
    }
  }
}
</style>
"""
