/**
 * Smooth fade-in when the page is ready (no loading screen)
 */
const MOBILE_MQ = "(max-width: 900px)";

if (!window.matchMedia(MOBILE_MQ).matches) {
  window.setTimeout(() => {
    document.documentElement.classList.add("is-revealed");
  }, 4500);
}

export function revealPage() {
  if (window.matchMedia(MOBILE_MQ).matches) {
    document.documentElement.classList.add("is-revealed");
    return;
  }
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      document.documentElement.classList.add("is-revealed");
    });
  });
}
