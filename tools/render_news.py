"""Daily news Short renderer (1080x1920, 30fps), real free-license photos + Ken Burns + kinetic captions.
python3 render_news.py <story.json> <voice.wav> <subs.srt> <out.mp4> [--frames t1,t2]
story.json:
{ "channel": "NAME", "date": "4 NOV 2026", "headline": "SHORT HEADLINE",
  "caps": [ {"t": "CAPTION TEXT", "img": "media/img/x/a_0.jpg", "hot": ["WORD"], "stat": "optional big number",
             "kicker": "optional small label e.g. KYA HUA?"} ...],   # one per spoken caption (same order as SRT)
  "credits": "Photos: Wikimedia Commons (CC BY-SA) — see description" }
"""
import sys, json, re, math, subprocess, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FM = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
ACC = (255, 196, 0); RED = (230, 35, 45); WHITE = (245, 245, 240); BG = (10, 12, 18)
def font(p, s): return ImageFont.truetype(p, s)

def srt(path):
    out = []
    for a, b in re.findall(r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)", open(path, encoding="utf-8").read()):
        f = lambda s: (lambda h, m, x: int(h) * 3600 + int(m) * 60 + float(x.replace(",", ".")))(*s.split(":"))
        out.append((f(a), f(b)))
    return out

def load_img(path, w, h):
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height) * 1.18
    im = im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
    return np.asarray(im)

def main():
    story = json.load(open(sys.argv[1], encoding="utf-8"))
    voice, subs, out = sys.argv[2:5]
    segs = srt(subs); caps = story["caps"]
    assert len(caps) == len(segs), f"caps {len(caps)} != srt {len(segs)}"
    T_END = segs[-1][1] + 2.2
    IW, IH = W, 1240
    cache = {}
    for c in caps:
        if c["img"] not in cache: cache[c["img"]] = load_img(c["img"], IW, IH)
    # group consecutive caps with same image into shots
    shots = []
    for i, c in enumerate(caps):
        st = segs[i][0] if i else 0.0
        if shots and shots[-1]["img"] == c["img"]: continue
        shots.append({"img": c["img"], "t0": st, "k": len(shots)})
    for i, sh in enumerate(shots): sh["t1"] = shots[i + 1]["t0"] if i + 1 < len(shots) else T_END
    yy = np.linspace(0, 1, IH)[:, None, None]
    grad = np.clip((yy - 0.55) / 0.45, 0, 1) ** 1.5
    fB, fK, fS, fM = font(FB, 82), font(FX, 40), font(FB, 150), font(FM, 28)
    chan = story.get("channel", "60 SEC KHABAR").upper()

    def shot_at(t):
        for sh in shots:
            if sh["t0"] <= t < sh["t1"]: return sh
        return shots[-1]

    def cap_at(t):
        for i, (a, b) in enumerate(segs):
            nb = segs[i + 1][0] if i + 1 < len(segs) else b + 0.5
            if a <= t < max(b, nb): return i, t - a
        return None, 0

    def frame(t):
        sh = shot_at(t); loc = t - sh["t0"]; dur = max(0.1, sh["t1"] - sh["t0"])
        src = cache[sh["img"]]; sh_h, sh_w = src.shape[:2]
        p = loc / dur
        z = 1.0 + 0.12 * p if sh["k"] % 2 == 0 else 1.12 - 0.12 * p
        cw, ch = int(sh_w / 1.18 / z * 1.0), int(sh_h / 1.18 / z)
        cw = min(cw, sh_w); ch = min(ch, sh_h)
        pan = (p - 0.5) * (0.06 if sh["k"] % 3 else -0.06)
        ox = int((sh_w - cw) / 2 + pan * sh_w); oy = int((sh_h - ch) / 2)
        ox = max(0, min(sh_w - cw, ox)); oy = max(0, min(sh_h - ch, oy))
        crop = cv2.resize(src[oy:oy + ch, ox:ox + cw], (IW, IH), interpolation=cv2.INTER_LINEAR).astype(np.float32)
        crop = crop * (1 - grad) + np.array(BG, np.float32) * grad
        canvas = np.zeros((H, W, 3), np.float32); canvas[:] = BG
        canvas[130:130 + IH] = crop
        if loc < 0.18 and t > 0.2:  # flash on cut
            canvas = canvas + 120 * (1 - loc / 0.18)
        pil = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(pil)
        # top bar
        d.rectangle([0, 0, W, 130], fill=(14, 16, 24))
        tw = d.textlength(chan, font=font(FB, 46))
        d.rectangle([40, 32, 40 + tw + 40, 98], fill=RED)
        d.text((60, 65), chan, font=font(FB, 46), fill=WHITE, anchor="lm")
        d.text((W - 40, 65), story.get("date", ""), font=font(FX, 36), fill=(190, 190, 200), anchor="rm")
        if int(t * 2) % 2 == 0: d.ellipse([W - 40 - d.textlength(story.get("date", ""), font=font(FX, 36)) - 44, 54, W - 40 - d.textlength(story.get("date", ""), font=font(FX, 36)) - 20, 78], fill=RED)
        ci, age = cap_at(t)
        if ci is not None and t < segs[-1][1] + 0.4:
            c = caps[ci]
            if c.get("kicker"):
                kt = c["kicker"].upper(); kw = d.textlength(kt, font=fK)
                d.rectangle([60, 1150, 60 + kw + 36, 1214], fill=ACC)
                d.text((78, 1182), kt, font=fK, fill=(10, 10, 12), anchor="lm")
            if c.get("stat"):
                a = min(1, age / 0.2); y = 760 + int(40 * (1 - a))
                d.text((W / 2 + 4, y + 6), c["stat"], font=fS, fill=(0, 0, 0), anchor="mm")
                d.text((W / 2, y), c["stat"], font=fS, fill=ACC, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            words = c["t"].upper().split(); lines, cur = [], ""
            for wd in words:
                test = (cur + " " + wd).strip()
                if d.textlength(test, font=fB) > 940 and cur: lines.append(cur); cur = wd
                else: cur = test
            lines.append(cur)
            hot = {h.upper() for h in c.get("hot", [])}
            y0 = 1250
            nw = 0
            for li, ln in enumerate(lines):
                x = (W - d.textlength(ln, font=fB)) / 2; y = y0 + li * 100
                for wd in ln.split(" "):
                    nw += 1
                    if age < 0.05 * nw: break
                    col = ACC if wd.strip(".,?!…") in hot else WHITE
                    d.text((x, y), wd, font=fB, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
                    x += d.textlength(wd + " ", font=fB)
        # headline strip + progress bar
        d.rectangle([0, 1640, W, 1740], fill=(20, 22, 32))
        d.rectangle([0, 1640, 18, 1740], fill=RED)
        d.text((48, 1690), story.get("headline", "").upper(), font=font(FX, 44), fill=WHITE, anchor="lm")
        d.rectangle([0, 1740, int(W * min(1, t / T_END)), 1752], fill=ACC)
        d.text((W / 2, 1830), story.get("credits", ""), font=fM, fill=(140, 140, 150), anchor="mm")
        if t >= segs[-1][1] + 0.4:
            e = min(1, (t - segs[-1][1] - 0.4) / 0.3)
            d.rectangle([0, 0, W, H], fill=(0, 0, 0))
            d.text((W / 2, 880), "FOLLOW", font=font(FB, 120), fill=tuple(int(v * e) for v in ACC), anchor="mm")
            d.text((W / 2, 1020), "ROZ KI KHABAR, AASAAN BHASHA MEIN", font=font(FX, 48), fill=tuple(int(v * e) for v in WHITE), anchor="mm")
        return np.asarray(pil)

    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            Image.fromarray(frame(float(ts))).save(f"{out}_{ts}.jpg", quality=88)
        return
    n = int(T_END * FPS); tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", voice, "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "6M", "-bufsize", "12M",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", tmp],
                         stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out); print("ok", n / FPS)

if __name__ == "__main__":
    main()
