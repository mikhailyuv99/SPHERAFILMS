"""Download any media referenced on site but missing locally."""
import re
import urllib.request
from pathlib import Path

BASE = "https://www.spherafilms.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Referer": "https://www.spherafilms.com/",
}
PROJECT = Path(r"c:\Users\mikha\Desktop\Sphera Films\assets")
html_path = Path(r"C:\Users\mikha\AppData\Local\Temp\sphera.html")
if not html_path.exists():
    import urllib.request as u
    html_path.write_bytes(
        u.urlopen(
            urllib.request.Request(BASE + "/", headers=HEADERS), timeout=60
        ).read()
    )
data = html_path.read_text(encoding="utf-8", errors="replace")
start = data.index("JSON.parse('") + 12
text = data[start : data.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")

refs = sorted(
    set(re.findall(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", text))
)

def fetch(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=120) as r:
        dest.write_bytes(r.read())

for ref in refs:
    dest = PROJECT.parent / ref.replace("_assets/", "assets/")
    if dest.exists() and dest.stat().st_size > 0:
        continue
    url = f"{BASE}/{ref}"
    try:
        fetch(url, dest)
        print("OK", ref)
    except Exception as e:
        print("FAIL", ref, e)

print("done", len(refs), "refs")
