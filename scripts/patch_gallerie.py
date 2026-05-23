"""Build gallerie.html: index shell + gallerie page bootstrap."""
import re
from pathlib import Path

ROOT = Path(r"c:\Users\mikha\Desktop\Sphera Films")

def prepare(html: str) -> str:
    html = re.sub(r'\s+integrity="[^"]*"', "", html)
    html = re.sub(r'\s+nonce="[^"]*"', "", html)
    html = re.sub(r'\s+crossorigin="[^"]*"', "", html)
    html = html.replace('<base href="/">', '<base href="./">')
    html = html.replace("window['__canva_public_path__'] = '_assets\\/';", "window['__canva_public_path__'] = '_assets/';")
    return html

home = (ROOT / "index.html").read_text(encoding="utf-8")
gal_src = (ROOT / "scripts" / "cache_gallerie_fresh.html").read_text(encoding="utf-8")

# Extract gallerie bootstrap block
start = gal_src.index("window['bootstrap'] = JSON.parse('")
end = gal_src.index("'); window['flags']", start) + 2
gal_bootstrap = gal_src[start:end]

# Index: replace bootstrap in body
home_body = re.search(r"<body>(.*)</body>", home, re.S).group(1)
idx_start = home_body.index("window['bootstrap'] = JSON.parse('")
idx_end = home_body.index("'); window['flags']", idx_start) + 2
new_body = home_body[:idx_start] + gal_bootstrap + home_body[idx_end:]

# Fix title in head
home_head = re.search(r"<head>(.*)</head>", home, re.S).group(1)
home_head = re.sub(r"<title>[^<]*</title>", "<title>Gallerie — Sphera Films</title>", home_head)

new_html = (
    '<!DOCTYPE html><html dir="ltr" lang="fr-FR" class="theme light classic">'
    f"<head>{home_head}</head><body>{new_body}</body></html>"
)
(ROOT / "gallerie.html").write_text(prepare(new_html), encoding="utf-8")
print("gallerie = index runtime + gallerie bootstrap")
