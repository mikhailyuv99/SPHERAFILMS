"""Download missing gallery images from spherafilms.com/_assets/media/ in page order."""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "assets/media-map"
MEDIA = ROOT / "assets/media"
ORDER = MAP / "gallery-page-order.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Referer": "https://spherafilms.com/gallerie",
}
BASE = "https://spherafilms.com/gallerie/_assets/media/"


def main():
    data = json.loads(ORDER.read_text(encoding="utf-8"))
    ok = fail = skip = 0
    out = []

    for item in data.get("order", []):
        name = item["name"]
        local = MEDIA / name
        src = f"assets/media/{name}"

        if local.is_file() and local.stat().st_size > 2000:
            skip += 1
            out.append({"path": item["path"], "src": src, "name": name})
            continue

        for url in (item.get("src"), BASE + name):
            if not url or not str(url).startswith("http"):
                continue
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                body = urllib.request.urlopen(req, timeout=60).read()
                if len(body) < 2000:
                    continue
                local.write_bytes(body)
                ok += 1
                out.append({"path": item["path"], "src": src, "name": name})
                print("OK", name)
                break
            except Exception as e:
                print("FAIL", name, url[:60], e)
        else:
            fail += 1
            out.append({"path": item["path"], "src": BASE + name, "name": name})

    ORDER.write_text(
        json.dumps({"order": out, "count": len(out), "downloaded": ok, "skipped": skip}, indent=2),
        encoding="utf-8",
    )
    print(f"done ok={ok} skip={skip} fail={fail} total={len(out)}")


if __name__ == "__main__":
    main()
