/**
 * Sphera Films — gallery page (strict unique images only)
 */

import { GALLERY_EXCLUDE, loadGalleryPageOrder, uniqueGalleryItems } from "./gallery-data.js";
import { bindLightbox } from "./lightbox.js";
import { initScrollReveal } from "./scroll-reveal.js";
import {
  startPreloader,
  finishPreloader,
  preloadImages,
  collectGalleryPreloadUrls,
  MOBILE_MQ,
} from "./preloader.js";

async function init() {
  const preloaderWait = startPreloader();

  let items = await loadGalleryPageOrder(GALLERY_EXCLUDE);
  items = uniqueGalleryItems(items, GALLERY_EXCLUDE);

  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  const grid = document.getElementById("gallery-grid");
  if (!grid) {
    await Promise.all([preloaderWait]);
    await finishPreloader();
    return;
  }

  if (!items.length) {
    grid.innerHTML = `<p class="gallery-empty">Galerie en cours de chargement.</p>`;
    initHeader();
    initNavToggle();
    await Promise.all([preloaderWait]);
    await finishPreloader();
    window.setTimeout(() => initScrollReveal(), 250);
    return;
  }

  const seenId = new Set();
  const seenSrc = new Set();
  const unique = items.filter((item) => {
    if (seenId.has(item.id) || seenSrc.has(item.src)) return false;
    seenId.add(item.id);
    seenSrc.add(item.src);
    return true;
  });

  const mobile = window.matchMedia(MOBILE_MQ).matches;
  const display = mobile && unique.length > 1 ? unique.slice(0, -1) : unique;
  const preloadWait = preloadImages(collectGalleryPreloadUrls(display), {
    limit: mobile ? 30 : 18,
  });

  grid.innerHTML = display
    .map((item, i) => {
      const eager = mobile && i < 16;
      const load = eager ? "eager" : "lazy";
      const priority = eager ? ' fetchpriority="high"' : "";
      return `<figure class="gallery-grid__cell" data-lightbox data-src="${item.src}" data-id="${item.id}">
          <img src="${item.src}" alt="" loading="${load}" decoding="async" width="800" height="1000"${priority}>
        </figure>`;
    })
    .join("");

  grid.querySelectorAll(".gallery-grid__cell img").forEach((img) => {
    img.addEventListener("error", () => img.closest(".gallery-grid__cell")?.remove());
  });

  bindLightbox(grid, "[data-lightbox]");
  initHeader();
  initNavToggle();

  await Promise.all([preloaderWait, preloadWait]);
  await finishPreloader();
  window.setTimeout(() => initScrollReveal(), 250);
}

function scrollY() {
  if (window.lenis && typeof window.lenis.scroll === "number") return window.lenis.scroll;
  return window.scrollY || 0;
}

function initHeader() {
  const header = document.querySelector(".site-header");
  if (!header) return;
  const onScroll = () => header.classList.toggle("is-scrolled", scrollY() > 40);
  onScroll();
  document.addEventListener("site-scroll", onScroll);
  window.addEventListener("scroll", onScroll, { passive: true });
}

function setNavOpen(open) {
  const btn = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (!btn || !nav) return;
  nav.classList.toggle("is-open", open);
  btn.setAttribute("aria-expanded", String(open));
  document.body.classList.toggle("nav-open", open);
}

function initNavToggle() {
  const btn = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (!btn || !nav) return;
  btn.addEventListener("click", () => setNavOpen(!nav.classList.contains("is-open")));
  nav.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => setNavOpen(false));
  });
}

init().catch(async (err) => {
  console.error(err);
  await finishPreloader();
  window.setTimeout(() => initScrollReveal(), 250);
});
