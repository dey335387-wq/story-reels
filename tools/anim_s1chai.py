"""Standalone story 'DO CHAI' (highway dhaba, 3 AM) - procedural ink-wash animation (no stock footage).
python3 anim_s1chai.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FPS = 30
END_CARD = 2.8
TITLE = "DO CHAI"

CAPS = ["DHAABE WAALE NE BILL DIYA...", "LIKHA THA: 2 CHAI", "PAR MAIN TOH AKELA THA",
        "RAAT KE 3 BAJE THE...", "HIGHWAY POORA SUNSAAN",
        "MAINE POOCHHA, DOOSRI CHAI KISKI?", "\"JO AAPKI GAADI KI PICHHLI SEAT PAR BAITHI HAI\"",
        "MAINE MUDKAR DEKHA... GAADI KHAALI THI", "MAIN HASA... PAISE DIYE... AUR NIKAL GAYA",
        "20 KM BAAD... PEECHHE SE KISI NE CHAI KI CHUSKI LI",
        "SHEESHE MEIN DEKHA...", "PICHHLI SEAT PAR EK KULHAD RAKHA THA... GARAM",
        "\"CHAI ACCHI THI... AB GHAR CHALEIN?\""]
HOT = {"2", "AKELA", "3", "PICHHLI", "SEAT", "KHAALI", "CHUSKI", "KULHAD", "GARAM", "GHAR", "CHALEIN"}
SCENE_OF = [0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4, 4, 4]

PAPER = paper(seed=17)
yy, xx = np.mgrid[0:H, 0:W]

def text(img, s, xy, size, col, anchor="mm", stroke=6):
    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(pil)
    d.text(xy, s, font=ImageFont.truetype(FB, size), fill=tuple(int(min(255, c)) for c in col), anchor=anchor, stroke_width=stroke, stroke_fill=(10, 10, 12))
    return np.asarray(pil).astype(np.float32)

def zoom(img, z, cx=W / 2, cy=H / 2, dx=0, dy=0):
    M = cv2.getRotationMatrix2D((cx, cy), 0, z); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(np.float32(img), M, (W, H), borderMode=cv2.BORDER_REFLECT)

def put(mask, s, org, font, scale, th):
    u = np.zeros(mask.shape, np.uint8); cv2.putText(u, s, org, font, scale, 255, th, cv2.LINE_AA)
    np.maximum(mask, u.astype(np.float32) / 255, out=mask)

def glow(img, cx, cy, r, col, amt):
    g = np.zeros((H, W), np.float32); cv2.circle(g, (int(cx), int(cy)), int(r * 0.3), 1, -1)
    g = cv2.GaussianBlur(g, (0, 0), r * 0.6)[..., None]; g = g / (g.max() + 1e-6) * amt
    return img * (1 - g) + np.float32(col) * g

def light(img, cx, cy, r, t, amt=0.75):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    jit = 1 + 0.03 * math.sin(t * 13) + 0.02 * math.sin(t * 29)
    m = np.clip(1 - (d / (r * jit)) ** 2, 0, 1)[..., None].astype(np.float32)
    return img * (1 - amt + amt * m)

def steam(k, x, y, t, n=3, h=220, val=0.35):
    for i in range(n):
        ph = t * 1.4 + i * 2.1
        pts = [(x + (i - 1) * 14 + math.sin(ph + j * 0.6) * (8 + j * 3), y - j * h / 10) for j in range(11)]
        k.stroke(pts, 7, 1.5, val, jitter=0.3, dry=0.4)

def kulhad(k, cx, cy, s=1.0, val=0.9):
    """clay tea cup: tapered, rim ellipse."""
    w0, w1, h = 70 * s, 50 * s, 105 * s
    k.wash([(cx - w0, cy), (cx + w0, cy), (cx + w1, cy + h), (cx - w1, cy + h)], val * 0.75, 2)
    k.stroke([(cx - w0, cy), (cx - w1, cy + h), (cx + w1, cy + h), (cx + w0, cy)], 4 * s, 3 * s, val)
    k.wash(cv2.ellipse2Poly((int(cx), int(cy)), (int(w0), int(15 * s)), 0, 0, 360, 10), 0.97, 1)
    for i in range(3):
        k.stroke([(cx - w0 + 6, cy + 25 * s + i * 25 * s), (cx + w0 - 6 - i * 6, cy + 27 * s + i * 25 * s)], 1.5, 1, 0.4, dry=0.5)

# ---------- backgrounds (built once) ----------
def bill_bg():
    k = Ink(seed=81)
    k.wash_rect(0, 0, W, H, 0.85, 30)                                    # dark wooden table
    for i in range(14):
        y = 80 + i * 140 + (i % 3) * 13
        k.stroke([(0, y), (W * 0.5, y + 12), (W, y - 6)], 2.5, 2, 0.98, dry=0.5)
    slip = [(250, 520), (860, 470), (900, 1430), (230, 1470)]
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [np.int32(slip)], 1); m = cv2.GaussianBlur(m, (0, 0), 3)
    k.a = k.a * (1 - m) + 0.06 * m
    k.stroke(slip + [slip[0]], 3, 2.5, 0.7)
    for r in range(9):
        y = 700 + r * 78
        k.stroke([(290, y + 3), (860, y - 18)], 1.4, 1.1, 0.3, dry=0.3)
    w = np.zeros((H, W), np.float32)
    put(w, "SHER-E-PUNJAB DHABA", (300, 600), cv2.FONT_HERSHEY_DUPLEX, 1.25, 3)
    put(w, "NH-48   03:04 AM", (330, 665), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
    put(w, "Paratha x1     60", (320, 1060), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.4, 3)
    put(w, "Total", (320, 1250), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.4, 3)
    k.a = np.maximum(k.a, w * 0.9)
    kulhad(k, 830, 1560, 1.25)
    red = np.zeros((H, W), np.float32)
    put(red, "Chai x 2     40", (320, 900), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.0, 5)
    put(red, "100", (650, 1250), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.6, 4)
    return k, red

BK, BRED = bill_bg()

def dhaba_bg():
    k = Ink(seed=91)
    k.wash_rect(0, 0, W, H, 0.6, 30)                                     # night sky
    k.wash([(0, 1180), (W, 1120), (W, H), (0, H)], 0.5, 10)               # ground
    k.wash([(0, 1460), (W, 1380), (W, 1560), (0, 1660)], 0.8, 6)          # highway strip
    for i in range(6):
        x = 60 + i * 190
        k.stroke([(x, 1530 - x * 0.07), (x + 90, 1524 - (x + 90) * 0.07)], 7, 7, 0.25, dry=0)
    # dhaba hut
    k.wash([(80, 760), (680, 700), (700, 1230), (90, 1250)], 0.55, 4)
    k.wash([(40, 780), (380, 560), (740, 720)], 0.97, 3)                  # tin roof
    k.stroke([(40, 780), (380, 560), (740, 720)], 8, 6)
    k.wash_rect(240, 900, 520, 1240, 0.12, 3)                             # lit door opening
    k.stroke([(120, 780), (130, 1250)], 9, 7); k.stroke([(660, 730), (670, 1230)], 9, 7)
    k.stroke([(380, 600), (380, 735)], 2, 2, 0.9)                         # bulb wire
    # charpai
    k.stroke([(110, 1310), (520, 1290)], 8, 7); k.stroke([(140, 1380), (560, 1350)], 8, 7)
    for x in (115, 515, 145, 555):
        k.stroke([(x, 1300 if x < 530 and x in (115, 515) else 1370), (x, 1430)], 6, 5)
    for i in range(10):
        k.stroke([(130 + i * 40, 1305), (160 + i * 40, 1370)], 1.5, 1, 0.5)
    # car (right side) parked, back towards viewer-ish
    k.wash([(700, 1250), (760, 1120), (930, 1100), (1060, 1160), (1080, 1300), (700, 1320)], 0.96, 3)
    k.wash([(770, 1135), (920, 1115), (960, 1170), (760, 1185)], 0.35, 2)     # rear window (faintly lit)
    for x in (760, 1010):
        k.blot(x, 1320, 38, 0.99)
    return k

DK = dhaba_bg()

def owner_front(k, cx, feet, height, arm=0.0, t=0.0):
    """Dhaba owner silhouette facing us, pagdi, shawl; right arm raises to point at car."""
    hu = height / 8.0; top = feet - height
    hx, hy = cx, top + hu * 0.75
    k.wash(cv2.ellipse2Poly((int(hx), int(hy)), (int(hu * .5), int(hu * .58)), 0, 0, 360, 10), 0.98, 2)
    k.wash(cv2.ellipse2Poly((int(hx), int(hy - hu * .45)), (int(hu * .62), int(hu * .38)), 0, 180, 360, 10), 0.99, 2)  # pagdi
    sh = top + hu * 1.6
    body = [(cx - hu * 1.0, sh), (cx + hu * 1.0, sh), (cx + hu * 1.1, top + hu * 5.2), (cx + hu * .6, feet), (cx - hu * .6, feet), (cx - hu * 1.1, top + hu * 5.2)]
    k.wash(body, 0.95, 3)
    k.stroke([(cx - hu * 1.0, sh), (cx - hu * 1.15, top + hu * 5.2)], 4, 2)
    # pointing arm
    ax, ay = cx + hu * 0.95, sh + hu * .2
    ang = -0.15 - arm * 1.15
    ex, ey = ax + math.cos(ang) * hu * 1.5, ay - math.sin(ang) * hu * 1.5
    wx, wy = ex + math.cos(ang * 1.05) * hu * 1.3, ey - math.sin(ang * 1.05) * hu * 1.3
    k.stroke([(ax, ay), (ex, ey)], hu * .32, hu * .22, 0.97, dry=0.05)
    k.stroke([(ex, ey), (wx, wy)], hu * .22, hu * .12, 0.97, dry=0.05)
    k.stroke([(wx, wy), (wx + math.cos(ang) * hu * .45, wy - math.sin(ang) * hu * .45)], hu * .07, hu * .03, 0.97, dry=0)
    return (hx - hu * .18, hy), (hx + hu * .18, hy)

def backseat_bg():
    """inside car, looking back at the rear seat from the front."""
    k = Ink(seed=101)
    k.wash_rect(0, 0, W, H, 0.7, 25)
    k.wash([(60, 520), (1020, 520), (980, 760), (100, 760)], 0.25, 6)      # rear windshield (night glow)
    k.stroke([(60, 520), (1020, 520), (980, 760), (100, 760), (60, 520)], 9, 7)
    # seat back
    seat = np.vstack([bezier((70, 820), (540, 760), (1010, 820)), [(1040, 1250), (40, 1250)]])
    k.wash(seat, 0.5, 5)
    k.stroke(bezier((70, 820), (540, 760), (1010, 820)), 8, 6)
    for x in (380, 700):
        k.stroke([(x, 790), (x - 10, 1240)], 3, 2, 0.85)
    # cushion
    cush = [(30, 1260), (1050, 1260), (1080, 1520), (0, 1520)]
    k.wash(cush, 0.4, 5); k.stroke([(30, 1260), (1050, 1260)], 7, 5)
    for x, y in ((230, 800), (540, 770), (850, 800)):                       # headrests
        k.wash(cv2.ellipse2Poly((x, y - 60), (95, 75), 0, 0, 360, 10), 0.6, 3)
        k.stroke(cv2.ellipse2Poly((x, y - 60), (95, 75), 0, 0, 360, 10)[::2], 4, 3, 0.95)
    # front seats framing bottom
    k.wash([(0, 1560), (380, 1500), (420, H), (0, H)], 0.97, 6)
    k.wash([(700, 1500), (W, 1560), (W, H), (660, H)], 0.97, 6)
    return k

SK = backseat_bg()

def road_bg():
    """driver's POV: dashboard, steering wheel, windshield onto dark highway."""
    k = Ink(seed=111)
    k.wash([(0, 1350), (W, 1300), (W, H), (0, H)], 0.99, 8)                 # dashboard
    k.stroke([(0, 1350), (W, 1300)], 10, 8)
    # steering wheel
    k.stroke(cv2.ellipse2Poly((330, 1700), (300, 260), 0, 180, 360, 6), 34, 30, 0.99, dry=0)
    k.stroke([(330, 1700), (120, 1640)], 26, 20, 0.99, dry=0); k.stroke([(330, 1700), (540, 1640)], 26, 20, 0.99, dry=0)
    # A-pillars
    k.wash([(0, 0), (120, 0), (40, 1340), (0, 1350)], 0.99, 4)
    k.wash([(W, 0), (W - 120, 0), (W - 40, 1300), (W, 1300)], 0.99, 4)
    return k

RK = road_bg()

def mirror_bg():
    k = Ink(seed=121)
    k.wash_rect(0, 0, W, H, 0.95, 25)
    k.wash([(0, 1450), (W, 1400), (W, H), (0, H)], 0.99, 8)
    k.stroke([(540, 0), (540, 520)], 30, 24, 0.99, dry=0)                    # mirror mount
    return k

MK = mirror_bg()
MX0, MY0, MX1, MY1 = 70, 520, 1010, 1060                                   # mirror rect

def mirror_content(t, lt, dur):
    """reflection: rear seat with steaming kulhad; ghost leaning in at the end."""
    k = Ink(seed=131)
    k.wash_rect(MX0, MY0, MX1, MY1, 0.45, 4)
    k.wash([(MX0, MY0 + 140), (MX1, MY0 + 140), (MX1, MY0 + 330), (MX0, MY0 + 330)], 0.15, 8)   # rear window glow
    k.wash(np.vstack([bezier((MX0, MY0 + 360), (540, MY0 + 320), (MX1, MY0 + 360)), [(MX1, MY1), (MX0, MY1)]]), 0.55, 4)
    k.stroke(bezier((MX0, MY0 + 360), (540, MY0 + 320), (MX1, MY0 + 360)), 6, 5)
    kulhad(k, 620, MY0 + 360, 0.9)
    steam(k, 620, MY0 + 350, t, 3, 190, 0.6)
    eyes = None
    p = lt / max(dur, 0.1)
    if p > 0.12:                                                           # long-haired woman rising behind seat at left
        rise = min(1, (p - 0.12) / 0.45)
        g = Ink(seed=132)
        e1, e2, hu = ghost_front(g, 330 + 120 * min(1, max(0, p - 0.6) / 0.4), MY0 + 1080 - 200 * rise, 760, sway=math.sin(t * 1.3) * 0.8)
        g.a[:MY0] = 0; g.a[MY0 + 375:] = 0; g.a[:, :MX0] = 0; g.a[:, MX1:] = 0
        k.a = np.maximum(k.a, g.a * 0.98)
        eyes = (e1, e2, hu)
    return k, eyes

SC_WARM = np.array([255, 205, 130], np.float32)

# ---------- scenes ----------
def sc_bill(lt, dur, t):
    k = Ink(seed=82); k.a = BK.a.copy(); steam(k, 830, 1545, t, 3, 260, 0.25)
    base = k.apply(PAPER.copy())
    reveal = min(1, 0.6 + lt / 1.4)
    rm = cv2.GaussianBlur(BRED, (0, 0), 0.8) * (xx < 300 + 600 * reveal)
    if lt > 0.9:                                                           # red circle around "x 2"
        c = np.zeros((H, W), np.float32); e = min(1, (lt - 0.9) / 0.8)
        cv2.ellipse(c, (480, 885), (120, 70), -5, 0, int(360 * e), 1.0, 6, cv2.LINE_AA)
        rm = np.maximum(rm, c)
    rm = rm[..., None]; base = base * (1 - rm) + RED * 1.2 * rm
    base = light(base, 560, 950, 760, t, 0.65)
    p = lt / max(dur, 0.1)
    return zoom(base, 1.55 - 0.3 * p, 520, 900, dx=40, dy=0 + 120 * p)

def sc_dhaba(lt, dur, t):
    k = Ink(seed=92); k.a = DK.a.copy()
    p = lt / max(dur, 0.1)
    arm = min(1, max(0, (p - 0.55) / 0.2))
    e = owner_front(k, 390, 1290, 560, arm, t)
    fl = flicker(t, 4)
    base = k.apply(PAPER.copy()) * (0.55 + 0.45 * fl)
    base = glow(base, 380, 745, 260, SC_WARM, 0.75 * fl)                    # single bulb
    base = light(base, 380, 900, 820, t, 0.55)
    if p > 0.75:                                                            # car rear window: faint shape?
        base = glow(base, 860, 1150, 90, (205, 215, 235), 0.25 + 0.2 * math.sin(t * 9))
    return zoom(base, 1.15 + 0.22 * p, 560 + 250 * arm, 1050, dx=0, dy=-80)

def sc_backseat(lt, dur, t):
    k = Ink(seed=102); k.a = SK.a.copy()
    fl = flicker(t, 7)
    base = k.apply(PAPER.copy())
    sweep = (lt * 380) % 1400 - 200                                         # passing street light sweep
    base = glow(base, sweep, 640, 330, (225, 225, 210), 0.45)
    base = base * (0.6 + 0.4 * fl)
    # a dent in the middle cushion (someone sat here)
    p = lt / max(dur, 0.1)
    if p > 0.45:
        d = Ink(seed=103); d.wash(cv2.ellipse2Poly((540, 1330), (170, 40), 0, 0, 360, 10), 0.35 * min(1, (p - 0.45) * 4), 12)
        base = d.apply(base)
    return zoom(base, 1.0 + 0.25 * p, 540, 1100)

def sc_road(lt, dur, t):
    k = Ink(seed=112)
    vx, vy = 560, 760
    k.wash([(vx - 30, vy), (vx + 30, vy), (W + 300, 1320), (-300, 1350)], 0.0, 0)
    base = PAPER.copy() * 0.18
    hl = np.zeros((H, W), np.float32)
    cv2.fillPoly(hl, [np.int32([(vx - 40, vy), (vx + 40, vy), (W + 200, 1320), (-200, 1350)])], 1)
    hl = cv2.GaussianBlur(hl, (0, 0), 40) * np.clip((yy - vy) / 560, 0, 1)
    base = base + (np.float32([200, 195, 175]) * 0.75 * hl[..., None])
    rd = Ink(seed=113)
    for i in range(8):                                                      # dashes rushing
        f = ((lt * 1.4 + i / 8) % 1) ** 2
        y = vy + 20 + f * 560; wdt = 3 + f * 26; ln = 10 + f * 120
        rd.wash_rect(vx - wdt / 2 + f * 30, y, vx + wdt / 2 + f * 30, min(1340, y + ln), 0.0 + 0.0, 0)
        cv2.rectangle(base, (int(vx - wdt / 2 + f * 30), int(y)), (int(vx + wdt / 2 + f * 30), int(min(1330, y + ln))), (215, 212, 200), -1, cv2.LINE_AA)
    km = np.zeros((H, W), np.float32); put(km, "NH-48", (880, 860), cv2.FONT_HERSHEY_DUPLEX, 0.9, 2)
    base = base + km[..., None] * 40
    kk = Ink(seed=114); kk.a = RK.a.copy()
    base = kk.apply(base)
    sh = math.sin(t * 23) * 2.5
    p = lt / max(dur, 0.1)
    return zoom(base, 1.0 + 0.08 * p, W / 2, 1000, dx=sh, dy=sh * 0.5)

def sc_mirror(lt, dur, t):
    k = Ink(seed=122); k.a = MK.a.copy()
    base = k.apply(PAPER.copy() * 0.2)
    mc, eyes = mirror_content(t, lt, dur)
    mpaper = PAPER.copy() * 0.95
    mimg = mc.apply(mpaper)
    mm = np.zeros((H, W), np.float32); cv2.rectangle(mm, (MX0, MY0), (MX1, MY1), 1, -1)
    mm = cv2.GaussianBlur(mm, (0, 0), 2)[..., None]
    base = base * (1 - mm) + mimg * mm
    fr = Ink(seed=123); fr.stroke([(MX0, MY0), (MX1, MY0), (MX1, MY1), (MX0, MY1), (MX0, MY0)], 26, 26, 0.99, dry=0)
    base = fr.apply(base)
    p = lt / max(dur, 0.1)
    if eyes and p > 0.62:
        for (ex, ey) in eyes[:2]:
            if MY0 < ey < MY1:
                cv2.ellipse(base, (int(ex), int(ey)), (10, 5), 0, 0, 360, tuple(float(c) for c in RED * 1.4), -1, cv2.LINE_AA)
    base = light(base, 540, 790, 700, t, 0.5)
    zc = 1.05 + (0.15 * min(1, p / 0.6)) + (0.45 * max(0, p - 0.6) / 0.4)
    return zoom(base, zc + 0.2, 450 if p > 0.6 else 540, 790)

SCENES = [sc_bill, sc_dhaba, sc_backseat, sc_road, sc_mirror]

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
    img = text(img, "DO CHAI  |  HORROR STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
    for ci, (ca, cb, s) in enumerate(SRT):
        if ca <= t < cb:
            size = 92 if ci <= 1 else 74
            lines = textwrap.wrap(s, 16 if ci <= 1 else 18)
            y0 = 1480 - (len(lines) - 1) * 45
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
