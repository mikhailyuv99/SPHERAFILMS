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

LOGO_FILL_FAVICON = 0.86
LOGO_FILL_APP = 0.94
LOGO_FILL_OG = 0.52
LOGO_PAD = 1.06
FAVICON_FILL = "#ffffff"


def _tokenize_path(d: str) -> list[str]:
    return re.findall(r"[a-zA-Z]|-?\d*\.?\d+(?:e[-+]?\d+)?", d)


def path_bbox(d: str) -> tuple[float, float, float, float]:
    tokens = _tokenize_path(d)
    i = 0
    cmd = "M"
    cx = cy = start_x = start_y = 0.0
    xs: list[float] = []
    ys: list[float] = []

    def add(x: float, y: float) -> None:
        xs.append(x)
        ys.append(y)

    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            continue

        rel = cmd.islower()
        c = cmd.upper()

        if c == "M":
            x = float(tokens[i])
            y = float(tokens[i + 1])
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            start_x, start_y = x, y
            add(x, y)
            i += 2
            cmd = "L" if c == "M" else "l"
        elif c == "L":
            x = float(tokens[i])
            y = float(tokens[i + 1])
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            add(x, y)
            i += 2
        elif c == "C":
            for j in (0, 2, 4):
                x = float(tokens[i + j])
                y = float(tokens[i + j + 1])
                if rel:
                    x += cx
                    y += cy
                add(x, y)
            x = float(tokens[i + 4])
            y = float(tokens[i + 5])
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            i += 6
        elif c == "Z":
            cx, cy = start_x, start_y
            i += 1
        else:
            i += 1

    return min(xs), min(ys), max(xs), max(ys)


def logo_metrics(path_d: str) -> tuple[float, float, float]:
    x0, y0, x1, y1 = path_bbox(path_d)
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    span = max(x1 - x0, y1 - y0) * LOGO_PAD
    return cx, cy, span


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


def logo_scale(size: int, fill_ratio: float, span: float) -> float:
    return (size * fill_ratio) / span


def mark_svg(
    path_d: str,
    fill: str,
    bg: str | None,
    size: int,
    fill_ratio: float,
    cx: float,
    cy: float,
    span: float,
) -> str:
    bg_rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    s = logo_scale(size, fill_ratio, span)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  {bg_rect}
  <g transform="translate({size / 2} {size / 2}) scale({s}) translate(-{cx} -{cy})">
    <path fill="{fill}" d="{path_d}"/>
  </g>
</svg>
"""


def og_svg(path_d: str, cx: float, cy: float, span: float) -> str:
    w, h = 1200, 630
    s = logo_scale(min(w, h), LOGO_FILL_OG, span)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" fill="{BG_LIGHT}"/>
  <g transform="translate({w / 2} {h * 0.36}) scale({s}) translate(-{cx} -{cy})">
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


def render_og_png(path_d: str, font_path: Path, cx: float, cy: float, span: float) -> None:
    w, h = 1200, 630
    logo_svg = BRANDING / "_og-logo-temp.svg"
    logo_png = BRANDING / "_og-logo-temp.png"
    write_text(logo_svg, og_svg(path_d, cx, cy, span))

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
    cx, cy, span = logo_metrics(path_d)
    print(f"Logo center ({cx:.1f}, {cy:.1f}), span {span:.1f}")

    favicon_svg = mark_svg(path_d, FAVICON_FILL, None, 512, LOGO_FILL_FAVICON, cx, cy, span)
    mark_light_svg = mark_svg(path_d, BG_DARK, BG_LIGHT, 512, LOGO_FILL_APP, cx, cy, span)
    mark_dark_svg = mark_svg(path_d, BG_LIGHT, BG_DARK, 512, LOGO_FILL_APP, cx, cy, span)

    write_text(BRANDING / "favicon.svg", favicon_svg)
    write_text(BRANDING / "logo-mark-black-on-white.svg", mark_light_svg)
    write_text(BRANDING / "logo-mark-white-on-black.svg", mark_dark_svg)
    write_text(BRANDING / "og-image.svg", og_svg(path_d, cx, cy, span))

    # Vector masters for platforms that accept SVG (and for re-export at any size).
    write_text(BRANDING / "apple-touch-icon.svg", mark_light_svg)
    write_text(BRANDING / "apple-touch-icon-dark.svg", mark_dark_svg)
    write_text(BRANDING / "instagram-profile.svg", mark_light_svg)
    write_text(BRANDING / "instagram-profile-dark.svg", mark_dark_svg)

    rasterize()
    render_og_png(path_d, font_path, cx, cy, span)

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

## Vector (preferred — never blurry)
| File | Use |
|------|-----|
| `favicon.svg` | Favicon (white mark, transparent) |
| `apple-touch-icon.svg` | Apple touch source (black on white) |
| `apple-touch-icon-dark.svg` | Apple touch dark (white on black) |
| `instagram-profile.svg` | Instagram / social (black on white) |
| `instagram-profile-dark.svg` | Instagram dark (white on black) |
| `og-image.svg` | OG source (logo only; wordmark added in PNG export) |

## Raster (for HTML meta / upload slots that require PNG)
| File | Use |
|------|-----|
| `favicon.ico` / `favicon-*.png` | Browser favicons (from SVG @ 600 DPI) |
| `apple-touch-icon.png` | Apple touch (180×180) |
| `apple-touch-icon-dark.png` | Apple touch dark |
| `instagram-profile.png` | Instagram profile (320×320) |
| `instagram-profile-dark.png` | Instagram dark |
| `og-image.png` | OG / Twitter card (1200×630, Syne wordmark) |

Logo is centered from measured path bounds. PNGs are rasterized from SVG at 600 DPI.
Wordmark: **SPHERA FILMS** — Syne 600, letter-spacing 0.42em.
""",
    )
    print("Branding assets written to", BRANDING)


if __name__ == "__main__":
    main()
