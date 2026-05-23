"""Install user logo (no background) + white nav variant."""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"c:\Users\mikha\Downloads\Design sans titre (11) (1).svg")
OUT = ROOT / "assets" / "logo.svg"
WHITE = ROOT / "assets" / "logo-white.svg"
# Logo geometry — padded viewBox so sphere is not clipped at top
VIEWBOX = "690 700 650 680"


def main() -> None:
    if not SRC.is_file():
        raise FileNotFoundError(SRC)
    raw = SRC.read_text(encoding="utf-8")
    OUT.write_text(raw, encoding="utf-8")

    white = re.sub(r"<!DOCTYPE[^>]*>\s*", "", raw)
    white = white.replace('fill="#000000"', 'fill="#ffffff"')
    white = white.replace('width="2000px" height="2000px"', 'width="650" height="680"')
    white = re.sub(r'viewBox="0 0 2000 2000"', f'viewBox="{VIEWBOX}"', white)
    WHITE.write_text(white, encoding="utf-8")
    shutil.copy2(SRC, ROOT / "Design sans titre (11) (1).svg")
    print("Installed", OUT, "and", WHITE)


if __name__ == "__main__":
    main()
