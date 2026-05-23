"""Rebuild gallery-page-order.json — jpg/webp only, sequential perceptual dedupe."""
import json
import re
from pathlib import Path

from PIL import Image
import imagehash

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "assets/media-map"
MEDIA = ROOT / "assets/media"
ORDER = MAP / "gallery-page-order.json"
PAGE = MAP / "10-galerie-page.json"
SKIP = MAP / "gallery-visual-skip.json"
CDN = "https://spherafilms.com/gallerie/_assets/media/"

EXCLUDE = {
    "f09e28130786425c25ceaa9561def661",
    "10f9a07b05780c7691c41a3bba7f817d",
    "e1f78e667dbffb6298b1859dcb1092af",
    "0bee10adc0a548861f7ce9fa2aa929e1",
    "0b15a29edb41617b26d8e9fd1cc1c12d",
    "40988032d76b9fba43f7ea7f5179c871",
    "15430ce4c716dcf666cc4d22e3a41eb4",
    "88c84b8adc504d0c6bc888ad132eb388",
    "fec4c46f59d2687154e3f364f3b1cff0",
    "fea1775c265beea9b248f4fa76d938d0",
    "founders",
    "test",
}

PHASH_THRESHOLD = 8


def is_photo(name: str) -> bool:
    if not re.search(r"\.(jpe?g|webp)$", name, re.I):
        return False
    stem = name.rsplit(".", 1)[0].lower()
    return stem not in EXCLUDE


def main() -> None:
    page = json.loads(PAGE.read_text(encoding="utf-8"))
    kept: list[dict] = []
    skipped: list[str] = []
    hashes: list[imagehash.ImageHash] = []

    for entry in page.get("items", []):
        path = entry.get("path", "")
        if not path:
            continue
        name = Path(path).name
        if not is_photo(name):
            continue

        local = MEDIA / name
        if not local.is_file() or local.stat().st_size < 800:
            continue

        try:
            h = imagehash.phash(Image.open(local).convert("RGB"), hash_size=16)
        except OSError:
            continue

        if any(h - prev <= PHASH_THRESHOLD for prev in hashes):
            skipped.append(name)
            continue

        hashes.append(h)
        kept.append(
            {
                "path": f"assets/media/{name}",
                "src": f"assets/media/{name}",
                "name": name,
                "fallbackSrc": CDN + name,
            }
        )

    out = {
        "order": kept,
        "count": len(kept),
        "source": "10-galerie-page.json",
        "deduped": True,
        "phashThreshold": PHASH_THRESHOLD,
    }
    ORDER.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    SKIP.write_text(
        json.dumps({"skip": skipped, "count": len(skipped)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Gallery: {len(kept)} unique photos, skipped {len(skipped)} visual duplicates")


if __name__ == "__main__":
    main()
