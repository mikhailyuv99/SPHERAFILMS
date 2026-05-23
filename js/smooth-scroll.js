/**
 * Luxury smooth scroll — Lenis with slow, weighted feel
 */
(function () {
  const script = document.createElement("script");
  script.src = "https://unpkg.com/lenis@1.1.18/dist/lenis.min.js";
  script.async = true;
  script.onload = initLenis;
  document.head.appendChild(script);

  function initLenis() {
    const lenis = new Lenis({
      duration: 1.8,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: "vertical",
      gestureOrientation: "vertical",
      smoothWheel: true,
      wheelMultiplier: 0.85,
      touchMultiplier: 1.2,
      infinite: false,
    });

    window.lenis = lenis;

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (e) => {
        const id = anchor.getAttribute("href");
        if (!id || id === "#") return;
        const target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        lenis.scrollTo(target, { offset: -110, duration: 2.2 });
      });
    });

    window.addEventListener("load", () => lenis.resize());

    lenis.on("scroll", () => {
      window.dispatchEvent(new CustomEvent("app-scroll"));
    });
  }
})();
