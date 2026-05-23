/**
 * 5s loading screen — logo, wordmark, progress line + image preload
 */
const MIN_MS = 5000;
export const MOBILE_MQ = "(max-width: 900px)";

export function startPreloader() {
  document.documentElement.classList.add("is-loading");
  const fill = document.querySelector(".site-preloader__fill");
  if (fill) fill.style.setProperty("--preloader-duration", `${MIN_MS}ms`);
  return new Promise((resolve) => window.setTimeout(resolve, MIN_MS));
}

export function preloadImages(urls, { limit = 28, timeout = 15000 } = {}) {
  const list = [...new Set(urls.filter(Boolean))].slice(0, limit);
  if (!list.length) return Promise.resolve();

  return Promise.race([
    Promise.all(
      list.map(
        (src) =>
          new Promise((resolve) => {
            const img = new Image();
            img.decoding = "async";
            img.onload = img.onerror = () => resolve();
            img.src = src;
          })
      )
    ),
    new Promise((resolve) => window.setTimeout(resolve, timeout)),
  ]);
}

export function collectHomePreloadUrls(galleryItems, brandPaths, foundersPhoto) {
  const mobile = window.matchMedia(MOBILE_MQ).matches;
  const urls = [];
  if (foundersPhoto) urls.push(foundersPhoto);
  brandPaths.slice(0, mobile ? 10 : 6).forEach((p) => urls.push(p));
  galleryItems.slice(0, mobile ? 24 : 12).forEach((item) => urls.push(item.src));
  return urls;
}

export function collectGalleryPreloadUrls(items) {
  const mobile = window.matchMedia(MOBILE_MQ).matches;
  const n = mobile ? 30 : 18;
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
    await new Promise((r) => window.setTimeout(r, 520));
    el.remove();
  }
}
