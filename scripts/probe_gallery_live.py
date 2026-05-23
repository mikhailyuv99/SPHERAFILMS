import re
import urllib.request

url = "https://spherafilms.com/gallerie"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
refs = sorted(set(re.findall(r"_assets/media/[a-f0-9]+\.[a-z]+", html)))
print("refs", len(refs))
if refs:
    test = "https://spherafilms.com/" + refs[0]
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(test, headers={"User-Agent": "Mozilla/5.0", "Referer": url}),
            timeout=30,
        )
        print("test ok", refs[0], r.status, r.headers.get("Content-Length"))
    except Exception as e:
        print("test fail", refs[0], e)
