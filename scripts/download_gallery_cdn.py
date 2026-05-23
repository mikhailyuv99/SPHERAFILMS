"""Extract Canva CDN URLs from gallery cache and download."""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "scripts/cache_gallerie_fresh.html").read_text(encoding="utf-8", errors="replace")

# asset id -> local hash mapping from _assets paths in bootstrap
local_refs = []
start = html.index("JSON.parse('") + 12
text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
for m in re.finditer(r'"url":"(_assets/media/[a-f0-9]+\.[a-z]+)"', text):
    local_refs.append(m.group(1))
for m in re.finditer(r"_assets/media/[a-f0-9]+\.[a-z]+", text):
    p = m.group(0)
    if p not in local_refs:
        local_refs.append(p)

# full https urls in export
https_urls = re.findall(r"https://[^\"\\]+/(?:media|image)/[^\"\\]+\.(?:jpg|jpeg|png|webp)", text, re.I)
print("local refs", len(local_refs), "https", len(set(https_urls)))

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://spherafilms.com/gallerie"}
ok = fail = 0
seen = set()
for ref in local_refs:
    name = Path(ref).name
    if name in seen:
        continue
    seen.add(name)
    dest = ROOT / "assets/media" / name
    if dest.is_file() and dest.stat().st_size > 2000:
        continue
    for url in [f"https://spherafilms.com/{ref}", f"https://www.spherafilms.com/{ref}"]:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) > 2000:
                dest.write_bytes(data)
                ok += 1
                print("OK", name)
                break
        except Exception:
            pass
    else:
        fail += 1

print("ok", ok, "fail", fail, "unique", len(seen))
