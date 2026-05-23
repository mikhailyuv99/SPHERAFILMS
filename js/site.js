/**
 * Sphera Films — home page
 */

import {
  GALLERY_EXCLUDE,
  loadGalleryPageOrder,
  partitionForRows,
  uniqueGalleryItems,
  stem,
} from "./gallery-data.js";
import { bindLightbox } from "./lightbox.js";
import { initScrollReveal, disableScrollReveal } from "./scroll-reveal.js";
import {
  startPreloader,
  finishPreloader,
  preloadImages,
  collectHomePreloadUrls,
  waitForDomImages,
  isMobileLayout,
} from "./preloader.js";
import { resolveVimeoThumbs } from "./vimeo-thumbs.js";
import { SOCIAL_ICONS } from "./social-icons.js";
const MAP = "assets/media-map";
const PHOTO_EXCLUDE = GALLERY_EXCLUDE;

const HERO_VIDEOS_TOP = 6;
const HERO_VIDEOS_BOTTOM = 5;
const SHOWCASE_ROWS = [
  { dir: "left", duration: 88 },
  { dir: "right", duration: 82 },
  { dir: "left", duration: 94 },
  { dir: "right", duration: 86 },
];

const FAQ_ITEMS = [
  {
    q: "Quels types de projets réalisez-vous généralement ?",
    a: "Spots publicitaires, films de marque, contenus pour réseaux sociaux, couverture d'événements et productions photo et vidéo sur la Côte d'Azur.",
  },
  {
    q: "Intervenez-vous uniquement à Cannes ?",
    a: "Basés à Cannes, nous tournons sur toute la French Riviera et nous déplaçons en France et à l'international selon vos besoins.",
  },
  {
    q: "Comment se déroule une collaboration ?",
    a: "Échange sur votre vision, proposition créative, planning de production, tournage et post-production jusqu'à la livraison des fichiers finaux.",
  },
  {
    q: "Quels sont vos délais de livraison ?",
    a: "Ils varient selon l'ampleur du projet. Un délai indicatif vous est communiqué dès la validation du devis.",
  },
  {
    q: "Proposez-vous photo et vidéo ?",
    a: "Oui, direction photo, réalisation, montage et direction artistique pour une image cohérente sur tous vos supports.",
  },
];

const FALLBACK_COPY = {
  founders: "Enzo Da Silva & Lani Giacinti",
  foundersIntro:
    "Duo créatif à la tête de Sphera Films, Enzo et Lani unissent leurs visions pour donner vie à des projets audiovisuels haut de gamme.",
  foundersEnzo:
    "Enzo, réalisateur et chef opérateur, façonne l'image et la mise en scène avec une approche cinématographique précise et émotionnelle.",
  foundersLani:
    "Lani, directrice artistique et co-réalisatrice, conçoit l'univers visuel, les moodboards et la direction esthétique de chaque projet.",
  foundersTogether:
    "Ensemble, ils s'entourent d'équipes techniques et créatives dédiées pour produire des œuvres visuellement fortes et cohérentes.",
  email: "spherafilms.contact@gmail.com",
  phones: "06.52.88.62.88 & 06.83.83.37.57",
};

const FALLBACK_SOCIAL = {
  instagram: "https://www.instagram.com/spherafilms",
  linkedin: "https://www.linkedin.com/company/sphera-films",
  youtube: "https://www.youtube.com/watch?v=d_y8a-BHyiQ",
  whatsapp: "https://wa.me/33652886288",
};

async function loadJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed ${path}`);
  return res.json();
}

function dedupe(paths) {
  const seen = new Set();
  return paths.filter((p) => {
    const id = stem(p);
    if (seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

function mergeCopy(copy) {
  return { ...FALLBACK_COPY, ...copy };
}

async function init() {
  const mobile = isMobileLayout();
  if (mobile) {
    document.documentElement.classList.add("is-mobile-home");
    disableScrollReveal();
    ["hero", "brands"].forEach((id) => {
      const section = document.getElementById(id);
      section?.removeAttribute("data-aos");
      section?.querySelectorAll("[data-aos]").forEach((el) => el.removeAttribute("data-aos"));
    });
  }

  const minWait = startPreloader();

  let copyData = { copy: FALLBACK_COPY, social: FALLBACK_SOCIAL, jotform: "" };
  let brands = { order: [] };
  let founders = { photo: "assets/media/founders.jpg" };
  let vimeo = { vimeoIds: [] };

  try {
    [copyData, brands, founders, vimeo] = await Promise.all([
      loadJson(`${MAP}/11-copy-text.json`),
      loadJson(`${MAP}/02-brand-marquee.json`),
      loadJson(`${MAP}/05-founders.json`),
      loadJson(`${MAP}/07-vimeo-realisations.json`),
    ]);
  } catch (err) {
    console.error("Media map load failed:", err);
  }

  const copy = mergeCopy(copyData.copy || {});
  const social = { ...FALLBACK_SOCIAL, ...(copyData.social || {}) };
  if (!social.youtube && social.facebook) {
    social.youtube = FALLBACK_SOCIAL.youtube;
  }

  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  const setText = (id, text) => {
    const el = document.getElementById(id);
    if (el && text) el.textContent = text;
  };

  setText("founders-names", copy.founders);
  setText("founders-intro-text", copy.foundersIntro);
  setText("founders-enzo-text", copy.foundersEnzo);
  setText("founders-lani-text", copy.foundersLani);
  setText("founders-together-text", copy.foundersTogether);

  const vimeoIds = vimeo.vimeoIds || [];
  const galleryItems = await loadGalleryPageOrder(PHOTO_EXCLUDE);
  const brandPaths = dedupe(brands.order || []);

  renderMarquee(brandPaths);
  renderHeroVideos(vimeoIds, {});

  const thumbMap = mobile ? await resolveVimeoThumbs(vimeoIds) : {};
  if (mobile && Object.keys(thumbMap).length) {
    document.querySelectorAll(".hero-video-card[data-vimeo]").forEach((card) => {
      const url = thumbMap[card.dataset.vimeo];
      const img = card.querySelector("img");
      if (url && img && img.src !== url) img.src = url;
    });
  }
  const vimeoThumbUrls = mobile ? vimeoIds.map((id) => thumbMap[id]).filter(Boolean) : [];

  const preloadUrls = collectHomePreloadUrls(galleryItems, brandPaths, founders.photo, vimeoThumbUrls);
  const preloadWait = preloadImages(preloadUrls, {
    limit: mobile ? 50 : 24,
    timeout: mobile ? 30000 : 12000,
    required: mobile,
  });
  renderShowcase(galleryItems);
  renderFounders(founders);
  renderFaqContact(social, copy);

  initHeader();
  initNavToggle();
  initHeroVideoCarousel();
  initFooterLogo();
  initFaq();

  await Promise.all([minWait, preloadWait]);
  if (mobile) {
    await waitForDomImages([".marquee", ".hero-videos"], { timeout: 22000 });
  }
  document.body.classList.add("site-ready");
  await finishPreloader();
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      resetHeroVideoTracks();
      initHeroMarquees({ reset: true });
    });
  });
  if (!mobile) window.setTimeout(() => initScrollReveal(), 250);
}

const LOGO_WHITE = new Set(["fc2f20543a9918c2f89d5674dd1518b0"]);
const LOGO_LARGE = new Set([
  "6fbf1b251541154a6934b7190875b5f4", // IZIPIZI
  "95471e4a40b667fab94d711c30697a66", // APM Monaco
  "a4671c3cdc93430705491cd465b7215a", // BMW
]);

function renderMarquee(logos) {
  const track = document.getElementById("marquee-track");
  if (!track || !logos.length) return;
  const mobile = isMobileLayout();
  const items = logos
    .map((src, i) => {
      const white = LOGO_WHITE.has(stem(src)) ? " marquee__logo--white" : "";
      const large = LOGO_LARGE.has(stem(src)) ? " marquee__logo--lg" : "";
      const decode = mobile ? ' decoding="sync"' : ' decoding="async"';
      const load = mobile ? "eager" : "lazy";
      const priority = mobile && i < 10 ? ' fetchpriority="high"' : "";
      return `<img class="marquee__logo${white}${large}" src="${src}" alt="" loading="${load}"${decode}${priority}>`;
    })
    .join("");
  const set = `<div class="marquee__set">${items}</div>`;
  track.innerHTML = `${set}<div class="marquee__set" aria-hidden="true">${items}</div>`;
}

function heroVideoCardDesktop(id) {
  return `<article class="hero-video-card" data-vimeo="${id}" role="button" tabindex="0" aria-label="Lire la vidéo">
      <div class="hero-video-card__media">
        <img class="hero-video-card__poster" src="https://vumbnail.com/${id}.jpg" alt="" loading="lazy" decoding="async">
        <span class="hero-video-card__play" aria-hidden="true"></span>
      </div>
    </article>`;
}

function heroVideoCardMobile(id, thumbMap = {}) {
  const poster = thumbMap[id] || `https://vumbnail.com/${id}.jpg`;
  return `<article class="hero-video-card" data-vimeo="${id}" role="button" tabindex="0" aria-label="Lire la vidéo">
      <div class="hero-video-card__media">
        <img src="${poster}" alt="" loading="eager" decoding="sync">
        <span class="hero-video-card__play" aria-hidden="true"></span>
      </div>
    </article>`;
}

function resetHeroVideoTracks() {
  document.querySelectorAll(".hero-videos__mover").forEach((mover) => {
    const track = mover.querySelector(".hero-videos__track");
    if (track && mover.parentElement) {
      mover.parentElement.insertBefore(track, mover);
    }
    mover.remove();
  });
  document.querySelectorAll(".hero-videos__track").forEach((track) => {
    track.style.removeProperty("transform");
    track.style.removeProperty("animation");
  });
}

let heroMarquees = [];
let heroDragStates = [];
let heroDragBound = false;
let heroRafId = 0;

function measureHeroLoop(track) {
  const cards = track.querySelectorAll(".hero-video-card");
  const half = cards.length / 2;
  if (!Number.isInteger(half) || half < 1 || !cards[half]) return 0;
  return Math.round(cards[half].offsetLeft - cards[0].offsetLeft);
}

function wrapHeroOffset(offset, loopW) {
  if (loopW <= 0) return offset;
  while (offset <= -loopW) offset += loopW;
  while (offset > 0) offset -= loopW;
  return offset;
}

function syncHeroMarqueeLoop(track) {
  if (!track) return;
  const loopW = measureHeroLoop(track);
  if (loopW > 0) track.style.setProperty("--loop-w", `${loopW}px`);
  else track.style.removeProperty("--loop-w");
}

function ensureHeroMover(track) {
  const parent = track.parentElement;
  if (parent?.classList.contains("hero-videos__mover")) return parent;
  const mover = document.createElement("div");
  mover.className = "hero-videos__mover";
  track.parentElement.insertBefore(mover, track);
  mover.appendChild(track);
  return mover;
}

function getHeroScrollState(track) {
  if (isMobileLayout()) {
    return heroMarquees.find((state) => state.track === track) || null;
  }
  return heroDragStates.find((state) => state.track === track) || null;
}

function applyHeroScrollTransform(state) {
  if (!state) return;
  if (isMobileLayout()) {
    state.track.style.transform = `translate3d(${state.offset + state.dragDelta}px, 0, 0)`;
  } else {
    state.mover.style.transform = `translate3d(${state.userX + state.dragDelta}px, 0, 0)`;
  }
}

function tickHeroMarquees(now) {
  if (!isMobileLayout() || !heroMarquees.length) return;

  for (const state of heroMarquees) {
    if (!state.active) continue;
    if (!state.lastTime) state.lastTime = now;
    const dt = Math.min(now - state.lastTime, 32);
    state.lastTime = now;

    if (!state.paused) {
      if (state.direction < 0) {
        state.offset -= state.speed * dt;
        if (state.offset <= -state.loopW) state.offset += state.loopW;
      } else {
        state.offset += state.speed * dt;
        if (state.offset >= 0) state.offset -= state.loopW;
      }
    }

    applyHeroScrollTransform(state);
  }
}

function ensureHeroTicker() {
  if (!isMobileLayout() || heroRafId) return;
  const loop = (t) => {
    tickHeroMarquees(t);
    heroRafId = requestAnimationFrame(loop);
  };
  heroRafId = requestAnimationFrame(loop);
}

function stopHeroMarquees() {
  heroMarquees.forEach((state) => {
    state.active = false;
  });
  heroMarquees = [];
  heroDragStates = [];
  if (heroRafId) {
    cancelAnimationFrame(heroRafId);
    heroRafId = 0;
  }
}

function startHeroMarqueeMobile(track, direction, durationSec = 48) {
  const loopW = measureHeroLoop(track);
  if (loopW <= 0) return null;

  track.style.animation = "none";

  const state = {
    track,
    direction,
    durationSec,
    loopW,
    offset: direction < 0 ? 0 : -loopW,
    dragDelta: 0,
    paused: false,
    active: true,
    lastTime: 0,
    speed: loopW / (durationSec * 1000),
  };

  heroMarquees.push(state);
  ensureHeroTicker();
  return state;
}

function initHeroMarqueesDesktop({ attempt = 0 } = {}) {
  heroDragStates = [];

  const top = document.getElementById("hero-video-track-top");
  const bottom = document.getElementById("hero-video-track-bottom");
  const tracks = [top, bottom].filter(Boolean);

  tracks.forEach((track) => {
    track.style.removeProperty("transform");
    track.style.removeProperty("animation");
    syncHeroMarqueeLoop(track);
    const mover = ensureHeroMover(track);
    mover.style.transform = "";
    heroDragStates.push({ mover, track, userX: 0, dragDelta: 0 });
  });

  if (heroDragStates.length === 0 && attempt < 15) {
    window.setTimeout(() => initHeroMarqueesDesktop({ attempt: attempt + 1 }), 150);
  }
}

function initHeroMarqueesMobile({ reset = false, attempt = 0 } = {}) {
  if (heroMarquees.length > 0 && !reset) {
    heroMarquees.forEach((state) => {
      const w = measureHeroLoop(state.track);
      if (w > 0) {
        state.loopW = w;
        state.speed = w / (state.durationSec * 1000);
        state.offset = wrapHeroOffset(state.offset, w);
      }
    });
    return;
  }

  heroMarquees = [];

  const top = document.getElementById("hero-video-track-top");
  const bottom = document.getElementById("hero-video-track-bottom");

  if (top) startHeroMarqueeMobile(top, -1, 48);
  if (bottom) startHeroMarqueeMobile(bottom, 1, 44);

  if (heroMarquees.length === 0 && attempt < 15) {
    window.setTimeout(() => initHeroMarqueesMobile({ reset: true, attempt: attempt + 1 }), 150);
  }
}

function initHeroMarquees({ reset = false, attempt = 0 } = {}) {
  if (isMobileLayout()) {
    if (reset) stopHeroMarquees();
    initHeroMarqueesMobile({ reset: true, attempt });
    return;
  }

  stopHeroMarquees();
  initHeroMarqueesDesktop({ attempt });
}

function initHeroDragScroll(wrap) {
  if (!wrap || heroDragBound) return;
  heroDragBound = true;

  const drag = {
    active: false,
    moved: false,
    pointerId: 0,
    startX: 0,
    startY: 0,
    startTime: 0,
    startDragDelta: 0,
    state: null,
    viewport: null,
    card: null,
  };

  const isMobileDeliberateTap = (e) => {
    const dx = e.clientX - drag.startX;
    const dy = e.clientY - drag.startY;
    const elapsed = performance.now() - drag.startTime;
    return (
      elapsed < 400 &&
      Math.abs(dx) < 12 &&
      Math.abs(dy) < 12 &&
      Math.hypot(dx, dy) < 14
    );
  };

  const finishDrag = (e) => {
    if (!drag.active || e.pointerId !== drag.pointerId) return;

    const card = drag.card;
    const moved = drag.moved;

    if (drag.state) {
      if (isMobileLayout()) {
        drag.state.offset = wrapHeroOffset(drag.state.offset + drag.state.dragDelta, drag.state.loopW);
      } else {
        drag.state.userX += drag.state.dragDelta;
      }
      drag.state.dragDelta = 0;
      applyHeroScrollTransform(drag.state);
    }

    drag.viewport?.classList.remove("is-dragging");
    wrap.classList.remove("is-dragging");

    if (card && !moved) {
      if (!isMobileLayout() || isMobileDeliberateTap(e)) {
        openVideo(card.dataset.vimeo);
      }
    }

    drag.active = false;
    drag.moved = false;
    drag.state = null;
    drag.viewport = null;
    drag.card = null;
    drag.pointerId = 0;
  };

  wrap.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return;
    const viewport = e.target.closest(".hero-videos__viewport");
    if (!viewport) return;
    const track = viewport.querySelector(".hero-videos__track");
    const state = getHeroScrollState(track);
    if (!state) return;

    drag.active = true;
    drag.moved = false;
    drag.pointerId = e.pointerId;
    drag.startX = e.clientX;
    drag.startY = e.clientY;
    drag.startTime = performance.now();
    drag.startDragDelta = state.dragDelta;
    drag.state = state;
    drag.viewport = viewport;
    drag.card = e.target.closest(".hero-video-card");

    viewport.classList.add("is-dragging");
    wrap.classList.add("is-dragging");

    try {
      viewport.setPointerCapture(e.pointerId);
    } catch (_) {
      /* ignore */
    }
  });

  wrap.addEventListener("pointermove", (e) => {
    if (!drag.active || e.pointerId !== drag.pointerId || !drag.state) return;

    const dx = e.clientX - drag.startX;
    const dy = e.clientY - drag.startY;
    if (!drag.moved && (Math.abs(dx) > 6 || Math.abs(dy) > 6)) {
      if (isMobileLayout()) {
        drag.moved = Math.abs(dy) > 8 || Math.abs(dx) > 12;
      } else {
        drag.moved = Math.abs(dx) > Math.abs(dy) * 0.55 || Math.abs(dx) > 10;
      }
    }

    if (drag.moved) {
      drag.state.dragDelta = drag.startDragDelta + dx;
      applyHeroScrollTransform(drag.state);
    }
  });

  wrap.addEventListener("pointerup", finishDrag);
  wrap.addEventListener("pointercancel", finishDrag);

  wrap.addEventListener(
    "wheel",
    (e) => {
      if (!Math.abs(e.deltaX)) return;
      const viewport = e.target.closest(".hero-videos__viewport");
      if (!viewport) return;
      const state = getHeroScrollState(viewport.querySelector(".hero-videos__track"));
      if (!state || Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;
      e.preventDefault();
      if (isMobileLayout()) {
        state.offset = wrapHeroOffset(state.offset - e.deltaX, state.loopW);
      } else {
        state.userX -= e.deltaX;
      }
      applyHeroScrollTransform(state);
    },
    { passive: false }
  );
}

function renderHeroVideos(ids, thumbMap = {}) {
  const topTrack = document.getElementById("hero-video-track-top");
  const bottomTrack = document.getElementById("hero-video-track-bottom");
  if (!topTrack || !bottomTrack || !ids.length) return;

  resetHeroVideoTracks();

  const mobile = isMobileLayout();
  const card = mobile ? (id) => heroVideoCardMobile(id, thumbMap) : (id) => heroVideoCardDesktop(id);

  const fillTrack = (track, videoIds) => {
    const items = videoIds.map(card).join("");
    if (mobile) {
      track.innerHTML = items + items;
    } else {
      track.innerHTML = `<div class="hero-videos__set">${items}</div>` + `<div class="hero-videos__set" aria-hidden="true">${items}</div>`;
    }
  };

  fillTrack(topTrack, ids.slice(0, HERO_VIDEOS_TOP));
  fillTrack(bottomTrack, ids.slice(HERO_VIDEOS_TOP, HERO_VIDEOS_TOP + HERO_VIDEOS_BOTTOM));

  requestAnimationFrame(() => {
    initHeroMarquees({ reset: true });
  });
}

function initHeroRowPause(wrap) {
  if (!wrap) return;
  wrap.querySelectorAll(".hero-videos__row").forEach((row) => {
    row.addEventListener("mouseenter", () => {
      row.classList.add("is-paused");
      if (isMobileLayout()) {
        const state = getHeroScrollState(row.querySelector(".hero-videos__track"));
        if (state) state.paused = true;
      }
    });
    row.addEventListener("mouseleave", () => {
      row.classList.remove("is-paused");
      if (isMobileLayout()) {
        const state = getHeroScrollState(row.querySelector(".hero-videos__track"));
        if (state) state.paused = false;
      }
    });
  });
}

function initRowPause(container, rowSelector) {
  if (!container) return;
  container.querySelectorAll(rowSelector).forEach((row) => {
    row.addEventListener("mouseenter", () => row.classList.add("is-paused"));
    row.addEventListener("mouseleave", () => row.classList.remove("is-paused"));
  });
}

function initHeroVideoCarousel() {
  const wrap = document.getElementById("hero-videos");
  if (!wrap) return;

  wrap.querySelectorAll(".hero-video-card").forEach((card) => {
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openVideo(card.dataset.vimeo);
      }
    });
  });

  initHeroRowPause(wrap);
  initHeroDragScroll(wrap);

  let resizeTimer;
  let marqueeViewportW = window.innerWidth;
  window.addEventListener(
    "resize",
    () => {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => {
        if (window.innerWidth === marqueeViewportW) return;
        marqueeViewportW = window.innerWidth;
        resetHeroVideoTracks();
        initHeroMarquees({ reset: true });
      }, 150);
    },
    { passive: true }
  );
}

function openVideo(id) {
  if (!id) return;
  let modal = document.getElementById("video-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "video-modal";
    modal.className = "video-modal";
    modal.innerHTML = `<div class="video-modal__backdrop"></div><div class="video-modal__box"><button type="button" class="video-modal__close" aria-label="Fermer">&times;</button><div class="video-modal__frame"></div></div>`;
    document.body.appendChild(modal);
    modal.querySelector(".video-modal__backdrop").addEventListener("click", closeVideo);
    modal.querySelector(".video-modal__close").addEventListener("click", closeVideo);
  }
  modal.querySelector(".video-modal__frame").innerHTML =
    `<iframe src="https://player.vimeo.com/video/${id}?autoplay=1&title=0&byline=0&portrait=0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen title="Sphera Films"></iframe>`;
  modal.classList.add("is-open");
  document.body.style.overflow = "hidden";
  if (window.lenis) window.lenis.stop();
}

function closeVideo() {
  const modal = document.getElementById("video-modal");
  if (!modal) return;
  modal.classList.remove("is-open");
  modal.querySelector(".video-modal__frame").innerHTML = "";
  document.body.style.overflow = "";
  if (window.lenis) window.lenis.start();
}

function showcaseCell(item, eager = false) {
  const load = eager ? "eager" : "lazy";
  const priority = eager ? ' fetchpriority="high"' : "";
  return `<figure class="showcase-marquee__cell" data-lightbox data-src="${item.src}" data-id="${item.id}">
    <img src="${item.src}" alt="" loading="${load}" decoding="async" width="600" height="750"${priority}>
  </figure>`;
}

function renderShowcaseRow(rowItems, dir, duration, eagerRow = false) {
  if (!rowItems.length) return "";
  const eager = eagerRow && isMobileLayout();
  const cells = rowItems.map((item, i) => showcaseCell(item, eager && i < 6)).join("");
  const set = `<div class="showcase-marquee__set">${cells}</div>`;
  return `<div class="showcase-marquee__row">
    <div class="showcase-marquee__track showcase-marquee__track--${dir}" style="--duration:${duration}s">
      ${set}${set}
    </div>
  </div>`;
}

function renderShowcase(items) {
  const root = document.getElementById("showcase-grid");
  if (!root) return;

  const rowPools = partitionForRows(items, SHOWCASE_ROWS.length, PHOTO_EXCLUDE);
  if (!rowPools.some((row) => row.length)) {
    root.innerHTML = "";
    return;
  }

  root.className = "showcase-marquee";
  root.innerHTML = SHOWCASE_ROWS.map((row, i) =>
    renderShowcaseRow(rowPools[i] || [], row.dir, row.duration, i < 2)
  )
    .filter(Boolean)
    .join("");

  root.querySelectorAll("img").forEach((img) => {
    img.addEventListener("error", () => img.closest(".showcase-marquee__cell")?.remove());
  });

  initRowPause(root, ".showcase-marquee__row");
  bindLightbox(root, "[data-lightbox]");
}

function linkHtml({ href, label, icon, external }) {
  const ext = external ? ' target="_blank" rel="noopener noreferrer"' : "";
  return `<a class="connect__link connect__link--${icon}" href="${href}"${ext} aria-label="${label}">${SOCIAL_ICONS[icon] || ""}</a>`;
}

function parsePhoneLinks(phonesStr) {
  const matches = String(phonesStr || "").match(/\d{2}(?:\.\d{2}){4}/g) || [];
  return matches.map((display) => {
    const digits = display.replace(/\./g, "");
    const href = `tel:+33${digits.startsWith("0") ? digits.slice(1) : digits}`;
    return { display, href };
  });
}

function renderFaqContact(social, copy) {
  const email = copy.email || FALLBACK_COPY.email;
  const phones = parsePhoneLinks(copy.phones || FALLBACK_COPY.phones);

  const socialLinks = [
    { href: social.instagram, label: "Instagram", icon: "instagram", external: true },
    { href: social.youtube, label: "YouTube", icon: "youtube", external: true },
    { href: social.linkedin, label: "LinkedIn", icon: "linkedin", external: true },
  ].filter((l) => l.href);

  const faqEl = document.getElementById("faq-list");
  if (faqEl) {
    faqEl.innerHTML = FAQ_ITEMS.map(
      (item) =>
        `<details class="faq__item">
          <summary class="faq__q">${item.q}</summary>
          <div class="faq__a"><p>${item.a}</p></div>
        </details>`
    ).join("");
  }

  const socialWrap = document.getElementById("contact-social");
  if (socialWrap) {
    const phoneLines = phones
      .map(({ display, href }) => `<a class="faq-contact__text" href="${href}">${display}</a>`)
      .join("");
    const emailLine = `<a class="faq-contact__text" href="mailto:${email}">${email}</a>`;

    socialWrap.innerHTML = `
      <div class="connect__row">${socialLinks.map(linkHtml).join("")}</div>
      <div class="faq-contact__text-block">${phoneLines}${emailLine}</div>`;
  }
}

function initFaq() {
  document.querySelectorAll(".faq__item").forEach((item) => {
    item.addEventListener("toggle", () => {
      if (!item.open) return;
      document.querySelectorAll(".faq__item").forEach((other) => {
        if (other !== item) other.open = false;
      });
    });
  });
}

function initFooterLogo() {
  const link = document.getElementById("footer-logo");
  if (!link) return;
  link.addEventListener("click", (e) => {
    e.preventDefault();
    if (window.lenis?.scrollTo) {
      window.lenis.scrollTo(0, { duration: 1.4 });
    } else {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  });
}

function renderFounders(data) {
  const img = document.getElementById("founders-photo");
  if (!img || !data?.photo) return;
  img.src = data.photo;
  if (isMobileLayout()) {
    img.loading = "eager";
    img.fetchPriority = "high";
  }
}

function scrollY() {
  if (window.lenis && typeof window.lenis.scroll === "number") return window.lenis.scroll;
  return window.scrollY || 0;
}

function initHeader() {
  const header = document.querySelector(".site-header");
  if (!header) return;
  const onScroll = () => header.classList.toggle("is-scrolled", scrollY() > 40);
  onScroll();
  document.addEventListener("site-scroll", onScroll);
  window.addEventListener("scroll", onScroll, { passive: true });
}

function setNavOpen(open) {
  const btn = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (!btn || !nav) return;
  nav.classList.toggle("is-open", open);
  btn.setAttribute("aria-expanded", String(open));
  document.body.classList.toggle("nav-open", open);
}

function initNavToggle() {
  const btn = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (!btn || !nav) return;

  btn.addEventListener("click", () => setNavOpen(!nav.classList.contains("is-open")));
  nav.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => setNavOpen(false));
  });
}

init().catch(async (err) => {
  console.error(err);
  if (isMobileLayout()) disableScrollReveal();
  document.body.classList.add("site-ready");
  await finishPreloader();
  if (!isMobileLayout()) initScrollReveal();
  document.querySelectorAll("[data-aos], .reveal").forEach((el) => {
    el.style.opacity = "1";
    el.style.transform = "none";
  });
});
