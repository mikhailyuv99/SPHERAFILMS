from pathlib import Path
import re

p = Path(r"C:\Users\mikha\Desktop\Sphera Films\index.html")
t = p.read_text(encoding="utf-8")
t = t.replace("<motion", "<div").replace("</motion>", "</div>")
t = re.sub(r"</div></motion></div>", "</div>", t)
t = re.sub(r"</motion></div>", "</div>", t)
p.write_text(t, encoding="utf-8")
print("fixed index.html")
