import re
from collections import Counter
from pathlib import Path

html = Path(__file__).resolve().parents[1] / "scripts" / "cache_home.html"
text = html.read_text(encoding="utf-8", errors="replace")
start = text.index("JSON.parse('") + 12
end = text.rindex("');")
raw = text[start:end].replace(r"\/", "/").replace(r"\'", "'")

order = []
for m in re.finditer(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", raw):
    p = m.group(0)
    if p not in order:
        order.append(p)

jpgs = [p for p in order if re.search(r"\.(jpe?g|webp)$", p, re.I)]
print("unique media in order:", len(order))
print("unique jpgs:", len(jpgs))
print("jpg ref count in raw:", len(re.findall(r"_assets/media/[a-f0-9]+\.jpe?g", raw, re.I)))

c = Counter(re.findall(r"_assets/media/[a-f0-9]+\.jpe?g", raw, re.I))
for p, n in c.most_common(20):
    if n > 1:
        print("dup ref", n, p)

print("\nfirst 20 jpgs in page order:")
for p in jpgs[:20]:
    name = p.split("/")[-1]
    exists = (Path(__file__).resolve().parents[1] / p).exists()
    print(name, "OK" if exists else "MISSING")
