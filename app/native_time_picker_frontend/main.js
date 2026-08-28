const picker = document.getElementById("time-picker");
const trigger = document.getElementById("time-trigger");
const valueLabel = document.getElementById("time-value");
const panel = document.getElementById("picker-panel");
const hoursWheel = document.getElementById("hours-wheel");
const minutesWheel = document.getElementById("minutes-wheel");
const cancelButton = document.getElementById("cancel-button");
const applyButton = document.getElementById("apply-button");

const TIME_RE = /^(?:[01]\d|2[0-3]):[0-5]\d$/;
const ITEM_HEIGHT = 36;
const CLOSED_HEIGHT = 40;
const OPEN_HEIGHT = 286;

let committedValue = "00:00";
let isOpen = false;
let hourFrame = null;
let minuteFrame = null;

function pad2(value) {
  return String(value).padStart(2, "0");
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function buildWheel(wheel, count) {
  const fragment = document.createDocumentFragment();
  for (let i = 0; i < count; i += 1) {
    const item = document.createElement("div");
    item.className = "wheel-item";
    item.setAttribute("role", "option");
    item.dataset.value = String(i);
    item.textContent = pad2(i);
    fragment.appendChild(item);
  }
  wheel.appendChild(fragment);
}

function selectedIndex(wheel, maxIndex) {
  return clamp(Math.round(wheel.scrollTop / ITEM_HEIGHT), 0, maxIndex);
}

function markSelected(wheel, index) {
  Array.from(wheel.children).forEach((item, itemIndex) => {
    const selected = itemIndex === index;
    item.classList.toggle("is-selected", selected);
    item.setAttribute("aria-selected", selected ? "true" : "false");
  });
}

function scrollWheelTo(wheel, index, behavior = "auto") {
  wheel.scrollTo({
    top: index * ITEM_HEIGHT,
    behavior,
  });
  markSelected(wheel, index);
}

function syncWheelSelection(wheel, maxIndex) {
  const index = selectedIndex(wheel, maxIndex);
  markSelected(wheel, index);
}

function setTheme(args) {
  document.documentElement.style.setProperty("--primary", args.primary_color || "#168AC1");
  document.documentElement.style.setProperty("--field-bg", args.background_color || "#F0F2F6");
  document.documentElement.style.setProperty("--text", args.text_color || "#31333F");
}

function parseValue(value) {
  const safe = TIME_RE.test(value) ? value : "00:00";
  const [hours, minutes] = safe.split(":").map(Number);
  return { hours, minutes };
}

function openPicker() {
  if (isOpen) return;
  isOpen = true;
  picker.classList.add("is-open");
  trigger.setAttribute("aria-expanded", "true");
  panel.hidden = false;
  Streamlit.setFrameHeight(OPEN_HEIGHT);

  const current = parseValue(committedValue);
  requestAnimationFrame(() => {
    scrollWheelTo(hoursWheel, current.hours, "auto");
    scrollWheelTo(minutesWheel, current.minutes, "auto");
  });
}

function closePicker() {
  if (!isOpen) return;
  isOpen = false;
  picker.classList.remove("is-open");
  trigger.setAttribute("aria-expanded", "false");
  panel.hidden = true;
  Streamlit.setFrameHeight(CLOSED_HEIGHT);
}

function applyValue() {
  const hours = selectedIndex(hoursWheel, 23);
  const minutes = selectedIndex(minutesWheel, 59);
  committedValue = `${pad2(hours)}:${pad2(minutes)}`;
  valueLabel.textContent = committedValue;
  closePicker();
  Streamlit.setComponentValue(committedValue);
}

function onRender(event) {
  const args = event.detail.args || {};
  setTheme(args);

  if (!isOpen && typeof args.value === "string" && TIME_RE.test(args.value)) {
    committedValue = args.value;
    valueLabel.textContent = committedValue;
  }

  Streamlit.setFrameHeight(isOpen ? OPEN_HEIGHT : CLOSED_HEIGHT);
}

buildWheel(hoursWheel, 24);
buildWheel(minutesWheel, 60);
markSelected(hoursWheel, 0);
markSelected(minutesWheel, 0);

trigger.addEventListener("click", () => {
  if (isOpen) {
    closePicker();
  } else {
    openPicker();
  }
});

cancelButton.addEventListener("click", closePicker);
applyButton.addEventListener("click", applyValue);

hoursWheel.addEventListener("scroll", () => {
  if (hourFrame !== null) cancelAnimationFrame(hourFrame);
  hourFrame = requestAnimationFrame(() => {
    syncWheelSelection(hoursWheel, 23);
    hourFrame = null;
  });
}, { passive: true });

minutesWheel.addEventListener("scroll", () => {
  if (minuteFrame !== null) cancelAnimationFrame(minuteFrame);
  minuteFrame = requestAnimationFrame(() => {
    syncWheelSelection(minutesWheel, 59);
    minuteFrame = null;
  });
}, { passive: true });

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && isOpen) {
    closePicker();
    trigger.focus();
  }
});

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
