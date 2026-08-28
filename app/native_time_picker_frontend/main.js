const display = document.getElementById("time-display");
const timeValue = document.getElementById("time-value");
const picker = document.getElementById("picker");
const hoursWheel = document.getElementById("hours-wheel");
const minutesWheel = document.getElementById("minutes-wheel");
const cancelButton = document.getElementById("cancel-button");
const setButton = document.getElementById("set-button");

const ITEM_HEIGHT = 44;
let committedValue = "00:00";
let pendingCommittedValue = null;
let initialized = false;
let draftHour = 0;
let draftMinute = 0;
let hourScrollTimer = null;
let minuteScrollTimer = null;

function setTheme(args) {
  document.documentElement.style.setProperty("--primary", args.primary_color || "#168AC1");
  document.documentElement.style.setProperty("--field-bg", args.background_color || "#F0F2F6");
  document.documentElement.style.setProperty("--text", args.text_color || "#31333F");
}

function parseTime(value) {
  const match = /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(value || "") ? value.split(":") : ["00", "00"];
  return { hour: Number(match[0]), minute: Number(match[1]) };
}

function formatTime(hour, minute) {
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function makeWheel(wheel, count) {
  const topSpacer = document.createElement("div");
  topSpacer.className = "wheel-spacer";
  wheel.appendChild(topSpacer);

  for (let i = 0; i < count; i += 1) {
    const item = document.createElement("div");
    item.className = "wheel-item";
    item.textContent = String(i).padStart(2, "0");
    item.dataset.value = String(i);
    item.setAttribute("role", "option");
    item.addEventListener("click", () => {
      wheel.scrollTo({ top: i * ITEM_HEIGHT, behavior: "smooth" });
    });
    wheel.appendChild(item);
  }

  const bottomSpacer = document.createElement("div");
  bottomSpacer.className = "wheel-spacer";
  wheel.appendChild(bottomSpacer);
}

function selectedIndex(wheel, max) {
  const raw = Math.round(wheel.scrollTop / ITEM_HEIGHT);
  return Math.max(0, Math.min(max, raw));
}

function paintSelection(wheel, value) {
  wheel.querySelectorAll(".wheel-item").forEach((item) => {
    const selected = Number(item.dataset.value) === value;
    item.classList.toggle("selected", selected);
    item.setAttribute("aria-selected", selected ? "true" : "false");
  });
}

function updateHourFromScroll() {
  draftHour = selectedIndex(hoursWheel, 23);
  paintSelection(hoursWheel, draftHour);
}

function updateMinuteFromScroll() {
  draftMinute = selectedIndex(minutesWheel, 59);
  paintSelection(minutesWheel, draftMinute);
}

function settleWheel(wheel, value, callback) {
  wheel.scrollTo({ top: value * ITEM_HEIGHT, behavior: "smooth" });
  window.setTimeout(callback, 150);
}

function openPicker() {
  const parsed = parseTime(committedValue);
  draftHour = parsed.hour;
  draftMinute = parsed.minute;
  picker.hidden = false;
  display.setAttribute("aria-expanded", "true");
  Streamlit.setFrameHeight(286);

  requestAnimationFrame(() => {
    hoursWheel.scrollTop = draftHour * ITEM_HEIGHT;
    minutesWheel.scrollTop = draftMinute * ITEM_HEIGHT;
    paintSelection(hoursWheel, draftHour);
    paintSelection(minutesWheel, draftMinute);
  });
}

function closePicker() {
  picker.hidden = true;
  display.setAttribute("aria-expanded", "false");
  Streamlit.setFrameHeight(40);
}

function commitDraft() {
  committedValue = formatTime(draftHour, draftMinute);
  pendingCommittedValue = committedValue;
  timeValue.textContent = committedValue;
  Streamlit.setComponentValue(committedValue);
  closePicker();
}

function onRender(event) {
  const args = event.detail.args || {};
  setTheme(args);

  const incomingValue = (
    typeof args.value === "string" && /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(args.value)
  ) ? args.value : null;

  if (incomingValue !== null) {
    if (!initialized) {
      committedValue = incomingValue;
      timeValue.textContent = committedValue;
      initialized = true;
    } else if (pendingCommittedValue !== null) {
      if (incomingValue === pendingCommittedValue) {
        committedValue = incomingValue;
        timeValue.textContent = committedValue;
        pendingCommittedValue = null;
      }
    } else {
      committedValue = incomingValue;
      timeValue.textContent = committedValue;
    }
  }

  Streamlit.setFrameHeight(picker.hidden ? 40 : 286);
}

makeWheel(hoursWheel, 24);
makeWheel(minutesWheel, 60);

display.addEventListener("click", () => {
  if (picker.hidden) {
    openPicker();
  } else {
    closePicker();
  }
});

hoursWheel.addEventListener("scroll", () => {
  window.clearTimeout(hourScrollTimer);
  updateHourFromScroll();
  hourScrollTimer = window.setTimeout(() => {
    settleWheel(hoursWheel, draftHour, updateHourFromScroll);
  }, 90);
}, { passive: true });

minutesWheel.addEventListener("scroll", () => {
  window.clearTimeout(minuteScrollTimer);
  updateMinuteFromScroll();
  minuteScrollTimer = window.setTimeout(() => {
    settleWheel(minutesWheel, draftMinute, updateMinuteFromScroll);
  }, 90);
}, { passive: true });

cancelButton.addEventListener("click", closePicker);
setButton.addEventListener("click", commitDraft);

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
