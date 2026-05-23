"""Build gallery-page-order.json — exact order from 10-galerie-page.json, local + CDN fallback."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "assets/media-map"
MEDIA = ROOT / "assets/media"
CACHE = ROOT / "scripts/cache_gallerie_fresh.html"


def extract_cdn_map(html: str) -> dict[str, str]:
    """Map filename -> https URL from Canva export HTML."""
    mapping: dict[str, str] = {}
    patterns = [
        r"https://[a-z0-9.-]+/[^\s\"'\\]+/[a-f0-9]+\.(?:jpe?g|png|webp)(?:\?[^\s\"'\\]*)?",
        r"https:\\\\/\\\\/([a-z0-9.-]+(?:\\/[a-z0-9._%-]+)*\\/[a-f0-9]+\\.(?:jpe?g|png|webp))",
    ]
    for pat in patterns:
        for m in re.finditer(pat, html, re.I):
            raw = m.group(0).replace("\\/", "/")
            if raw.startswith("("):
                raw = "https://" + m.group(1).replace("\\/", "/")
            name = Path(urlparse(raw).path).name.split("?")[0]
            if re.match(r"^[a-f0-9]+\.(jpe?g|png|webp)$", name, re.I):
                mapping.setdefault(name, raw.split("?")[0])
    return mapping


def main():
    page = json.loads((MAP / "10-galerie-page.json").read_text(encoding="utf-8"))
    html = CACHE.read_text(encoding="utf-8", errors="replace") if CACHE.is_file() else ""
    cdn = extract_cdn_map(html)

    items = []
    seen: set[str] = set()

    for entry in page.get("items", []):
        path = entry.get("path", "")
        if not path:
            continue
        name = Path(path).name
        if name in seen:
            continue
        seen.add(name)

        local = MEDIA / name
        src = path
        if local.is_file() and local.stat().st_size > 500:
            src = f"assets/media/{name}"
        elif name in cdn:
            src = cdn[name]
        else:
            continue

        items.append({"path": path, "src": src, "name": name})

    out = {"order": items, "count": len(items), "source": "10-galerie-page.json"}
    (MAP / "gallery-page-order.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Gallery order: {len(items)} images (CDN fallbacks: {sum(1 for i in items if i['src'].startswith('http'))})")


if __name__ == "__main__":
    main()
