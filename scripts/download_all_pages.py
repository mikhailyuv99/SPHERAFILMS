"""Download every asset referenced on all spherafilms.com pages."""
import re
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://www.spherafilms.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Referer": "https://www.spherafilms.com/",
}
PROJECT = Path(r"c:\Users\mikha\Desktop\Sphera Films")
PAGES = ["/", "/gallerie", "/mentionslegales", "/politiquedeconfidentialite"]

def extract_refs(html):
    start = html.index("JSON.parse('") + 12
    text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
    return sorted(set(re.findall(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", text)))

def fetch_page(path):
    url = BASE + path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", errors="replace")

def download_one(ref):
    dest = PROJECT / ref.replace("_assets/", "assets/")
    if dest.exists() and dest.stat().st_size > 100:
        return ref, "skip"
    url = f"{BASE}/{ref}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
        return ref, "ok"
    except Exception as e:
        return ref, f"fail:{e}"

all_refs = []
for path in PAGES:
    print(f"Fetching {path}...")
    html = fetch_page(path)
    refs = extract_refs(html)
    print(f"  {len(refs)} refs")
    cache = PROJECT / "scripts" / f"cache_{path.strip('/') or 'home'}.html"
    cache.write_text(html, encoding="utf-8")
    all_refs.extend(refs)

unique = sorted(set(all_refs))
print(f"\nTotal unique assets: {len(unique)}")

ok = skip = fail = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(download_one, r): r for r in unique}
    for i, fut in enumerate(as_completed(futures), 1):
        ref, status = fut.result()
        if status == "ok":
            ok += 1
        elif status == "skip":
            skip += 1
        else:
            fail += 1
            print(status, ref)
        if i % 50 == 0:
            print(f"  progress {i}/{len(unique)}")

print(f"\nDone: {ok} downloaded, {skip} skipped, {fail} failed")

# Write combined manifest
import json
images, videos, other = [], [], []
for ref in unique:
    local = ref.replace("_assets/", "assets/")
    ext = ref.rsplit(".", 1)[-1].lower()
    if ext in ("mp4", "webm", "m4a", "m3u"):
        videos.append(local)
    elif ext in ("jpg", "jpeg", "png", "webp", "gif", "svg"):
        images.append(local)
    else:
        other.append(local)

manifest = {
    "images": images,
    "videos": videos,
    "other": other,
    "all": [r.replace("_assets/", "assets/") for r in unique],
}
(PROJECT / "assets" / "manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)
print(f"manifest: {len(images)} images, {len(videos)} videos, {len(other)} other")
