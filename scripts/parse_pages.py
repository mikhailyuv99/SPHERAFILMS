import re
from pathlib import Path

def extract(path):
    data = Path(path).read_text(encoding="utf-8", errors="replace")
    start = data.index("JSON.parse('") + 12
    text = data[start : data.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
    media = []
    for m in re.finditer(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", text):
        p = m.group(0).replace("_assets/", "assets/")
        if p not in media:
            media.append(p)
    title = re.search(r'"D":"([^"]+)"', text)
    return title.group(1) if title else "?", media

home = extract(r"C:\Users\mikha\AppData\Local\Temp\sphera.html")
gal = extract(r"C:\Users\mikha\AppData\Local\Temp\sphera_gallerie.html")
print("HOME", home[0], len(home[1]))
print("GALLERIE", gal[0], len(gal[1]))
print("\nGallerie media:")
for p in gal[1]:
    print(p)
