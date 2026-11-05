"""Free AI image generation via Pollinations (runs in GitHub Actions, no key).
python free_image.py <in.pimg> <outdir>   (same format as .gimg: line1 style, then name|scene)"""
import sys, os, time, urllib.request, urllib.parse
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
lines = [l for l in open(src, encoding="utf-8").read().splitlines() if l.strip()]
style, items = lines[0], [l.split("|", 1) for l in lines[1:]]
log = []
for i, (name, scene) in enumerate(items):
    prompt = f"{scene}. {style}. No text, no letters, no watermark. Fictional people."
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) +
           f"?width=1080&height=1920&nologo=true&model=flux&seed={1000 + i}")
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "story-reels"}), timeout=180).read()
            if len(data) > 20000:
                open(os.path.join(outdir, f"{name}.jpg"), "wb").write(data); log.append(f"{name} OK {len(data)}"); break
            log.append(f"{name} small {len(data)}")
        except Exception as e:
            log.append(f"{name} ERR {e}")
        time.sleep(8)
    print(log[-1])
open(os.path.join(outdir, "log.txt"), "a").write("\n".join(log) + "\n")
