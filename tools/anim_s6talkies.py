"""Standalone story 'RAJ TALKIES' (old single-screen cinema, last show 12 AM, one ticket bought but ticket says 2) -
procedural ink-wash animation (no stock footage).  python3 anim_s6talkies.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FH = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"   # 'handwriting'
FPS = 30
END_CARD = 2.8
TITLE = "RAJ TALKIES"

CAPS = ["MAINE EK TICKET LI THI...", "PAR TICKET PE CHHAPA THA: 2",
        "MAIN ARJUN. RAJ TALKIES KA LAST SHOW, RAAT 12 BAJE",
        "POORA HALL KHAALI THA.", "PHIR BHI BAGAL WAALI SEAT... APNE AAP KHUL GAYI",
        "ANDHERE MEIN, MERE BAGAL MEIN...", "KOI POPCORN KHA RAHA THA",
        "INTERVAL MEIN LIGHT JALI. SEAT KHAALI THI...", "PAR US PE EK PURAANI TICKET PADI THI, 1998 KI",
        "GATEKEEPER BOLA, 98 KI AAG MEIN", "EK LADKI ISI SEAT PE JAL GAYI THI",
        "TABHI FILM RUK GAYI...", "AUR SCREEN PE DIKHA, MERE KANDHE PE SIR RAKHE...", "EK JALI HUI LADKI",
        "KAAN MEIN AAWAAZ AAYI...", "AGLA SHOW BHI SAATH DEKHENGE?"]
HOT = {"2", "KHAALI", "APNE", "AAP", "POPCORN", "1998", "98", "AAG", "JAL", "LADKI", "AGLA", "SAATH"}
SCENE_OF = [0, 0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 7, 7]
PAPER = paper(seed=23)
yy, xx = np.mgrid[0:H, 0:W]
WHITE = np.array([245, 242, 235], np.float32)
BLUE = np.array([30, 40, 95], np.float32)
WARM = np.array([255, 225, 160], np.float32)
COLD = np.array([190, 205, 230], np.float32)


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


PINK = np.array([238, 196, 196], np.float32)
FIRE = np.array([255, 120, 30], np.float32)
SCREEN = np.array([215, 225, 245], np.float32)
SX0, SY0, SX1, SY1 = 150, 300, 930, 760          # cinema screen rect

# ---------- backgrounds ----------
def seat_row(k, y, s, gap=True, val=0.95):
    """one row of seat backs seen from behind (rounded blobs), size s (0..1 nearer)."""
    sw = 60 + 120 * s; sh = 40 + 110 * s
    n = int(W / sw) + 2
    for j in range(n):
        x = (j - n / 2) * sw + W / 2 + (sw / 2 if int(y) % 2 else 0)
        if gap and abs(x - W / 2) < 70 + 60 * s: continue
        k.wash(cv2.ellipse2Poly((int(x), int(y)), (int(sw * 0.44), int(sh * 0.6)), 0, 180, 360, 12) .tolist()
               + [(int(x + sw * .44), int(y + sh)), (int(x - sw * .44), int(y + sh))], val, 2)

def hall_bg(seed=601):
    k = Ink(seed=seed)
    k.wash_rect(0, 0, W, H, 0.8, 25)
    k.wash_rect(SX0 - 30, SY0 - 30, SX1 + 30, SY1 + 30, 0.95, 4)                    # screen frame
    rows = [(860, 0.05), (930, 0.12), (1020, 0.22), (1140, 0.36), (1300, 0.55), (1500, 0.78), (1740, 1.05)]
    for y, s in rows: seat_row(k, y, s)
    return k
HK = hall_bg()

def screen_light(img, t, amt=1.0, col=SCREEN):
    f = flicker(t, 3) * amt
    a = np.zeros((H, W), np.float32); a[SY0:SY1, SX0:SX1] = 1
    a3 = (a * 0.85 * f)[..., None]
    img = img * (1 - a3) + col * a3
    # projector beam haze from top-back towards screen + spill on rows
    img = glow(img, 540, 540, 700, col * 0.9, 0.22 * f)
    return img

_FIG = {}
def man(key, phase, walk=True, cx=540, feet=1880, h=820):
    ph = round(phase * 2) / 2
    if len(_FIG) > 40: _FIG.clear()
    if (key, ph) not in _FIG:
        g = Ink(seed=7); person_back(g, cx, feet, h, phase=ph, walk=walk, hair_long=False, dress="shirt"); _FIG[(key, ph)] = g.a
    return _FIG[(key, ph)]

# ---------- scenes ----------
def sc_hook(lt, dur, t):
    """FULL-SCREEN proof: old cinema ticket 'ADULT: 2' circled in red, seats J-7, J-8."""
    p = lt / max(dur, 0.1)
    img = paper(seed=61) * (PINK / 228)
    k = Ink(seed=602)
    for i in range(22):                                                             # age stains
        k.blot(80 + (i * 233) % 920, 260 + (i * 397) % 1500, 30 + (i * 13) % 60, 0.1)
    img = k.apply(img, np.array([120, 60, 50], np.float32))
    for y in range(240, 1700, 46): cv2.circle(img, (110, y), 10, (40, 30, 30), -1, cv2.LINE_AA)   # perforation
    cv2.rectangle(img, (170, 250), (990, 1680), (120, 40, 45), 5, cv2.LINE_AA)
    img = text(img, "RAJ TALKIES", (580, 400), 108, (120, 25, 35), stroke=0)
    img = text(img, "LAST SHOW  12:00 AM", (580, 540), 62, INK, stroke=0)
    img = text(img, "ADULT :", (230, 800), 110, INK, "lm", 0)
    img = text(img, "2", (760, 800), 250, RED * 1.1, "mm", 0, FH, rot=-4)
    img = text(img, "SEAT :  J-7 , J-8", (230, 1080), 84, INK, "lm", 0)
    img = text(img, "Rs 60 x 2", (230, 1260), 70, BLUE, "lm", 0, FH, rot=2)
    kr = Ink(seed=603)
    ell = cv2.ellipse2Poly((765, 805), (150, 160), -8, 0, int(40 + 330 * min(1, p * 1.6)), 6)
    if len(ell) > 2: kr.stroke(ell, 11, 6, 0.95, dry=0.1)
    kr.stroke([(590, 1135), (960, 1125)], 8, 5, 0.9)                                # J-8 underlined in red
    img = kr.apply(img, RED * 1.15)
    img = img * (0.78 + 0.22 * flicker(t, 1))
    return zoom(img, 1.05 + 0.2 * p, 700, 860)

def sc_hall(lt, dur, t, figure=True, dark=0.0):
    """empty single-screen hall from the back; Arjun walks down the aisle."""
    p = lt / max(dur, 0.1)
    k = Ink(seed=605); k.a = HK.a.copy()
    base = k.apply(PAPER.copy() * (0.85 - dark))
    base = screen_light(base, t, 1 - dark)
    if figure:
        g = man('walk', t * 5, True, 540, 1900 - 260 * p, 900 - 300 * p)
        base = base * (1 - g[..., None]) + INK * g[..., None]
    return zoom(base, 1.04 + 0.12 * p, 540, 900)

def seat_poly(cx, base_y, ang, w=180):
    """folding seat cushion hinged at (cx, base_y): ang 90=folded up, 0=open (seen from side-front)."""
    L = 170; a = math.radians(ang)
    tip = (0, -L * math.sin(a)); dep = L * math.cos(a) * 0.45
    return [(cx - w / 2, base_y), (cx + w / 2, base_y), (cx + w / 2 + 0, base_y + tip[1] + dep), (cx - w / 2, base_y + tip[1] + dep)]

def sc_seat(lt, dur, t):
    """close row of folding seats, all folded up; J-8 (beside Arjun) flips open by itself."""
    p = lt / max(dur, 0.1)
    flip_t = SRT[4][0] - (t - lt) + 0.8
    img = PAPER.copy() * 0.5
    img = glow(img, 540, 200, 700, SCREEN, 0.3 * flicker(t, 4))
    k = Ink(seed=606)
    xs = [140, 400, 680, 940]
    for i, cx in enumerate(xs):
        k.wash(cv2.ellipse2Poly((cx, 760), (115, 70), 0, 180, 360, 10).tolist() + [(cx + 115, 1180), (cx - 115, 1180)], 0.93, 3)  # backrest
        k.stroke([(cx - 125, 1180), (cx - 125, 1560)], 16, 14, 0.95); k.stroke([(cx + 125, 1180), (cx + 125, 1560)], 16, 14, 0.95)
        ang = 90
        if i == 2 and lt >= flip_t: ang = max(0, 90 - 300 * (lt - flip_t))
        k.wash(seat_poly(cx, 1230, ang, 230), 0.97, 2)
    base = k.apply(img)
    # Arjun's arm resting at left seat
    kk = Ink(seed=607); kk.stroke(bezier((0, 1100), (180, 1150), (300, 1200)), 70, 50, 0.97, dry=0.05)
    base = kk.apply(base)
    base = text(base, "J-7", (400, 1640), 54, (200, 190, 180), stroke=3)
    base = text(base, "J-8", (680, 1640), 54, RED * 1.3, stroke=3)
    shake = 6 * math.sin(t * 60) if (lt >= flip_t and lt - flip_t < 0.35) else 0
    return zoom(base, 1.05 + 0.2 * p, 680, 1200, dx=shake)

def sc_popcorn(lt, dur, t):
    """darkness; red-white popcorn tub on the armrest; charred fingers reach in from the right."""
    p = lt / max(dur, 0.1)
    img = PAPER.copy() * 0.28
    img = glow(img, 540, 300, 800, SCREEN, 0.25 * flicker(t, 5))
    # tub
    top, bot = 800, 1500
    for i in range(8):
        x0 = 330 + i * 52.5; x1 = x0 + 52.5
        poly = np.int32([(x0, top), (x1, top), (380 + (i + 1) * 40, bot), (380 + i * 40, bot)])
        cv2.fillPoly(img, [poly], tuple(float(v) for v in (RED * 0.9 if i % 2 == 0 else np.array([200, 195, 190]))), cv2.LINE_AA)
    rng = np.random.default_rng(5)
    for i in range(70):                                                             # popcorn heap
        x = 340 + rng.random() * 400; y = top - 10 - rng.random() * 120 * (1 - abs(x - 540) / 240)
        cv2.circle(img, (int(x), int(y)), int(18 + rng.random() * 14), (235, 225, 190), -1, cv2.LINE_AA)
        cv2.circle(img, (int(x + 5), int(y + 6)), 8, (190, 170, 120), -1, cv2.LINE_AA)
    # charred hand reaching in & pulling out
    r = min(1, p * 1.8); back = max(0, (p - 0.65) / 0.35)
    hx = 1080 - 470 * r + 260 * back; hy = 760 - 30 * math.sin(r * 3) - 80 * back
    k = Ink(seed=608)
    k.stroke(bezier((1100, 1050), (900, 900), (hx, hy)), 80, 46, 0.99, dry=0.25)
    for f in range(4):
        k.stroke([(hx, hy - 10 + f * 16), (hx - 120 - (f % 2) * 25, hy - 30 + f * 24)], 20, 8, 0.99, dry=0.2)
    base = k.apply(img, np.array([24, 18, 16], np.float32))
    for f in range(5):                                                              # embers on burnt skin
        ex = int(hx + 60 + f * 70); ey = int(hy + 40 + f * 30 * math.sin(f))
        base = glow(base, ex, ey, 40, FIRE, 0.5 * (0.5 + 0.5 * math.sin(t * 9 + f)))
    return zoom(base, 1.05 + 0.18 * p, 560, 900)

def sc_interval(lt, dur, t):
    """lights on: J-8 empty, an old burnt ticket lies on it; push-in to '13-11-1998'."""
    p = lt / max(dur, 0.1)
    img = PAPER.copy() * 0.95
    k = Ink(seed=609)
    k.wash(cv2.ellipse2Poly((540, 500), (330, 160), 0, 180, 360, 10).tolist() + [(870, 1000), (210, 1000)], 0.75, 4)
    k.wash([(170, 1040), (910, 1040), (980, 1350), (100, 1350)], 0.65, 4)          # open seat cushion
    k.stroke([(150, 1000), (150, 1800)], 30, 24, 0.85); k.stroke([(930, 1000), (930, 1800)], 30, 24, 0.85)
    img = k.apply(img)
    # ticket with charred edges
    tk = np.zeros((H, W), np.float32)
    poly = np.int32([(330, 1100), (760, 1070), (780, 1290), (345, 1320)])
    cv2.fillPoly(tk, [poly], 1.0, cv2.LINE_AA)
    t3 = tk[..., None]
    img = img * (1 - t3) + PINK * 0.85 * t3
    img = text(img, "RAJ TALKIES", (555, 1150), 46, (120, 25, 35), stroke=0, rot=4)
    img = text(img, "13-11-1998", (560, 1230), 64, BLUE, stroke=0, font=FH, rot=4)
    kb = Ink(seed=610)
    for e in range(18):                                                             # burnt edges
        x = 330 + e * 26; kb.blot(x, 1088 - e * 1.6 + (e % 3) * 6, 22 + (e % 4) * 6, 0.95)
        kb.blot(760 + (e % 3) * 8, 1090 + e * 12, 18 + (e % 3) * 6, 0.95)
    img = kb.apply(img, np.array([30, 22, 18], np.float32))
    return zoom(img, 1.0 + 0.7 * p, 560, 1200)

def sc_fire(lt, dur, t):
    """memory: same hall in 1998 on fire; a girl's silhouette in seat J-8."""
    p = lt / max(dur, 0.1)
    k = Ink(seed=611); k.a = HK.a.copy()
    k.a = np.maximum(k.a, ghost_alpha(0.0))
    base = k.apply(PAPER.copy() * 0.55)
    for i in range(9):                                                              # flames
        fx = 60 + i * 120; amp = 140 + 60 * math.sin(t * 7 + i * 1.7)
        base = glow(base, fx, 1650 - amp, 160 + 40 * math.sin(t * 5 + i), FIRE, 0.75)
        base = glow(base, fx + 40, 1400 - amp * 1.4, 110, RED * 1.3, 0.55)
    ks = Ink(seed=612)
    for i in range(7):                                                              # smoke strokes rising
        x = 100 + i * 150; o = (t * 120 + i * 90) % 600
        ks.stroke(bezier((x, 1300 - o), (x + 80, 1000 - o), (x - 40, 700 - o)), 60, 20, 0.5, dry=0.3)
    base = ks.apply(base)
    base = text(base, "1998", (540, 520), 160, np.array([240, 230, 210]) * (0.6 + 0.4 * flicker(t, 7)), stroke=6)
    return zoom(base, 1.08 + 0.15 * p, 540, 1200, dx=4 * math.sin(t * 40))

_GH = {}
def ghost_alpha(sway, cx=700, feet=1900, h=1000):
    key = (round(sway * 5) / 5, cx, feet, h)
    if len(_GH) > 30: _GH.clear()
    if key not in _GH:
        g = Ink(seed=9); ghost_front(g, cx, feet, h, sway=key[0]); _GH[key] = g.a
    return _GH[key]

def sc_screen(lt, dur, t):
    """film freezes; on the screen: Arjun from behind in his seat, a burnt girl's head resting on his shoulder.
    Foreground: the real Arjun, seat beside him empty."""
    p = lt / max(dur, 0.1)
    k = Ink(seed=613); k.a = HK.a.copy()
    base = k.apply(PAPER.copy() * 0.6)
    show = lt >= (SRT[12][0] - (t - lt))
    col = SCREEN if not show else np.array([200, 205, 215], np.float32)
    base = screen_light(base, t, 1.0, col)
    if lt < 0.5 or not show:                                                        # film 'stops': scratch lines
        for i in range(6):
            x = int(SX0 + ((i * 137 + int(t * 50) * 31) % (SX1 - SX0)))
            cv2.line(base, (x, SY0), (x + 3, SY1), (90, 90, 100), 2)
    if show:
        si = Ink(seed=614)
        person_back(si, 470, 860, 500, walk=False, hair_long=False)                # Arjun on screen (cut at bottom)
        gi = Ink(seed=15); e1, e2, hu = ghost_front(gi, 610, 1080, 640, sway=0.2)
        R = cv2.getRotationMatrix2D((610, 1080), 9, 1.0)
        si.a = np.maximum(si.a, cv2.warpAffine(gi.a, R, (W, H)))
        e1, e2 = [tuple(R @ np.array([x, y, 1.0])) for (x, y) in (e1, e2)]
        m = np.zeros((H, W), np.float32); m[SY0:SY1, SX0:SX1] = 1
        a = (si.a * m)[..., None]
        base = base * (1 - a) + INK * a
        if p > 0.5:
            for (ex, ey) in (e1, e2): cv2.circle(base, (int(ex), int(ey)), 5, (255, 30, 30), -1, cv2.LINE_AA)
        base = glow(base, 560, 560, 120, FIRE, 0.25 * (0.5 + 0.5 * math.sin(t * 8)))
    g = man('sit', 0, False, 380, 2400, 1300)
    base = base * (1 - g[..., None]) + INK * g[..., None]
    return zoom(base, 1.0 + 0.35 * p, 540, 560)

def sc_whisper(lt, dur, t):
    """extreme close: burnt girl leaning in at his ear, hair over face, red eyes, ash drifting."""
    p = lt / max(dur, 0.1)
    img = PAPER.copy() * 0.3
    img = glow(img, 540, 700, 600, SCREEN, 0.2 * flicker(t, 8))
    sway = math.sin(t * 1.8) * 0.4
    a = ghost_alpha(sway, 620, 3300, 2600)
    base = img * (1 - a[..., None]) + np.array([20, 15, 14], np.float32) * a[..., None]
    g = Ink(seed=9); e1, e2, hu = ghost_front(g, 620, 3300, 2600, sway=0)
    if p > 0.25:
        for (ex, ey) in (e1, e2):
            cv2.circle(base, (int(ex), int(ey)), 12, (255, 35, 30), -1, cv2.LINE_AA)
            base = glow(base, ex, ey, 60, RED * 1.4, 0.4)
    # Arjun's ear/cheek silhouette at left
    k = Ink(seed=616); k.wash(cv2.ellipse2Poly((-40, 1100), (260, 520), 0, 0, 360, 10), 0.98, 3)
    k.wash(cv2.ellipse2Poly((200, 1050), (55, 95), 0, 0, 360, 10), 0.98, 2)
    base = k.apply(base)
    rng = np.random.default_rng(3)
    for i in range(40):                                                             # ash
        x = (rng.random() * W + t * 30 * (rng.random() - .5)) % W; y = (rng.random() * H + t * 90 * (0.5 + rng.random())) % H
        cv2.circle(base, (int(x), int(y)), int(2 + rng.random() * 3), (200, 200, 195) if i % 3 else tuple(float(v) for v in FIRE), -1, cv2.LINE_AA)
    return zoom(base, 1.0 + 0.25 * p, 600, 900, dx=-80 * p)

SCENES = [sc_hook, sc_hall, sc_seat, sc_popcorn, sc_interval, sc_fire, sc_screen, sc_whisper]

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
    img = text(img, "RAJ TALKIES  |  HORROR STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
