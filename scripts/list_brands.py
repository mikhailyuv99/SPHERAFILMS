import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "scripts/cache_home.html").read_text(encoding="utf-8", errors="replace")
start = html.index("JSON.parse('") + 12
text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
order = []
for m in re.finditer(r"_assets/media/[a-f0-9]+\.[a-z0-9]+", text):
    p = m.group(0)
    if p not in order:
        order.append(p)
first_jpg = next(i for i, p in enumerate(order) if p.endswith(".jpg"))
pngs = [p for p in order[:first_jpg] if p.endswith(".png")]
UI = {"15430ce4c716dcf666cc4d22e3a41eb4", "88c84b8adc504d0c6bc888ad132eb388", "fec4c46f59d2687154e3f364f3b1cff0", "fea1775c265beea9b248f4fa76d938d0"}
brands = [p for p in pngs if Path(p).stem not in UI]
print("brand pngs:", len(brands))
for i, p in enumerate(brands[:10]):
    print(i + 1, Path(p).stem)
