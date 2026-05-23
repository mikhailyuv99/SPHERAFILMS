(async function () {
  const grid = document.getElementById("video-grid");
  if (!grid) return;

  try {
    const res = await fetch("assets/vimeo.json");
    const ids = await res.json();
    grid.innerHTML = ids
      .map(
        (id, i) => `
      <div class="video-card" data-reveal="fade" style="--i:${i}">
        <iframe
          src="https://player.vimeo.com/video/${id}?title=0&byline=0&portrait=0&dnt=1"
          allow="autoplay; fullscreen; picture-in-picture"
          allowfullscreen
          loading="lazy"
          title="Sphera Films reel ${i + 1}"
        ></iframe>
      </div>`
      )
      .join("");
    document.dispatchEvent(new Event("gallery-loaded"));
  } catch (e) {
    console.warn("Vimeo grid failed", e);
  }
})();
