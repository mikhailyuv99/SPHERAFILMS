"""Copy user SVG exactly — only strip the full-page white export rect."""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"c:\Users\mikha\Downloads\Design sans titre (11).svg")
FALLBACK = ROOT / "Design sans titre (11).svg"
OUT = ROOT / "assets" / "logo.svg"
WHITE_BG = re.compile(
    r'\s*<path d="M0 1000 l0 -1000 1000 0 1000 0 0 1000 0 1000 -1000 0 -1000 0 0 -1000z[^"]*"/>'
)


def main() -> None:
    src = SRC if SRC.is_file() else FALLBACK
    if not src.is_file():
        raise FileNotFoundError("Design sans titre (11).svg")
    shutil.copy2(src, ROOT / "Design sans titre (11).svg")
    svg = src.read_text(encoding="utf-8")
    svg = WHITE_BG.sub("", svg, count=1)
    OUT.write_text(svg, encoding="utf-8")
    print("Copied user SVG ->", OUT, "(viewBox untouched, white page rect removed only)")


if __name__ == "__main__":
    main()
