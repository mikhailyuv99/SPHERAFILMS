"""Generate Sphera Films branding assets in /branding (favicon, OG, social icons)."""
from __future__ import annotations

import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BRANDING = ROOT / "branding"
FONTS = BRANDING / "fonts"
SRC_BLACK = ROOT / "assets" / "logo.svg"
BG_LIGHT = "#ffffff"
BG_DARK = "#000000"
WORDMARK = "SPHERA FILMS"
SYNE_TTF_URL = "https://fonts.gstatic.com/s/syne/v24/8vIS7w4qzmVxsWxjBZRjr0FKM_3mvj6k.ttf"

# Logo path lives in a ~620×620 region around (1000, 980) inside the 2000×2000 source.
LOGO_CX = 1000
LOGO_CY = 980
LOGO_SPAN = 580

# Fraction of canvas filled by the logo mark.
LOGO_FILL_FAVICON = 0.98
LOGO_FILL_APP = 0.98
LOGO_FILL_OG = 0.58


def load_logo_path() -> str:
    svg = SRC_BLACK.read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', svg)
    if not match:
        raise SystemExit("Could not parse logo path from assets/logo.svg")
    return match.group(1)


def ensure_syne_font() -> Path:
    dest = FONTS / "Syne-SemiBold.ttf"
    if not dest.is_file():
        print("Downloading Syne SemiBold…")
        urllib.request.urlretrieve(SYNE_TTF_URL, dest)
    return dest


def logo_scale(size: int, fill_ratio: float) -> float:
    return (size * fill_ratio) / LOGO_SPAN


def mark_svg(path_d: str, fill: str, bg: str | None, size: int, fill_ratio: float) -> str:
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    s = logo_scale(size, fill_ratio)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  {bg_rect}
  <g transform="translate({size / 2} {size / 2}) scale({s}) translate(-{LOGO_CX} -{LOGO_CY})">
    <path fill="{fill}" d="{path_d}"/>
  </g>
</svg>
"""


def og_svg(path_d: str) -> str:
    w, h = 1200, 630
    s = logo_scale(min(w, h), LOGO_FILL_OG)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" fill="{BG_LIGHT}"/>
  <g transform="translate({w / 2} {h * 0.38}) scale({s}) translate(-{LOGO_CX} -{LOGO_CY})">
    <path fill="{BG_DARK}" d="{path_d}"/>
  </g>
</svg>
"""


def draw_syne_wordmark(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
    text: str,
    cx: float,
    y: float,
    letter_spacing_em: float = 0.42,
    indent_em: float = 0.42,
) -> None:
    size = font.size
    spacing = size * letter_spacing_em
    indent = size * indent_em
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * max(0, len(text) - 1)
    x = cx - total / 2 + indent
    for i, ch in enumerate(text):
        draw.text((x, y), ch, fill=BG_DARK, font=font)
        x += widths[i] + spacing


def render_og_png(path_d: str, font_path: Path) -> None:
    w, h = 1200, 630
    logo_svg = BRANDING / "_og-logo-temp.svg"
    logo_png = BRANDING / "_og-logo-temp.png"
    write_text(logo_svg, og_svg(path_d))

    subprocess.run(
        [
            "node",
            str(ROOT / "scripts" / "svg2png.mjs"),
            str(logo_svg),
            str(logo_png),
            str(w),
            str(h),
            "white",
        ],
        cwd=ROOT,
        check=True,
    )

    base = Image.open(logo_png).convert("RGB")
    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype(str(font_path), 46)
    bbox = font.getbbox(WORDMARK)
    text_h = bbox[3] - bbox[1]
    draw_syne_wordmark(draw, font, WORDMARK, w / 2, h * 0.78 - text_h / 2)
    base.save(BRANDING / "og-image.png", optimize=True)

    logo_svg.unlink(missing_ok=True)
    logo_png.unlink(missing_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def rasterize() -> None:
    subprocess.run(["node", str(ROOT / "scripts" / "rasterize-branding.mjs")], cwd=ROOT, check=True)


def copy_deploy() -> None:
    copies = [
        (BRANDING / "favicon.ico", ROOT / "favicon.ico"),
        (BRANDING / "favicon.svg", ROOT / "favicon.svg"),
        (BRANDING / "favicon-16x16.png", ROOT / "favicon-16x16.png"),
        (BRANDING / "favicon-32x32.png", ROOT / "favicon-32x32.png"),
        (BRANDING / "favicon-48x48.png", ROOT / "favicon-48x48.png"),
        (BRANDING / "apple-touch-icon.png", ROOT / "apple-touch-icon.png"),
        (BRANDING / "og-image.png", ROOT / "og-image.png"),
    ]
    for src, dst in copies:
        if src.is_file():
            shutil.copy2(src, dst)


def main() -> None:
    BRANDING.mkdir(parents=True, exist_ok=True)
    font_path = ensure_syne_font()
    path_d = load_logo_path()

    write_text(BRANDING / "favicon.svg", mark_svg(path_d, BG_DARK, None, 512, LOGO_FILL_FAVICON))
    write_text(
        BRANDING / "logo-mark-black-on-white.svg",
        mark_svg(path_d, BG_DARK, BG_LIGHT, 512, LOGO_FILL_APP),
    )
    write_text(
        BRANDING / "logo-mark-white-on-black.svg",
        mark_svg(path_d, BG_LIGHT, BG_DARK, 512, LOGO_FILL_APP),
    )
    write_text(BRANDING / "og-image.svg", og_svg(path_d))

    rasterize()
    render_og_png(path_d, font_path)

    imgs = [
        Image.open(BRANDING / "favicon-16x16.png"),
        Image.open(BRANDING / "favicon-32x32.png"),
        Image.open(BRANDING / "favicon-48x48.png"),
    ]
    imgs[0].save(BRANDING / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])

    copy_deploy()

    write_text(
        BRANDING / "README.md",
        """# Sphera Films — branding

| File | Use |
|------|-----|
| `favicon.svg` / `favicon.ico` | Black logo mark, transparent background, max size |
| `og-image.png` | Black logo + SPHERA FILMS (Syne 600) on white (1200×630) |
| `logo-mark-black-on-white.svg` | Social / Apple touch source |
| `logo-mark-white-on-black.svg` | Dark-mode social source |
| `apple-touch-icon.png` | Logo mark on white (180×180) |
| `apple-touch-icon-dark.png` | Logo mark on black (180×180) |
| `instagram-profile.png` | Logo mark on white (320×320) |
| `instagram-profile-dark.png` | Logo mark on black (320×320) |

Wordmark: **SPHERA FILMS** — Syne 600, letter-spacing 0.42em, text-indent 0.42em.
""",
    )
    print("Branding assets written to", BRANDING)


if __name__ == "__main__":
    main()
