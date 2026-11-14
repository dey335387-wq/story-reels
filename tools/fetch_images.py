"""Fetch free-license photos from Wikimedia Commons (runs in GitHub Actions).
python fetch_images.py <in.img> <outdir>
in.img: one search query per line, optionally "name|query". Saves <outdir>/<name>_<k>.jpg + credits.txt.
Only files whose license is CC0/PD/CC-BY/CC-BY-SA are kept (credit recorded)."""
import sys, os, json, re, urllib.request, urllib.parse, urllib.error
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
UA = {"User-Agent": "story-reels-bot/1.0 (github.com/dey335387-wq/story-reels)"}
def get(url):
    import time
    for a in range(5):  # Wikimedia rate-limits bursts (429): back off and retry
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or a == 4: raise
            time.sleep(5 * (a + 1))
OK = re.compile(r"(cc0|public domain|pd|cc[- ]by(-sa)?[- ]?\d)", re.I)
credits = []
for n, line in enumerate(open(src, encoding="utf-8").read().splitlines()):
    line = line.strip()
    if not line: continue
    name, q = (line.split("|", 1) if "|" in line else (f"img{n}", line))
    p = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
         "gsrsearch": q + " filetype:bitmap", "gsrlimit": "12", "prop": "imageinfo",
         "iiprop": "url|extmetadata|size", "iiurlwidth": "1600"}
    data = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)))
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda x: x.get("index", 99))
    k = 0
    for pg in pages:
        ii = (pg.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        lic = (md.get("LicenseShortName", {}) or {}).get("value", "")
        if not OK.search(lic) or ii.get("width", 0) < 900: continue
        url = ii.get("thumburl") or ii.get("url")
        if not url or not re.search(r"\.(jpe?g|png)$", url.split("?")[0], re.I): continue
        try:
            open(os.path.join(outdir, f"{name}_{k}.jpg"), "wb").write(get(url))
        except Exception as e:
            print("skip", e); continue
        artist = re.sub("<[^>]+>", "", (md.get("Artist", {}) or {}).get("value", "unknown")).strip()
        credits.append(f"{name}_{k}.jpg | {pg.get('title')} | {artist} | {lic} | https://commons.wikimedia.org/wiki/{urllib.parse.quote(pg.get('title','').replace(' ','_'))}")
        k += 1
        if k >= 3: break
    print(name, q, "->", k)
open(os.path.join(outdir, "credits.txt"), "a", encoding="utf-8").write("\n".join(credits) + "\n")
