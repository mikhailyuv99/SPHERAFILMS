from pathlib import Path
t = Path(r"c:\Users\mikha\Desktop\Sphera Films\index.html").read_text(encoding="utf-8")
print(t[-2500:])
