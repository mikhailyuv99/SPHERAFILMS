import re
from pathlib import Path
ROOT = Path(r"c:\Users\mikha\Desktop\Sphera Films")
t = (ROOT / "gallerie.html").read_text(encoding="utf-8")
scripts = re.findall(r'<script[^>]*src="([^"]+)"', t)
print("scripts:", len(scripts))
for s in scripts:
    p = ROOT / s.replace("/", "\\")
    print(s, "OK" if p.exists() else "MISSING")
