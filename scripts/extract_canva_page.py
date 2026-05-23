"""Try to parse Canva page JSON and extract elements with Y positions."""
import re
import json
from pathlib import Path

text = Path(r"c:\Users\mikha\Desktop\Sphera Films\scripts\cache_home.html").read_text(
    encoding="utf-8", errors="replace"
)
start = text.index("JSON.parse('") + 12
raw = text[start : text.rindex("');")]
# Unescape JS string to valid JSON
unescaped = raw.encode("utf-8").decode("unicode_escape") if False else raw
unescaped = raw.replace(r"\/", "/")
# Fix JS escapes for JSON
unescaped = unescaped.replace(r"\'", "'")

# Canva bootstrap might be one object - find first complete parse
for end in range(len(unescaped), 1000, -1):
    try:
        data = json.loads(unescaped[:end])
        print("Parsed at length", end)
        break
    except json.JSONDecodeError:
        continue
else:
    # brute: extract page subtree
    m = re.search(r'"page":(\{.+\}),\s*"ui"', unescaped)
    if not m:
        m = re.search(r'"page":(\{.+\})\s*\}\s*\)\s*;', unescaped)
    data = None
    if m:
        try:
            page = json.loads(m.group(1) + "}")
            data = {"page": page}
            print("Parsed page subtree")
        except Exception as e:
            print("page parse fail", e)

if data:
    Path(r"c:\Users\mikha\Desktop\Sphera Films\scripts\bootstrap_parsed.json").write_text(
        json.dumps(data, indent=2)[:500000], encoding="utf-8"
    )
    print("saved bootstrap_parsed.json", len(json.dumps(data)))

# Extract all text+media pairs by proximity in raw string
media_refs = list(re.finditer(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", unescaped))
print("media count", len(media_refs))

# Find text near each media (500 chars before)
elements = []
for m in media_refs:
    pos = m.start()
    chunk = unescaped[max(0, pos - 800) : pos + 200]
    texts = re.findall(r'"([A-Za-zÀ-ÿ][^"]{4,120})"', chunk)
    texts = [t for t in texts if "http" not in t and "_assets" not in t and "?" not in t[:3]]
    elements.append({"media": m.group(0), "near_text": texts[-3:] if texts else []})

for e in elements[:25]:
    print(e)
print("...")
for e in elements[55:72]:
    print(e)
