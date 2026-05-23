/**
 * Loading screen — visible from first paint, minimum 5s from page load
 */
const MIN_MS = 5000;
export const MOBILE_MQ = "(max-width: 900px)";

export function isMobileLayout() {
  return window.matchMedia(MOBILE_MQ).matches;
}

function pageStart() {
  if (!window.__SF_PAGE_START) window.__SF_PAGE_START = Date.now();
  return window.__SF_PAGE_START;
}

export function waitPreloaderMin() {
  const remain = Math.max(0, MIN_MS - (Date.now() - pageStart()));
  return new Promise((resolve) => window.setTimeout(resolve, remain));
}

export function startPreloader() {
  document.documentElement.classList.add("is-loading");
  const fill = document.querySelector(".site-preloader__fill");
  if (fill) fill.style.setProperty("--preloader-duration", `${MIN_MS}ms`);
  return waitPreloaderMin();
}

function loadImage(src) {
  return new Promise((resolve) => {
    const img = new Image();
    const done = () => resolve(src);
    img.onload = () => {
      if (img.decode) img.decode().then(done).catch(done);
      else done();
    };
    img.onerror = done;
    img.src = src;
  });
}

export function preloadImages(urls, { limit = 40, timeout = 12000, required = false } = {}) {
  const list = [...new Set(urls.filter(Boolean))].slice(0, limit);
  if (!list.length) return Promise.resolve();

  const loads = Promise.all(list.map(loadImage));
  if (required) return loads;
  return Promise.race([loads, new Promise((resolve) => window.setTimeout(resolve, timeout))]);
}

/** Wait until marquee / hero imgs in DOM have decoded (mobile). */
export function waitForDomImages(selectors, { timeout = 20000 } = {}) {
  const imgs = selectors.flatMap((sel) => [...document.querySelectorAll(`${sel} img`)]);
  if (!imgs.length) return Promise.resolve();

  const pending = imgs.map(
    (img) =>
      new Promise((resolve) => {
        if (img.complete && img.naturalWidth > 0) {
          if (img.decode) img.decode().then(resolve).catch(resolve);
          else resolve();
          return;
        }
        const done = () => resolve();
        img.addEventListener("load", done, { once: true });
        img.addEventListener("error", done, { once: true });
      })
  );

  return Promise.race([
    Promise.all(pending),
    new Promise((resolve) => window.setTimeout(resolve, timeout)),
  ]);
}

export function collectHomePreloadUrls(galleryItems, brandPaths, foundersPhoto, vimeoThumbUrls = []) {
  const mobile = isMobileLayout();
  const urls = [...brandPaths, ...vimeoThumbUrls];
  if (foundersPhoto) urls.push(foundersPhoto);
  galleryItems.slice(0, mobile ? 16 : 12).forEach((item) => urls.push(item.src));
  return urls;
}

export function collectGalleryPreloadUrls(items) {
  const n = isMobileLayout() ? 24 : 18;
  return items.slice(0, n).map((item) => item.src);
}

export async function finishPreloader() {
  const el = document.getElementById("site-preloader");
  const bar = document.querySelector(".site-preloader__bar");
  if (bar) bar.setAttribute("aria-valuenow", "100");

  document.documentElement.classList.remove("is-loading");
  document.documentElement.classList.add("is-revealed");

  if (el) {
    el.classList.add("is-done");
    el.setAttribute("aria-busy", "false");
    await new Promise((r) => window.setTimeout(r, 480));
    el.remove();
  }
}
