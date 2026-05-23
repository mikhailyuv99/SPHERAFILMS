"""Build gallery-on-disk.json from assets/media + merge order from galerie page."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "assets/media"
MAP = ROOT / "assets/media-map"
EXT = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    on_disk = sorted(
        f"assets/media/{p.name}"
        for p in MEDIA.iterdir()
        if p.suffix.lower() in EXT and p.stat().st_size > 2000
    )
    (MAP / "gallery-on-disk.json").write_text(
        json.dumps({"order": on_disk, "count": len(on_disk)}, indent=2),
        encoding="utf-8",
    )

    page_path = MAP / "10-galerie-page.json"
    scraped_path = MAP / "gallery-scraped-order.json"
    disk_set = {Path(p).name for p in on_disk}

    merged: list[str] = []
    seen: set[str] = set()

    def add(path: str) -> None:
        name = Path(path).name
        if name in seen:
            return
        if name not in disk_set:
            return
        seen.add(name)
        merged.append(f"assets/media/{name}")

    if scraped_path.is_file():
        for p in json.loads(scraped_path.read_text(encoding="utf-8")).get("order", []):
            add(p)

    if page_path.is_file():
        for item in json.loads(page_path.read_text(encoding="utf-8")).get("items", []):
            add(item.get("path", ""))

    for p in on_disk:
        add(p)

    scraped_path.write_text(
        json.dumps({"order": merged, "count": len(merged)}, indent=2),
        encoding="utf-8",
    )
    print(f"On disk: {len(on_disk)} | Merged order: {len(merged)}")


if __name__ == "__main__":
    main()
