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
WORDMARK = "Sphera Films"


def load_logo_path() -> str:
    import re

    svg = SRC_BLACK.read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', svg)
    if not match:
        raise SystemExit("Could not parse logo path from assets/logo.svg")
    return match.group(1)


def wordmark_svg(path_d: str, fill: str, bg: str | None, width: int = 800, height: int = 400) -> str:
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    text_fill = fill
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  {bg_rect}
  <g transform="translate({width / 2} {height * 0.38}) scale(0.11) translate(-1000 -1000)">
    <path fill="{text_fill}" d="{path_d}"/>
  </g>
  <text x="{width / 2}" y="{height * 0.78}" fill="{text_fill}" font-family="Syne, Arial, sans-serif"
    font-size="48" font-weight="600" letter-spacing="0.12em" text-anchor="middle">{WORDMARK}</text>
</svg>
"""


def mark_only_svg(path_d: str, fill: str, bg: str | None, size: int = 512) -> str:
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    pad = size * 0.12
    inner = size - pad * 2
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  {bg_rect}
  <g transform="translate({pad} {pad}) scale({inner / 2000})">
    <path fill="{fill}" d="{path_d}"/>
  </g>
</svg>
"""


def og_svg(path_d: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="{BG_DARK}"/>
  <g transform="translate(600 250) scale(0.14) translate(-1000 -1000)">
    <path fill="#ffffff" d="{path_d}"/>
  </g>
  <text x="600" y="420" fill="#ffffff" font-family="Syne, Arial, sans-serif"
    font-size="56" font-weight="600" letter-spacing="0.14em" text-anchor="middle">SPHERA FILMS</text>
  <text x="600" y="480" fill="#8eb8e8" font-family="Syne, Arial, sans-serif"
    font-size="22" font-weight="500" letter-spacing="0.28em" text-anchor="middle">AGENCE AUDIOVISUELLE · CANNES</text>
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

    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    imgs = [Image.open(BRAND / "favicon-16x16.png"), Image.open(BRAND / "favicon-32x32.png")]
    imgs[0].save(BRAND / "favicon.ico", format="ICO", sizes=ico_sizes)

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

## Logo mark (no wordmark)
| File | Use |
|------|-----|
| `logo-mark-black.svg` | Dark logo on transparent |
| `logo-mark-white.svg` | Light logo on transparent |
| `logo-mark-black-on-white.svg` | Dark logo on white background |
| `logo-mark-white-on-black.svg` | Light logo on dark background |

## Logo + wordmark
| File | Use |
|------|-----|
| `logo-wordmark-black-on-white.svg` | Print / light backgrounds |
| `logo-wordmark-white-on-black.svg` | Web / dark backgrounds |

## Web & social
| File | Size | Use |
|------|------|-----|
| `favicon.svg` / `favicon.ico` | — | Browser tab |
| `favicon-16x16.png` | 16×16 | Favicon |
| `favicon-32x32.png` | 32×32 | Favicon |
| `apple-touch-icon.png` | 180×180 | iOS home screen |
| `social/og-image.png` | 1200×630 | Open Graph (Facebook, WhatsApp, LinkedIn, iMessage) |
| `social/instagram-profile.png` | 320×320 | Instagram profile picture |

Site URL for meta tags: https://spherafilms.com
"""
    write_text(BRAND / "README.md", readme)
    print("Brand assets written to", BRAND)


if __name__ == "__main__":
    main()
