"""Download all media assets from spherafilms.com."""
import re
import urllib.request
from pathlib import Path

BASE = "https://www.spherafilms.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.spherafilms.com/",
    "Accept": "*/*",
}
PROJECT = Path(r"c:\Users\mikha\Desktop\Sphera Films")
MEDIA_DIR = PROJECT / "assets" / "media"
VIDEO_DIR = PROJECT / "assets" / "video"

html = Path(r"C:\Users\mikha\AppData\Local\Temp\sphera.html").read_text(
    encoding="utf-8", errors="replace"
)
start = html.index("JSON.parse('") + len("JSON.parse('")
end = html.rindex("');")
text = html[start:end].replace(r"\/", "/").replace(r"\'", "'")

files = sorted(
    set(
        re.findall(
            r"([a-f0-9]{32}\.(?:jpg|jpeg|png|webp|gif|svg|mp4|webm))",
            text,
            re.I,
        )
    )
)

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

ok, fail = 0, 0
for name in files:
    ext = name.rsplit(".", 1)[-1].lower()
    folder = "video" if ext in ("mp4", "webm", "mov") else "media"
    dest = PROJECT / "assets" / folder / name
    if dest.exists() and dest.stat().st_size > 0:
        ok += 1
        continue
    url = f"{BASE}/_assets/{folder}/{name}"
    def fetch(target_url, out_path):
        req = urllib.request.Request(target_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as resp:
            out_path.write_bytes(resp.read())

    try:
        fetch(url, dest)
        ok += 1
        print(f"OK {name}")
    except Exception as e:
        # try alternate folder
        alt = "media" if folder == "video" else "video"
        url2 = f"{BASE}/_assets/{alt}/{name}"
        alt_dest = PROJECT / "assets" / alt / name
        try:
            fetch(url2, alt_dest)
            ok += 1
            print(f"OK (alt) {name}")
        except Exception:
            fail += 1
            print(f"FAIL {name}: {e}")

print(f"\nDone: {ok} ok, {fail} failed, {len(files)} total")
