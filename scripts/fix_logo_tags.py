"""Ensure single logo-swap script tag in HTML pages."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = '<script id="sphera-logo-swap" src="js/logo-swap.js" defer></script>'

for page in ("index.html", "gallerie.html", "mentions-legales.html", "politique-de-confidentialite.html"):
    path = ROOT / page
    if not path.exists():
        continue
    html = path.read_text(encoding="utf-8")
    html = re.sub(
        r'<script id="sphera-logo-swap" src="js/logo-swap\.js" defer></script>\s*',
        "",
        html,
    )
    if TAG not in html:
        html = html.replace("</head>", TAG + "</head>", 1)
    path.write_text(html, encoding="utf-8")
    print("ok", page)
