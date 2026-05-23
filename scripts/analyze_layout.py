"""Extract page structure from Canva bootstrap."""
import re
import json
from pathlib import Path

html = Path(r"c:\Users\mikha\Desktop\Sphera Films\scripts\cache_home.html").read_text(
    encoding="utf-8", errors="replace"
)
start = html.index("JSON.parse('") + 12
text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")

# Page dimensions
for pat in [
    r'"D":"([^"]+)"',
    r'"E":"([^"]{20,300})"',
    r'"P":"([^"]+)"',
]:
    m = re.search(pat, text)
    if m:
        print(pat, "=>", m.group(1)[:200])

# Find background colors
colors = sorted(set(re.findall(r'"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})"', text)))
print("\nColors:", colors[:30])

# Font families mentioned
fonts = sorted(set(re.findall(r'"([A-Za-z][A-Za-z0-9 ]{3,40})"', text)))
font_like = [f for f in fonts if any(x in f for x in ["Gothic", "Indifference", "Pragmatic", "Franklin", "Pearl", "Serif", "Sans"])]
print("\nFonts:", font_like)

# Links in page
links = sorted(set(re.findall(r"https?://[^\s\"\\]+|spherafilms\.com/[a-z]+", text)))
print("\nLinks:")
for l in links:
    if "canva" not in l.lower() or "sphera" in l:
        print(" ", l)

# Text blocks with newlines (UI copy)
blocks = re.findall(r'"((?:[^"\\]|\\n){5,400})"', text)
ui = []
for b in blocks:
    b = b.replace("\\n", "\n")
    if re.search(r"[a-zA-ZÀ-ÿ]{4}", b) and "http" not in b and "_assets" not in b and "{" not in b:
        if any(k in b for k in ["Film", "film", "Agence", "Créat", "galler", "Contac", "Riviera", "Cannes", "image", "travail", "réalis", "Fondateur", "Enzo", "lumière"]):
            ui.append(b)
print("\nUI blocks:")
for u in sorted(set(ui), key=len):
    print("---")
    print(u)
