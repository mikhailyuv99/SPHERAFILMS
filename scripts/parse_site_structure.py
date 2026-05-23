"""Parse Canva bootstrap to extract copy and media placement."""
import re
import json
from pathlib import Path

html = Path(r"C:\Users\mikha\AppData\Local\Temp\sphera.html")
if not html.exists():
    import urllib.request
    req = urllib.request.Request(
        "https://www.spherafilms.com/",
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.spherafilms.com/"},
    )
    data = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", errors="replace")
    html.write_text(data, encoding="utf-8")
else:
    data = html.read_text(encoding="utf-8", errors="replace")

start = data.index("JSON.parse('") + len("JSON.parse('")
end = data.rindex("');")
text = data[start:end].replace(r"\/", "/").replace(r"\'", "'")

# All readable French/English strings (likely copy)
strings = re.findall(r'"((?:[^"\\]|\\.){3,500})"', text)
copy = []
for s in strings:
    s = s.replace("\\n", "\n").replace("\\t", " ")
    if re.search(r"[a-zA-ZÀ-ÿ]{4}", s) and not s.startswith("_assets"):
        if not re.match(r"^[A-Za-z0-9_./:?=&%-]+$", s) or " " in s:
            if "{" not in s and "http" not in s[:8]:
                copy.append(s)

seen = set()
print("=== COPY (unique, sorted by length) ===")
for c in sorted(set(copy), key=len):
    if c not in seen and len(c) > 8:
        seen.add(c)
        print(repr(c))

print("\n=== MEDIA PATHS IN ORDER (first occurrences) ===")
media_paths = []
for m in re.finditer(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", text):
    p = m.group(0)
    if p not in media_paths:
        media_paths.append(p)
for p in media_paths:
    print(p)

print(f"\nTotal unique media refs: {len(media_paths)}")

# Page titles / routes
print("\n=== ROUTES ===")
for r in sorted(set(re.findall(r"spherafilms\.com/[a-zA-Z]+", text))):
    print(r)

# Save raw extract for inspection
out = Path(r"c:\Users\mikha\Desktop\Sphera Films\scripts\site_extract.txt")
out.write_text(
    "COPY:\n" + "\n---\n".join(sorted(set(copy), key=lambda x: (-len(x), x)))[:80000]
    + "\n\nMEDIA:\n"
    + "\n".join(media_paths),
    encoding="utf-8",
)
print(f"\nWrote {out}")
