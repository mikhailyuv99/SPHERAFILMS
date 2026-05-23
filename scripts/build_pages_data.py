"""Build page-specific JSON from cached HTML."""
import re
import json
from pathlib import Path

SCRIPTS = Path(r"c:\Users\mikha\Desktop\Sphera Films\scripts")
PROJECT = Path(r"c:\Users\mikha\Desktop\Sphera Films")

def parse(html):
    start = html.index("JSON.parse('") + 12
    text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
    media = []
    for m in re.finditer(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", text):
        p = m.group(0).replace("_assets/", "assets/")
        if p not in media:
            media.append(p)
    return text, media

def existing_only(paths):
    out = []
    for p in paths:
        if (PROJECT / p).exists():
            out.append(p)
    return out

home_html = (SCRIPTS / "cache_home.html").read_text(encoding="utf-8", errors="replace")
gal_html = (SCRIPTS / "cache_gallerie.html").read_text(encoding="utf-8", errors="replace")

_, home_media = parse(home_html)
_, gal_media = parse(gal_html)

# Split home media into sections by first video index
video_idx = next(
    (i for i, p in enumerate(home_media) if p.endswith(".mp4")),
    len(home_media),
)
home_images = home_media[:video_idx]
home_videos = [p for p in home_media if p.endswith((".mp4", ".m4a", ".m3u"))]

# Decorative PNGs before first jpg (likely UI)
first_jpg = next((i for i, p in enumerate(home_images) if ".jpg" in p), 0)
brand_assets = home_images[:first_jpg]
photo_start = home_images[first_jpg:]

data = {
    "copy": {
        "siteTitle": "Sphera Films",
        "tagline": "Agence        Audiovisuelle",
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
    "home": {
        "brandAssets": existing_only(brand_assets),
        "photos": existing_only(photo_start),
        "videos": existing_only(home_videos),
        "allMedia": existing_only(home_media),
    },
    "gallery": {
        "allMedia": existing_only(gal_media),
        "photos": existing_only([p for p in gal_media if re.search(r"\.(jpg|jpeg|png|webp)$", p, re.I)]),
    },
    "vimeoIds": [],
}

# vimeo from home
home_text, _ = parse(home_html)
for m in re.finditer(r"vimeo\.com/(\d+)", home_text):
    vid = m.group(1)
    if vid not in data["vimeoIds"]:
        data["vimeoIds"].append(vid)

out = PROJECT / "assets" / "site-data.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("home all:", len(data["home"]["allMedia"]))
print("gallery available:", len(data["gallery"]["photos"]), "/", len(gal_media))
