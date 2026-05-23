"""Build site-data.json: copy + media order from original Canva export."""
import re
import json
from pathlib import Path

html = Path(r"C:\Users\mikha\AppData\Local\Temp\sphera.html").read_text(
    encoding="utf-8", errors="replace"
)
start = html.index("JSON.parse('") + 12
text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")

media_order = []
for m in re.finditer(r"_assets/(?:media|video)/([a-f0-9]+\.[a-z0-9]+)", text):
    full = m.group(0)
    if full not in media_order:
        media_order.append(full)

vimeo_ids = []
for m in re.finditer(r"vimeo\.com/(\d+)", text):
    vid = m.group(1)
    if vid not in vimeo_ids:
        vimeo_ids.append(vid)

def to_local(p):
    return p.replace("_assets/", "assets/")

data = {
    "copy": {
        "siteTitle": "Sphera Films",
        "tagline": "Agence Audiovisuelle",
        "hero": "Créateurs d'images d'exception.\nBasés sur la French Riviera.",
        "intro": "Sphera Films, agence de production audiovisuelle basée à Cannes, spécialisée dans la création de contenus visuels d'exception.",
        "artEnImage": "L'art en image",
        "manifesto": "Façonner la lumière, capturer l'instant, révéler l'âme d'une vision.",
        "service1": "Transformez vos contenus en véritables leviers de réservation & d'achat.",
        "service2": "Une réalisation haut de gamme pour une perception premium de votre entreprise.",
        "notreTravail": "Notre travail",
        "nosRealisations": "Nos réalisations",
        "voirGallerie": "Voir la gallerie",
        "nousContacter": "Nous contacter",
        "fondateurs": "Fondateurs",
        "equipe": "Notre équipe",
        "founders": "Enzo Da Silva & Lani Giacinti",
        "contact": "Contact",
        "email": "spherafilms.contact@gmail.com",
        "mentionsLegales": "Mentions Légales",
        "confidentialite": "Politique de Confidentialité",
    },
    "mediaOrder": [to_local(p) for p in media_order],
    "heroVideo": "assets/video/2fd03eee1d475c88c16ce9971695f4fd.mp4",
    "videos": [
        to_local(p)
        for p in media_order
        if p.endswith(".mp4")
    ],
    "vimeoIds": vimeo_ids,
    "routes": {
        "home": "index.html",
        "gallery": "gallerie.html",
        "legal": "mentions-legales.html",
        "privacy": "politique-de-confidentialite.html",
    },
}

out = Path(r"c:\Users\mikha\Desktop\Sphera Films\assets\site-data.json")
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("media:", len(data["mediaOrder"]), "vimeo:", len(vimeo_ids))
