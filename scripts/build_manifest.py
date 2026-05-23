import json
from pathlib import Path

root = Path(r"c:\Users\mikha\Desktop\Sphera Films\assets")
manifest = {"images": [], "videos": []}

for folder, key, exts in [
    ("media", "images", {".jpg", ".jpeg", ".png", ".webp"}),
    ("video", "videos", {".mp4", ".webm"}),
]:
    d = root / folder
    if not d.exists():
        continue
    for f in sorted(d.iterdir()):
        if f.suffix.lower() in exts:
            manifest[key].append(f"assets/{folder}/{f.name}")

out = root.parent / "assets" / "manifest.json"
out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"images: {len(manifest['images'])}, videos: {len(manifest['videos'])}")
