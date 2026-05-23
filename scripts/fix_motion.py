from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / "js" / "site.js"
t = p.read_text(encoding="utf-8")
t = re.sub(r"</?motion>", "", t)
p.write_text(t, encoding="utf-8")
print("fixed")
