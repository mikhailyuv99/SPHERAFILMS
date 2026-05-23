/**
 * Scroll reveal — fade in/out on enter/leave (works with Lenis smooth scroll)
 */
const REVEAL_SELECTOR = ".reveal, [data-reveal], [data-aos]";

let observer = null;

function onIntersect(entries) {
  for (const entry of entries) {
    const el = entry.target;
    if (entry.isIntersecting) {
      el.classList.add("is-inview");
      el.classList.remove("is-outview");
    } else {
      el.classList.remove("is-inview");
      el.classList.add("is-outview");
    }
  }
}

function shouldReveal(el) {
  if (el.classList.contains("gallery-page") || el.id === "gallery-grid") return false;
  return true;
}

export function applySectionReveal(root = document) {
  const targets = root.querySelectorAll(
    "main section, main .showcase__mosaic-wrap, .site-footer"
  );

  targets.forEach((el, i) => {
    el.classList.add("reveal");
    if (!el.dataset.revealDelay) {
      el.style.setProperty("--reveal-delay", `${Math.min(i * 70, 280)}ms`);
    }
  });
}

export function initScrollReveal(root = document) {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  applySectionReveal(root);

  const elements = [...root.querySelectorAll(REVEAL_SELECTOR)].filter(shouldReveal);
  if (!elements.length) return;

  if (reduceMotion) {
    elements.forEach((el) => el.classList.add("is-inview"));
    return;
  }

  if (observer) {
    observer.disconnect();
  }

  observer = new IntersectionObserver(onIntersect, {
    root: null,
    rootMargin: "-10% 0px -10% 0px",
    threshold: 0.08,
  });

  elements.forEach((el) => {
    el.classList.add("reveal");
    const delay = el.getAttribute("data-aos-delay") || el.dataset.revealDelay;
    if (delay) el.style.setProperty("--reveal-delay", `${delay}ms`);
    observer.observe(el);
  });

  requestAnimationFrame(() => {
    for (const el of elements) {
      const r = el.getBoundingClientRect();
      const vh = window.innerHeight || document.documentElement.clientHeight;
      if (r.top < vh * 0.92 && r.bottom > vh * 0.08) {
        el.classList.add("is-inview");
        el.classList.remove("is-outview");
      }
    }
  });
}
