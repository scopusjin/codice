const input = document.getElementById("time-input");

function setTheme(args) {
  document.documentElement.style.setProperty("--primary", args.primary_color || "#168AC1");
  document.documentElement.style.setProperty("--field-bg", args.background_color || "#F0F2F6");
  document.documentElement.style.setProperty("--text", args.text_color || "#31333F");
}

function commitValue() {
  if (/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(input.value)) {
    Streamlit.setComponentValue(input.value);
  }
}

function onRender(event) {
  const args = event.detail.args || {};
  setTheme(args);

  if (document.activeElement !== input && typeof args.value === "string" && input.value !== args.value) {
    input.value = args.value;
  }

  Streamlit.setFrameHeight(40);
}

input.addEventListener("change", commitValue);

input.addEventListener("pointerdown", () => {
  const coarsePointer = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;
  if (coarsePointer && typeof input.showPicker === "function") {
    try {
      input.showPicker();
    } catch (_) {
      // Il browser può già aver aperto il picker nativo: non serve altro.
    }
  }
});

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
