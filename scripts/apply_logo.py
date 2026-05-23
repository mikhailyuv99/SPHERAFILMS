"""Apply user logo (no bg) to Canva mirror site."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOGO_SVGS = [
    "fec4c46f59d2687154e3f364f3b1cff0.svg",
    "fea1775c265beea9b248f4fa76d938d0.svg",
]

LOGO_PNGS = [
    "a4671c3cdc93430705491cd465b7215a.png",
    "88c84b8adc504d0c6bc888ad132eb388.png",
    "4c51dd0398a1625f638af77912acc3e1.png",
    "84672a2709fae3b97a971eb98320ab9f.png",
]

PAGES = ("index.html", "gallerie.html", "mentions-legales.html", "politique-de-confidentialite.html")

def build_logo_svg() -> Path:
    sys.path.insert(0, str(ROOT / "scripts"))
    import fix_logo

    fix_logo.main()
    return ROOT / "assets" / "logo.svg"


def rasterize_png(svg: Path, dest: Path, size: int = 800) -> bool:
    try:
        import cairosvg

        cairosvg.svg2png(url=str(svg), write_to=str(dest), output_width=size)
        return True
    except Exception:
        pass
    return False


def patch_pages() -> None:
    tag = '<script id="sphera-logo-swap" src="js/logo-swap.js" defer></script>'
    for page in PAGES:
        path = ROOT / page
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        html = re.sub(
            r'<script id="sphera-logo-swap" src="js/logo-swap\.js" defer></script>\s*',
            "",
            html,
        )
        if tag not in html:
            html = html.replace("</head>", tag + "</head>", 1)
        path.write_text(html, encoding="utf-8")
        print("patched", page)


def main() -> None:
    logo = build_logo_svg()
    svg_text = logo.read_text(encoding="utf-8")

    for name in LOGO_SVGS:
        dest = ROOT / "_assets" / "media" / name
        dest.write_text(svg_text, encoding="utf-8")
        print("svg ->", dest.name)

    for name in LOGO_PNGS:
        dest = ROOT / "_assets" / "media" / name
        if rasterize_png(logo, dest):
            print("png ->", dest.name)
        else:
            print("png skip (install cairosvg for PNG slots):", dest.name)

    patch_pages()
    if (ROOT / "index.html").exists():
        shutil.copy2(ROOT / "index.html", ROOT / "index-canva-mirror.html")
    print("done — hard refresh (Ctrl+Shift+R)")


if __name__ == "__main__":
    main()
