/**
 * Scroll reveals that regenerate when elements leave and re-enter viewport
 */
(function () {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReduced) {
    document.querySelectorAll("[data-reveal]").forEach((el) => el.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const el = entry.target;
        if (entry.isIntersecting) {
          el.classList.add("is-visible");
        } else {
          // Regenerate: remove class when scrolled away (threshold allows re-trigger)
          if (entry.intersectionRatio === 0) {
            el.classList.remove("is-visible");
          }
        }
      });
    },
    {
      root: null,
      rootMargin: "0px 0px -8% 0px",
      threshold: [0, 0.12, 0.35],
    }
  );

  function observeAll(root = document) {
    root.querySelectorAll("[data-reveal]").forEach((el) => {
      if (!el.dataset.revealBound) {
        el.dataset.revealBound = "1";
        observer.observe(el);
      }
    });
    root.querySelectorAll("[data-reveal-stagger]").forEach((parent) => {
      [...parent.children].forEach((child, i) => {
        child.style.setProperty("--i", i);
        if (!child.hasAttribute("data-reveal")) child.setAttribute("data-reveal", "up");
        if (!child.dataset.revealBound) {
          child.dataset.revealBound = "1";
          observer.observe(child);
        }
      });
    });
  }

  observeAll();
  document.addEventListener("gallery-loaded", () => observeAll());
})();
