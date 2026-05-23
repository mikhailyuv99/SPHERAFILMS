/**
 * Image lightbox — gallery & home mosaic
 */

let lbIndex = 0;
let lbSources = [];

function ensureLightbox() {
  let el = document.getElementById("lightbox");
  if (el) return el;

  el = document.createElement("div");
  el.id = "lightbox";
  el.className = "lightbox";
  el.hidden = true;
  el.innerHTML = `
    <button type="button" class="lightbox__close" aria-label="Fermer">&times;</button>
    <button type="button" class="lightbox__nav lightbox__nav--prev" aria-label="Image précédente">&#8592;</button>
    <button type="button" class="lightbox__nav lightbox__nav--next" aria-label="Image suivante">&#8594;</button>
    <div class="lightbox__stage">
      <img class="lightbox__img" id="lightbox-img" alt="">
    </div>`;
  document.body.appendChild(el);

  el.querySelector(".lightbox__close").addEventListener("click", closeLightbox);
  el.querySelector(".lightbox__nav--prev").addEventListener("click", () => stepLightbox(-1));
  el.querySelector(".lightbox__nav--next").addEventListener("click", () => stepLightbox(1));
  el.addEventListener("click", (e) => {
    if (e.target === el) closeLightbox();
  });

  document.addEventListener("keydown", (e) => {
    if (el.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") stepLightbox(-1);
    if (e.key === "ArrowRight") stepLightbox(1);
  });

  return el;
}

function stepLightbox(dir) {
  if (!lbSources.length) return;
  lbIndex = (lbIndex + dir + lbSources.length) % lbSources.length;
  const img = document.getElementById("lightbox-img");
  if (img) img.src = lbSources[lbIndex];
}

export function openLightbox(src, sources = []) {
  lbSources = sources.length ? sources : [src];
  lbIndex = Math.max(0, lbSources.indexOf(src));
  const box = ensureLightbox();
  const img = document.getElementById("lightbox-img");
  if (img) img.src = lbSources[lbIndex];
  box.hidden = false;
  document.body.classList.add("lightbox-open");
  document.body.style.overflow = "hidden";
  if (window.lenis) window.lenis.stop();
}

export function closeLightbox() {
  const box = document.getElementById("lightbox");
  if (!box) return;
  box.hidden = true;
  document.body.classList.remove("lightbox-open");
  document.body.style.overflow = "";
  if (window.lenis) window.lenis.start();
}

export function bindLightbox(container, itemSelector = "[data-lightbox]") {
  if (!container) return;
  const items = [...container.querySelectorAll(itemSelector)];
  const seen = new Set();
  const sources = [];
  for (const el of items) {
    const src = el.dataset.src || el.querySelector("img")?.src;
    if (src && !seen.has(src)) {
      seen.add(src);
      sources.push(src);
    }
  }

  items.forEach((el) => {
    el.addEventListener("click", () => {
      const src = el.dataset.src || el.querySelector("img")?.src;
      if (src) openLightbox(src, sources);
    });
  });
}
