from pathlib import Path

p = Path(r"C:\Users\mikha\Desktop\Sphera Films\index.html")
lines = p.read_text(encoding="utf-8").splitlines()
out = []
for line in lines:
    if "bg-texture" in line:
        out.append('    <div class="bg-texture" aria-hidden="true"></div>')
    else:
        out.append(line)
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print("ok")
