import re
from pathlib import Path

html = Path(r"C:\Users\mikha\AppData\Local\Temp\sphera.html").read_text(
    encoding="utf-8", errors="replace"
)
start = html.index("JSON.parse('") + len("JSON.parse('")
end = html.rindex("');")
text = html[start:end].replace(r"\/", "/").replace(r"\'", "'")

# French readable strings
candidates = re.findall(r'"([^"]{15,300})"', text)
keywords = (
    "film",
    "cann",
    "production",
    "sphera",
    "agence",
    "nous",
    "contact",
    "galler",
    "vidéo",
    "video",
    "cinéma",
    "luxe",
    "marque",
    "créat",
)
seen = set()
for c in candidates:
    if any(k in c.lower() for k in keywords) and c not in seen:
        if not c.startswith("http") and "{" not in c:
            seen.add(c)
            print(c)

print("\n--- Page routes ---")
for r in re.findall(r"spherafilms\.com/[a-z]+", text):
    print(r)
