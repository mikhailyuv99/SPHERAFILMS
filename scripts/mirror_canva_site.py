"""Mirror spherafilms.com Canva export for local hosting."""
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(r"c:\Users\mikha\Desktop\Sphera Films")
SRC_HTML = ROOT / "scripts" / "cache_home.html"
GAL_HTML = ROOT / "scripts" / "cache_gallerie.html"
ASSETS = ROOT / "_assets"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.spherafilms.com/",
}
BASE = "https://www.spherafilms.com"

def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 100:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
        print("fetched", dest.name)
        return True
    except Exception as e:
        print("skip", dest.name, e)
        return False

def prepare_html(html: str) -> str:
    html = re.sub(r'\s+integrity="[^"]*"', "", html)
    html = re.sub(r'\s+nonce="[^"]*"', "", html)
    html = re.sub(r'\s+crossorigin="[^"]*"', "", html)
    html = html.replace('<base href="/">', '<base href="./">')
    html = re.sub(r'<base href="/[^"]*/">', '<base href="./">', html)
    html = html.replace("window['__canva_public_path__'] = '_assets\\/';", "window['__canva_public_path__'] = '_assets/';")
    return html

# Sync media to _assets (Canva expects _assets/media and _assets/video)
for sub in ("media", "video"):
    src_dir = ROOT / "assets" / sub
    dst_dir = ASSETS / sub
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for f in src_dir.iterdir():
            dst = dst_dir / f.name
            if not dst.exists():
                shutil.copy2(f, dst)

# Download all _assets/*.js and *.css referenced
home = SRC_HTML.read_text(encoding="utf-8", errors="replace")
refs = sorted(set(re.findall(r"_assets/([a-zA-Z0-9_.-]+\.(?:js|css))", home)))
for ref in refs:
    fetch(f"{BASE}/_assets/{ref}", ASSETS / ref)

# gallerie page assets
if GAL_HTML.exists():
    gal = GAL_HTML.read_text(encoding="utf-8", errors="replace")
    for ref in set(re.findall(r"_assets/([a-zA-Z0-9_.-]+\.(?:js|css))", gal)):
        fetch(f"{BASE}/_assets/{ref}", ASSETS / ref)

(ROOT / "index.html").write_text(prepare_html(home), encoding="utf-8")
print("wrote index.html")

if GAL_HTML.exists():
    import subprocess
    subprocess.run(["python", str(ROOT / "scripts" / "patch_gallerie.py")], check=True)
    print("wrote gallerie.html (patched)")

# Legal pages
for path, out in [("mentionslegales", "mentions-legales.html"), ("politiquedeconfidentialite", "politique-de-confidentialite.html")]:
    cache = ROOT / "scripts" / f"cache_{path}.html"
    if not cache.exists():
        fetch(f"{BASE}/{path}", cache)
    if cache.exists():
        name = out
        (ROOT / name).write_text(prepare_html(cache.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
        print("wrote", name)

print("done")
