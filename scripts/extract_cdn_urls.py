import re
import urllib.request
from pathlib import Path

url = "https://spherafilms.com/gallerie"
html = urllib.request.urlopen(
    urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
    timeout=90,
).read().decode("utf-8", "replace")

# Full CDN URLs in page
urls = []
seen = set()
for m in re.finditer(
    r"https?://[a-z0-9.-]+(?:/_assets/media/|/media/)[a-f0-9]{32}\.[a-z]{3,4}",
    html,
    re.I,
):
    u = m.group(0).split("?")[0]
    if u not in seen:
        seen.add(u)
        urls.append(u)

print("full urls", len(urls))
for u in urls[:5]:
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Referer": url}),
            timeout=20,
        )
        print("OK", u, r.status, r.headers.get("Content-Length"))
    except Exception as e:
        print("FAIL", u, e)

# escaped urls in bootstrap
esc = re.findall(r"https:\\\\/\\\\/[^\"\\]+[a-f0-9]{32}\\.[a-z]{3,4}", html)
print("escaped samples", len(esc))
if esc:
    sample = esc[0].replace("\\/", "/")
    print("sample", sample[:120])
