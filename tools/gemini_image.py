"""Gemini image generation (runs in GitHub Actions with GEMINI_API_KEY).
python gemini_image.py <in.gimg> <outdir>
in.gimg: first line = shared style prompt; then one "name|scene prompt" per line. 9:16 portrait.
Writes <outdir>/<name>.png and log.txt. Fictional characters only."""
import sys, os, json, base64, urllib.request, urllib.error
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
lines = [l for l in open(src, encoding="utf-8").read().splitlines() if l.strip()]
style, items = lines[0], [l.split("|", 1) for l in lines[1:]]
MODELS = [m for m in os.environ.get("GEMINI_IMAGE_MODELS", "gemini-2.5-flash-image,gemini-2.5-flash-image-preview,gemini-2.0-flash-preview-image-generation").split(",") if m]
log = []
def call(model, prompt):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": "9:16"}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    return json.load(urllib.request.urlopen(req, timeout=300))
for name, scene in items:
    prompt = f"{style}\nScene: {scene}\nVertical 9:16 composition. No text, no letters, no watermark. All people are fictional."
    ok = False
    for m in MODELS:
        try:
            data = call(m, prompt)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if "imageConfig" in msg or "aspect" in msg.lower():
                try:
                    body_fallback = True
                    data = None
                except Exception: pass
            log.append(f"{name} {m} HTTP {e.code}: {msg}"); continue
        except Exception as e:
            log.append(f"{name} {m} ERR {e}"); continue
        for c in data.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if "inlineData" in p:
                    open(os.path.join(outdir, f"{name}.png"), "wb").write(base64.b64decode(p["inlineData"]["data"]))
                    ok = True; break
            if ok: break
        if ok: log.append(f"{name} OK {m}"); break
        log.append(f"{name} {m} no image: {json.dumps(data)[:300]}")
    print(log[-1])
open(os.path.join(outdir, "log.txt"), "a").write("\n".join(log) + "\n")
