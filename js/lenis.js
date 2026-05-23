/**
 * Lenis smooth scroll (skipped in Instagram / in-app browsers — breaks fixed backgrounds)
 */
(function () {
  if (document.documentElement.classList.contains("is-inapp")) return;
  if (window.matchMedia("(max-width: 900px)").matches) return;

  const s = document.createElement("script");
  s.src = "https://unpkg.com/lenis@1.1.18/dist/lenis.min.js";
  s.onload = () => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 1.15,
      lerp: 0.1,
    });
    window.lenis = lenis;

    function raf(t) {
      lenis.raf(t);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href");
        if (!id || id === "#") return;
        const el = document.querySelector(id);
        if (!el) return;
        e.preventDefault();
        lenis.scrollTo(el, { offset: -88, duration: 1.6 });
      });
    });

    lenis.on("scroll", () => {
      document.dispatchEvent(new CustomEvent("site-scroll"));
    });
  };
  document.head.appendChild(s);
})();
