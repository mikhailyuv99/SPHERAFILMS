"""Build correct site-data.json from Canva order + assets folder."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Client logos on home (before first portfolio jpg), from Canva export order
BRAND_IDS = [
    "a4671c3cdc93430705491cd465b7215a",
    "84672a2709fae3b97a971eb98320ab9f",
    "c4fcce3364564e92d4ad555bf386937c",
    "9d7668e4c7c08e8cb1946a80bb5ede63",
    "ed0daa89eb4c258242db825578b85c8e",
    "c9aa0e0d0679c4a111001079955af830",
    "94171031270bfe9aca961fa8679d9d51",
    "afea03826d98699578d72f995aecde38",
    "8d76b3aa5af47f3e9229754765cccf9e",
    "bdaa994ff318a0180e8f7347ec38ed93",
    "0bba10f772c36893da50ba66a1cae041",
    "0486027ee497aca970f2144ab2cd0eb0",
    "58173bf191ca69a669ca6a08606372a5",
    "fc2f20543a9918c2f89d5674dd1518b0",
    "5c093d045eb7fcb08e378a1af2b355f8",
    "3cee74569b6270caff79a95787569469",
    "6fbf1b251541154a6934b7190875b5f4",
    "fd94faffd16c389f9343a0c4f1b6d660",
    "d925bcb22407bf9216272431883dd5d4",
    "a988a6c5bde226b78d47976c0be85b3a",
    "ece99664c5026f3bf74e9e58420344af",
    "132716e179c2035f3c1d642632355a92",
    "c75b4c094366f2f6d242d3cd027fb0d4",
    "95471e4a40b667fab94d711c30697a66",
    "b0470b57a414cddd102187a652fa360e",
    "fcdea0dbaaa87a98fd796f8f6908b316",
    "359a2a91c063a61ac4fb01a58347a01d",
    "58cdb9a2f7cce327825e711b67ead991",
]

# Social / UI icons — never in client marquee
EXCLUDE_BRAND = {
    "88c84b8adc504d0c6bc888ad132eb388",
    "4c51dd0398a1625f638af77912acc3e1",
    "fec4c46f59d2687154e3f364f3b1cff0",
    "fea1775c265beea9b248f4fa76d938d0",
    "9184fd18c8c2435d46d9dfd396824526",
    "65b841d9c6b2b61ae45be9881ae7db97",
    "9771207b0afeccc0e4f4cde7bd363366",
    "536556aee892b7ba1f17321aa683cf2f",
    "e326174da2306cfbaa00b7bcde2a04ee",
    "15430ce4c716dcf666cc4d22e3a41eb4",
}

FOUNDERS = [
    "assets/media/10f9a07b05780c7691c41a3bba7f817d.jpg",
    "assets/media/e1f78e667dbffb6298b1859dcb1092af.jpg",
]


def parse_gallery_order() -> list[str]:
    gal = ROOT / "scripts" / "cache_gallerie.html"
    if not gal.is_file():
        return []
    html = gal.read_text(encoding="utf-8", errors="replace")
    start = html.index("JSON.parse('") + 12
    end = html.rindex("');")
    text = html[start:end].replace(r"\/", "/").replace(r"\'", "'")
    out = []
    for m in re.finditer(r"_assets/media/[a-f0-9]+\.(?:jpe?g|png|webp)", text, re.I):
        p = m.group(0)
        if p not in out:
            out.append(p)
    return out


def to_assets(path: str) -> str:
    return path.replace("_assets/", "assets/")


def main() -> None:
    base = json.loads((ROOT / "assets" / "site-data.json").read_text(encoding="utf-8"))

    brand_logos = []
    seen = set()
    for aid in BRAND_IDS:
        if aid in EXCLUDE_BRAND or aid in seen:
            continue
        p = ROOT / "assets" / "media" / f"{aid}.png"
        if p.is_file():
            brand_logos.append(f"assets/media/{aid}.png")
            seen.add(aid)

    gallery = []
    seen_g = set()
    for p in parse_gallery_order():
        ap = to_assets(p)
        aid = Path(ap).stem
        if aid in seen_g:
            continue
        if not (ROOT / ap).is_file():
            continue
        if ap.endswith(".png") and aid in EXCLUDE_BRAND | set(BRAND_IDS):
            continue
        seen_g.add(aid)
        gallery.append(ap)

    if len(gallery) < 5:
        for p in base.get("homeShowcase", []):
            ap = to_assets(p)
            if not re.search(r"\.jpe?g$", ap, re.I):
                continue
            aid = Path(ap).stem
            if aid in seen_g or aid in {Path(x).stem for x in FOUNDERS}:
                continue
            if (ROOT / ap).is_file():
                seen_g.add(aid)
                gallery.append(ap)

    founders = [p for p in FOUNDERS if (ROOT / p).is_file()]

    data = {
        **base,
        "logo": "assets/logo-white.svg",
        "heroVideo": "assets/video/2fd03eee1d475c88c16ce9971695f4fd.mp4",
        "heroPoster": "assets/media/0bee10adc0a548861f7ce9fa2aa929e1.jpg",
        "brandLogos": brand_logos,
        "gallery": gallery,
        "foundersPhotos": founders,
        "social": {
            "instagram": "https://www.instagram.com/spherafilms",
            "linkedin": "https://www.linkedin.com/in/sphera-films-2a9956343/",
        },
    }

    out = ROOT / "assets" / "site-data.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("brands:", len(brand_logos))
    print("gallery:", len(gallery))
    print("founders:", founders)


if __name__ == "__main__":
    main()
