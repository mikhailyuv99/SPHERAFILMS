/**
 * Loading screen — min 5s + wait for critical home/gallery media
 */
const MIN_MS = 5000;
export const MOBILE_MQ = "(max-width: 900px)";

export function isMobileLayout() {
  return window.matchMedia(MOBILE_MQ).matches;
}

export function startPreloader() {
  document.documentElement.classList.add("is-loading");
  const fill = document.querySelector(".site-preloader__fill");
  if (fill) fill.style.setProperty("--preloader-duration", `${MIN_MS}ms`);
  return new Promise((resolve) => window.setTimeout(resolve, MIN_MS));
}

export function preloadImages(urls, { limit = 40, timeout = 20000 } = {}) {
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

/** After DOM render — wait for visible <img> elements in key sections */
export function waitForSectionImages(selectors, { timeout = 18000 } = {}) {
  const imgs = selectors.flatMap((sel) => [...document.querySelectorAll(`${sel} img`)]);
  if (!imgs.length) return Promise.resolve();

  const pending = imgs.map(
    (img) =>
      new Promise((resolve) => {
        if (img.complete && img.naturalWidth > 0) {
          resolve();
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

export function collectHomePreloadUrls(galleryItems, brandPaths, foundersPhoto, vimeoIds = []) {
  const mobile = isMobileLayout();
  const urls = [...brandPaths];
  vimeoIds.forEach((id) => urls.push(`https://vumbnail.com/${id}.jpg`));
  if (foundersPhoto) urls.push(foundersPhoto);
  galleryItems.slice(0, mobile ? 28 : 12).forEach((item) => urls.push(item.src));
  return urls;
}

export function collectGalleryPreloadUrls(items) {
  const n = isMobileLayout() ? 32 : 18;
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
