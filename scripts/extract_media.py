"""Extract media URLs from spherafilms.com Canva export HTML."""
import re
import json
from pathlib import Path

html_path = Path(r"C:\Users\mikha\AppData\Local\Temp\sphera.html")
html = html_path.read_text(encoding="utf-8", errors="replace")

start = html.index("JSON.parse('") + len("JSON.parse('")
end = html.rindex("');")
raw = html[start:end]
text = raw.replace(r"\/", "/").replace(r"\'", "'")

paths = set(re.findall(r"_assets/[a-zA-Z0-9_.%-]+", text))
urls = set(re.findall(r"https?://[^\s\"\\]+", text))
media_ext = re.findall(
    r"([a-zA-Z0-9_-]+\.(?:jpg|jpeg|png|webp|gif|svg|mp4|webm|mov))",
    text,
    re.I,
)

print("=== _assets paths ===")
for p in sorted(paths):
    print(p)

print("\n=== http urls (sample) ===")
for u in sorted(urls)[:50]:
    print(u)

print("\n=== filenames with media ext ===")
for m in sorted(set(media_ext)):
    print(m)

# Try JSON parse
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    print("\nJSON parse failed:", e)
    data = None

if data:

    def walk(o, found=None):
        if found is None:
            found = []
        if isinstance(o, dict):
            for v in o.values():
                walk(v, found)
        elif isinstance(o, list):
            for v in o:
                walk(v, found)
        elif isinstance(o, str):
            low = o.lower()
            if any(
                x in low
                for x in [
                    ".jpg",
                    ".png",
                    ".mp4",
                    ".webp",
                    "_assets",
                    "media",
                    "video",
                    "image",
                ]
            ):
                if len(o) < 800:
                    found.append(o)
        return found

    found = sorted(set(walk(data)))
    print("\n=== strings from JSON walk ===")
    for f in found[:80]:
        print(f)
