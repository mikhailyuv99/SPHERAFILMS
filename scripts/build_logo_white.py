"""White logo mark for dark UI — paths unchanged, only fills + no page rect."""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"c:\Users\mikha\Downloads\Design sans titre (11).svg")
FALLBACK = ROOT / "Design sans titre (11).svg"
OUT = ROOT / "assets" / "logo-white.svg"
VIEWBOX = "738 757 558 588"
WHITE_BG = re.compile(
    r'\s*<path d="M0 1000 l0 -1000 1000 0 1000 0 0 1000 0 1000 -1000 0 -1000 0 0 -1000z[^"]*"/>'
)


def main() -> None:
    src = SRC if SRC.is_file() else FALLBACK
    svg = src.read_text(encoding="utf-8")
    svg = WHITE_BG.sub("", svg, count=1)
    svg = re.sub(r'fill="#000000"', 'fill="#ffffff"', svg)
    svg = re.sub(r'fill="#ffffff"', 'fill="#ffffff"', svg)
    svg = re.sub(r'width="2000px" height="2000px"', 'width="558" height="588"', svg)
    svg = re.sub(r'viewBox="0 0 2000 2000"', f'viewBox="{VIEWBOX}"', svg)
    OUT.write_text(svg, encoding="utf-8")
    shutil.copy2(OUT, ROOT / "assets" / "logo.svg")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
