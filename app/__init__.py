# -*- coding: utf-8 -*-

import streamlit as st

import app.perioral_single_grid as _perioral_single_grid
import app.sopraciliare_ui as _sopraciliare_ui
from app.special_datetime_ui import install_special_datetime_ui
from app.special_heading_ui import install_special_heading_style
from app.supra_single_grid import install_supra_single_grid


_DECIMAL_POINT_SCRIPT = r"""
<script>
(() => {
  let hostWindow = window;
  let doc = document;
  try {
    if (window.parent && window.parent !== window) {
      hostWindow = window.parent;
      doc = hostWindow.document;
    }
  } catch (_) {
    hostWindow = window;
    doc = document;
  }

  const observerKey = "__mortemDecimalPointObserver";
  if (hostWindow[observerKey]) {
    hostWindow[observerKey].disconnect();
  }

  const selector = 'input[data-testid="stNumberInputField"]';

  function isDecimalInput(el) {
    const stepRaw = el.getAttribute("step");
    if (stepRaw && stepRaw !== "any") {
      const step = Number(stepRaw);
      if (Number.isFinite(step) && Math.abs(step - Math.trunc(step)) > 1e-12) {
        return true;
      }
    }
    return /[.,]/.test(el.value || "");
  }

  function canonicalize(raw) {
    let value = String(raw || "").replace(/,/g, ".");
    const negative = value.startsWith("-");
    value = value.replace(/-/g, "").replace(/[^0-9.]/g, "");
    const firstDot = value.indexOf(".");
    if (firstDot >= 0) {
      value = value.slice(0, firstDot + 1) + value.slice(firstDot + 1).replace(/\./g, "");
    }
    return (negative ? "-" : "") + value;
  }

  function normalize(el) {
    const original = el.value || "";
    const normalized = canonicalize(original);
    if (normalized === original) return;

    const start = el.selectionStart;
    el.value = normalized;
    if (start !== null && el.setSelectionRange) {
      const pos = Math.min(start, normalized.length);
      el.setSelectionRange(pos, pos);
    }
  }

  function patch(el) {
    if (!(el instanceof hostWindow.HTMLInputElement) || !isDecimalInput(el)) return;

    el.setAttribute("lang", "en-US");
    el.setAttribute("inputmode", "decimal");
    if (el.type !== "text") {
      el.type = "text";
    }

    if (el.dataset.mortemDecimalPointPatched !== "1") {
      el.dataset.mortemDecimalPointPatched = "1";
      el.addEventListener("input", (event) => {
        normalize(event.target);
      }, true);
    }
    normalize(el);
  }

  function scan(root = doc) {
    if (root.querySelectorAll) {
      root.querySelectorAll(selector).forEach(patch);
    }
  }

  scan();
  const observer = new hostWindow.MutationObserver(() => scan());
  observer.observe(doc.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["type", "step"],
  });
  hostWindow[observerKey] = observer;

  if (window === hostWindow && document.currentScript) {
    const container = document.currentScript.closest('[data-testid="stHtml"]');
    if (container) container.style.display = "none";
  }
})();
</script>
"""


def _install_decimal_point_inputs() -> None:
    """Forza il punto negli input numerici decimali senza cambiare i valori Python."""
    try:
        st.html(_DECIMAL_POINT_SCRIPT, unsafe_allow_javascript=True, width=1)
    except (AttributeError, TypeError):
        from streamlit.components.v1 import html as components_html
        components_html(_DECIMAL_POINT_SCRIPT, height=0, width=0)


# Tutte le pagine dell'app passano da set_page_config: installa la correzione
# subito dopo la configurazione, così vale anche dopo ogni rerun di Streamlit.
if not getattr(st.set_page_config, "_mortem_decimal_point_wrapper", False):
    _set_page_config_original = st.set_page_config

    def _set_page_config_with_decimal_point(*args, **kwargs):
        result = _set_page_config_original(*args, **kwargs)
        _install_decimal_point_inputs()
        return result

    _set_page_config_with_decimal_point._mortem_decimal_point_wrapper = True
    st.set_page_config = _set_page_config_with_decimal_point


# La tavola peribuccale originale lascia più bianco sotto i disegni rispetto
# alla sopraciliare. Manteniamo però bocca e mento integralmente visibili.
_perioral_single_grid._IMAGE_ONLY_FRACTION = 0.82

install_supra_single_grid(_sopraciliare_ui)
_perioral_single_grid.install_perioral_single_grid(_sopraciliare_ui)
_sopraciliare_ui.install_sopraciliare_click_selector()

_electrical_selectbox = st.selectbox


def _selectbox_with_perioral_grid(label, options, *args, **kwargs):
    if label == _sopraciliare_ui._PERIORAL_LABEL:
        return _sopraciliare_ui._render_perioral_tile_grid(
            widget_key=kwargs.get("key"),
            options=list(options),
        )
    return _electrical_selectbox(label, options, *args, **kwargs)


st.selectbox = _selectbox_with_perioral_grid
install_special_heading_style()
install_special_datetime_ui()
