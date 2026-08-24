const control = document.getElementById("number-control");
const mobileLabel = document.getElementById("mobile-label");
const input = document.getElementById("number-input");
const mobileUnit = document.getElementById("mobile-unit");
const minusButton = document.getElementById("number-minus");
const plusButton = document.getElementById("number-plus");

let step = 1;
let decimals = 0;
let minimum = null;
let maximum = null;
let disabled = false;
let currentSyncToken = null;
let sendTimer = null;
let lastSentValue = undefined;
let compactMobileEnabled = false;
let compactLabelText = "";
let unitText = "";
let hiddenParentLabel = null;
let hiddenParentLabelDisplay = "";

function sameValue(a, b) {
  if (a === null || b === null) return a === b;
  if (a === undefined || b === undefined) return a === b;
  return Math.abs(Number(a) - Number(b)) < 1e-12;
}

function finiteNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(String(value).replace(/,/g, "."));
  return Number.isFinite(parsed) ? parsed : null;
}

function canonicalize(raw) {
  let value = String(raw ?? "").replace(/,/g, ".");
  const negative = value.startsWith("-");
  value = value.replace(/-/g, "").replace(/[^0-9.]/g, "");
  const firstDot = value.indexOf(".");
  if (firstDot >= 0) {
    value = value.slice(0, firstDot + 1) + value.slice(firstDot + 1).replace(/\./g, "");
  }
  return (negative ? "-" : "") + value;
}

function roundValue(value) {
  const factor = 10 ** Math.max(0, decimals);
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

function clampValue(value) {
  let result = value;
  if (minimum !== null) result = Math.max(minimum, result);
  if (maximum !== null) result = Math.min(maximum, result);
  return roundValue(result);
}

function formatValue(value) {
  if (value === null || value === undefined) return "";
  return clampValue(Number(value)).toFixed(decimals);
}

function parsedInput() {
  const text = canonicalize(input.value).trim();
  if (text === "" || text === "-" || text === "." || text === "-.") return null;
  const parsed = Number(text);
  return Number.isFinite(parsed) ? parsed : null;
}

function canStep(direction) {
  if (disabled) return false;
  const current = parsedInput();
  if (current === null) return false;
  if (direction < 0 && minimum !== null && current <= minimum + 1e-12) return false;
  if (direction > 0 && maximum !== null && current >= maximum - 1e-12) return false;
  return true;
}

function updateButtons() {
  minusButton.disabled = !canStep(-1);
  plusButton.disabled = !canStep(1);
}

function setDisplayedValue(value) {
  input.value = formatValue(value);
  updateButtons();
}

function sendValue(value) {
  const normalized = value === null ? null : clampValue(value);
  if (sameValue(normalized, lastSentValue)) return;
  lastSentValue = normalized;
  Streamlit.setComponentValue(normalized);
}

function scheduleValue(value) {
  if (sendTimer !== null) window.clearTimeout(sendTimer);
  sendTimer = window.setTimeout(() => {
    sendTimer = null;
    sendValue(value);
  }, 160);
}

function commitInput() {
  const parsed = parsedInput();
  if (parsed === null) {
    if (input.value.trim() === "") {
      sendValue(null);
      updateButtons();
    } else {
      setDisplayedValue(lastSentValue === undefined ? null : lastSentValue);
    }
    return;
  }
  const normalized = clampValue(parsed);
  setDisplayedValue(normalized);
  sendValue(normalized);
}

function stepBy(direction) {
  if (!canStep(direction)) return;
  const current = parsedInput();
  const next = clampValue(current + direction * step);
  setDisplayedValue(next);
  scheduleValue(next);
}

function parentViewportWidth() {
  try {
    if (window.parent && window.parent !== window) {
      return Number(window.parent.innerWidth) || Infinity;
    }
  } catch (_) {
    return Infinity;
  }
  return Infinity;
}

function restoreParentLabel() {
  if (!hiddenParentLabel) return;
  hiddenParentLabel.style.display = hiddenParentLabelDisplay;
  hiddenParentLabel = null;
  hiddenParentLabelDisplay = "";
}

function setParentLabelHidden(hidden) {
  if (!hidden) {
    restoreParentLabel();
    return;
  }

  try {
    const frame = window.frameElement;
    const currentElement = frame
      ? (frame.closest('[data-testid="stElementContainer"]') || frame.parentElement)
      : null;
    const candidate = currentElement ? currentElement.previousElementSibling : null;

    if (!candidate) return;
    if (hiddenParentLabel && hiddenParentLabel !== candidate) {
      restoreParentLabel();
    }
    if (!hiddenParentLabel) {
      hiddenParentLabel = candidate;
      hiddenParentLabelDisplay = candidate.style.display || "";
    }
    candidate.style.display = "none";
  } catch (_) {
    restoreParentLabel();
  }
}

function updateCompactLayout() {
  const compact = compactMobileEnabled && parentViewportWidth() <= 768;
  control.classList.toggle("compact-mobile", compact);
  mobileLabel.textContent = compactLabelText;
  mobileUnit.textContent = unitText;
  setParentLabelHidden(compact);
}

input.addEventListener("input", () => {
  const raw = input.value;
  const start = input.selectionStart;
  const normalized = canonicalize(raw);
  if (normalized !== raw) {
    input.value = normalized;
    if (start !== null && typeof input.setSelectionRange === "function") {
      const pos = Math.min(start, normalized.length);
      input.setSelectionRange(pos, pos);
    }
  }
  updateButtons();
});

input.addEventListener("blur", commitInput);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    commitInput();
    input.blur();
  } else if (event.key === "ArrowDown") {
    event.preventDefault();
    stepBy(-1);
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    stepBy(1);
  }
});

minusButton.addEventListener("click", () => stepBy(-1));
plusButton.addEventListener("click", () => stepBy(1));
window.addEventListener("resize", updateCompactLayout);
window.addEventListener("beforeunload", restoreParentLabel);

function setTheme(args) {
  document.documentElement.style.setProperty("--primary", args.primary_color || "#168AC1");
  document.documentElement.style.setProperty("--field-bg", args.background_color || "#F0F2F6");
  document.documentElement.style.setProperty("--text", args.text_color || "#31333F");
}

function onRender(event) {
  const args = event.detail.args || {};
  setTheme(args);

  step = finiteNumber(args.step) ?? 1;
  decimals = Number.isInteger(args.decimals) ? Math.max(0, Math.min(8, args.decimals)) : 0;
  minimum = finiteNumber(args.min_value);
  maximum = finiteNumber(args.max_value);
  disabled = Boolean(args.disabled);
  compactMobileEnabled = Boolean(args.compact_mobile);
  compactLabelText = String(args.compact_label || "");
  unitText = String(args.unit || "");
  input.disabled = disabled;
  control.classList.toggle("is-disabled", disabled);
  input.setAttribute("aria-label", args.aria_label || "Valore numerico");

  const incomingToken = Number.isInteger(args.sync_token) ? args.sync_token : 0;
  const incomingValue = finiteNumber(args.value);

  if (currentSyncToken === null) {
    currentSyncToken = incomingToken;
    lastSentValue = incomingValue;
    setDisplayedValue(incomingValue);
  } else if (incomingToken !== currentSyncToken) {
    currentSyncToken = incomingToken;
    if (sendTimer !== null) {
      window.clearTimeout(sendTimer);
      sendTimer = null;
    }
    lastSentValue = incomingValue;
    setDisplayedValue(incomingValue);
    Streamlit.setComponentValue(incomingValue);
  }

  updateCompactLayout();
  updateButtons();
  Streamlit.setFrameHeight(40);
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
