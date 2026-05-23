import json
from pathlib import Path

p = Path(r"c:\Users\mikha\Desktop\Sphera Films\assets\site-data.json")
old = json.loads(p.read_text(encoding="utf-8"))

photos = old.get("home", {}).get("photos") or []
if not photos:
    photos = [
        x for x in old.get("home", {}).get("allMedia", [])
        if any(x.endswith(e) for e in (".jpg", ".jpeg", ".png", ".webp"))
    ]

old["photos"] = photos
old["homeMediaOrder"] = old.get("home", {}).get("allMedia", photos)
p.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(photos), "photos")
