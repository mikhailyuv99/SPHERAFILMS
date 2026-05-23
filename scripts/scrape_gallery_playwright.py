"""Scrape ALL gallery images from live spherafilms.com/gallerie via Playwright."""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "assets/media"
MAP = ROOT / "assets/media-map"
ORDER_PATH = MAP / "gallery-page-order.json"
SCRAPED_PATH = MAP / "gallery-scraped-order.json"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://spherafilms.com/gallerie"}

EXCLUDE = {
    "f09e28130786425c25ceaa9561def661",
    "10f9a07b05780c7691c41a3bba7f817d",
    "e1f78e667dbffb6298b1859dcb1092af",
    "0bee10adc0a548861f7ce9fa2aa929e1",
    "founders",
}


def bootstrap_order() -> list[str]:
    html = (ROOT / "scripts/cache_gallerie_fresh.html").read_text(encoding="utf-8", errors="replace")
    if "bootstrap" not in html:
        import urllib.request as ur

        html = ur.urlopen(
            ur.Request("https://spherafilms.com/gallerie", headers={"User-Agent": "Mozilla/5.0"}),
            timeout=90,
        ).read().decode("utf-8", "replace")
        (ROOT / "scripts/cache_gallerie_live.html").write_text(html, encoding="utf-8")

    seen: set[str] = set()
    names: list[str] = []
    for m in re.finditer(r"([a-f0-9]{32})\.(jpe?g|png|webp)", html, re.I):
        name = f"{m.group(1).lower()}.{m.group(2).lower()}"
        stem = name.rsplit(".", 1)[0]
        if stem in EXCLUDE or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


async def scrape_urls() -> dict[str, str]:
    from playwright.async_api import async_playwright

    url_map: dict[str, str] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        def on_response(resp):
            try:
                u = resp.url
                if resp.status != 200:
                    return
                name = Path(urlparse(u).path).name.split("?")[0]
                if not re.match(r"^[a-f0-9]{32}\.(jpe?g|png|webp)$", name, re.I):
                    return
                ct = resp.headers.get("content-type", "")
                if "image" in ct or name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    url_map.setdefault(name.lower(), u.split("?")[0] if "?" not in u else u)
            except Exception:
                pass

        page.on("response", on_response)
        await page.goto("https://spherafilms.com/gallerie", wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_timeout(2500)

        last_count = 0
        stale = 0
        for i in range(120):
            await page.evaluate(
                """async () => {
                  const step = Math.max(window.innerHeight, 600);
                  for (let y = 0; y < document.body.scrollHeight; y += step) {
                    window.scrollTo(0, y);
                    await new Promise(r => setTimeout(r, 120));
                  }
                  window.scrollTo(0, document.body.scrollHeight);
                }"""
            )
            await page.wait_for_timeout(500)
            dom = await page.evaluate(
                """() => Array.from(document.querySelectorAll('img'))
                  .flatMap(i => [i.currentSrc, i.src].filter(Boolean))"""
            )
            for u in dom:
                name = Path(urlparse(u).path).name.split("?")[0].lower()
                if re.match(r"^[a-f0-9]{32}\.(jpe?g|png|webp)$", name, re.I):
                    url_map.setdefault(name, u)

            if len(url_map) == last_count:
                stale += 1
                if stale >= 12:
                    break
            else:
                stale = 0
                last_count = len(url_map)
            print(f"scroll {i+1}: {len(url_map)} images")

        await browser.close()
    return url_map


def download(name: str, url: str) -> str | None:
    dest = MEDIA / name
    local = f"assets/media/{name}"
    if dest.is_file() and dest.stat().st_size > 2000:
        return local
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=90).read()
        if len(data) > 2000:
            dest.write_bytes(data)
            print("  OK", name)
            return local
    except Exception as e:
        print("  FAIL", name, str(e)[:60])
    return None


def main() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    names = bootstrap_order()
    print("bootstrap order:", len(names))

    url_map = asyncio.run(scrape_urls())
    print("playwright captured:", len(url_map))

    order: list[dict] = []
    local_paths: list[str] = []
    seen: set[str] = set()

    for name in names:
        stem = name.rsplit(".", 1)[0]
        if stem in seen:
            continue
        seen.add(stem)

        live_url = url_map.get(name.lower())
        local = MEDIA / name
        src = f"assets/media/{name}"
        fallback = None

        if live_url:
            downloaded = download(name, live_url)
            if downloaded:
                src = downloaded
                local_paths.append(downloaded)
            else:
                src = live_url
                fallback = live_url
        elif local.is_file() and local.stat().st_size > 2000:
            local_paths.append(src)
        else:
            continue

        order.append(
            {
                "path": f"assets/media/{name}",
                "src": src,
                "name": name,
                "fallbackSrc": fallback,
            }
        )

    # Append any captured images not in bootstrap order
    for name, live_url in url_map.items():
        stem = name.rsplit(".", 1)[0]
        if stem in EXCLUDE or stem in seen:
            continue
        seen.add(stem)
        downloaded = download(name, live_url)
        src = downloaded or live_url
        if downloaded:
            local_paths.append(downloaded)
        order.append(
            {
                "path": f"assets/media/{name}",
                "src": src,
                "name": name,
                "fallbackSrc": live_url if not downloaded else None,
            }
        )

    out = {
        "order": order,
        "count": len(order),
        "source": "https://spherafilms.com/gallerie",
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
    }
    ORDER_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    SCRAPED_PATH.write_text(
        json.dumps({"order": local_paths, "count": len(local_paths)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(order)} gallery items ({len(local_paths)} local)")


if __name__ == "__main__":
    main()
