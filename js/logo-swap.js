/**
 * Replace Canva export logo assets with assets/logo.svg (transparent).
 */
(function () {
  const LOGO = "./assets/logo.svg?v=4";
  const MARKERS = [
    "a4671c3cdc93430705491cd465b7215a",
    "88c84b8adc504d0c6bc888ad132eb388",
    "4c51dd0398a1625f638af77912acc3e1",
    "84672a2709fae3b97a971eb98320ab9f",
    "fec4c46f59d2687154e3f364f3b1cff0",
    "fea1775c265beea9b248f4fa76d938d0",
  ];

  function isLogo(url) {
    if (!url || typeof url !== "string") return false;
    return MARKERS.some((m) => url.includes(m));
  }

  function patchImg(img) {
    if (!isLogo(img.currentSrc || img.src)) return;
    img.src = LOGO;
    img.removeAttribute("srcset");
    img.style.background = "transparent";
    img.style.backgroundColor = "transparent";
    img.style.objectFit = "contain";
  }

  function patchNode(el) {
    if (el.tagName === "IMG") {
      patchImg(el);
      return;
    }
    const bg = el.style && el.style.backgroundImage;
    if (bg && isLogo(bg)) {
      el.style.backgroundImage = `url("${LOGO}")`;
      el.style.backgroundColor = "transparent";
      el.style.backgroundSize = "contain";
      el.style.backgroundRepeat = "no-repeat";
      el.style.backgroundPosition = "center";
    }
  }

  function scan(root) {
    if (!root || !root.querySelectorAll) return;
    root.querySelectorAll("img, [style*='background']").forEach(patchNode);
  }

  function start() {
    const root = document.getElementById("root");
    if (!root) return;
    scan(root);
    new MutationObserver(() => scan(root)).observe(root, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["src", "srcset"],
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
