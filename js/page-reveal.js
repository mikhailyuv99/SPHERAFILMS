/**
 * Smooth fade-in when the page is ready (no loading screen)
 */
window.setTimeout(() => {
  document.documentElement.classList.add("is-revealed");
}, 4500);

export function revealPage() {
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      document.documentElement.classList.add("is-revealed");
    });
  });
}
