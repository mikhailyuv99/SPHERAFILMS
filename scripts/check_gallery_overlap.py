"""Check overlap between home showcase and gallery list."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
showcase = json.loads((ROOT / "assets/media-map/04-home-showcase.json").read_text())["order"]
gallery = json.loads((ROOT / "assets/media-map/10-galerie-page.json").read_text())["items"]
gal_paths = [i["path"] for i in gallery]
gal_set = set(gal_paths)
overlap = [p for p in showcase if p in gal_set]
print("showcase", len(showcase), "gallery", len(gal_paths))
print("overlap", len(overlap))
print("downloaded gallery", sum(1 for i in gallery if i["downloaded"]))
# jpg on disk not in showcase
media = {f"assets/media/{f.name}" for f in (ROOT / "assets/media").glob("*") if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}}
show_set = set(showcase)
founders = {"assets/media/founders.jpg", "assets/media/10f9a07b05780c7691c41a3bba7f817d.jpg", "assets/media/e1f78e667dbffb6298b1859dcb1092af.jpg"}
extra = sorted(media - show_set - founders - {p for p in media if "logo" in p or p.endswith(".svg")})
print("extra media jpg/png on disk", len(extra))
for p in extra[:15]:
    print(" ", p)
