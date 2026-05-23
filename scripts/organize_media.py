"""
Map all scraped Sphera Films media to original site sections.

Output: assets/media-map/*.json (one file per section) + index.json + README.md

Run: python scripts/organize_media.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "media-map"

# ── Original site section IDs (from Canva export order on spherafilms.com) ──

BRAND_MARQUEE_IDS = [
    "6fbf1b251541154a6934b7190875b5f4",  # IZIPIZI
    "ece99664c5026f3bf74e9e58420344af",  # L'ORÉAL
    "b0470b57a414cddd102187a652fa360e",  # Le Méridien
    "fd94faffd16c389f9343a0c4f1b6d660",  # Universal Music
    "fc2f20543a9918c2f89d5674dd1518b0",  # Galimard
    "95471e4a40b667fab94d711c30697a66",  # apm MONACO
    "a988a6c5bde226b78d47976c0be85b3a",  # Motor's Concept
    "8d76b3aa5af47f3e9229754765cccf9e",  # Le Confidentiel
    "a4671c3cdc93430705491cd465b7215a",  # BMW
    "0486027ee497aca970f2144ab2cd0eb0",  # MINI
]

CANVA_LOGO_UI = ["fec4c46f59d2687154e3f364f3b1cff0", "fea1775c265beea9b248f4fa76d938d0"]

SOCIAL_UI = [
    "88c84b8adc504d0c6bc888ad132eb388",
    "4c51dd0398a1625f638af77912acc3e1",
    "9184fd18c8c2435d46d9dfd396824526",
    "65b841d9c6b2b61ae45be9881ae7db97",
    "9771207b0afeccc0e4f4cde7bd363366",
    "536556aee892b7ba1f17321aa683cf2f",
    "e326174da2306cfbaa00b7bcde2a04ee",
]

FOUNDERS = ["founders"]
HERO_VIDEO = "2fd03eee1d475c88c16ce9971695f4fd"
HERO_POSTER = "0bee10adc0a548861f7ce9fa2aa929e1"

SKIP_HOME_PHOTO = set(CANVA_LOGO_UI + SOCIAL_UI + BRAND_MARQUEE_IDS + FOUNDERS + [HERO_POSTER, "15430ce4c716dcf666cc4d22e3a41eb4"])


def parse_media_order(html_path: Path) -> list[str]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    start = html.index("JSON.parse('") + 12
    text = html[start : html.rindex("');")].replace(r"\/", "/").replace(r"\'", "'")
    order = []
    for m in re.finditer(r"_assets/(?:media|video)/[a-f0-9]+\.[a-z0-9]+", text):
        p = m.group(0)
        if p not in order:
            order.append(p)
    return order


def vimeo_ids(html_path: Path) -> list[str]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    ids = []
    for m in re.finditer(r"vimeo\.com/(\d+)", html):
        if m.group(1) not in ids:
            ids.append(m.group(1))
    return ids


def to_assets(path: str) -> str:
    return path.replace("_assets/", "assets/")


def sid(path: str) -> str:
    return Path(path).stem


def on_disk(path: str) -> bool:
    p = path.replace("_assets/", "assets/")
    return (ROOT / p).is_file() or (ROOT / path).is_file()


def uniq(paths: list[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def pack(desc: str, page: str, paths: list[str]) -> dict:
    paths = uniq(paths)
    order = [p for p in paths if on_disk(p)]
    missing = [p for p in paths if not on_disk(p)]
    return {
        "description": desc,
        "page": page,
        "order": order,
        "missingOnDisk": missing,
        "countOnDisk": len(order),
        "countListed": len(paths),
    }


def main() -> None:
    home_order = parse_media_order(ROOT / "scripts" / "cache_home.html")
    gal_paths = parse_media_order(ROOT / "scripts" / "cache_gallerie_fresh.html")
    if len(gal_paths) < 10:
        gal_paths = parse_media_order(ROOT / "scripts" / "cache_gallerie.html")

    video_idx = next((i for i, p in enumerate(home_order) if p.endswith(".mp4")), len(home_order))

    home_showcase = []
    for p in home_order[:video_idx]:
        if not re.search(r"\.(jpe?g|png|webp)$", p, re.I):
            continue
        if sid(p) in SKIP_HOME_PHOTO:
            continue
        home_showcase.append(to_assets(p))

    sections: dict[str, dict] = {}

    sections["00-user-assets"] = {
        "description": "Your custom assets (not from Canva scrape)",
        "page": "global",
        "order": [
            p
            for p in [
                "assets/logo.svg",
                "assets/logo-white.svg",
                "assets/bg-texture.png",
            ]
            if on_disk(p)
        ],
        "notes": "Use logo-white.svg in nav. bg-texture.png = site background.",
    }

    sections["01-canva-logo-ui"] = pack(
        "Old Canva logo placeholders in export — ignore, use 00-user-assets",
        "index",
        [f"assets/media/{x}.svg" for x in CANVA_LOGO_UI],
    )

    sections["02-brand-marquee"] = pack(
        "Ils nous font confiance — client brand logos (keep original colors)",
        "index",
        [f"assets/media/{x}.png" for x in BRAND_MARQUEE_IDS],
    )

    sections["03-hero"] = {
        "description": "Hero — autoplay background video + poster JPG",
        "page": "index",
        "video": f"assets/video/{HERO_VIDEO}.mp4",
        "poster": f"assets/media/{HERO_POSTER}.jpg",
        "downloaded": {
            "video": on_disk(f"assets/video/{HERO_VIDEO}.mp4"),
            "poster": on_disk(f"assets/media/{HERO_POSTER}.jpg"),
        },
    }

    sections["04-home-showcase"] = pack(
        "Home page portfolio photos (before hero video in scroll order, excl. founders/brands)",
        "index",
        home_showcase,
    )

    sections["05-founders"] = {
        "description": "Fondateurs — Enzo & Lani duo photo",
        "page": "index",
        "photo": "assets/media/founders.jpg",
        "order": ["assets/media/founders.jpg"],
    }

    sections["06-social-icons"] = pack(
        "Contact section — Instagram/LinkedIn/etc. icon PNGs (NOT client brands)",
        "index",
        [f"assets/media/{x}.png" for x in SOCIAL_UI if (ROOT / "assets/media" / f"{x}.png").exists()]
        + [f"assets/media/{x}.png" for x in SOCIAL_UI if (ROOT / "assets/media" / f"{x}.svg").exists()],
    )

    vimeo = vimeo_ids(ROOT / "scripts" / "cache_home.html")
    sections["07-vimeo-realisations"] = {
        "description": "Nos réalisations — Vimeo embed carousel (remote, not local files)",
        "page": "index",
        "vimeoIds": vimeo,
        "count": len(vimeo),
    }

    local_videos = [to_assets(p) for p in home_order if p.endswith((".mp4", ".m4a", ".m3u"))]
    sections["08-local-videos"] = pack(
        "All video/audio files downloaded from Canva export",
        "index",
        local_videos,
    )

    video_thumbs = [to_assets(p) for p in home_order if "/video/" in p and p.endswith(".jpg")]
    sections["09-video-thumbnails"] = pack(
        "Thumbnail JPGs stored under assets/video/",
        "index",
        video_thumbs,
    )

    gallery_items = []
    seen_g = set()
    for p in gal_paths:
        if not re.search(r"\.(jpe?g|png|webp)$", p, re.I):
            continue
        if sid(p) in set(CANVA_LOGO_UI + SOCIAL_UI + BRAND_MARQUEE_IDS):
            continue
        if sid(p) in seen_g:
            continue
        seen_g.add(sid(p))
        ap = to_assets(p)
        gallery_items.append({"path": ap, "downloaded": on_disk(ap)})

    sections["10-galerie-page"] = {
        "description": "gallerie.html — full photo grid in original site order",
        "page": "gallerie",
        "items": gallery_items,
        "countListed": len(gallery_items),
        "countDownloaded": sum(1 for i in gallery_items if i["downloaded"]),
    }

    # Copy text from site
    copy_path = ROOT / "assets" / "site-data.json"
    if copy_path.is_file():
        sd = json.loads(copy_path.read_text(encoding="utf-8"))
        sections["11-copy-text"] = {
            "description": "All French copy from original site — labels, paragraphs, contact",
            "page": "global",
            "copy": sd.get("copy", {}),
            "social": sd.get("social", {}),
            "jotform": "https://form.jotform.com/243464053454354",
        }

    # Unassigned on disk
    assigned = set()
    for key, sec in sections.items():
        if key.startswith("99"):
            continue
        for p in sec.get("order", []):
            assigned.add(p)
        if "video" in sec:
            assigned.add(sec["video"])
        if "poster" in sec:
            assigned.add(sec["poster"])
        for item in sec.get("items", []):
            if item.get("downloaded"):
                assigned.add(item["path"])

    disk_media = sorted(f"assets/media/{f.name}" for f in (ROOT / "assets/media").glob("*") if f.is_file())
    disk_video = sorted(f"assets/video/{f.name}" for f in (ROOT / "assets/video").glob("*") if f.is_file())

    sections["99-unassigned"] = pack(
        "Files on disk not assigned above (review manually)",
        "unknown",
        [p for p in disk_media + disk_video if p not in assigned],
    )

    OUT.mkdir(parents=True, exist_ok=True)

    index = {
        "source": "spherafilms.com Canva export (scripts/cache_*.html)",
        "regenerate": "python scripts/organize_media.py",
        "originalSiteSections": [
            {"id": "00-user-assets", "where": "Global", "what": "Your logo + background"},
            {"id": "02-brand-marquee", "where": "Home", "what": "Client logos band"},
            {"id": "03-hero", "where": "Home top", "what": "Autoplay video"},
            {"id": "04-home-showcase", "where": "Home", "what": "Portfolio stills"},
            {"id": "05-founders", "where": "Home — Fondateurs", "what": "Enzo + Lani photos"},
            {"id": "07-vimeo-realisations", "where": "Home — Nos réalisations", "what": "Vimeo IDs"},
            {"id": "06-social-icons", "where": "Home — Contact", "what": "Social icons only"},
            {"id": "10-galerie-page", "where": "gallerie.html", "what": "Full photo gallery"},
            {"id": "11-copy-text", "where": "All pages", "what": "French text content"},
        ],
        "stats": {
            "filesOnDisk": len(disk_media) + len(disk_video),
            "galleryListedOnLiveSite": len(gallery_items),
            "galleryDownloaded": sum(1 for i in gallery_items if i["downloaded"]),
            "vimeoVideos": len(vimeo),
            "brandLogos": sections["02-brand-marquee"]["countOnDisk"],
        },
        "files": {k: f"{k}.json" for k in sorted(sections.keys())},
    }

    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, data in sections.items():
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme = """# Media map — Sphera Films

Parsed from the **original Canva site** (`scripts/cache_home.html`, `scripts/cache_gallerie*.html`).

Use these JSON files when rebuilding — each file = one section of the live site.

| File | Original section |
|------|------------------|
| `00-user-assets.json` | Your logo + background (not scraped) |
| `01-canva-logo-ui.json` | Old Canva logo slots — **ignore** |
| `02-brand-marquee.json` | **Ils nous font confiance** — client PNG logos |
| `03-hero.json` | Hero autoplay **video** + poster |
| `04-home-showcase.json` | Home portfolio photos |
| `05-founders.json` | **Fondateurs** portraits |
| `06-social-icons.json` | Contact social icons (not brands) |
| `07-vimeo-realisations.json` | **Nos réalisations** Vimeo IDs |
| `08-local-videos.json` | Downloaded mp4/m4a/m3u files |
| `09-video-thumbnails.json` | Video thumbnail JPGs |
| `10-galerie-page.json` | **gallerie.html** full grid (order + download status) |
| `11-copy-text.json` | All French copy + social URLs |
| `99-unassigned.json` | Unmapped files on disk |

## Physical files

All scraped media lives in:
- `assets/media/` — images + brand PNGs
- `assets/video/` — mp4, thumbnails, audio

## Gallery note

Live site lists **{galleryListed}** photos; **{galleryDownloaded}** are on disk (rest 404 on Canva CDN).

Regenerate: `python scripts/organize_media.py`
""".format(
        galleryListed=len(gallery_items),
        galleryDownloaded=sum(1 for i in gallery_items if i["downloaded"]),
    )
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    print("Wrote", OUT)
    print(json.dumps(index["stats"], indent=2))


if __name__ == "__main__":
    main()
