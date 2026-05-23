"""
Sync gallery from https://spherafilms.com/gallerie — page order + download.
CDN path: /gallerie/_assets/media/{hash}.ext
"""
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "assets/media-map"
MEDIA = ROOT / "assets/media"
ORDER_PATH = MAP / "gallery-page-order.json"
PAGE_URL = "https://spherafilms.com/gallerie"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": PAGE_URL,
}
CDN = "https://spherafilms.com/gallerie/_assets/media/"

EXCLUDE_STEMS = {
    "f09e28130786425c25ceaa9561def661",
    "10f9a07b05780c7691c41a3bba7f817d",
    "e1f78e667dbffb6298b1859dcb1092af",
    "0bee10adc0a548861f7ce9fa2aa929e1",
    "founders",
}


def fetch_html() -> str:
    req = urllib.request.Request(PAGE_URL, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")


def extract_order(html: str) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for m in re.finditer(r"([a-f0-9]{32})\.(jpe?g|png|webp)", html, re.I):
        name = f"{m.group(1).lower()}.{m.group(2).lower()}"
        stem = name.rsplit(".", 1)[0]
        if stem in EXCLUDE_STEMS or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


def download_one(name: str) -> bool:
    dest = MEDIA / name
    if dest.is_file() and dest.stat().st_size > 2000:
        return True
    url = CDN + name
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=60).read()
        if len(data) > 800:
            dest.write_bytes(data)
            print("  OK", name)
            return True
    except Exception as e:
        print("  FAIL", name, e)
    return False


def main() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    print("Fetching", PAGE_URL)
    html = fetch_html()
    names = extract_order(html)
    print(f"Gallery order: {len(names)} images")

    order: list[dict] = []
    skipped = 0
    for i, name in enumerate(names, 1):
        path = f"assets/media/{name}"
        remote = CDN + name
        if not download_one(name):
            skipped += 1
            print(f"  skip (unavailable): {name}")
            continue
        order.append(
            {
                "path": path,
                "src": path,
                "name": name,
                "fallbackSrc": remote,
            }
        )
        if i % 25 == 0:
            print(f"  … {i}/{len(names)}")
    if skipped:
        print(f"Skipped {skipped} unavailable images")

    local = sum(1 for i in order if (MEDIA / i["name"]).is_file())
    out = {
        "order": order,
        "count": len(order),
        "source": PAGE_URL,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
    }
    ORDER_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Done: {len(order)} in order, {local} saved under assets/media/")


if __name__ == "__main__":
    main()
