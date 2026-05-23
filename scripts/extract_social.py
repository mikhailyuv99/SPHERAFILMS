import re
from pathlib import Path

html = Path(__file__).resolve().parents[1] / "scripts" / "cache_home.html"
text = html.read_text(encoding="utf-8", errors="replace")
urls = sorted(set(re.findall(r"https?://(?:www\.)?(?:instagram|linkedin|facebook|tiktok|youtube)\.com/[^\s\"\\]+", text, re.I)))
for u in urls:
    print(u)
