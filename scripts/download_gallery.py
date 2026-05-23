"""Download all gallery media from Canva cache (gallerie page)."""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.spherafilms.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Referer": "https://www.spherafilms.com/gallerie",
}

for name in ("cache_gallerie_fresh.html", "cache_gallerie.html"):
    gal = ROOT / "scripts" / name
    if gal.is_file():
        break
else:
    raise SystemExit("no gallery cache")

html = gal.read_text(encoding="utf-8", errors="replace")
start = html.index("JSON.parse('") + 12
text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
refs = []
for m in re.finditer(r"_assets/media/[a-f0-9]+\.(?:jpe?g|png|webp)", text, re.I):
    p = m.group(0)
    if p not in refs:
        refs.append(p)

ok = fail = skip = 0
for ref in refs:
    dest = ROOT / ref.replace("_assets/", "assets/")
    if dest.is_file() and dest.stat().st_size > 500:
        skip += 1
        continue
    url = f"{BASE}/{ref}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        if len(data) < 500:
            fail += 1
            print("SMALL", ref)
            continue
        dest.write_bytes(data)
        ok += 1
        print("OK", ref)
    except Exception as e:
        fail += 1
        print("FAIL", ref, e)

print(f"refs={len(refs)} ok={ok} skip={skip} fail={fail}")
