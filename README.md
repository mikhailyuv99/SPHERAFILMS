# Sphera Films

Premium enhanced site built from [spherafilms.com](https://www.spherafilms.com) content and media.

- **Original copy & media** (same text, images, videos, Vimeo reels)
- **Your logo** (`assets/logo.svg`) — large in header, hero watermark, preloader
- **Lenis** smooth scroll
- **Scroll animations** (re-trigger when scrolling back)

Canva mirror backup: `index-canva-mirror.html`

## Preview

```bash
python -m http.server 8765
```

http://localhost:8765

## Re-sync media from live site

```bash
python scripts/mirror_canva_site.py
python scripts/rebuild_site_data.py
```
