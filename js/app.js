/**
 * Sphera Films — original media order, premium layout
 */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  function media(src) {
    if (!src) return src;
    if (src.startsWith("_assets/")) return src;
    if (src.startsWith("assets/")) return src.replace(/^assets\//, "_assets/");
    return src;
  }

  function setCopy(c) {
    $$("[data-copy]").forEach((el) => {
      const k = el.dataset.copy;
      const v = c[k];
      if (v == null) return;
      if (v.includes("\n") && el.tagName !== "INPUT") {
        el.innerHTML = v.split("\n").join("<br />");
      } else {
        el.textContent = v.replace(/\s+/g, " ").trim();
      }
    });
    document.title = c.siteTitle || "Sphera Films";
  }

  function buildHomeShowcase(items, container) {
    if (!container || !items.length) return;
    container.innerHTML = items
      .map((src, i) => {
        const isWide = i % 5 === 2;
        const cls = isWide ? "home-shot home-shot--wide" : "home-shot";
        return `
        <figure class="${cls}" data-reveal="fade" style="--d:${(i % 10) * 50}ms">
          <img src="${media(src)}" alt="" loading="lazy" decoding="async" />
        </figure>`;
      })
      .join("");
  }

  function buildVideos(videos, container) {
    if (!container) return;
    container.innerHTML = videos
      .map(
        (src, i) => `
      <div class="video-item" data-reveal="fade" style="--d:${i * 80}ms">
        <video src="${media(src)}" controls playsinline preload="metadata"></video>
      </div>`
      )
      .join("");
  }

  function buildVimeo(ids, container) {
    if (!container) return;
    container.innerHTML = ids
      .map(
        (id, i) => `
      <div class="reel" data-reveal="fade" style="--d:${i * 50}ms">
        <iframe src="https://player.vimeo.com/video/${id}?title=0&byline=0&portrait=0"
          allow="autoplay; fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe>
      </div>`
      )
      .join("");
  }

  function buildMosaic(photos, container) {
    if (!container) return;
    container.innerHTML = photos
      .map(
        (src, i) => `
      <div class="g-mosaic__item" data-reveal="fade" style="--d:${(i % 14) * 40}ms">
        <img src="${media(src)}" alt="" loading="lazy" decoding="async" />
      </div>`
      )
      .join("");
  }

  function initScrollProgress() {
    const bar = $(".scroll-progress");
    if (!bar) return;
    const onScroll = () => {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = h > 0 ? `${(window.scrollY / h) * 100}%` : "0%";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("app-scroll", onScroll);
    onScroll();
  }

  function initHeader() {
    const header = $(".header");
    let last = 0;
    const onScroll = () => {
      const y = window.scrollY;
      header?.classList.toggle("is-scrolled", y > 40);
      if (y > 200 && y > last) header?.classList.add("is-hidden");
      else header?.classList.remove("is-hidden");
      last = y;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("app-scroll", onScroll);

    $(".menu-btn")?.addEventListener("click", () => {
      $(".nav")?.classList.toggle("is-open");
    });
    $$(".nav a").forEach((a) =>
      a.addEventListener("click", () => $(".nav")?.classList.remove("is-open"))
    );
  }

  function initCursor() {
    if (!matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    const d = document.createElement("div");
    const r = document.createElement("div");
    d.className = "cursor-d";
    r.className = "cursor-r";
    document.body.append(d, r);
    let mx = 0,
      my = 0,
      rx = 0,
      ry = 0;
    document.addEventListener("mousemove", (e) => {
      mx = e.clientX;
      my = e.clientY;
      d.style.left = mx + "px";
      d.style.top = my + "px";
    });
    const loop = () => {
      rx += (mx - rx) * 0.12;
      ry += (my - ry) * 0.12;
      r.style.left = rx + "px";
      r.style.top = ry + "px";
      requestAnimationFrame(loop);
    };
    loop();
    document.querySelectorAll("a, button, .home-shot, .g-mosaic__item, .reel").forEach((el) => {
      el.addEventListener("mouseenter", () => document.body.classList.add("cursor-hover"));
      el.addEventListener("mouseleave", () => document.body.classList.remove("cursor-hover"));
    });
  }

  function dismissPreloader() {
    if (document.body.classList.contains("is-ready")) return;
    document.body.classList.add("is-ready");
    setTimeout(() => document.body.classList.remove("is-loading"), 800);
  }

  function initPreloader() {
    const finish = () => setTimeout(dismissPreloader, 350);
    if (document.readyState === "complete") finish();
    else window.addEventListener("load", finish, { once: true });
    setTimeout(dismissPreloader, 3500);
  }

  async function init() {
    initPreloader();

    let data;
    try {
      const res = await fetch("assets/site-data.json");
      if (!res.ok) throw new Error(`site-data.json ${res.status}`);
      data = await res.json();
    } catch (err) {
      console.error("[Sphera Films]", err);
      return;
    }

    setCopy(data.copy);

    const heroVideo = $("#hero-video");
    if (heroVideo && data.heroVideo) {
      heroVideo.src = media(data.heroVideo);
      heroVideo.poster = media(data.heroPoster || "");
    }

    $$(".logo__mark, .preloader__logo").forEach((img) => {
      if (data.logo) img.src = data.logo;
    });

    const homeItems =
      data.homeShowcase ||
      (data.photos || []).filter((p) => !/fec4c46f|a4671c3c/i.test(p));

    buildHomeShowcase(homeItems, $("#home-showcase"));
    buildVideos(data.videos || [], $("#video-list"));
    buildVimeo(data.vimeoIds || [], $("#reel-grid"));
    buildMosaic(data.galleryPhotos || homeItems, $("#g-mosaic"));

    const gHero = $("#g-hero-img");
    const gal = data.galleryPhotos || homeItems;
    if (gHero && gal[0]) gHero.src = media(gal[0]);

    document.dispatchEvent(new Event("gallery-loaded"));
    initHeader();
    initScrollProgress();
    initCursor();

    const path = location.pathname.split("/").pop() || "index.html";
    $$(".nav a").forEach((a) => {
      const href = a.getAttribute("href");
      if (href === path || (path === "" && href === "index.html")) a.classList.add("is-active");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
