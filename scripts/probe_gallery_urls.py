import re
import urllib.request
from pathlib import Path

url = "https://spherafilms.com/gallerie"
html = urllib.request.urlopen(
    urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
).read().decode("utf-8", "replace")

patterns = [
    r"https://[^\"'\\]+\.(?:jpg|jpeg|png|webp)",
    r"document-export[^\"'\\]+",
    r"media\.canva[^\"'\\]+",
    r"export-download[^\"'\\]+",
]
for pat in patterns:
    found = sorted(set(re.findall(pat, html, re.I)))
    print(pat, len(found))
    for x in found[:3]:
        print(" ", x[:140])

Path(__file__).resolve().parents[1].joinpath("scripts/cache_gallerie_live.html").write_text(
    html, encoding="utf-8"
)
print("saved cache_gallerie_live.html", len(html))
