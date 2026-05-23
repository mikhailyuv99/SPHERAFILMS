import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = ROOT.joinpath("scripts/cache_gallerie_fresh.html").read_text(encoding="utf-8", errors="replace")
m = re.search(r"window\['bootstrap'\]\s*=\s*JSON\.parse\('(.+?)'\);", html, re.S)
raw = m.group(1).encode().decode("unicode_escape")
data = json.loads(raw)

photos: list[tuple[str, str]] = []


def walk(obj):
    if isinstance(obj, dict):
        u = obj.get("url")
        if isinstance(u, str) and re.search(r"[a-f0-9]{32}\.(jpe?g|png|webp)$", u, re.I):
            name = u.split("/")[-1]
            full = u if u.startswith("http") else f"https://spherafilms.com/{u.lstrip('/')}"
            photos.append((name, full))
        for v in obj.values():
            walk(v)
    elif isinstance(obj, list):
        for v in obj:
            walk(v)


walk(data)
seen = set()
ordered = []
for name, url in photos:
    if name in seen:
        continue
    seen.add(name)
    ordered.append((name, url))

print("photos", len(ordered))
ok = 0
for name, url in ordered[:8]:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://spherafilms.com/gallerie"}
        )
        body = urllib.request.urlopen(req, timeout=30).read()
        print("OK", name, len(body))
        ok += 1
    except Exception as e:
        print("FAIL", name, e)

print("ok count in sample", ok)
