const temperatureHelpButton = document.getElementById("temperature-help");
const temperatureHelpPopup = document.getElementById("temperature-help-popup");

let temperatureHelpText = "";
let temperatureHelpOpen = false;

function parentViewportWidthForHelp() {
  try {
    if (window.parent && window.parent !== window) {
      return Number(window.parent.innerWidth) || Infinity;
    }
  } catch (_) {
    return Infinity;
  }
  return Infinity;
}

function resizeForTemperatureHelp() {
  if (!temperatureHelpOpen) {
    Streamlit.setFrameHeight(40);
    return;
  }
  window.requestAnimationFrame(() => {
    const popupHeight = temperatureHelpPopup.scrollHeight || 0;
    Streamlit.setFrameHeight(Math.max(96, 48 + popupHeight));
  });
}

function setTemperatureHelpOpen(open) {
  temperatureHelpOpen = Boolean(open && temperatureHelpText);
  temperatureHelpPopup.classList.toggle("is-open", temperatureHelpOpen);
  temperatureHelpButton.setAttribute("aria-expanded", temperatureHelpOpen ? "true" : "false");
  document.documentElement.classList.toggle("help-open", temperatureHelpOpen);
  resizeForTemperatureHelp();
}

function updateTemperatureHelp(event) {
  const args = event.detail.args || {};
  temperatureHelpText = String(args.help_text || "");
  const compactMobile = Boolean(args.compact_mobile) && parentViewportWidthForHelp() <= 768;
  const visible = compactMobile && Boolean(temperatureHelpText);

  temperatureHelpButton.classList.toggle("is-visible", visible);
  temperatureHelpPopup.textContent = temperatureHelpText;

  if (!visible) {
    setTemperatureHelpOpen(false);
  }
}

temperatureHelpButton.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  setTemperatureHelpOpen(!temperatureHelpOpen);
});

document.addEventListener("click", (event) => {
  if (!temperatureHelpOpen) return;
  if (temperatureHelpButton.contains(event.target) || temperatureHelpPopup.contains(event.target)) return;
  setTemperatureHelpOpen(false);
});

window.addEventListener("resize", () => {
  if (parentViewportWidthForHelp() > 768) {
    setTemperatureHelpOpen(false);
    temperatureHelpButton.classList.remove("is-visible");
  }
});

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, updateTemperatureHelp);
