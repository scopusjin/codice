let resizeObserver = null;
let resizeFrame = null;

function sendValue(value) {
  Streamlit.setComponentValue(value);
}

function syncFrameHeight() {
  if (resizeFrame !== null) {
    cancelAnimationFrame(resizeFrame);
  }
  resizeFrame = requestAnimationFrame(() => {
    const img = document.getElementById("image");
    if (!img) return;
    const rect = img.getBoundingClientRect();
    if (rect.height > 0) {
      Streamlit.setFrameHeight(Math.ceil(rect.height));
    }
  });
}

function observeImageSize() {
  const img = document.getElementById("image");
  if (!img || typeof ResizeObserver === "undefined") return;

  if (resizeObserver !== null) {
    resizeObserver.disconnect();
  }
  resizeObserver = new ResizeObserver(syncFrameHeight);
  resizeObserver.observe(img);
}

function clickListener(event) {
  const img = document.getElementById("image");
  const rect = img.getBoundingClientRect();
  sendValue({
    x: event.offsetX,
    y: event.offsetY,
    width: rect.width,
    height: rect.height,
    unix_time: Date.now(),
  });
}

function onRender(event) {
  const {src, cursor} = event.detail.args;
  const img = document.getElementById("image");

  img.style.cursor = cursor || "pointer";
  img.onclick = clickListener;

  const onReady = () => {
    observeImageSize();
    syncFrameHeight();
    setTimeout(syncFrameHeight, 0);
    setTimeout(syncFrameHeight, 100);
    setTimeout(syncFrameHeight, 300);
  };

  if (img.src !== src) {
    img.onload = onReady;
    img.src = src;
  } else if (img.complete && img.naturalWidth > 0) {
    onReady();
  }
}

window.addEventListener("resize", syncFrameHeight);
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
