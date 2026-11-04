"""Render 'Camera 4' Part 2 reel: CCTV / dark comic style, 1080x1920, 30fps.
Usage: python3 render_p2.py <audio.mp3> <subs.srt> <out.mp4> [--frames t1,t2,...]
"""
import sys, re, math, subprocess, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
import os
TEMPO = float(os.environ.get("TEMPO", "1.10"))
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
RED = (225, 30, 40); WHITE = (240, 240, 235); BG = (14, 16, 22)
INK = (205, 210, 215); DIM = (70, 76, 88)

SERIES = "KHAALI COACH"
CAPS = ["MAA!...", "MAINE POORI TAAQAT SE CHAIN KHEENCHI!", "BRAKE CHEEKHE...", "LIGHTS BUJH GAYI...",
        "AUR WO AURAT CHILLAAYI... ROHAN!", "PHIR... SAB SHAANT.", "BEEP... BEEP...", "EK MACHINE KI AAWAAZ.",
        "MAINE AANKHEIN KHOLI...", "SAAMNE MAA RO RAHI THI...", "DOCTOR! ISNE AANKHEIN KHOL DI!",
        "DO SAAL... MAIN COMA MEIN THA.", "US HAADSE KE BAAD SE.", "MAIN ZINDA THA...", "MAIN GHAR AA GAYA THA.",
        "TABHI EK NURSE DAWAI DENE AAYI...", "USKI KALAAI MEIN...", "LAAL CHOODIYAN THI.",
        "AUR JAATE HUE USNE DHEERE SE KAHA...", "AGLI BAAR... TRAIN MAT CHHODNA, ROHAN."]
HOT = {"MAA!...", "CHAIN", "CHEEKHE...", "BUJH", "ROHAN!", "SHAANT.", "BEEP...", "AANKHEIN", "MAA", "COMA",
       "ZINDA", "NURSE", "KALAAI", "LAAL", "CHOODIYAN", "TRAIN", "ROHAN."}
SCENE_OF = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 2, 2, 3, 3, 5, 4, 4, 5, 5]
STAMP = {0: ("00:40:59", "LIVE"), 1: ("00:41:02", "LIVE"), 2: ("06:12:40", "ICU"), 5: ("06:31:12", "ICU")}

PX0, PY0, PX1, PY1 = 60, 230, 1020, 1330   # main panel
PW, PH = PX1 - PX0, PY1 - PY0

def font(p, s): return ImageFont.truetype(p, s)

def srt(path):
    t = open(path, encoding="utf-8").read()
    out = []
    for a, b in re.findall(r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)", t):
        f = lambda s: (lambda h, m, x: int(h) * 3600 + int(m) * 60 + float(x.replace(",", ".")))(*s.split(":"))
        out.append((f(a) / TEMPO, f(b) / TEMPO))
    return out

# ---------- illustrations (drawn at 2x then downsampled for smooth edges) ----------
def halftone(img, strength=0.55, step=9):
    a = np.asarray(img.convert("L"), np.float32) / 255
    dots = Image.new("L", img.size, 0); d = ImageDraw.Draw(dots)
    for y in range(0, img.size[1], step):
        for x in range((y // step) % 2 * step // 2, img.size[0], step):
            v = a[min(y, img.size[1] - 1), min(x, img.size[0] - 1)]
            r = v * step * 0.55
            if r > 0.6: d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    base = np.asarray(img, np.float32)
    m = np.asarray(dots, np.float32)[..., None] / 255
    return Image.fromarray(np.clip(base * (1 - strength) + base * m * strength * 1.6, 0, 255).astype(np.uint8))

def canvas(top=(30, 34, 46), bot=(8, 9, 13)):
    S = 2; w, h = PW * S, PH * S
    g = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top) * (1 - g) + np.array(bot) * g) * np.ones((1, w, 1))
    return Image.fromarray(arr.astype(np.uint8)), S

def finish(img, S, ht=True):
    img = img.resize((PW, PH), Image.LANCZOS)
    return halftone(img) if ht else img

def room_base(d, S, almirah_open=0.0):
    w, h = PW * S, PH * S
    fl = int(h * 0.62)
    d.polygon([(0, fl), (w, fl), (w, h), (0, h)], fill=(22, 24, 30))
    for i in range(-6, 14):  # floor lines
        d.line([(w * 0.5 + i * 160 * S * 0.6, fl), (w * 0.5 + i * 420 * S * 0.6, h)], fill=(30, 33, 41), width=2 * S)
    # window with moonlight
    d.rectangle([w * 0.62, h * 0.12, w * 0.9, h * 0.42], fill=(48, 56, 74), outline=INK, width=3 * S)
    d.line([(w * 0.76, h * 0.12), (w * 0.76, h * 0.42)], fill=INK, width=3 * S)
    d.line([(w * 0.62, h * 0.27), (w * 0.9, h * 0.27)], fill=INK, width=3 * S)
    # almirah
    ax0, ay0, ax1, ay1 = w * 0.06, h * 0.14, w * 0.34, fl + 20 * S
    d.rectangle([ax0, ay0, ax1, ay1], fill=(26, 26, 30), outline=INK, width=4 * S)
    mid = (ax0 + ax1) / 2
    d.line([(mid, ay0), (mid, ay1)], fill=INK, width=3 * S)
    if almirah_open > 0:
        dw = (ax1 - mid) * almirah_open
        d.polygon([(mid, ay0), (mid, ay1), (mid + dw * 0.35, ay1 + 25 * S), (mid + dw * 0.35, ay0 - 25 * S)],
                  fill=(4, 4, 6))
        d.polygon([(ax1, ay0), (ax1, ay1), (ax1 + dw * 0.7, ay1 + 30 * S), (ax1 + dw * 0.7, ay0 - 30 * S)],
                  fill=(34, 34, 40), outline=INK)
    return fl

def bed(d, S, x0, x1, top, sleeper=True, legs_under=False):
    d.rectangle([x0, top, x1, top + 70 * S], fill=(58, 62, 74), outline=INK, width=4 * S)
    d.rectangle([x0, top + 70 * S, x1, top + 150 * S], fill=(30, 32, 40), outline=INK, width=4 * S)
    d.rectangle([x1 - 20 * S, top - 120 * S, x1, top + 170 * S], fill=(40, 42, 50), outline=INK, width=4 * S)
    d.rectangle([x0, top + 150 * S, x0 + 20 * S, top + 175 * S], fill=INK)
    d.rectangle([x1 - 20 * S, top + 150 * S, x1, top + 175 * S], fill=INK)
    if sleeper:
        d.ellipse([x1 - 170 * S, top - 55 * S, x1 - 70 * S, top + 20 * S], fill=(200, 200, 205))  # pillow
        d.ellipse([x1 - 160 * S, top - 75 * S, x1 - 95 * S, top - 10 * S], fill=(150, 150, 160), outline=INK, width=3 * S)
        d.chord([x0 + 30 * S, top - 70 * S, x1 - 120 * S, top + 50 * S], 180, 360, fill=(90, 96, 112), outline=INK, width=3 * S)
    if legs_under:
        for k, dx in enumerate((0, 46 * S)):
            y = top + 140 * S + k * 10 * S
            d.line([(x0 - 10 * S, y), (x0 - 150 * S - dx, y + 25 * S)], fill=INK, width=34 * S)
            d.ellipse([x0 - 179 * S - dx, y + 4 * S, x0 - 131 * S - dx, y + 46 * S], fill=INK)
            d.line([(x0 - 10 * S, y), (x0 - 150 * S - dx, y + 25 * S)], fill=(8, 8, 10), width=26 * S)
            d.ellipse([x0 - 175 * S - dx, y + 8 * S, x0 - 135 * S - dx, y + 42 * S], fill=(8, 8, 10))

def figure(d, S, cx, feet, hgt, col=(6, 6, 8), eyes=True, outline=INK):
    hr = hgt * 0.09
    hy = feet - hgt + hr
    d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=col, outline=outline, width=2 * S)
    d.polygon([(cx - hr * 1.6, hy + hr * 1.3), (cx + hr * 1.6, hy + hr * 1.3),
               (cx + hr * 1.3, feet - hgt * 0.42), (cx - hr * 1.3, feet - hgt * 0.42)], fill=col, outline=outline)
    d.polygon([(cx - hr * 1.3, feet - hgt * 0.42), (cx + hr * 1.3, feet - hgt * 0.42),
               (cx + hr * 1.0, feet), (cx + hr * 0.2, feet), (cx, feet - hgt * 0.3),
               (cx - hr * 0.2, feet), (cx - hr, feet)], fill=col, outline=outline)
    for s in (-1, 1):
        d.line([(cx + s * hr * 1.5, hy + hr * 1.5), (cx + s * hr * 1.9, feet - hgt * 0.38)], fill=col, width=int(hr * 0.55))
    if eyes:
        for s in (-1, 1):
            ex = cx + s * hr * 0.38
            d.polygon([(ex - hr * 0.26, hy - hr * 0.05), (ex + hr * 0.26, hy - hr * 0.05 - s * hr * 0.08),
                       (ex, hy + hr * 0.12)], fill=WHITE)

def eyes_dark(d, S, cx, cy, size, slant=True, col=WHITE, pupils=True):
    for s in (-1, 1):
        ex = cx + s * size * 1.25
        if slant:
            d.polygon([(ex - size, cy - s * size * 0.15), (ex + size, cy + s * size * 0.15),
                       (ex + size * 0.5, cy + size * 0.42), (ex - size * 0.6, cy + size * 0.32)], fill=col)
        else:
            d.ellipse([ex - size, cy - size * 0.55, ex + size, cy + size * 0.55], fill=col)
        if pupils:
            d.ellipse([ex - size * 0.18, cy - size * 0.05, ex + size * 0.18, cy + size * 0.3], fill=(0, 0, 0))

def coach(d, S, w, h):
    vx, vy = w * 0.5, h * 0.42
    d.polygon([(0, h), (w, h), (vx + 90 * S, vy + 60 * S), (vx - 90 * S, vy + 60 * S)], fill=(28, 30, 36))  # floor
    d.polygon([(0, 0), (w, 0), (vx + 90 * S, vy - 70 * S), (vx - 90 * S, vy - 70 * S)], fill=(40, 43, 52))  # ceiling
    d.rectangle([vx - 90 * S, vy - 70 * S, vx + 90 * S, vy + 60 * S], fill=(12, 12, 16), outline=INK, width=3 * S)  # end door
    for side in (-1, 1):  # walls with windows
        x_out = 0 if side < 0 else w
        x_in = vx + side * 90 * S
        d.polygon([(x_out, 0), (x_in, vy - 70 * S), (x_in, vy + 60 * S), (x_out, h)], fill=(34, 37, 46), outline=INK)
        for i in range(4):
            f0, f1 = i / 4.0, i / 4.0 + 0.16
            def at(f, yo, yi):
                return (x_out + (x_in - x_out) * f, yo + (yi - yo) * f)
            q = [at(f0, h * 0.18, vy - 40 * S), at(f1, h * 0.18, vy - 40 * S), at(f1, h * 0.45, vy + 5 * S), at(f0, h * 0.45, vy + 5 * S)]
            d.polygon(q, fill=(4, 4, 6), outline=INK)
            sq = [at(f0, h * 0.62, vy + 25 * S), at(f1 + 0.06, h * 0.62, vy + 25 * S), at(f1 + 0.06, h * 0.78, vy + 45 * S), at(f0, h * 0.78, vy + 45 * S)]
            d.polygon(sq, fill=(70, 80, 100), outline=INK)  # seats
    for i in range(3):  # tube lights
        f = i / 3.2; y = 0 + (vy - 70 * S) * f; half = (w / 2) * (1 - f) * 0.35
        d.rectangle([vx - half, y + 20 * S, vx + half, y + 34 * S * (1 - f) + 22 * S], fill=(225, 230, 210))
    for i, f in enumerate((0.15, 0.45)):  # poles + handles
        for side in (-1, 1):
            x = vx + side * (w * 0.32) * (1 - f)
            d.line([(x, (vy - 70 * S) * f + 10 * S), (x, h - (h - vy - 60 * S) * f)], fill=(170, 170, 180), width=int(8 * S * (1 - f)))
    return vx, vy

def paper(d, S, w, h, x0, y0, x1, y1):
    d.polygon([(x0, y0 + 20 * S), (x1, y0), (x1 + 10 * S, y1), (x0 - 10 * S, y1 + 15 * S)], fill=(205, 198, 175), outline=INK)
    d.rectangle([x0 + 30 * S, y0 + 40 * S, x1 - 30 * S, y0 + 130 * S], fill=(30, 28, 26))
    for i in range(6):
        y = y0 + 170 * S + i * 34 * S
        if y < y1 - 30 * S: d.line([(x0 + 40 * S, y), (x0 + (x1 - x0) * 0.45, y)], fill=(120, 115, 100), width=6 * S)

def scene_img(k):
    img, S = canvas(); d = ImageDraw.Draw(img); w, h = PW * S, PH * S
    if k in (0, 1):
        coach(d, S, w, h)
        if k == 0:  # red emergency chain + hand pulling
            d.rectangle([w * 0.10, h * 0.10, w * 0.90, h * 0.16], fill=(60, 62, 70), outline=INK, width=4 * S)
            d.line([(w * 0.55, h * 0.16), (w * 0.55, h * 0.55)], fill=RED, width=12 * S)
            d.rectangle([w * 0.50, h * 0.50, w * 0.60, h * 0.58], fill=RED, outline=INK, width=4 * S)
            d.ellipse([w * 0.46, h * 0.55, w * 0.64, h * 0.66], fill=(205, 200, 195), outline=INK, width=4 * S)
            d.polygon([(w * 0.47, h * 0.64), (w * 0.63, h * 0.64), (w * 0.70, h), (w * 0.40, h)], fill=(200, 200, 208), outline=INK)
            d.text((w * 0.80, h * 0.22), "EMERGENCY", font=font(FB, 40 * S), fill=RED, anchor="mm")
        else:  # lights out: dark coach + red silhouette at the end
            arr = np.asarray(img).astype(np.float32) * 0.25
            img = Image.fromarray(arr.astype(np.uint8)); d = ImageDraw.Draw(img)
            d.polygon([(w * 0.47, h * 0.62), (w * 0.53, h * 0.62), (w * 0.55, h * 0.40), (w * 0.45, h * 0.40)], fill=(150, 18, 28))
            d.ellipse([w * 0.47, h * 0.34, w * 0.53, h * 0.41], fill=(10, 10, 12))
    elif k == 2:  # ICU monitor
        img, S = canvas((20, 26, 30), (6, 8, 10)); d = ImageDraw.Draw(img)
        d.rounded_rectangle([w * 0.10, h * 0.18, w * 0.90, h * 0.66], radius=30 * S, fill=(4, 10, 8), outline=(140, 150, 150), width=10 * S)
        for i in range(1, 6):
            d.line([(w * 0.12, h * (0.18 + i * 0.08)), (w * 0.88, h * (0.18 + i * 0.08))], fill=(10, 40, 26), width=2 * S)
        d.rectangle([w * 0.42, h * 0.66, w * 0.58, h * 0.80], fill=(90, 96, 104))
        d.line([(w * 0.5, h * 0.80), (w * 0.5, h)], fill=(90, 96, 104), width=14 * S)
        return finish(img, S, ht=False)
    elif k == 3:  # POV from hospital bed: Maa crying (generic figure in shawl)
        img, S = canvas((210, 214, 216), (150, 156, 160)); d = ImageDraw.Draw(img)
        d.rectangle([0, h * 0.78, w, h], fill=(225, 228, 230), outline=INK, width=4 * S)  # blanket edge
        cx = w * 0.50
        d.polygon([(cx - 260 * S, h * 0.80), (cx + 260 * S, h * 0.80), (cx + 180 * S, h * 0.38), (cx - 180 * S, h * 0.38)], fill=(120, 60, 110), outline=INK)
        d.ellipse([cx - 120 * S, h * 0.14, cx + 120 * S, h * 0.44], fill=(190, 150, 120), outline=INK, width=5 * S)
        d.chord([cx - 140 * S, h * 0.10, cx + 140 * S, h * 0.40], 180, 360, fill=(120, 60, 110))
        for s_ in (-1, 1):
            ex = cx + s_ * 45 * S
            d.arc([ex - 30 * S, h * 0.27, ex + 30 * S, h * 0.31], 200, 340, fill=(30, 20, 20), width=6 * S)
            d.ellipse([ex - 8 * S, h * 0.32, ex + 8 * S, h * 0.35], fill=(120, 170, 230))
        d.arc([cx - 40 * S, h * 0.36, cx + 40 * S, h * 0.40], 200, 340, fill=(60, 30, 30), width=6 * S)
    elif k == 4:  # nurse wrist with red bangles holding a pill cup
        img, S = canvas((200, 206, 210), (140, 146, 150)); d = ImageDraw.Draw(img)
        d.polygon([(0, h * 0.70), (w * 0.62, h * 0.48), (w * 0.70, h * 0.62), (0, h * 0.90)], fill=(240, 240, 242), outline=INK)  # white sleeve
        d.polygon([(w * 0.60, h * 0.48), (w * 0.82, h * 0.40), (w * 0.88, h * 0.52), (w * 0.68, h * 0.62)], fill=(120, 90, 80), outline=INK)  # dark wrist
        for i in range(4):
            x = w * (0.64 + i * 0.03)
            d.ellipse([x - 14 * S, h * 0.42 + i * 6 * S, x + 14 * S, h * 0.60 - i * 4 * S], outline=RED, width=10 * S)
        d.polygon([(w * 0.84, h * 0.36), (w * 0.96, h * 0.36), (w * 0.94, h * 0.50), (w * 0.86, h * 0.50)], fill=(250, 250, 250), outline=INK)
        for i in range(3):
            d.ellipse([w * (0.87 + i * 0.025), h * 0.37, w * (0.89 + i * 0.025), h * 0.39], fill=RED)
    elif k == 5:  # nurse leaving through the ICU door, red saree hem under white coat
        img, S = canvas((190, 196, 200), (120, 126, 130)); d = ImageDraw.Draw(img)
        d.rectangle([w * 0.30, h * 0.08, w * 0.70, h * 0.90], fill=(60, 66, 74), outline=INK, width=8 * S)
        d.rectangle([w * 0.36, h * 0.14, w * 0.64, h * 0.36], fill=(20, 22, 26))
        d.text((w * 0.5, h * 0.05), "ICU", font=font(FB, 60 * S), fill=RED, anchor="mm")
        cx = w * 0.5
        d.polygon([(cx - 90 * S, h * 0.84), (cx + 90 * S, h * 0.84), (cx + 70 * S, h * 0.42), (cx - 70 * S, h * 0.42)], fill=(240, 240, 242), outline=INK)
        d.polygon([(cx - 100 * S, h * 0.84), (cx + 100 * S, h * 0.84), (cx + 90 * S, h * 0.92), (cx - 90 * S, h * 0.92)], fill=(160, 18, 30), outline=INK)
        d.ellipse([cx - 45 * S, h * 0.30, cx + 45 * S, h * 0.42], fill=(10, 10, 12), outline=INK, width=4 * S)
    return finish(img, S)

# ---------- per-frame compositing ----------
def build_frame_fn(segs):
    scenes = [np.asarray(scene_img(k)) for k in range(6)]
    starts = {}
    for i, (a, b) in enumerate(segs):
        sc = SCENE_OF[i]
        if sc not in starts: starts[sc] = a if i else 0.0
    order = sorted(starts.items(), key=lambda kv: kv[1])
    end = segs[-1][1]
    T_END = end + 2.6
    fB, fS, fM, fT = font(FB, 74), font(FX, 34), font(FM, 40), font(FB, 96)
    rng = np.random.default_rng(7)
    noise = [rng.integers(0, 40, (H // 2, W // 2), dtype=np.uint8) for _ in range(6)]
    scan = np.ones((H, W, 1), np.float32); scan[::4] = 0.82
    yy, xx = np.mgrid[0:H, 0:W]
    vig = (1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)).clip(0.25, 1)[..., None].astype(np.float32)

    def scene_at(t):
        cur, t0 = order[0]
        for sc, st in order:
            if t >= st: cur, t0 = sc, st
        nxt = [st for sc, st in order if st > t0]
        t1 = nxt[0] if nxt else T_END
        return cur, t0, t1

    def cap_at(t):
        for i, (a, b) in enumerate(segs):
            nb = segs[i + 1][0] if i + 1 < len(segs) else b + 0.6
            if a <= t < max(b, nb): return i, t - a
        return None, 0

    def draw_caption(base, text, age):
        d = ImageDraw.Draw(base)
        words = text.split(); lines, cur = [], ""
        for wd in words:
            test = (cur + " " + wd).strip()
            if d.textlength(test, font=fB) > 860 and cur: lines.append(cur); cur = wd
            else: cur = test
        lines.append(cur)
        lh = 92; bh = lh * len(lines) + 50; by = 1420
        pop = min(1, age / 0.12); sc = 0.9 + 0.1 * pop
        bw = 940
        box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.rectangle([0, 0, bw - 1, bh - 1], fill=(8, 8, 10, 235), outline=RED + (255,), width=6)
        for li, ln in enumerate(lines):
            x = (bw - bd.textlength(ln, font=fB)) / 2; y = 25 + li * lh
            for wd in ln.split(" "):
                c = RED if wd in HOT else WHITE
                bd.text((x + 4, y + 4), wd, font=fB, fill=(0, 0, 0, 255))
                bd.text((x, y), wd, font=fB, fill=c + (255,))
                x += bd.textlength(wd + " ", font=fB)
        if sc < 1: box = box.resize((int(bw * sc), int(bh * sc)), Image.BILINEAR)
        base.paste(box, ((W - box.width) // 2, by + (bh - box.height) // 2), box)

    def frame(t):
        sc, t0, t1 = scene_at(t)
        loc = t - t0; dur = max(0.1, t1 - t0)
        img = scenes[sc]
        z = 1.0 + 0.10 * (loc / dur) + (0.10 if sc in (4, 5) else 0) * (loc / dur)
        if sc == 7: z = 1.0 + 0.02 * math.sin(loc * 30) * (loc < 0.3)
        cw, ch = int(PW / z), int(PH / z)
        ox, oy = (PW - cw) // 2, (PH - ch) // 2
        if sc in (0, 1):  # shake
            ox += int(6 * math.sin(loc * 37)); oy += int(5 * math.cos(loc * 29))
            ox = max(0, min(PW - cw, ox)); oy = max(0, min(PH - ch, oy))
        crop = cv2.resize(img[oy:oy + ch, ox:ox + cw], (PW, PH), interpolation=cv2.INTER_LINEAR)
        out = np.zeros((H, W, 3), np.uint8); out[:] = BG
        out[PY0:PY1, PX0:PX1] = crop
        pil = Image.fromarray(out); d = ImageDraw.Draw(pil)
        # dynamic overlays inside panel
        if sc == 0 and loc > 0.8:
            d.text((PX0 + PW * 0.5, PY0 + PH * 0.88), "SCREEEECH!", font=font(FB, 80), fill=RED, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
        if sc == 1 and loc > 0.9:
            d.text((PX0 + PW * 0.5, PY0 + PH * 0.20), "ROHAN!", font=font(FB, 110), fill=RED, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
        if sc == 2:  # ECG line, beeping
            pts = []
            for i in range(120):
                x = PX0 + PW * (0.12 + 0.76 * i / 119)
                ph = (i / 119 * 4 - t * 1.2) % 1.0
                y = PY0 + PH * 0.42 - (180 if 0.45 < ph < 0.48 else (-60 if 0.48 < ph < 0.51 else 0))
                pts.append((x, y))
            d.line(pts, fill=(60, 255, 120), width=6)
            d.text((PX0 + PW * 0.80, PY0 + PH * 0.24), "72", font=font(FB, 90), fill=(60, 255, 120), anchor="mm")
            if int(t * 1.2 * 2) % 2 == 0:
                d.text((PX0 + PW * 0.30, PY0 + PH * 0.24), "BEEP", font=font(FB, 60), fill=(60, 255, 120), anchor="mm")
        if sc == 5 and loc > 1.0:
            d.text((PX0 + PW * 0.5, PY0 + PH * 0.96), "shhh...", font=font(FX, 50), fill=RED, anchor="mm")
        # CCTV HUD
        d.rectangle([PX0 - 6, PY0 - 6, PX1 + 6, PY1 + 6], outline=(60, 64, 76), width=4)
        tw = d.textlength(SERIES, font=font(FB, 44))
        d.rectangle([PX0 - 6, PY0 - 76, PX0 + tw + 34, PY0 - 6], fill=RED)
        d.text((PX0 + 14, PY0 - 41), SERIES, font=font(FB, 44), fill=WHITE, anchor="lm")
        d.text((PX1, PY0 - 41), "SUSPENSE", font=fS, fill=(150, 150, 160), anchor="rm")
        if sc in STAMP:
            st, tag = STAMP[sc]
            secs = int(st[-2:]) + int(loc)
            d.text((PX0 + 24, PY0 + 22), "COACH 7" if sc < 2 else "ICU BED 7", font=fM, fill=WHITE)
            d.text((PX1 - 24, PY0 + 22), st[:-2] + "%02d" % (secs % 60), font=fM, fill=WHITE, anchor="ra")
            if int(t * 2) % 2 == 0:
                tx = PX1 - 24 - d.textlength(tag, font=fM) - 40
                d.ellipse([tx, PY0 + 82, tx + 24, PY0 + 106], fill=RED)
            d.text((PX1 - 24, PY0 + 74), tag, font=fM, fill=RED, anchor="ra")
        # caption
        ci, age = cap_at(t)
        if ci is not None and t < segs[-1][1] + 0.5:
            draw_caption(pil, CAPS[ci], age)
        # end card
        if t >= segs[-1][1] + 0.5:
            e = min(1, (t - segs[-1][1] - 0.5) / 0.4)
            d.rectangle([0, 0, W, H], fill=(0, 0, 0))
            cx, cy = W / 2, 760
            for s in (-1, 1):
                ex = cx + s * 110
                d.polygon([(ex - 80, cy - s * 12), (ex + 80, cy + s * 12), (ex + 40, cy + 26), (ex - 46, cy + 20)], fill=WHITE)
            d.text((W / 2, 1150), "THE END...?", font=fT, fill=tuple(int(c * e) for c in RED), anchor="mm")
            d.text((W / 2, 1290), "NAYI KAHANI KAL SUBAH", font=font(FX, 54), fill=tuple(int(c * e) for c in WHITE), anchor="mm")
        arr = np.asarray(pil).astype(np.float32)
        # grain + scanlines + vignette
        nz = cv2.resize(noise[int(t * FPS) % 6], (W, H), interpolation=cv2.INTER_NEAREST)[..., None].astype(np.float32)
        arr = (arr * scan * vig + nz * 0.35 - 6).clip(0, 255)
        # glitch at scene cuts
        if loc < 0.16 and t > 0.2:
            sh = 22
            arr[..., 0] = np.roll(arr[..., 0], sh, axis=1); arr[..., 2] = np.roll(arr[..., 2], -sh, axis=1)
            y0 = random.randint(200, 1600); arr[y0:y0 + 60] = np.roll(arr[y0:y0 + 60], 60, axis=1)
            arr = (arr * 1.15).clip(0, 255)
        return arr.astype(np.uint8)
    return frame, T_END

def main():
    audio, subs, out = sys.argv[1:4]
    segs = srt(subs)
    frame, T_END = build_frame_fn(segs)
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            Image.fromarray(frame(float(ts))).save(f"{out}_{ts}.jpg", quality=88)
        return
    n = int(T_END * FPS)
    tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio,
                          "-filter_complex", f"[1:a]atempo={TEMPO},apad[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-maxrate", "5M", "-bufsize", "10M", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", tmp],
                         stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        import os; os.replace(tmp, out); print("ok", n / FPS)

if __name__ == "__main__":
    main()
