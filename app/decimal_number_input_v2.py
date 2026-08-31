# -*- coding: utf-8 -*-
"""Renderer frameless V2 per gli input decimali della sola Full mobile."""

import math

import streamlit as st


_FULL_MOBILE_COMPONENT_KEYS = {
    "mortem_decimal_rt_val",
    "mortem_decimal_tm_val",
    "mortem_decimal_peso",
    "mortem_decimal_ta_base_val",
    "mortem_decimal_ta_other_val",
    "mortem_decimal_fattore_correzione",
    "mortem_decimal_fc_min_val",
    "mortem_decimal_fc_other_val",
    "mortem_decimal_fcpanel_std_strati_sottili",
    "mortem_decimal_fcpanel_std_strati_spessi",
    "mortem_decimal_fcpanel_std_coperte_medie",
    "mortem_decimal_fcpanel_std_coperte_pesanti",
    "mortem_decimal_fcpanel_caut_strati_sottili",
    "mortem_decimal_fcpanel_caut_strati_spessi",
    "mortem_decimal_fcpanel_caut_coperte_medie",
    "mortem_decimal_fcpanel_caut_coperte_pesanti",
}

_HTML = r"""
<div class="number-control compact-mobile">
  <span class="mobile-label"></span>
  <button class="temperature-help" type="button" aria-label="Informazioni sulla temperatura ambientale"><span>?</span></button>
  <input class="number-input" type="text" inputmode="decimal" autocomplete="off" />
  <span class="mobile-unit"></span>
  <button class="step-button number-minus" type="button" aria-label="Diminuisci">−</button>
  <button class="step-button number-plus" type="button" aria-label="Aumenta">+</button>
  <button class="suggest-button suggest-action" type="button" aria-label="Suggerisci fattore di correzione"></button>
</div>
"""

_CSS = r"""
.number-control {
  box-sizing: border-box;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 3rem 1.5rem 1.8rem 1.8rem 4.4rem;
  grid-template-rows: 1fr;
  align-items: stretch;
  width: 100%;
  height: 40px;
  min-width: 0;
  overflow: hidden;
  border: 1px solid transparent;
  border-radius: 8px;
  background: var(--st-secondary-background-color, #F0F2F6);
  color: var(--st-text-color, #31333F);
}
.number-control.external-action {
  grid-template-columns: minmax(0, 1fr) 3rem 1.5rem 1.8rem 1.8rem;
}
.number-control:hover {
  border-color: color-mix(in srgb, var(--st-primary-color, #168AC1) 45%, transparent);
}
.number-control:focus-within {
  border-color: var(--st-primary-color, #168AC1);
  box-shadow: 0 0 0 1px var(--st-primary-color, #168AC1);
}
.mobile-label {
  box-sizing: border-box;
  grid-column: 1;
  grid-row: 1;
  display: flex;
  min-width: 0;
  align-items: center;
  padding: 0 5px 0 8px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-family: var(--st-font, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
  font-size: 0.82rem;
  font-weight: 400;
  line-height: 1.1;
}
.number-control.has-help .mobile-label {
  padding-right: 24px;
}
.number-input {
  box-sizing: border-box;
  grid-column: 2;
  grid-row: 1;
  width: 100%;
  min-width: 0;
  height: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: inherit;
  padding: 0 3px 0 1px;
  text-align: right;
  font-family: var(--st-font, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.2;
}
.number-control:not(.is-dense) .number-input {
  border: 1px solid #d6ad21;
  border-radius: 6px;
}
.number-control:not(.is-dense).has-unit .number-input {
  border-right: 0;
  border-radius: 6px 0 0 6px;
}
.number-control:not(.is-dense).has-unit .mobile-unit {
  border: 1px solid #d6ad21;
  border-left: 0;
  border-radius: 0 6px 6px 0;
}
.mobile-unit {
  box-sizing: border-box;
  grid-column: 3;
  grid-row: 1;
  display: flex;
  width: 100%;
  min-width: 0;
  align-items: center;
  justify-content: flex-start;
  padding: 0 1px;
  white-space: nowrap;
  font-family: var(--st-font, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
  font-size: 0.80rem;
  font-weight: 400;
  line-height: 1.1;
  opacity: 0.82;
}
.mobile-unit:empty {
  display: flex;
  visibility: hidden;
}
.step-button,
.suggest-button,
.temperature-help {
  box-sizing: border-box;
  height: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: inherit;
  padding: 0;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
.number-minus {
  grid-column: 4;
  grid-row: 1;
}
.number-plus {
  grid-column: 5;
  grid-row: 1;
}
.step-button {
  width: 100%;
  min-width: 0;
  font-family: var(--st-font, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1;
}
.temperature-help {
  grid-column: 1;
  grid-row: 1;
  display: none;
  width: 22px;
  justify-self: end;
  align-items: center;
  justify-content: center;
  margin: 0 2px 0 0;
  z-index: 2;
  font: 600 0.78rem var(--st-font, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
}
.temperature-help.is-visible { display: flex; }
.temperature-help > span {
  box-sizing: border-box;
  display: inline-flex;
  width: 18px;
  height: 18px;
  align-items: center;
  justify-content: center;
  border: 1px solid color-mix(in srgb, var(--st-text-color, #31333F) 58%, transparent);
  border-radius: 50%;
  line-height: 1;
  opacity: 0.8;
}
.suggest-button {
  grid-column: 6;
  grid-row: 1;
  display: none;
  width: 100%;
  min-width: 0;
  align-items: center;
  justify-content: center;
  border-left: 1px solid color-mix(in srgb, var(--st-text-color, #31333F) 12%, transparent);
  padding: 0 4px;
  white-space: nowrap;
  font-family: var(--st-font, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
  font-size: 0.76rem;
  font-weight: 500;
  line-height: 1;
}
.suggest-button.is-visible,
.number-control.reserve-action .suggest-button {
  display: flex;
}
.number-control.reserve-action:not(.has-suggest) .suggest-button {
  visibility: hidden;
  pointer-events: none;
}
.number-control.external-action .suggest-button {
  display: none !important;
}
.suggest-button.is-visible.is-active {
  background: color-mix(in srgb, var(--st-primary-color, #168AC1) 14%, transparent);
  color: var(--st-primary-color, #168AC1);
  font-weight: 650;
}
.step-button:hover:not(:disabled),
.suggest-button:hover:not(:disabled),
.temperature-help:hover:not(:disabled),
.step-button:active:not(:disabled),
.suggest-button:active:not(:disabled),
.temperature-help:active:not(:disabled) {
  background: color-mix(in srgb, var(--st-text-color, #31333F) 9%, transparent);
}
.step-button:disabled,
.suggest-button:disabled,
.temperature-help:disabled {
  cursor: default;
  opacity: 0.32;
}
.number-control.is-disabled { opacity: 0.65; }
.number-control.is-dense {
  grid-template-columns: minmax(0, 1fr) 38px 0 30px 30px;
  height: 34px;
  border-radius: 7px;
  background: color-mix(in srgb, var(--st-primary-color, #168AC1) 16%, var(--st-secondary-background-color, #F0F2F6));
}
.number-control.is-dense .mobile-label {
  padding-left: 8px;
  padding-right: 4px;
  font-size: 0.79rem;
}
.number-control.is-dense .number-input {
  width: 100%;
  min-width: 0;
  padding-right: 4px;
  font-size: 0.90rem;
}
.number-control.is-dense .mobile-unit {
  width: 0;
  padding: 0;
  overflow: hidden;
}
.number-control.is-dense .step-button {
  width: 100%;
  min-width: 0;
  font-size: 1.02rem;
}
.number-control.is-dense .suggest-button {
  display: none !important;
}
"""

_JS = r"""
export default function({ parentElement, data, setStateValue, setTriggerValue }) {
  const control = parentElement.querySelector('.number-control');
  const label = parentElement.querySelector('.mobile-label');
  const input = parentElement.querySelector('.number-input');
  const unit = parentElement.querySelector('.mobile-unit');
  const minusButton = parentElement.querySelector('.number-minus');
  const plusButton = parentElement.querySelector('.number-plus');
  const helpButton = parentElement.querySelector('.temperature-help');
  const suggestButton = parentElement.querySelector('.suggest-action');

  const finiteNumber = (value) => {
    if (value === null || value === undefined || value === '') return null;
    const parsed = Number(String(value).replace(/,/g, '.'));
    return Number.isFinite(parsed) ? parsed : null;
  };
  const step = finiteNumber(data?.step) ?? 1;
  const decimals = Number.isInteger(data?.decimals) ? Math.max(0, Math.min(8, data.decimals)) : 0;
  const minimum = finiteNumber(data?.min_value);
  const maximum = finiteNumber(data?.max_value);
  const disabled = Boolean(data?.disabled);

  const sameValue = (a, b) => {
    if (a === null || b === null) return a === b;
    if (a === undefined || b === undefined) return a === b;
    return Math.abs(Number(a) - Number(b)) < 1e-12;
  };
  const canonicalize = (raw) => {
    let value = String(raw ?? '').replace(/,/g, '.');
    const negative = value.startsWith('-');
    value = value.replace(/-/g, '').replace(/[^0-9.]/g, '');
    const firstDot = value.indexOf('.');
    if (firstDot >= 0) {
      value = value.slice(0, firstDot + 1) + value.slice(firstDot + 1).replace(/\./g, '');
    }
    return (negative ? '-' : '') + value;
  };
  const roundValue = (value) => {
    const factor = 10 ** decimals;
    return Math.round((value + Number.EPSILON) * factor) / factor;
  };
  const clampValue = (value) => {
    let result = value;
    if (minimum !== null) result = Math.max(minimum, result);
    if (maximum !== null) result = Math.min(maximum, result);
    return roundValue(result);
  };
  const formatValue = (value) => {
    if (value === null || value === undefined) return '';
    return clampValue(Number(value)).toFixed(decimals);
  };
  const parsedInput = () => {
    const text = canonicalize(input.value).trim();
    if (text === '' || text === '-' || text === '.' || text === '-.') return null;
    const parsed = Number(text);
    return Number.isFinite(parsed) ? parsed : null;
  };
  const canStep = (direction) => {
    if (disabled) return false;
    const current = parsedInput();
    if (current === null) return false;
    if (direction < 0 && minimum !== null && current <= minimum + 1e-12) return false;
    if (direction > 0 && maximum !== null && current >= maximum - 1e-12) return false;
    return true;
  };
  const updateButtons = () => {
    minusButton.disabled = !canStep(-1);
    plusButton.disabled = !canStep(1);
    helpButton.disabled = disabled;
    suggestButton.disabled = disabled;
  };
  const setDisplayedValue = (value) => {
    input.value = formatValue(value);
    updateButtons();
  };
  const sendValue = (value) => {
    const normalized = value === null ? null : clampValue(value);
    if (sameValue(normalized, control._lastSentValue)) return;
    control._lastSentValue = normalized;
    setStateValue('value', normalized);
  };
  const scheduleValue = (value) => {
    if (control._sendTimer) window.clearTimeout(control._sendTimer);
    control._sendTimer = window.setTimeout(() => {
      control._sendTimer = null;
      sendValue(value);
    }, 160);
  };
  const commitInput = () => {
    const parsed = parsedInput();
    if (parsed === null) {
      if (input.value.trim() === '') {
        sendValue(null);
        updateButtons();
      } else {
        setDisplayedValue(control._lastSentValue ?? null);
      }
      return;
    }
    const normalized = clampValue(parsed);
    setDisplayedValue(normalized);
    sendValue(normalized);
  };
  const stepBy = (direction) => {
    if (!canStep(direction)) return;
    const current = parsedInput();
    const next = clampValue(current + direction * step);
    setDisplayedValue(next);
    scheduleValue(next);
  };

  label.textContent = String(data?.compact_label || '');
  unit.textContent = String(data?.unit || '');
  const showHelp = Boolean(data?.help_enabled);
  const showSuggest = Boolean(data?.suggest_enabled);
  const reserveAction = Boolean(data?.reserve_action);
  const externalAction = Boolean(data?.external_action);
  control.classList.toggle('has-help', showHelp);
  control.classList.toggle('has-unit', Boolean(String(data?.unit || '')));
  const dense = Boolean(data?.dense);
  control.classList.toggle('has-suggest', showSuggest);
  control.classList.toggle('reserve-action', reserveAction);
  control.classList.toggle('external-action', externalAction);
  control.classList.toggle('is-dense', dense);
  control.classList.toggle('is-disabled', disabled);
  helpButton.classList.toggle('is-visible', showHelp);
  suggestButton.classList.toggle('is-visible', showSuggest);
  suggestButton.classList.toggle('is-active', showSuggest && Boolean(data?.suggest_active));
  suggestButton.textContent = String(data?.suggest_label || '');
  suggestButton.setAttribute('aria-pressed', data?.suggest_active ? 'true' : 'false');
  input.disabled = disabled;
  input.setAttribute('aria-label', String(data?.aria_label || 'Valore numerico'));

  const syncToken = String(data?.sync_token ?? 0);
  if (control.dataset.initialized !== '1' || control.dataset.syncToken !== syncToken) {
    const incoming = finiteNumber(data?.value);
    control.dataset.initialized = '1';
    control.dataset.syncToken = syncToken;
    control._lastSentValue = incoming;
    setDisplayedValue(incoming);
  }

  input.oninput = () => {
    const raw = input.value;
    const start = input.selectionStart;
    const normalized = canonicalize(raw);
    if (normalized !== raw) {
      input.value = normalized;
      if (start !== null && typeof input.setSelectionRange === 'function') {
        input.setSelectionRange(Math.min(start, normalized.length), Math.min(start, normalized.length));
      }
    }
    updateButtons();
  };
  input.onblur = commitInput;
  input.onkeydown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      commitInput();
      input.blur();
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      stepBy(-1);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      stepBy(1);
    }
  };
  minusButton.onclick = () => stepBy(-1);
  plusButton.onclick = () => stepBy(1);
  helpButton.onclick = () => {
    if (!disabled && showHelp) setTriggerValue('help', true);
  };
  suggestButton.onclick = () => {
    if (!disabled && showSuggest) setTriggerValue('suggest', true);
  };

  updateButtons();
}
"""

_renderer = None


def is_full_mobile_v2_key(key) -> bool:
    return key in _FULL_MOBILE_COMPONENT_KEYS


def mobile_decimal_v2_available() -> bool:
    components = getattr(st, "components", None)
    v2 = getattr(components, "v2", None)
    return callable(getattr(v2, "component", None))


def _get_renderer():
    global _renderer
    if _renderer is None:
        if not mobile_decimal_v2_available():
            return None
        _renderer = st.components.v2.component(
            "mortem_decimal_number_input_mobile_v2",
            html=_HTML,
            css=_CSS,
            js=_JS,
        )
    return _renderer


def _component_instance_key(key) -> str:
    """Chiave V2 compatibile: ``__`` è riservato internamente da Streamlit."""
    return f"{key}-v2"


def _state_value(state, name, default=None):
    if state is None:
        return default
    try:
        return state.get(name, default)
    except Exception:
        return getattr(state, name, default)


def _set_state_value(state, name, value) -> None:
    if state is None:
        return
    try:
        state[name] = value
        return
    except Exception:
        pass
    try:
        setattr(state, name, value)
    except Exception:
        pass


def _finite_float(value):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def render_mobile_decimal_v2(
    *,
    value,
    step,
    decimals,
    min_value,
    max_value,
    disabled,
    sync_token,
    aria_label,
    compact_label,
    unit,
    help_enabled,
    help_state_key,
    suggest_enabled,
    suggest_label,
    suggest_active,
    on_suggest,
    on_change,
    key,
):
    """Renderizza il controllo V2 mantenendo compatibile lo stato V1 esterno."""
    renderer = _get_renderer()
    if renderer is None:
        raise RuntimeError("Streamlit Components V2 non disponibile")

    internal_key = _component_instance_key(key)
    sync_key = f"{internal_key}:sync-token"
    sync_token = int(sync_token)
    dense = bool(key and key.startswith("mortem_decimal_fcpanel_"))
    full_mobile = bool(st.session_state.get("__full_device_mobile", False))
    external_action = bool(
        (
            key == "mortem_decimal_peso"
            and st.session_state.get("stima_cautelativa_beta", False)
        )
        or (
            not full_mobile
            and not dense
            and not suggest_enabled
        )
    )
    reserve_action = bool(not dense and not external_action)

    if st.session_state.get(sync_key) != sync_token:
        _set_state_value(st.session_state.get(internal_key), "value", value)
        st.session_state[sync_key] = sync_token

    def _on_value_change():
        incoming = _finite_float(_state_value(st.session_state.get(internal_key), "value", value))
        if key:
            st.session_state[key] = incoming
        if callable(on_change):
            on_change()

    def _on_help_change():
        if help_enabled and help_state_key:
            st.session_state[help_state_key] = not bool(st.session_state.get(help_state_key, False))

    def _on_suggest_change():
        if suggest_enabled and callable(on_suggest):
            on_suggest()

    result = renderer(
        data={
            "value": value,
            "step": float(step),
            "decimals": int(decimals),
            "min_value": min_value,
            "max_value": max_value,
            "disabled": bool(disabled),
            "sync_token": sync_token,
            "aria_label": str(aria_label or "Valore numerico"),
            "compact_label": str(compact_label or ""),
            "unit": str(unit or ""),
            "help_enabled": bool(help_enabled),
            "suggest_enabled": bool(suggest_enabled),
            "suggest_label": str(suggest_label or ""),
            "suggest_active": bool(suggest_active),
            "reserve_action": reserve_action,
            "external_action": external_action,
            "dense": dense,
        },
        default={"value": value},
        on_value_change=_on_value_change,
        on_help_change=_on_help_change,
        on_suggest_change=_on_suggest_change,
        key=internal_key,
        width="stretch",
        height=34 if dense else 40,
    )

    return _finite_float(_state_value(result, "value", value))
