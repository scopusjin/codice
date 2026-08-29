const timeInput = document.getElementById("time-input");
const pickerToggle = document.getElementById("picker-toggle");
const picker = document.getElementById("picker");
const hoursWheel = document.getElementById("hours-wheel");
const minutesWheel = document.getElementById("minutes-wheel");
const cancelButton = document.getElementById("cancel-button");
const setButton = document.getElementById("set-button");

const ITEM_HEIGHT = 36;
const WHEEL_CYCLES = 7;
const CENTER_CYCLE = Math.floor(WHEEL_CYCLES / 2);
const OPEN_HEIGHT = 224;

let committedValue = "00:00";
let pendingCommittedValue = null;
let initialized = false;
let isMobile = false;
let draftHour = 0;
let draftMinute = 0;
let hourScrollTimer = null;
let minuteScrollTimer = null;
let desktopWheelCommitTimer = null;

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

function normalizeTypedTime(value) {
  const raw = String(value || "").trim();

  const colonMatch = raw.match(/^(\d{1,2}):([0-5]\d)$/);
  if (colonMatch) {
    const hour = Number(colonMatch[1]);
    const minute = Number(colonMatch[2]);
    if (hour <= 23) {
      return formatTime(hour, minute);
    }
  }

  if (/^\d{3,4}$/.test(raw)) {
    const digits = raw.padStart(4, "0");
    const hour = Number(digits.slice(0, 2));
    const minute = Number(digits.slice(2, 4));
    if (hour <= 23 && minute <= 59) {
      return formatTime(hour, minute);
    }
  }

  return null;
}

function commitNormalizedValue(value) {
  committedValue = value;
  pendingCommittedValue = value;
  timeInput.value = value;
  Streamlit.setComponentValue(value);
}

function commitTypedValue() {
  const normalized = normalizeTypedTime(timeInput.value);
  if (normalized === null) {
    timeInput.value = committedValue;
    return false;
  }

  timeInput.value = normalized;
  if (normalized !== committedValue) {
    commitNormalizedValue(normalized);
  }
  return true;
}

function adjustByMinutes(delta, commit = true) {
  const normalized = normalizeTypedTime(timeInput.value) || committedValue;
  const parsed = parseTime(normalized);
  let total = parsed.hour * 60 + parsed.minute + delta;
  total = ((total % 1440) + 1440) % 1440;
  const value = formatTime(Math.floor(total / 60), total % 60);

  if (commit) {
    commitNormalizedValue(value);
  } else {
    timeInput.value = value;
  }
}

function scheduleDesktopWheelCommit() {
  window.clearTimeout(desktopWheelCommitTimer);
  desktopWheelCommitTimer = window.setTimeout(() => {
    desktopWheelCommitTimer = null;
    commitTypedValue();
  }, 320);
}

function middleIndex(value, count) {
  return CENTER_CYCLE * count + value;
}

function makeWheel(wheel, count) {
  const topSpacer = document.createElement("div");
  topSpacer.className = "wheel-spacer";
  wheel.appendChild(topSpacer);

  for (let cycle = 0; cycle < WHEEL_CYCLES; cycle += 1) {
    for (let value = 0; value < count; value += 1) {
      const physicalIndex = cycle * count + value;
      const item = document.createElement("div");
      item.className = "wheel-item";
      item.textContent = String(value).padStart(2, "0");
      item.dataset.value = String(value);
      item.dataset.physical = String(physicalIndex);
      item.setAttribute("role", "option");
      item.addEventListener("click", () => {
        wheel.scrollTo({ top: physicalIndex * ITEM_HEIGHT, behavior: "smooth" });
      });
      wheel.appendChild(item);
    }
  }

  const bottomSpacer = document.createElement("div");
  bottomSpacer.className = "wheel-spacer";
  wheel.appendChild(bottomSpacer);
}

function selectedPhysicalIndex(wheel, count) {
  const max = count * WHEEL_CYCLES - 1;
  const raw = Math.round(wheel.scrollTop / ITEM_HEIGHT);
  return Math.max(0, Math.min(max, raw));
}

function valueForIndex(index, count) {
  return ((index % count) + count) % count;
}

function paintSelection(wheel, physicalIndex) {
  wheel.querySelectorAll(".wheel-item.selected").forEach((item) => {
    item.classList.remove("selected");
    item.setAttribute("aria-selected", "false");
  });

  const selected = wheel.querySelector(`.wheel-item[data-physical="${physicalIndex}"]`);
  if (selected) {
    selected.classList.add("selected");
    selected.setAttribute("aria-selected", "true");
  }
}

function setWheelValue(wheel, count, value) {
  const physicalIndex = middleIndex(value, count);
  wheel.scrollTop = physicalIndex * ITEM_HEIGHT;
  paintSelection(wheel, physicalIndex);
}

function updateFromScroll(wheel, count, setter) {
  const physicalIndex = selectedPhysicalIndex(wheel, count);
  setter(valueForIndex(physicalIndex, count));
  paintSelection(wheel, physicalIndex);
}

function settleWheel(wheel, count, setter) {
  let physicalIndex = selectedPhysicalIndex(wheel, count);
  wheel.scrollTo({ top: physicalIndex * ITEM_HEIGHT, behavior: "smooth" });

  window.setTimeout(() => {
    physicalIndex = selectedPhysicalIndex(wheel, count);
    const value = valueForIndex(physicalIndex, count);

    if (physicalIndex < count || physicalIndex >= (WHEEL_CYCLES - 1) * count) {
      physicalIndex = middleIndex(value, count);
      wheel.scrollTop = physicalIndex * ITEM_HEIGHT;
    }

    setter(value);
    paintSelection(wheel, physicalIndex);
  }, 120);
}

function openPicker() {
  if (!isMobile) {
    return;
  }

  commitTypedValue();
  const parsed = parseTime(committedValue);
  draftHour = parsed.hour;
  draftMinute = parsed.minute;
  picker.hidden = false;
  pickerToggle.setAttribute("aria-expanded", "true");
  Streamlit.setFrameHeight(OPEN_HEIGHT);

  requestAnimationFrame(() => {
    setWheelValue(hoursWheel, 24, draftHour);
    setWheelValue(minutesWheel, 60, draftMinute);
  });
}

function closePicker() {
  picker.hidden = true;
  pickerToggle.setAttribute("aria-expanded", "false");
  Streamlit.setFrameHeight(40);
}

function commitDraft() {
  const value = formatTime(draftHour, draftMinute);
  if (value !== committedValue) {
    commitNormalizedValue(value);
  } else {
    timeInput.value = value;
  }
  closePicker();
}

function onRender(event) {
  const args = event.detail.args || {};
  setTheme(args);

  isMobile = Boolean(args.mobile);
  pickerToggle.hidden = !isMobile;
  if (!isMobile && !picker.hidden) {
    closePicker();
  }

  const incomingValue = (
    typeof args.value === "string" && /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(args.value)
  ) ? args.value : null;

  if (incomingValue !== null) {
    if (!initialized) {
      committedValue = incomingValue;
      timeInput.value = committedValue;
      initialized = true;
    } else if (pendingCommittedValue !== null) {
      if (incomingValue === pendingCommittedValue) {
        committedValue = incomingValue;
        pendingCommittedValue = null;
        if (document.activeElement !== timeInput) {
          timeInput.value = committedValue;
        }
      }
    } else {
      committedValue = incomingValue;
      if (document.activeElement !== timeInput) {
        timeInput.value = committedValue;
      }
    }
  }

  Streamlit.setFrameHeight(isMobile && !picker.hidden ? OPEN_HEIGHT : 40);
}

makeWheel(hoursWheel, 24);
makeWheel(minutesWheel, 60);

timeInput.addEventListener("focus", () => {
  if (!picker.hidden) {
    closePicker();
  }
  window.setTimeout(() => timeInput.select(), 0);
});

timeInput.addEventListener("input", () => {
  const raw = timeInput.value.trim();
  if (/^\d{4}$/.test(raw)) {
    const normalized = normalizeTypedTime(raw);
    if (normalized !== null) {
      timeInput.value = normalized;
    }
  }
});

timeInput.addEventListener("blur", () => {
  window.clearTimeout(desktopWheelCommitTimer);
  desktopWheelCommitTimer = null;
  commitTypedValue();
});

timeInput.addEventListener("keydown", (event) => {
  if (!isMobile && event.key === "ArrowUp") {
    event.preventDefault();
    adjustByMinutes(5);
  } else if (!isMobile && event.key === "ArrowDown") {
    event.preventDefault();
    adjustByMinutes(-5);
  } else if (event.key === "Enter") {
    event.preventDefault();
    commitTypedValue();
    timeInput.blur();
  } else if (event.key === "Escape") {
    event.preventDefault();
    timeInput.value = committedValue;
    timeInput.blur();
  }
});

timeInput.addEventListener("wheel", (event) => {
  if (isMobile) {
    return;
  }
  event.preventDefault();
  adjustByMinutes(event.deltaY < 0 ? 5 : -5, false);
  scheduleDesktopWheelCommit();
}, { passive: false });

pickerToggle.addEventListener("click", () => {
  if (!isMobile) {
    return;
  }
  timeInput.blur();
  if (picker.hidden) {
    openPicker();
  } else {
    closePicker();
  }
});

hoursWheel.addEventListener("scroll", () => {
  window.clearTimeout(hourScrollTimer);
  updateFromScroll(hoursWheel, 24, (value) => { draftHour = value; });
  hourScrollTimer = window.setTimeout(() => {
    settleWheel(hoursWheel, 24, (value) => { draftHour = value; });
  }, 70);
}, { passive: true });

minutesWheel.addEventListener("scroll", () => {
  window.clearTimeout(minuteScrollTimer);
  updateFromScroll(minutesWheel, 60, (value) => { draftMinute = value; });
  minuteScrollTimer = window.setTimeout(() => {
    settleWheel(minutesWheel, 60, (value) => { draftMinute = value; });
  }, 70);
}, { passive: true });

cancelButton.addEventListener("click", closePicker);
setButton.addEventListener("click", commitDraft);

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
