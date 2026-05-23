# Media map — Sphera Films

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

Live site lists **268** photos; **26** are on disk (rest 404 on Canva CDN).

Regenerate: `python scripts/organize_media.py`
