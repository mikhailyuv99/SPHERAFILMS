(function () {
  const body = document.body;
  const header = document.querySelector(".header");
  const menuToggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav");

  /* Preloader */
  window.addEventListener("load", () => {
    setTimeout(() => body.classList.add("is-ready"), 400);
    setTimeout(() => body.classList.remove("is-loading"), 1200);
  });

  /* Header hide on scroll */
  let lastY = 0;
  const onScroll = () => {
    const y = window.scrollY || 0;
    if (header) {
      if (y > 120 && y > lastY) header.classList.add("is-hidden");
      else header.classList.remove("is-hidden");
    }
    lastY = y;
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("app-scroll", onScroll);

  /* Mobile menu */
  menuToggle?.addEventListener("click", () => {
    nav?.classList.toggle("is-open");
    menuToggle.classList.toggle("is-active");
  });

  nav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => nav.classList.remove("is-open"));
  });

  /* Custom cursor */
  if (matchMedia("(hover: hover) and (pointer: fine)").matches) {
    const dot = document.createElement("div");
    const ring = document.createElement("div");
    dot.className = "cursor-dot";
    ring.className = "cursor-ring";
    document.body.append(dot, ring);

    let mx = 0,
      my = 0,
      rx = 0,
      ry = 0;

    document.addEventListener("mousemove", (e) => {
      mx = e.clientX;
      my = e.clientY;
      dot.style.left = mx + "px";
      dot.style.top = my + "px";
    });

    const animateCursor = () => {
      rx += (mx - rx) * 0.12;
      ry += (my - ry) * 0.12;
      ring.style.left = rx + "px";
      ring.style.top = ry + "px";
      requestAnimationFrame(animateCursor);
    };
    animateCursor();

    document.querySelectorAll("a, button, .mosaic__item, .h-scroll__card").forEach((el) => {
      el.addEventListener("mouseenter", () => body.classList.add("has-cursor-hover"));
      el.addEventListener("mouseleave", () => body.classList.remove("has-cursor-hover"));
    });
  }

  /* Horizontal scroll section */
  const hScroll = document.querySelector(".h-scroll");
  if (hScroll && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const pin = hScroll.querySelector(".h-scroll__pin");
    const track = hScroll.querySelector(".h-scroll__track");
    if (pin && track) {
      const updateHorizontal = () => {
        const rect = pin.getBoundingClientRect();
        const pinH = pin.offsetHeight;
        const trackW = track.scrollWidth - window.innerWidth + parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--gutter")) * 2;
        if (trackW <= 0) return;

        const progress = Math.min(1, Math.max(0, (-rect.top) / (pinH - window.innerHeight)));
        track.style.transform = `translateX(${-progress * trackW}px)`;
      };
      window.addEventListener("scroll", updateHorizontal, { passive: true });
      window.addEventListener("app-scroll", updateHorizontal);
      window.addEventListener("resize", updateHorizontal);
      updateHorizontal();
    }
  }

  /* Active nav link */
  const path = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav a").forEach((a) => {
    const href = a.getAttribute("href");
    if (href === path || (path === "" && href === "index.html")) a.classList.add("is-active");
  });

  /* Marquee duplicate for seamless loop */
  document.querySelectorAll(".marquee__track").forEach((track) => {
    const html = track.innerHTML;
    track.innerHTML = html + html;
  });
})();
