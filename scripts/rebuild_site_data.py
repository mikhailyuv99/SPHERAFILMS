"""Rebuild site-data.json from original Canva home + gallery order."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA_ROOT = ROOT / "_assets"


def parse_media(html: str) -> list[str]:
    start = html.index("JSON.parse('") + 12
    text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
    order = []
    for m in re.finditer(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", text):
        p = m.group(0)
        if p not in order:
            order.append(p)
    return order


def exists(path: str) -> bool:
    return (ROOT / path).is_file()


def unique_keep_order(paths: list[str]) -> list[str]:
    seen = set()
    out = []
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def filter_existing(paths: list[str]) -> list[str]:
    return [p for p in paths if exists(p)]


def is_brand_asset(path: str) -> bool:
    """UI / old logo assets from Canva — not page gallery photos."""
    name = path.lower()
    if name.endswith(".svg") and "fec4c46f" in name:
        return True
    if name.endswith(".png") and any(
        x in name
        for x in (
            "a4671c3cdc93430705491cd465b7215a",
            "88c84b8adc504d0c6bc888ad132eb388",
            "4c51dd0398a1625f638af77912acc3e1",
            "84672a2709fae3b97a971eb98320ab9f",
            "c4fcce3364564e92d4ad555bf386937c",
            "9d7668e4c7c08e8cb1946a80bb5ede63",
            "15430ce4c716dcf666cc4d22e3a41eb4",
            "ed0daa89eb4c258242db825578b85c8e",
            "c9aa0e0d0679c4a111001079955af830",
            "94171031270bfe9aca961fa8679d9d51",
            "afea03826d98699578d72f995aecde38",
            "8d76b3aa5af47f3e9229754765cccf9e",
            "bdaa994ff318a0180e8f7347ec38ed93",
            "0bba10f772c36893da50ba66a1cae041",
        )
    ):
        return True
    return False


def split_home(order: list[str]) -> dict:
    video_idx = next((i for i, p in enumerate(order) if p.endswith(".mp4")), len(order))
    before_video = order[:video_idx]
    videos = [p for p in order if p.endswith((".mp4", ".m4a", ".m3u"))]

    # Photos for showcase: order on site, no brand UI, each once
    showcase = []
    for p in before_video:
        if is_brand_asset(p):
            continue
        if re.search(r"\.(jpe?g|png|webp)$", p, re.I):
            showcase.append(p)

    showcase = unique_keep_order(filter_existing(showcase))
    videos = filter_existing(videos)

    return {"showcase": showcase, "videos": videos}


def main() -> None:
    home_order = parse_media(
        (ROOT / "scripts" / "cache_home.html").read_text(encoding="utf-8", errors="replace")
    )
    gal_order = parse_media(
        (ROOT / "scripts" / "cache_gallerie.html").read_text(encoding="utf-8", errors="replace")
    )

    home = split_home(home_order)
    gal_photos = unique_keep_order(
        filter_existing(
            [p for p in gal_order if re.search(r"\.(jpe?g|png|webp)$", p, re.I) and not is_brand_asset(p)]
        )
    )

    home_text = (ROOT / "scripts" / "cache_home.html").read_text(encoding="utf-8", errors="replace")
    vimeo_ids = []
    for m in re.finditer(r"vimeo\.com/(\d+)", home_text):
        vid = m.group(1)
        if vid not in vimeo_ids:
            vimeo_ids.append(vid)

    copy = {
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
        "foundersIntro": "Duo créatif à la tête de Sphera Films, Enzo et Lani unissent leurs visions pour donner vie à des projets audiovisuels haut de gamme.",
        "foundersEnzo": "Enzo, réalisateur et chef opérateur, façonne l'image et la mise en scène avec une approche cinématographique précise et émotionnelle.",
        "foundersLani": "Lani, directrice artistique et co-réalisatrice, conçoit l'univers visuel, les moodboards et la direction esthétique de chaque projet.",
        "foundersTogether": "Ensemble, ils s'entourent d'équipes techniques et créatives dédiées pour produire des œuvres visuellement fortes et cohérentes.",
        "contact": "Contact",
        "email": "spherafilms.contact@gmail.com",
        "phones": "06.52.88.62.88 & 06.83.83.37.57",
        "mentionsLegales": "Mentions Légales",
        "confidentialite": "Politique de Confidentialité",
    }

    data = {
        "copy": copy,
        "logo": "assets/logo.svg?v=3",
        "heroVideo": "_assets/video/2fd03eee1d475c88c16ce9971695f4fd.mp4",
        "heroPoster": "_assets/media/0bee10adc0a548861f7ce9fa2aa929e1.jpg",
        "homeShowcase": home["showcase"],
        "galleryPhotos": gal_photos if gal_photos else home["showcase"],
        "videos": home["videos"],
        "vimeoIds": vimeo_ids
        or [
            "1041966449",
            "1074771023",
            "1074402244",
            "1161941583",
            "1041727422",
            "956409625",
            "1074768985",
            "1124321394",
            "1124324296",
            "980775525",
            "1089006526",
        ],
        "homeMediaOrder": filter_existing(home_order),
    }

    out = ROOT / "assets" / "site-data.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("home showcase:", len(home["showcase"]))
    print("gallery photos:", len(data["galleryPhotos"]))
    print("videos:", len(home["videos"]))


if __name__ == "__main__":
    main()
