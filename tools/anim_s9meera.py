"""Standalone story 'MEERA' (love story: wrong-number love turns out to be the bride, who planned it all) -
procedural ink-wash animation.  python3 anim_s9meera.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FH = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
FPS = 30
END_CARD = 2.8
TITLE = "MEERA"

CAPS = ["PHERON SE 5 MINUT PEHLE...", "DULHAN KE PHONE PE MERA MESSAGE CHAMKA!",
        "6 MAHINE SE EK WRONG NUMBER PE", "'MEERA' SE RAAT BHAR BAATEIN KARTA THA", "HUM KABHI MILE NAHI",
        "GHARWALON NE MERI SHAADI KAVYA SE TAY KAR DI", "AAJ MEERA KO AAKHRI MESSAGE BHEJA...", "BAS EK BAAR MIL LO",
        "AUR WO MESSAGE... MERI DULHAN KE PHONE PE AAYA", "MERA DIL RUK GAYA",
        "KAVYA NE GHOONGHAT MEIN PHONE DEKHA...", "AUR DHEERE SE BOLI...", "MEERA MERA GHAR KA NAAM HAI",
        "AUR WO WRONG NUMBER... GALTI SE NAHI LAGA THA", "3 SAAL SE TUMHE COLLEGE BUS MEIN DEKHTI THI...",
        "YE RISHTA BHI MAINE HI BHIJWAYA THA"]
HOT = {"5", "DULHAN", "MESSAGE", "WRONG", "NUMBER", "MEERA", "KAVYA", "AAKHRI", "RUK", "GALTI", "NAHI", "3", "SAAL", "RISHTA", "MAINE"}
SCENE_OF = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 6]
PAPER = paper(seed=31)
yy, xx = np.mgrid[0:H, 0:W]

def text(img, s, xy, size, col, anchor="mm", stroke=6, font=FB, rot=0):
    if rot == 0:
        pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(pil)
        d.text(xy, s, font=ImageFont.truetype(font, size), fill=tuple(int(min(255, c)) for c in col), anchor=anchor,
               stroke_width=stroke, stroke_fill=(10, 10, 12))
        return np.asarray(pil).astype(np.float32)
    # rotated text via alpha mask
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.text(xy, s, font=ImageFont.truetype(font, size), fill=255, anchor=anchor)
    m = m.rotate(rot, center=xy, resample=Image.BICUBIC)
    a = (np.asarray(m).astype(np.float32) / 255)[..., None]
    return img * (1 - a) + np.float32(col) * a

def zoom(img, z, cx=W / 2, cy=H / 2, dx=0, dy=0, rot=0):
    M = cv2.getRotationMatrix2D((cx, cy), rot, z); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(np.float32(img), M, (W, H), borderMode=cv2.BORDER_REFLECT)

_GL = {}
def glow(img, cx, cy, r, col, amt):
    key = (int(cx), int(cy), int(r))
    if len(_GL) > 120: _GL.clear()
    if key not in _GL:
        g = np.zeros((H // 8, W // 8), np.float32); cv2.circle(g, (int(cx / 8), int(cy / 8)), max(1, int(r * 0.3 / 8)), 1, -1)
        g = cv2.GaussianBlur(g, (0, 0), r * 0.6 / 8); g = cv2.resize(g / (g.max() + 1e-6), (W, H))[..., None]
        _GL[key] = g
    g = _GL[key] * amt
    return img * (1 - g) + np.float32(col) * g

def light(img, cx, cy, r, t, amt=0.75):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    jit = 1 + 0.03 * math.sin(t * 13) + 0.02 * math.sin(t * 29)
    m = np.clip(1 - (d / (r * jit)) ** 2, 0, 1)[..., None].astype(np.float32)
    return img * (1 - amt + amt * m)



# ================= MEERA: scenes =================
DARKBG = np.array([24, 26, 34], np.float32)
SCR = np.array([236, 236, 230], np.float32)
FIRE = np.array([255, 150, 45], np.float32)
GOLD = np.array([225, 180, 70], np.float32)
WARM = np.array([255, 214, 160], np.float32)
NIGHT = np.array([60, 70, 110], np.float32)
PHN = np.array([170, 210, 255], np.float32)
BRIDE = np.array([185, 20, 34], np.float32)

_ST = {}
def static(key, fn):
    if key not in _ST: _ST[key] = fn()
    return _ST[key].copy()

def lay(img, ink, col):
    return ink.apply(img, np.float32(col))

def fig(seed, cx, feet, height, **kw):
    g = Ink(seed=seed); person_back(g, cx, feet, height, **kw); return g

def veil(cx, feet, height, seed=50, sway=0.0):
    """red bridal ghoonghat over head + shoulders of a person_back figure (same geometry)."""
    hu = height / 8.0; top = feet - height; hx, hy = cx, top + hu * 0.5
    k = Ink(seed=seed)
    pts = np.vstack([bezier((hx - hu * 1.25 + sway * 6, top + hu * 3.4), (hx - hu * 0.9, hy - hu * 0.9), (hx, hy - hu * 0.75)),
                     bezier((hx, hy - hu * 0.75), (hx + hu * 0.9, hy - hu * 0.9), (hx + hu * 1.25 + sway * 6, top + hu * 3.4))])
    k.wash(pts, 0.93, 4)
    g = Ink(seed=seed + 1)
    g.stroke(np.vstack([bezier((hx - hu * 1.25 + sway * 6, top + hu * 3.4), (hx - hu * 0.9, hy - hu * 0.9), (hx, hy - hu * 0.75)),
                        bezier((hx, hy - hu * 0.75), (hx + hu * 0.9, hy - hu * 0.9), (hx + hu * 1.25 + sway * 6, top + hu * 3.4))]),
             hu * 0.09, hu * 0.06, 0.9, dry=0.2)
    return k, g

def safa(cx, feet, height, seed=60):
    """groom's turban (safa) as a wash over the head."""
    hu = height / 8.0; top = feet - height; hx, hy = cx, top + hu * 0.5
    k = Ink(seed=seed)
    k.wash(cv2.ellipse2Poly((int(hx), int(hy - hu * 0.15)), (int(hu * 0.58), int(hu * 0.5)), 0, 180, 360, 10).tolist()
           + [(int(hx + hu * 0.58), int(hy + hu * 0.05)), (int(hx - hu * 0.58), int(hy + hu * 0.05))], 0.95, 2)
    g = Ink(seed=seed + 1)
    for i in range(4):
        g.stroke(bezier((hx - hu * 0.55, hy - hu * (0.05 + i * 0.15)), (hx, hy - hu * (0.35 + i * 0.13)), (hx + hu * 0.55, hy - hu * (0.05 + i * 0.15))), 4, 3, 0.8, dry=0.3)
    g.stroke(bezier((hx + hu * 0.45, hy - hu * 0.2), (hx + hu * 0.7, hy + hu * 0.8), (hx + hu * 0.55, hy + hu * 1.6)), hu * 0.16, hu * 0.06, 0.9)  # tail
    return k, g

def fire(img, cx, cy, s, t, amt=1.0):
    img = glow(img, cx, cy - s * 0.6, s * 4.0, FIRE, 0.55 * amt * (0.85 + 0.15 * math.sin(t * 17)))
    k = Ink(seed=int(t * 30) % 50 + 100)
    for j in range(5):
        ox = (j - 2) * s * 0.28; hgt = s * (1.5 - abs(j - 2) * 0.3) * (0.85 + 0.25 * math.sin(t * (9 + j) + j))
        k.wash(np.vstack([bezier((cx + ox - s * 0.3, cy), (cx + ox - s * 0.25, cy - hgt * 0.5), (cx + ox + math.sin(t * 7 + j) * s * 0.2, cy - hgt)),
                          bezier((cx + ox + math.sin(t * 7 + j) * s * 0.2, cy - hgt), (cx + ox + s * 0.25, cy - hgt * 0.5), (cx + ox + s * 0.3, cy))]), 0.9, 3)
    img = k.apply(img, FIRE * 1.0)
    k2 = Ink(seed=7); k2.wash([(cx - s * 1.1, cy), (cx + s * 1.1, cy), (cx + s * 0.8, cy + s * 0.5), (cx - s * 0.8, cy + s * 0.5)], 0.95, 2)  # havan kund
    return k2.apply(img)

def phone_frame(img, x0, y0, x1, y1, scr=SCR):
    k = Ink(seed=801); k.wash([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.97, 4); img = k.apply(img)
    m = np.zeros((H, W), np.float32); cv2.rectangle(m, (x0 + 30, y0 + 60), (x1 - 30, y1 - 50), 1, -1)
    m = cv2.GaussianBlur(m, (0, 0), 2)[..., None]
    img = img * (1 - m) + paper(seed=88) * scr / 228 * m
    return img

# ---------- 0: hook - bride's phone on red dupatta, my message on it ----------
def hook_bg():
    img = PAPER.copy() * BRIDE / 228 * 1.15
    k = Ink(seed=901)
    for i in range(14):                                   # dupatta folds
        x = -100 + i * 95
        k.stroke(bezier((x, 0), (x + 60 + (i % 3) * 30, H / 2), (x + 20, H)), 26, 10, 0.35, dry=0.4)
    img = k.apply(img, np.array([90, 8, 18], np.float32))
    g = Ink(seed=902)                                     # gold zari border + dots
    g.stroke([(0, 120), (W, 160)], 30, 30, 0.9, dry=0.4); g.stroke([(0, 1790), (W, 1760)], 30, 30, 0.9, dry=0.4)
    rng = np.random.default_rng(3)
    for _ in range(90): g.blot(rng.uniform(0, W), rng.uniform(200, 1700), rng.uniform(4, 8), 0.85)
    img = g.apply(img, GOLD)
    img = phone_frame(img, 170, 330, 910, 1560, scr=np.array([30, 34, 50], np.float32))
    img = text(img, "7:55", (540, 520), 150, (240, 240, 245), stroke=0)
    img = text(img, "Wednesday, 11 November", (540, 630), 40, (190, 190, 205), stroke=0)
    cv2.rectangle(img, (230, 780), (850, 1080), (245, 245, 240), -1, cv2.LINE_AA)
    img = text(img, "AARAV", (270, 840), 52, INK, "lm", 0)
    img = text(img, "now", (810, 840), 36, (90, 90, 100), "rm", 0)
    img = text(img, "Meera, bas ek baar", (270, 940), 54, INK, "lm", 0)
    img = text(img, "mil lo...", (270, 1015), 54, INK, "lm", 0)
    h = Ink(seed=903)                                     # mehendi hands holding the phone
    for side in (-1, 1):
        x = 540 + side * 420
        for f in range(4):
            yy0 = 1150 + f * 95
            h.stroke([(x + side * 120, yy0 + 30), (x - side * 30, yy0)], 70, 46, 0.97, dry=0)
    img = h.apply(img, np.array([150, 90, 60], np.float32))
    d = Ink(seed=904)
    for side in (-1, 1):
        x = 540 + side * 420
        for f in range(4):
            d.blot(x + side * 10, 1150 + f * 95, 9, 0.9); d.stroke(bezier((x + side * 70, 1170 + f * 95), (x + side * 40, 1150 + f * 95), (x + side * 70, 1135 + f * 95)), 5, 3, 0.9)
    img = d.apply(img, np.array([90, 30, 15], np.float32))
    return img

def sc_hook(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = static("hook", hook_bg)
    img = glow(img, 540, 930, 420, PHN, 0.18 + 0.1 * math.sin(t * 6))
    kr = Ink(seed=905); ell = cv2.ellipse2Poly((540, 930), (370, 190), -3, 0, int(30 + 330 * min(1, p * 1.8)), 6)
    if len(ell) > 2: kr.stroke(ell, 13, 8, 0.95, dry=0.1)
    img = kr.apply(img, np.array([255, 240, 90], np.float32))
    sh = 7 * math.sin(t * 80) if lt < 0.45 else 0
    return zoom(img, 1.0 + 0.14 * p, 540, 930, dx=sh)

# ---------- 1: night, me texting 'Meera' ----------
def night_bg():
    img = PAPER.copy() * NIGHT / 228
    k = Ink(seed=911); k.wash_rect(0, 0, W, H, 0.45, 0); k.a[200:1100, 180:900] = 0; k.a = cv2.GaussianBlur(k.a, (0, 0), 6)
    for x in (180, 540, 900): k.stroke([(x, 200), (x, 1100)], 16, 14, 0.95, dry=0)
    for y in (200, 1100): k.stroke([(180, y), (900, y)], 16, 14, 0.95, dry=0)
    img = glow(img, 720, 380, 150, np.array([250, 245, 220], np.float32), 0.85)          # moon
    for i in range(9):                                                                   # city skyline
        x = 180 + i * 80; hgt = 120 + (i * 53 % 160)
        k.wash_rect(x, 1100 - hgt, x + 70, 1100, 0.85, 2)
    img = k.apply(img)
    g = fig(7, 540, 2350, 1650, walk=False, hair_long=False); img = g.apply(img)
    return img

def bubble(img, s, y, right, a=1.0, col=(245, 245, 240)):
    tw = 30 * len(s) + 60; x0 = 1000 - tw if right else 80
    ov = img.copy(); cv2.rectangle(ov, (x0, y), (x0 + tw, y + 100), col, -1, cv2.LINE_AA)
    img = img * (1 - a) + ov * a
    return text(img, s, (x0 + 30, y + 50), 46, np.float32(INK) * a + img[y + 50, x0 + 30] * (1 - a), "lm", 0)

def sc_night(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = static("night", night_bg)
    img = glow(img, 690, 1180, 140, PHN, 0.6 + 0.1 * math.sin(t * 4))
    img = zoom(img, 1.04 + 0.1 * p, 540, 900)
    msgs = [("Good night, Meera", True), ("Kal phir baat karein?", False), ("3:12 AM... so jao ab", False), ("Tumse milna hai", True)]
    for i, (s, r) in enumerate(msgs):
        q = (p - i * 0.2) / 0.1
        if q > 0: img = bubble(img, s, 260 + i * 140, r, min(1, q), (220, 245, 220) if r else (245, 245, 240))
    return img

# ---------- 2: wedding day, groom in safa sends the last message ----------
def groom_bg():
    img = PAPER.copy() * WARM / 228
    k = Ink(seed=921); k.wash_rect(0, 0, W, H, 0.3, 0); img = k.apply(img)
    for r in range(3):                                                    # fairy-light strings
        for i in range(22):
            x = i * 52; y = 200 + r * 220 + 60 * math.sin(i / 21 * math.pi)
            cv2.circle(img, (int(x), int(y)), 7, (255, 220, 120), -1, cv2.LINE_AA)
    m = Ink(seed=922)
    for i in range(10):                                                   # marigold garlands
        x = 60 + i * 105
        for j in range(12): m.blot(x + math.sin(j) * 4, 900 + j * 40, 17, 0.9)
    img = m.apply(img, np.array([235, 130, 20], np.float32))
    g = fig(7, 540, 2350, 1650, walk=False, hair_long=False); img = g.apply(img)
    a, b = safa(540, 2350, 1650); img = a.apply(img, BRIDE); img = b.apply(img, GOLD)
    return img

def sc_groom(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = static("groom", groom_bg)
    img = glow(img, 700, 1280, 130, PHN, 0.55)
    img = zoom(img, 1.03 + 0.1 * p, 540, 1000)
    if p > 0.45:
        q = min(1, (p - 0.45) / 0.12)
        img = bubble(img, "Bas ek baar mil lo", 330, True, q, (220, 245, 220))
        img = text(img, "To: MEERA   Sent", (1000, 470), 36, np.float32((40, 40, 50)) * q + img[470, 900] * (1 - q), "rm", 0)
    return img

# ---------- 3: mandap, bride's phone lights up ----------
def mandap_bg():
    img = PAPER.copy() * np.array([120, 70, 50], np.float32) / 228
    k = Ink(seed=931)
    for x in (90, 990): k.wash_rect(x - 40, 150, x + 40, 1500, 0.95, 3)        # pillars
    k.wash([(0, 120), (W, 120), (W, 230), (0, 230)], 0.95, 3)
    img = k.apply(img)
    m = Ink(seed=932)
    for i in range(18):
        m.blot(60 + i * 56, 240 + 30 * math.sin(i / 17 * math.pi), 20, 0.9)
    for x in (90, 990):
        for j in range(20): m.blot(x, 260 + j * 60, 18, 0.9)
    img = m.apply(img, np.array([235, 130, 20], np.float32))
    img = glow(img, 540, 900, 900, FIRE, 0.25)
    gm = fig(7, 330, 2500, 1700, walk=False, hair_long=False); img = gm.apply(img)
    a, b = safa(330, 2500, 1700); img = a.apply(img, BRIDE); img = b.apply(img, GOLD)
    gb = fig(5, 760, 2500, 1600, walk=False, hair_long=False); img = gb.apply(img)
    a, b = veil(760, 2500, 1600); img = a.apply(img, BRIDE); img = b.apply(img, GOLD)
    return img

def sc_mandap(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = static("mandap", mandap_bg)
    img = fire(img, 540, 1640, 90, t)
    pulse = 0.5 + 0.5 * math.sin(t * 10)
    img = glow(img, 820, 1250, 160, PHN, 0.5 + 0.35 * pulse * (p > 0.15))
    if p > 0.15 and (lt * 2.5) % 1 < 0.6:
        img = text(img, "!", (900, 1150), 120, RED * 1.3, stroke=5)
    cx = 540 + 220 * min(1, p * 1.3)
    return zoom(img, 1.0 + 0.3 * p, cx, 1100, dx=3 * math.sin(t * 60) * (p > 0.6))

# ---------- 4: bride under ghoonghat looks at the phone ----------
def bride_bg():
    img = PAPER.copy() * np.array([110, 60, 45], np.float32) / 228
    img = glow(img, 200, 1500, 700, FIRE, 0.35)
    g = fig(5, 560, 2700, 2300, walk=False, hair_long=False); img = g.apply(img)
    a, b = veil(560, 2700, 2300, seed=55); img = a.apply(img, BRIDE); img = b.apply(img, GOLD)
    z = Ink(seed=941)
    rng = np.random.default_rng(9)
    for _ in range(60): z.blot(rng.uniform(260, 860), rng.uniform(500, 1400), rng.uniform(3, 6), 0.8)
    img = z.apply(img, GOLD)
    return img

def sc_bride(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = static("bride", bride_bg)
    img = img * (0.9 + 0.1 * math.sin(t * 13) * math.sin(t * 5))
    img = glow(img, 560, 1250, 260, PHN, 0.55)
    ph = Ink(seed=942); ph.wash_rect(480, 1200, 640, 1300, 0.95, 2); img = ph.apply(img, np.array([200, 225, 255], np.float32))
    if p > 0.55:                                          # small red heart floats up = she smiles
        q = (p - 0.55) / 0.45
        img = text(img, "♥", (560, int(1130 - 260 * q)), int(80 + 40 * q), RED * 1.3 * min(1, q * 3) + img[1300, 560] * 0, stroke=0, font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return zoom(img, 1.05 + 0.18 * p, 560, 1200)

# ---------- 5: flashback, college bus 3 years ago ----------
def bus_bg():
    img = PAPER.copy()
    k = Ink(seed=951)
    k.wash_rect(0, 0, W, 260, 0.75, 3)
    for i in range(3):
        x = 40 + i * 350; k.stroke([(x, 300), (x + 300, 300), (x + 300, 800), (x, 800), (x, 300)], 12, 12, 0.8, dry=0.2)
    k.stroke([(0, 270), (W, 270)], 14, 14, 0.9, dry=0)                    # hand rail
    for x in (300, 780): k.stroke([(x, 270), (x, 1900)], 12, 12, 0.85, dry=0)
    k.wash([(0, 1700), (W, 1650), (W, H), (0, H)], 0.6, 6)
    img = k.apply(img)
    g = fig(7, 640, 1700, 1050, walk=False, hair_long=False, val=0.85); img = g.apply(img)   # him standing ahead
    s = fig(5, 230, 2600, 2000, walk=False, hair_long=True, sway=0.3); img = s.apply(img)    # her seated, foreground
    return img

def sc_bus(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = static("bus", bus_bg)
    img = img * (0.94 + 0.06 * math.sin(t * 3))
    sep = img.mean(2, keepdims=True); img = sep * np.array([1.05, 0.95, 0.78], np.float32)
    nb = Ink(seed=952); nb.wash([(520, 1640), (1020, 1620), (1050, 1900), (550, 1910)], 0.15, 2); img = nb.apply(img, (250, 248, 238))
    cv2.rectangle(img, (540, 1650), (1030, 1910), (250, 248, 238), -1, cv2.LINE_AA)
    img = text(img, "Aarav - Bus No. 4", (570, 1710), 44, INK, "lm", 0, font=FH)
    img = text(img, "98XXX 4X1X7", (570, 1800), 56, INK, "lm", 0, font=FH)
    if p > 0.3: img = text(img, "♥", (960, 1700), 90, RED * 1.2, stroke=0, font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    img = text(img, "3 SAAL PEHLE", (W / 2, 330), 64, (250, 245, 230), stroke=5)
    return zoom(img, 1.02 + 0.1 * p, 640, 900)

# ---------- 6: pheras, gathbandhan ----------
def sc_phere(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = static("mandap0", lambda: (lambda im: (lambda k: k.apply(im))((lambda k: ([k.wash_rect(x - 40, 150, x + 40, 1500, 0.95, 3) for x in (90, 990)], k)[1])(Ink(seed=931))))(PAPER.copy() * np.array([120, 70, 50], np.float32) / 228))
    img = fire(img, 540, 1450, 80, t)
    ph = 0.6 + lt * 0.5
    gx, bx = 420 - 60 * math.sin(ph), 690 - 60 * math.sin(ph)
    gm = fig(7, gx, 1820, 900, phase=lt * 5, walk=True, hair_long=False); img = gm.apply(img)
    a, b = safa(gx, 1820, 900); img = a.apply(img, BRIDE); img = b.apply(img, GOLD)
    gb = fig(5, bx, 1820, 860, phase=lt * 5 + 1.5, walk=True, hair_long=False); img = gb.apply(img)
    a, b = veil(bx, 1820, 860, sway=math.sin(lt * 3)); img = a.apply(img, BRIDE); img = b.apply(img, GOLD)
    k = Ink(seed=961)                                     # red gathbandhan knot joining them
    k.stroke(bezier((gx + 70, 1820 - 900 + 220), ((gx + bx) / 2, 1820 - 900 + 480 + 20 * math.sin(lt * 4)), (bx - 60, 1820 - 860 + 230)), 16, 12, 0.95, dry=0.1)
    k.blot((gx + bx) / 2, 1820 - 900 + 470, 20, 0.95)
    img = k.apply(img, RED * 1.3)
    return zoom(img, 1.12 - 0.1 * p, 540, 1200)

SCENES = [sc_hook, sc_night, sc_groom, sc_mandap, sc_bride, sc_bus, sc_phere]
def load_srt(p):
    out = []
    for blk in open(p).read().strip().split("\n\n"):
        ln = blk.split("\n"); a, b = ln[1].split(" --> ")
        f = lambda s: sum(float(x) * m for x, m in zip(re.split("[:,]", s), (3600, 60, 1, 0.001)))
        out.append((f(a), f(b), ln[2]))
    return out

SRT = []
def scene_spans(total):
    spans = []
    for si in range(len(SCENES)):
        idx = [i for i, s in enumerate(SCENE_OF) if s == si]
        a = 0 if si == 0 else SRT[idx[0]][0]
        b = total if si == len(SCENES) - 1 else SRT[SCENE_OF.index(si + 1)][0]
        spans.append((a, b))
    return spans

def glitch(img, t, cuts):
    for c in cuts:
        if 0 <= t - c < 0.12:
            sh = int(30 * math.sin(t * 90)); img = np.roll(img, sh, axis=1)
            img[..., 0] = np.roll(img[..., 0], 12, axis=1); img = img * 1.25
    return img

def frame(t):
    total = SRT[-1][1] + 0.5
    spans = scene_spans(total)
    if t >= total:
        img = PAPER.copy() * 0.12
        e = min(1, (t - total) / 0.5)
        img = text(img, TITLE, (W / 2, 800), 140, RED * 1.25)
        img = text(img, "THE END...?", (W / 2, 980), 90, np.array([235, 232, 225]) * e)
        img = text(img, "Follow for a new", (W / 2, 1200), 60, np.array([235, 232, 225]) * e, stroke=4)
        img = text(img, "story every day", (W / 2, 1280), 60, np.array([235, 232, 225]) * e, stroke=4)
        return finish(img, t, 9)
    si = max(i for i, (a, b) in enumerate(spans) if t >= a)
    a, b = spans[si]
    img = SCENES[si](t - a, b - a, t)
    img = glitch(np.float32(img), t, [s[0] for s in spans[1:]])
    img = finish(img, t, si)
    img = np.float32(img)
    img = text(img, TITLE + "  |  LOVE STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
    for ci, (ca, cb, s) in enumerate(SRT):
        if ca <= t < cb:
            size = 96 if ci <= 1 else 74
            lines = textwrap.wrap(s, 16 if ci <= 1 else 18)
            y0 = 1500 - (len(lines) - 1) * 45
            for li, ln in enumerate(lines):
                hot = any(re.sub(r"[^A-Z0-9]", "", w) in HOT for w in ln.split())
                img = text(img, ln, (W / 2, y0 + li * (size + 16)), size, RED * 1.35 if hot else (245, 242, 235))
    return np.clip(img, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    wav, srt, out = sys.argv[1:4]
    SRT[:] = load_srt(srt)
    T = SRT[-1][1] + 0.5 + END_CARD
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            cv2.imwrite(f"{out}_{ts}.jpg", cv2.cvtColor(frame(float(ts)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
        sys.exit()
    tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(T * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out); print("ok", T)
