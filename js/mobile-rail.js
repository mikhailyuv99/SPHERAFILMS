/**
 * Mobile-only horizontal touch scroll (no arrows). Desktop keeps CSS marquees.
 */
import { MOBILE_MQ } from "./preloader.js";

export function isMobileLayout() {
  return window.matchMedia(MOBILE_MQ).matches;
}

/** Stop Lenis from hijacking horizontal swipes on scroll rails */
export function initMobileRails() {
  if (!isMobileLayout()) return;

  document.documentElement.classList.add("is-mobile-rail");

  document.querySelectorAll(".js-touch-rail").forEach((rail) => {
    rail.setAttribute("data-lenis-prevent", "");
    rail.setAttribute("data-lenis-prevent-touch", "");

    let startX = 0;
    let startY = 0;

    rail.addEventListener(
      "touchstart",
      (e) => {
        const t = e.touches[0];
        startX = t.clientX;
        startY = t.clientY;
      },
      { passive: true }
    );

    rail.addEventListener(
      "touchmove",
      (e) => {
        const t = e.touches[0];
        const dx = Math.abs(t.clientX - startX);
        const dy = Math.abs(t.clientY - startY);
        if (dx > dy && dx > 8) e.stopPropagation();
      },
      { passive: true }
    );
  });
}
