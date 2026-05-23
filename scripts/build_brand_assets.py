"""Generate brand folder: SVG variants + favicon, OG, apple-touch, Instagram PNGs."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "assets" / "brand"
SRC_BLACK = ROOT / "assets" / "logo.svg"
SRC_WHITE = ROOT / "assets" / "logo-white.svg"
BG_DARK = "#04080e"
BG_LIGHT = "#ffffff"
WORDMARK = "SPHERA FILMS"
# Match site .hero__wordmark (Syne, uppercase, wide tracking)
WORDMARK_STYLE = (
    'font-family="Syne, Arial, sans-serif" font-size="{size}" font-weight="600" '
    'letter-spacing="0.42em" text-transform="uppercase" text-anchor="middle"'
)
LOGO_SCALE_WORDMARK = 0.22
LOGO_SCALE_OG = 0.32
LOGO_SCALE_FAVICON_PAD = 0.08


def load_logo_path() -> str:
    import re

    svg = SRC_BLACK.read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', svg)
    if not match:
        raise SystemExit("Could not parse logo path from assets/logo.svg")
    return match.group(1)


def wordmark_svg(path_d: str, fill: str, bg: str | None, width: int = 800, height: int = 400) -> str:
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    text_size = int(width * 0.065)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  {bg_rect}
  <g transform="translate({width / 2} {height * 0.42}) scale({LOGO_SCALE_WORDMARK}) translate(-1000 -1000)">
    <path fill="{fill}" d="{path_d}"/>
  </g>
  <text x="{width / 2}" y="{height * 0.82}" fill="{fill}" {WORDMARK_STYLE.format(size=text_size)} text-indent="0.42em">{WORDMARK}</text>
</svg>
"""


def mark_only_svg(path_d: str, fill: str, bg: str | None, size: int = 512) -> str:
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    pad = size * LOGO_SCALE_FAVICON_PAD
    inner = size - pad * 2
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  {bg_rect}
  <g transform="translate({size / 2} {size / 2}) scale({inner / 2000}) translate(-1000 -1000)">
    <path fill="{fill}" d="{path_d}"/>
  </g>
</svg>
"""


def og_svg(path_d: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="{BG_DARK}"/>
  <g transform="translate(600 255) scale({LOGO_SCALE_OG}) translate(-1000 -1000)">
    <path fill="#ffffff" d="{path_d}"/>
  </g>
  <text x="600" y="500" fill="#e8eef5" {WORDMARK_STYLE.format(size=52)} text-indent="0.42em">{WORDMARK}</text>
</svg>
"""


def rasterize_pngs() -> None:
    import subprocess

    script = ROOT / "scripts" / "rasterize-brand.mjs"
    subprocess.run(["node", str(script)], cwd=ROOT / "scripts", check=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)
    (BRAND / "social").mkdir(exist_ok=True)

    if SRC_BLACK.is_file():
        shutil.copy2(SRC_BLACK, BRAND / "logo-mark-black.svg")
    if SRC_WHITE.is_file():
        shutil.copy2(SRC_WHITE, BRAND / "logo-mark-white.svg")

    path_d = load_logo_path()

    variants = [
        ("logo-wordmark-black-on-white.svg", wordmark_svg(path_d, "#000000", BG_LIGHT)),
        ("logo-wordmark-white-on-black.svg", wordmark_svg(path_d, "#ffffff", BG_DARK)),
        ("logo-mark-black-on-white.svg", mark_only_svg(path_d, "#000000", BG_LIGHT)),
        ("logo-mark-white-on-black.svg", mark_only_svg(path_d, "#ffffff", BG_DARK)),
        ("favicon.svg", mark_only_svg(path_d, "#ffffff", BG_DARK, 64)),
    ]
    for name, content in variants:
        write_text(BRAND / name, content)

    og_path = BRAND / "social" / "og-image.svg"
    write_text(og_path, og_svg(path_d))
    insta_path = BRAND / "social" / "instagram-profile.svg"
    write_text(insta_path, mark_only_svg(path_d, "#ffffff", BG_DARK, 320))

    rasterize_pngs()

    from PIL import Image

    imgs = [Image.open(BRAND / "favicon-16x16.png"), Image.open(BRAND / "favicon-32x32.png")]
    imgs[0].save(BRAND / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])

    root_copies = [
        (BRAND / "favicon.ico", ROOT / "favicon.ico"),
        (BRAND / "favicon-32x32.png", ROOT / "favicon-32x32.png"),
        (BRAND / "favicon-16x16.png", ROOT / "favicon-16x16.png"),
        (BRAND / "apple-touch-icon.png", ROOT / "apple-touch-icon.png"),
        (BRAND / "social" / "og-image.png", ROOT / "og-image.png"),
        (BRAND / "favicon.svg", ROOT / "favicon.svg"),
    ]
    for src, dst in root_copies:
        if src.is_file():
            shutil.copy2(src, dst)

    readme = """# Sphera Films — brand assets

Wordmark on generated files: **SPHERA FILMS** (Syne, uppercase, site tracking).

See files in this folder and `social/` for OG (1200×630), favicon, apple-touch-icon, Instagram profile.
"""
    write_text(BRAND / "README.md", readme)
    print("Brand assets written to", BRAND)


if __name__ == "__main__":
    main()
