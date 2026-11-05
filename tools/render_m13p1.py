"""Render '13vi Manzil' Part 1 reel: CCTV / dark comic style, 1080x1920, 30fps.
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

SERIES = "13VI MANZIL"
CAPS = ["HAMARI BUILDING MEIN SIRF 12 FLOOR HAIN...", "PHIR LIFT MEIN 13 KAISE JAL RAHA HAI?",
        "RAAT KE 2:40.", "MAIN NIGHT SHIFT SE LAUTI THI.",
        "MAINE 7 DABAAYA...", "PAR LIFT RUKI HI NAHI...", "8... 10... 12...", "AUR PHIR... 13. TING!",
        "DARWAAZA KHULA...", "BILKUL MERE FLOOR JAISA GALIYAARA.",
        "PAR HAR NAMEPLATE PAR EK HI NAAM THA...", "NEHA.",
        "1303 KA DARWAAZA KHULA THA...", "ANDAR KOI MERE BISTAR PAR BAITHA THA.",
        "USNE MUDKAR DEKHA...", "USKA CHEHRA... MERA THA.",
        "BADI DER KAR DI, NEHA...", "AB TUMHARI BAARI HAI."]
HOT = {"12", "13", "2:40.", "7", "RUKI", "NAHI...", "13.", "TING!", "GALIYAARA.", "NEHA.", "1303", "BISTAR",
       "CHEHRA...", "MERA", "THA.", "NEHA...", "BAARI"}
SCENE_OF = [0, 0, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 5, 5]
STAMP = {0: ("02:40:11", "LIVE"), 1: ("02:40:14", "LIVE"), 2: ("02:40:31", "LIVE"), 3: ("02:41:05", "REC"),
         4: ("02:41:22", "REC"), 5: ("02:41:40", "REC")}

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

def woman(d, S, cx, top, sc=1.0, face=(190, 150, 120), kurti=(30, 110, 120), back=False):
    r = 70 * S * sc
    d.polygon([(cx - r * 1.25, top + r * 0.2), (cx + r * 1.25, top + r * 0.2), (cx + r * 1.5, top + r * 4.2), (cx - r * 1.5, top + r * 4.2)], fill=(8, 8, 10))  # long hair
    d.polygon([(cx - r * 1.9, top + r * 2.2), (cx + r * 1.9, top + r * 2.2), (cx + r * 2.4, top + r * 8), (cx - r * 2.4, top + r * 8)], fill=kurti, outline=INK)
    if not back:
        d.ellipse([cx - r, top, cx + r, top + r * 2.3], fill=face, outline=INK, width=3 * S)
        d.chord([cx - r * 1.1, top - r * 0.15, cx + r * 1.1, top + r * 1.3], 180, 360, fill=(8, 8, 10))
    else:
        d.ellipse([cx - r * 1.1, top - r * 0.1, cx + r * 1.1, top + r * 2.3], fill=(8, 8, 10), outline=INK, width=2 * S)

def lift_panel(d, S, w, h, hand=False):
    d.rectangle([w * 0.22, h * 0.02, w * 0.78, h * 0.98], fill=(120, 126, 136), outline=INK, width=6 * S)
    for i in range(12):
        d.line([(w * (0.24 + i * 0.045), h * 0.02), (w * (0.22 + i * 0.045), h * 0.98)], fill=(132, 138, 148), width=3 * S)
    d.rectangle([w * 0.32, h * 0.06, w * 0.68, h * 0.17], fill=(6, 4, 4), outline=INK, width=4 * S)
    labels = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]
    fnt = font(FB, 44 * S)
    for r, (a, b) in enumerate(labels):
        y = h * (0.92 - r * 0.10)
        for x, n in ((w * 0.40, a), (w * 0.60, b)):
            d.ellipse([x - 52 * S, y - 52 * S, x + 52 * S, y + 52 * S], fill=(170, 176, 186), outline=(40, 42, 48), width=6 * S)
            d.text((x, y), str(n), font=fnt, fill=(40, 42, 50), anchor="mm")
    y = h * 0.92 - 6 * h * 0.10 - h * 0.01; x = w * 0.5
    for g in range(6, 0, -1):
        d.ellipse([x - (52 + g * 7) * S, y - (52 + g * 7) * S, x + (52 + g * 7) * S, y + (52 + g * 7) * S], fill=(120 + g * 12, 30, 34))
    d.ellipse([x - 52 * S, y - 52 * S, x + 52 * S, y + 52 * S], fill=RED, outline=(255, 150, 150), width=6 * S)
    d.text((x, y), "13", font=fnt, fill=WHITE, anchor="mm")
    if hand:  # dark thin hand with long nails pressing 13
        hx, hy = x + 30 * S, y + 30 * S
        d.polygon([(w * 1.02, h * 0.78), (hx + 40 * S, hy + 10 * S), (hx + 10 * S, hy + 60 * S), (w * 1.02, h * 0.92)], fill=(14, 14, 16), outline=INK)
        d.ellipse([hx - 30 * S, hy - 10 * S, hx + 70 * S, hy + 80 * S], fill=(14, 14, 16), outline=INK, width=3 * S)
        for k, (dx, dy) in enumerate(((-70, -55), (-80, -15), (-70, 25), (-45, 60))):
            fx, fy = hx + dx * S, hy + dy * S
            d.line([(hx + 10 * S, hy + 20 * S + k * 8 * S), (fx, fy)], fill=(14, 14, 16), width=16 * S)
            d.line([(fx, fy), (fx - 22 * S, fy - 6 * S)], fill=RED, width=9 * S)

def lift_box(d, S, w, h):
    d.polygon([(0, 0), (w, 0), (w * 0.82, h * 0.12), (w * 0.18, h * 0.12)], fill=(60, 64, 72))
    d.rectangle([w * 0.18, h * 0.12, w * 0.82, h * 0.86], fill=(96, 100, 110), outline=INK, width=4 * S)
    d.polygon([(0, 0), (w * 0.18, h * 0.12), (w * 0.18, h * 0.86), (0, h)], fill=(76, 80, 90), outline=INK)
    d.polygon([(w, 0), (w * 0.82, h * 0.12), (w * 0.82, h * 0.86), (w, h)], fill=(76, 80, 90), outline=INK)
    d.polygon([(0, h), (w, h), (w * 0.82, h * 0.86), (w * 0.18, h * 0.86)], fill=(40, 42, 48))
    d.rectangle([w * 0.36, h * 0.03, w * 0.64, h * 0.06], fill=(235, 238, 220))

def corridor(d, S, w, h):
    vx, vy = w * 0.5, h * 0.45
    d.polygon([(0, h), (w, h), (vx + 70 * S, vy + 70 * S), (vx - 70 * S, vy + 70 * S)], fill=(34, 32, 30))
    d.polygon([(0, 0), (w, 0), (vx + 70 * S, vy - 80 * S), (vx - 70 * S, vy - 80 * S)], fill=(44, 46, 52))
    d.rectangle([vx - 70 * S, vy - 80 * S, vx + 70 * S, vy + 70 * S], fill=(2, 2, 3))
    for side in (-1, 1):
        x_out = 0 if side < 0 else w; x_in = vx + side * 70 * S
        d.polygon([(x_out, 0), (x_in, vy - 80 * S), (x_in, vy + 70 * S), (x_out, h)], fill=(70, 66, 58), outline=INK)
        for i in range(3):
            f0 = 0.08 + i * 0.30; f1 = f0 + 0.17
            at = lambda f, yo, yi: (x_out + (x_in - x_out) * f, yo + (yi - yo) * f)
            q = [at(f0, h * 0.22, vy - 50 * S), at(f1, h * 0.22, vy - 50 * S), at(f1, h * 0.95, vy + 68 * S), at(f0, h * 0.95, vy + 68 * S)]
            d.polygon(q, fill=(52, 34, 26), outline=INK)
            fm = (f0 + f1) / 2; p = at(fm, h * 0.33, vy - 35 * S); s = 1 - fm * 0.85
            d.rectangle([p[0] - 70 * S * s, p[1] - 22 * S * s, p[0] + 70 * S * s, p[1] + 22 * S * s], fill=(200, 190, 160), outline=INK)
            d.text(p, "NEHA", font=font(FB, max(8, int(30 * S * s))), fill=(150, 10, 20), anchor="mm")
    d.rectangle([vx - 220 * S, 40 * S, vx + 220 * S, 62 * S], fill=(225, 228, 210))
    return vx, vy

def scene_img(k):
    img, S = canvas(); d = ImageDraw.Draw(img); w, h = PW * S, PH * S
    if k in (0, 2):
        img, S = canvas((70, 74, 82), (24, 26, 30)); d = ImageDraw.Draw(img)
        lift_panel(d, S, w, h, hand=(k == 0))
    elif k == 1:
        lift_box(d, S, w, h)
        woman(d, S, w * 0.5, h * 0.30, 1.25)
        cx = w * 0.5
        for s_ in (-1, 1):
            d.ellipse([cx + s_ * 34 * S - 12 * S, h * 0.30 + 95 * S, cx + s_ * 34 * S + 12 * S, h * 0.30 + 108 * S], fill=(30, 20, 20))
        d.line([(cx - 60 * S, h * 0.43), (cx, h * 0.55), (cx + 60 * S, h * 0.43)], fill=RED, width=5 * S)
        d.rectangle([cx - 40 * S, h * 0.55, cx + 40 * S, h * 0.61], fill=WHITE, outline=INK, width=3 * S)
        d.rectangle([w * 0.62, h * 0.50, w * 0.80, h * 0.70], fill=(40, 30, 26), outline=INK, width=4 * S)  # bag
    elif k == 3:
        corridor(d, S, w, h)
    elif k == 4:
        img, S = canvas((10, 12, 18), (4, 4, 6)); d = ImageDraw.Draw(img)
        d.polygon([(w * 0.18, h * 0.05), (w * 0.82, h * 0.05), (w * 0.82, h * 0.98), (w * 0.18, h * 0.98)], fill=(20, 22, 30))
        d.rectangle([w * 0.58, h * 0.14, w * 0.78, h * 0.36], fill=(60, 72, 98), outline=INK, width=3 * S)  # window
        d.rectangle([w * 0.22, h * 0.62, w * 0.80, h * 0.74], fill=(70, 74, 90), outline=INK, width=4 * S)  # bed
        d.rectangle([w * 0.22, h * 0.74, w * 0.80, h * 0.80], fill=(30, 32, 40), outline=INK, width=4 * S)
        woman(d, S, w * 0.50, h * 0.40, 0.9, kurti=(30, 110, 120), back=True)
        d.polygon([(0, 0), (w * 0.18, h * 0.05), (w * 0.18, h * 0.98), (0, h)], fill=(52, 34, 26), outline=INK)  # door ajar
        d.polygon([(w, 0), (w * 0.82, h * 0.05), (w * 0.82, h * 0.98), (w, h)], fill=(70, 66, 58), outline=INK)
        d.rectangle([w * 0.02, h * 0.20, w * 0.15, h * 0.26], fill=(200, 190, 160), outline=INK)
        d.text((w * 0.085, h * 0.23), "1303", font=font(FB, 34 * S), fill=(150, 10, 20), anchor="mm")
    elif k == 5:  # her own face, but wrong: white eyes, too-wide smile
        img, S = canvas((90, 22, 26), (18, 4, 6)); d = ImageDraw.Draw(img)
        cx = w * 0.5
        d.polygon([(cx - 360 * S, h * 0.10), (cx + 360 * S, h * 0.10), (cx + 440 * S, h), (cx - 440 * S, h)], fill=(6, 6, 8))
        d.ellipse([cx - 270 * S, h * 0.14, cx + 270 * S, h * 0.80], fill=(196, 172, 160), outline=INK, width=6 * S)
        d.chord([cx - 300 * S, h * 0.08, cx + 300 * S, h * 0.46], 180, 360, fill=(6, 6, 8))
        d.polygon([(cx - 280 * S, h * 0.28), (cx - 120 * S, h * 0.24), (cx - 270 * S, h * 0.62)], fill=(6, 6, 8))
        eyes_dark(d, S, cx, h * 0.44, 70 * S, slant=False, col=(245, 245, 240), pupils=False)
        d.ellipse([cx - 14 * S, h * 0.36, cx + 14 * S, h * 0.385], fill=RED)  # bindi
        d.chord([cx - 170 * S, h * 0.52, cx + 170 * S, h * 0.70], 0, 180, fill=(40, 6, 8), outline=INK, width=5 * S)
        for i in range(9):
            x = cx - 150 * S + i * 37 * S
            d.rectangle([x, h * 0.61, x + 26 * S, h * 0.64], fill=(230, 226, 210))
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
    fBn, fS, fM, fT = font(FB, 74), font(FX, 34), font(FM, 40), font(FB, 96)
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

    def draw_caption(base, text, age, big=False):
        d = ImageDraw.Draw(base)
        fB = font(FB, 92) if big else fBn
        words = text.split(); lines, cur = [], ""
        for wd in words:
            test = (cur + " " + wd).strip()
            if d.textlength(test, font=fB) > 860 and cur: lines.append(cur); cur = wd
            else: cur = test
        lines.append(cur)
        lh = 112 if big else 92; bh = lh * len(lines) + 50; by = 1420
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
        z = 1.0 + 0.10 * (loc / dur) + (0.15 if sc == 5 else 0) * (loc / dur)
        if sc == 7: z = 1.0 + 0.02 * math.sin(loc * 30) * (loc < 0.3)
        cw, ch = int(PW / z), int(PH / z)
        ox, oy = (PW - cw) // 2, (PH - ch) // 2
        if sc in (2, 5):  # shake
            ox += int(6 * math.sin(loc * 37)); oy += int(5 * math.cos(loc * 29))
            ox = max(0, min(PW - cw, ox)); oy = max(0, min(PH - ch, oy))
        crop = cv2.resize(img[oy:oy + ch, ox:ox + cw], (PW, PH), interpolation=cv2.INTER_LINEAR)
        out = np.zeros((H, W, 3), np.uint8); out[:] = BG
        out[PY0:PY1, PX0:PX1] = crop
        pil = Image.fromarray(out); d = ImageDraw.Draw(pil)
        # dynamic overlays inside panel
        if sc in (0, 2):
            if sc == 0: num, col = ("13" if int(t * 3) % 2 == 0 else ""), RED
            else:
                fl = [7, 8, 9, 10, 11, 12, 13][min(6, int(7 * loc / (dur * 0.85)))]; num, col = str(fl), (RED if fl == 13 else (255, 170, 40))
            d.text((PX0 + PW * 0.5, PY0 + PH * 0.115), num, font=font(FM, 120), fill=col, anchor="mm")
        if sc == 2 and loc > dur * 0.85:
            d.text((PX0 + PW * 0.5, PY0 + PH * 0.50), "TING!", font=font(FB, 130), fill=RED, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
        if sc == 3 and int(t * 9) % 11 == 0:
            d.rectangle([PX0, PY0, PX1, PY1], fill=(0, 0, 0))  # tube light flicker
        if sc == 5 and loc > 1.4 and int(t * 10) % 3 == 0:
            d.text((PX0 + PW * 0.5, PY0 + PH * 0.92), "NEHA...", font=font(FB, 90), fill=RED, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
        # CCTV HUD
        d.rectangle([PX0 - 6, PY0 - 6, PX1 + 6, PY1 + 6], outline=(60, 64, 76), width=4)
        tw = d.textlength(SERIES, font=font(FB, 44))
        d.rectangle([PX0 - 6, PY0 - 76, PX0 + tw + 34, PY0 - 6], fill=RED)
        d.text((PX0 + 14, PY0 - 41), SERIES, font=font(FB, 44), fill=WHITE, anchor="lm")
        d.text((PX1, PY0 - 41), "SUSPENSE", font=fS, fill=(150, 150, 160), anchor="rm")
        if sc in STAMP:
            st, tag = STAMP[sc]
            secs = int(st[-2:]) + int(loc)
            d.text((PX0 + 24, PY0 + 22), "LIFT CAM-1" if sc < 3 else "FLOOR 13", font=fM, fill=WHITE)
            d.text((PX1 - 24, PY0 + 22), st[:-2] + "%02d" % (secs % 60), font=fM, fill=WHITE, anchor="ra")
            if int(t * 2) % 2 == 0:
                tx = PX1 - 24 - d.textlength(tag, font=fM) - 40
                d.ellipse([tx, PY0 + 82, tx + 24, PY0 + 106], fill=RED)
            d.text((PX1 - 24, PY0 + 74), tag, font=fM, fill=RED, anchor="ra")
        # caption
        ci, age = cap_at(t)
        if ci is not None and t < segs[-1][1] + 0.5:
            draw_caption(pil, CAPS[ci], age, big=(ci == 0))
        # end card
        if t >= segs[-1][1] + 0.5:
            e = min(1, (t - segs[-1][1] - 0.5) / 0.4)
            d.rectangle([0, 0, W, H], fill=(0, 0, 0))
            cx, cy = W / 2, 760
            for s in (-1, 1):
                ex = cx + s * 110
                d.polygon([(ex - 80, cy - s * 12), (ex + 80, cy + s * 12), (ex + 40, cy + 26), (ex - 46, cy + 20)], fill=WHITE)
            d.text((W / 2, 1150), "TO BE CONTINUED...", font=font(FB, 84), fill=tuple(int(c * e) for c in RED), anchor="mm")
            d.text((W / 2, 1290), "PART 2 AAJ RAAT", font=font(FX, 54), fill=tuple(int(c * e) for c in WHITE), anchor="mm")
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
