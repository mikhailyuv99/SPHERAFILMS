import re
from pathlib import Path
t = Path(r"c:\Users\mikha\Desktop\Sphera Films\index.html").read_text(encoding="utf-8")
scripts = re.findall(r'<script[^>]*src="([^"]+)"', t)
print("scripts:", scripts)
for s in scripts:
    p = Path(r"c:\Users\mikha\Desktop\Sphera Films") / s.replace("/", "\\")
    print(s, "OK" if p.exists() else "MISSING")
