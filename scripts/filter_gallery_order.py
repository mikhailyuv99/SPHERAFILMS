import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "assets/media-map/gallery-page-order.json"
media = ROOT / "assets/media"
d = json.loads(p.read_text(encoding="utf-8"))
cdn = "https://spherafilms.com/gallerie/_assets/media/"

order = []
seen = set()
for item in d["order"]:
    name = item["name"]
    stem = name.rsplit(".", 1)[0]
    if stem in seen:
        continue
    local = media / name
    if not local.is_file() or local.stat().st_size < 800:
        continue
    seen.add(stem)
    order.append(
        {
            "path": f"assets/media/{name}",
            "src": f"assets/media/{name}",
            "name": name,
            "fallbackSrc": cdn + name,
        }
    )

out = {"order": order, "count": len(order), "source": d.get("source", "")}
p.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print("filtered to", len(order), "unique local images")
