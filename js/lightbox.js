/**
 * Image lightbox — gallery & home mosaic
 */

import { isMobileLayout } from "./preloader.js";

let lbIndex = 0;
let lbSources = [];
let touchStartX = 0;

function ensureLightbox() {
  let el = document.getElementById("lightbox");
  if (el) return el;

  const mobile = isMobileLayout();
  el = document.createElement("div");
  el.id = "lightbox";
  el.className = "lightbox";
  el.hidden = true;
  el.innerHTML = mobile
    ? `
    <button type="button" class="lightbox__close" aria-label="Fermer">&times;</button>
    <div class="lightbox__strip" id="lightbox-strip"></div>`
    : `
    <button type="button" class="lightbox__close" aria-label="Fermer">&times;</button>
    <button type="button" class="lightbox__nav lightbox__nav--prev" aria-label="Image précédente">&#8592;</button>
    <button type="button" class="lightbox__nav lightbox__nav--next" aria-label="Image suivante">&#8594;</button>
    <div class="lightbox__stage">
      <img class="lightbox__img" id="lightbox-img" alt="">
    </div>`;
  document.body.appendChild(el);

  el.querySelector(".lightbox__close").addEventListener("click", closeLightbox);
  if (!mobile) {
    el.querySelector(".lightbox__nav--prev").addEventListener("click", () => stepLightbox(-1));
    el.querySelector(".lightbox__nav--next").addEventListener("click", () => stepLightbox(1));
  }

  const strip = el.querySelector("#lightbox-strip");
  if (strip) {
    strip.addEventListener(
      "touchstart",
      (e) => {
        touchStartX = e.touches[0].clientX;
      },
      { passive: true }
    );
    strip.addEventListener(
      "touchend",
      (e) => {
        const dx = e.changedTouches[0].clientX - touchStartX;
        if (Math.abs(dx) < 48) return;
        stepLightbox(dx > 0 ? -1 : 1);
      },
      { passive: true }
    );
    strip.addEventListener(
      "scroll",
      () => {
        const slides = [...strip.querySelectorAll(".lightbox__slide")];
        if (!slides.length) return;
        const mid = strip.scrollLeft + strip.clientWidth / 2;
        let best = 0;
        let bestDist = Infinity;
        slides.forEach((slide, i) => {
          const center = slide.offsetLeft + slide.offsetWidth / 2;
          const dist = Math.abs(center - mid);
          if (dist < bestDist) {
            bestDist = dist;
            best = i;
          }
        });
        if (best !== lbIndex) {
          lbIndex = best;
          strip.querySelectorAll(".lightbox__slide").forEach((slide, i) => {
            slide.classList.toggle("is-active", i === lbIndex);
          });
        }
      },
      { passive: true }
    );
  }

  el.addEventListener("click", (e) => {
    if (e.target === el) closeLightbox();
  });

  document.addEventListener("keydown", (e) => {
    if (el.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (!mobile) {
      if (e.key === "ArrowLeft") stepLightbox(-1);
      if (e.key === "ArrowRight") stepLightbox(1);
    }
  });

  return el;
}

function stepLightbox(dir) {
  if (!lbSources.length) return;
  lbIndex = (lbIndex + dir + lbSources.length) % lbSources.length;
  updateLightboxView();
}

function updateLightboxView() {
  const mobile = isMobileLayout();
  if (mobile) {
    const strip = document.getElementById("lightbox-strip");
    if (!strip) return;
    strip.querySelectorAll(".lightbox__slide").forEach((slide, i) => {
      slide.classList.toggle("is-active", i === lbIndex);
    });
    const active = strip.querySelector(".lightbox__slide.is-active");
    if (active) {
      active.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
    return;
  }
  const img = document.getElementById("lightbox-img");
  if (img) img.src = lbSources[lbIndex];
}

function buildMobileStrip() {
  const strip = document.getElementById("lightbox-strip");
  if (!strip) return;
  strip.innerHTML = lbSources
    .map(
      (src, i) =>
        `<figure class="lightbox__slide${i === lbIndex ? " is-active" : ""}">
          <img src="${src}" alt="" loading="eager" decoding="async">
        </figure>`
    )
    .join("");
}

export function openLightbox(src, sources = []) {
  lbSources = sources.length ? sources : [src];
  lbIndex = Math.max(0, lbSources.indexOf(src));
  const box = ensureLightbox();

  if (isMobileLayout()) {
    buildMobileStrip();
  } else {
    const img = document.getElementById("lightbox-img");
    if (img) img.src = lbSources[lbIndex];
  }

  box.hidden = false;
  document.body.classList.add("lightbox-open");
  document.body.style.overflow = "hidden";
  if (window.lenis) window.lenis.stop();

  requestAnimationFrame(() => updateLightboxView());
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
