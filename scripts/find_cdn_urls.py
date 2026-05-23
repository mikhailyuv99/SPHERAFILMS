import re
from pathlib import Path

html = Path(__file__).resolve().parents[1].joinpath("scripts/cache_gallerie_fresh.html").read_text(encoding="utf-8", errors="replace")
# find url fields near media hashes
for m in re.finditer(r'"url":"([^"]+)"', html):
    u = m.group(1).replace(r"\/", "/")
    if "media" in u or "jpg" in u or "png" in u:
        print(u[:160])
