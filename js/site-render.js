/**
 * Renders media in the same order as spherafilms.com (from site-data.json).
 */
(function () {
  const isImage = (s) => /\.(jpg|jpeg|png|webp|gif|svg)$/i.test(s);
  const isVideo = (s) => s.endsWith(".mp4");

  function el(tag, attrs, html) {
    const n = document.createElement(tag);
    if (attrs) Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
    if (html != null) n.innerHTML = html;
    return n;
  }

  function mediaFigure(src, index) {
    const fig = el("figure", { class: "media-block", "data-reveal": "fade" });
    fig.style.setProperty("--i", index % 14);
    if (isVideo(src)) {
      const v = el("video", {
        src,
        muted: "",
        loop: "",
        playsinline: "",
        preload: "metadata",
      });
      v.autoplay = true;
      fig.appendChild(v);
    } else if (isImage(src)) {
      const img = el("img", { src, alt: "", loading: "lazy" });
      fig.appendChild(img);
    }
    return fig;
  }

  async function init() {
    const res = await fetch("assets/site-data.json");
    const data = await res.json();
    const c = data.copy;

    document.querySelectorAll("[data-copy]").forEach((node) => {
      const key = node.getAttribute("data-copy");
      const text = c[key];
      if (!text) return;
      if (text.includes("\n")) {
        node.innerHTML = text.split("\n").join("<br />");
      } else {
        node.textContent = text.replace(/\s+/g, " ").trim();
      }
    });

    const artGrid = document.getElementById("art-photos");
    if (artGrid && data.home.photos) {
      const artPhotos = data.home.photos.slice(0, 10);
      artGrid.innerHTML = "";
      artPhotos.forEach((src, i) => artGrid.appendChild(mediaFigure(src, i)));
    }

    const services = document.getElementById("service-media");
    if (services && data.home.photos.length > 11) {
      services.innerHTML = "";
      [10, 11].forEach((idx, i) => {
        if (data.home.photos[idx]) {
          const wrap = el("div", { class: "service-media__item", "data-reveal": "scale" });
          wrap.style.setProperty("--i", i);
          wrap.appendChild(mediaFigure(data.home.photos[idx], i));
          services.appendChild(wrap);
        }
      });
    }

    const flow = document.getElementById("photo-flow");
    if (flow && data.home.photos) {
      flow.innerHTML = "";
      data.home.photos.slice(12).forEach((src, i) => flow.appendChild(mediaFigure(src, i)));
    }

    const travail = document.getElementById("travail-videos");
    if (travail) {
      travail.innerHTML = "";
      data.home.videos
        .filter((s) => isVideo(s))
        .forEach((src, i) => {
          const block = el("div", { class: "travail-item", "data-reveal": "fade" });
          block.style.setProperty("--i", i);
          const v = el("video", {
            src,
            controls: "",
            playsinline: "",
            preload: "metadata",
            poster: data.home.photos[0] || "",
          });
          block.appendChild(v);
          travail.appendChild(block);
        });
    }

    const vimeo = document.getElementById("vimeo-grid");
    if (vimeo && data.vimeoIds) {
      vimeo.innerHTML = "";
      data.vimeoIds.forEach((id, i) => {
        const card = el("div", { class: "video-card", "data-reveal": "fade" });
        card.style.setProperty("--i", i);
        card.innerHTML = `<iframe src="https://player.vimeo.com/video/${id}?title=0&byline=0&portrait=0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen loading="lazy" title="Réalisation ${i + 1}"></iframe>`;
        vimeo.appendChild(card);
      });
    }

    const team = document.getElementById("team-photos");
    if (team && data.home.photos.length > 4) {
      team.innerHTML = "";
      data.home.photos.slice(-4).forEach((src, i) => team.appendChild(mediaFigure(src, i)));
    }

    const decor = document.getElementById("brand-decor");
    if (decor && data.home.brandAssets) {
      decor.innerHTML = "";
      data.home.brandAssets.forEach((src, i) => {
        if (!isImage(src)) return;
        const img = el("img", { src, alt: "", loading: "lazy", class: "brand-decor__img" });
        img.setAttribute("data-reveal", "fade");
        decor.appendChild(img);
      });
    }

    const mosaic = document.getElementById("gallerie-mosaic");
    if (mosaic) {
      const items = [
        ...data.home.photos,
        ...(data.gallery.photos || []).filter((p) => !data.home.photos.includes(p)),
      ];
      mosaic.innerHTML = "";
      items.forEach((src, i) => {
        const item = el("div", { class: "mosaic__item", "data-reveal": "fade" });
        item.style.setProperty("--i", i % 16);
        item.innerHTML = `<img src="${src}" alt="" loading="lazy" />`;
        mosaic.appendChild(item);
      });
    }

    const allStrip = document.getElementById("all-media-strip");
    if (allStrip) {
      allStrip.innerHTML = "";
      data.home.allMedia.forEach((src, i) => {
        if (src.endsWith(".m3u") || src.endsWith(".m4a")) return;
        allStrip.appendChild(mediaFigure(src, i));
      });
    }

    document.dispatchEvent(new Event("gallery-loaded"));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
