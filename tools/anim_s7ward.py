"""Standalone story 'BED NO. 11' (govt hospital night ward: 10 beds but night chart lists 11 patients) -
procedural ink-wash animation (no stock footage).  python3 anim_s7ward.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FH = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"   # 'handwriting'
FPS = 30
END_CARD = 2.8
TITLE = "BED NO. 11"

CAPS = ["WARD MEIN SIRF 10 BED HAIN...", "PAR AAJ RAAT KE CHART PE 11 MAREEZ THE",
        "MAIN MEENA. SARKARI HOSPITAL KI NIGHT SHIFT NURSE",
        "11 NUMBER PE LIKHA THA: SHANTI DEVI", "DAWAI, RAAT 2 BAJE",
        "WARD BOY BOLA, MADAM, SHANTI DEVI TOH KAL RAAT HI CHAL BASI", "11 NUMBER KA BED TAB SE HATA DIYA",
        "THEEK 2 BAJE, KHAALI KONE SE...", "BED KI CHARR-CHARR AAWAAZ AAYI",
        "TORCH MAARI... DEEWAR PE EK BED KI PARCHHAI THI", "AUR US PE KOI BAITHA THA",
        "MAINE CHART DEKHA... 11 NUMBER PE NAYA NAAM THA", "MERI LIKHAWAT MEIN... MEENA",
        "PEECHHE SE THANDI AAWAAZ AAYI...", "SISTER, AB AAPKI DAWAI KA TIME HAI"]
HOT = {"10", "11", "2", "CHAL", "BASI", "HATA", "KHAALI", "CHARRCHARR", "PARCHHAI", "BAITHA", "MEENA", "DAWAI", "TIME"}
SCENE_OF = [0, 0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]
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
TUBE = np.array([225, 245, 235], np.float32)
GREEN = np.array([205, 222, 205], np.float32)
TORCH = np.array([255, 240, 200], np.float32)
VX, VY, F = 540, 820, 420

def P(X, Y, z):
    return (VX + X * F / z, VY + Y * F / z)

# ---------- ward background (perspective, 10 iron beds, empty corner where bed 11 was) ----------
def ward_bg(seed=701, marks=True):
    k = Ink(seed=seed)
    zf = 9.5
    # floor + walls + ceiling planes
    k.wash([P(-3, 2.5, 0.6), P(3, 2.5, 0.6), P(3, 2.5, zf), P(-3, 2.5, zf)], 0.45, 10)
    k.wash([P(-3, -2.5, 0.6), P(-3, 2.5, 0.6), P(-3, 2.5, zf), P(-3, -2.5, zf)], 0.3, 10)
    k.wash([P(3, -2.5, 0.6), P(3, 2.5, 0.6), P(3, 2.5, zf), P(3, -2.5, zf)], 0.3, 10)
    k.wash([P(-3, -2.5, zf), P(3, -2.5, zf), P(3, 2.5, zf), P(-3, 2.5, zf)], 0.55, 6)       # back wall
    k.wash([P(-0.6, 0.0, zf), P(0.6, 0.0, zf), P(0.6, 2.5, zf), P(-0.6, 2.5, zf)], 0.9, 3)   # dark door
    for z in (1.4, 2.7, 4.0, 5.3, 6.6):
        for side in (-1, 1):
            if side == 1 and z > 6: continue                       # right side: only 4 beds... (bed 10 at left back)
            draw_bed(k, side, z)
    draw_bed(k, -1, 7.9)                                            # bed 10 (left, last)
    # right back corner (z 6.6-8.6) is EMPTY: rust marks where bed 11 stood
    if marks:
        for X, z in ((2.9, 7.0), (1.3, 7.0), (2.9, 7.9), (1.3, 7.9)):
            x, y = P(X, 2.5, z); k.blot(x, y, 5, 0.9)
    # tube lights on ceiling
    return k

def draw_bed(k, side, z, L=0.9):
    X0, X1 = 3 * side, 1.2 * side
    top = [P(X0, 1.5, z), P(X1, 1.5, z), P(X1, 1.5, z + L), P(X0, 1.5, z + L)]
    k.wash(top, 0.18, 2)                                            # sheet
    for X in (X1,):
        for zz in (z, z + L):
            a = P(X, 1.5, zz); b = P(X, 2.5, zz); k.stroke([a, b], 9 / zz * 3, 6 / zz * 3, 0.95, dry=0)
    a, b = P(X1, 1.5, z), P(X1, 1.5, z + L); k.stroke([a, b], 8 / z * 3, 6 / z * 3, 0.95, dry=0)
    hb0, hb1 = P(X0, 0.6, z), P(X1, 0.6, z)                         # headboard rail
    k.stroke([hb0, hb1], 7 / z * 3, 6 / z * 3, 0.95, dry=0)
    k.stroke([P(X1, 0.6, z), P(X1, 1.5, z)], 7 / z * 3, 6 / z * 3, 0.95, dry=0)
    k.wash([P(X0, 1.25, z + 0.05), P(X0 * 0.75 + X1 * 0.25, 1.25, z + 0.05), P(X0 * 0.75 + X1 * 0.25, 1.45, z + 0.3), P(X0, 1.45, z + 0.3)], 0.08, 2)

WK = ward_bg()

def tubes(img, t, amt=1.0, kill=None):
    for i, z in enumerate((1.6, 3.0, 4.6, 6.3, 8.0)):
        if kill is not None and i >= kill: continue
        f = flicker(t, 11 + i * 3) * amt
        x, y = P(0, -2.5, z)
        img = glow(img, x, y + 10, 260 / z * 2.2, TUBE, 0.55 * f)
        cv2.line(img, (int(P(-0.7, -2.45, z)[0]), int(y)), (int(P(0.7, -2.45, z)[0]), int(y)), (250, 255, 250), max(2, int(14 / z)), cv2.LINE_AA)
    return img

def ward_base(t, dark=0.0, kill=None):
    k = Ink(seed=705); k.a = WK.a.copy()
    base = k.apply(PAPER.copy() * GREEN / 228 * (0.95 - dark))
    return tubes(base, t, 1 - dark, kill)

_FIG = {}
def fig(key, phase, cx, feet, h, walk=True, hair=True, dress="kurta"):
    ph = round(phase * 2) / 2
    if len(_FIG) > 40: _FIG.clear()
    k2 = (key, ph, int(cx), int(feet), int(h))
    if k2 not in _FIG:
        g = Ink(seed=7); person_back(g, cx, feet, h, phase=ph, walk=walk, hair_long=hair, dress=dress); _FIG[k2] = g.a
    return _FIG[k2]

_GH = {}
def ghost_alpha(sway, cx=700, feet=1900, h=1000):
    key = (round(sway * 5) / 5, int(cx), int(feet), int(h))
    if len(_GH) > 30: _GH.clear()
    if key not in _GH:
        g = Ink(seed=9); ghost_front(g, cx, feet, h, sway=key[0]); _GH[key] = g.a
    return _GH[key]

# ---------- night-round chart ----------
NAMES = ["Ramesh", "Sunita", "Abdul", "Kamla", "Gopal", "Rekha", "Mohan", "Fatima", "Suresh", "Lakshmi"]
_CH = {}
def chart(name11="Shanti Devi", reveal=1.0):
    key = (name11, round(reveal, 2))
    if len(_CH) > 60: _CH.clear()
    if key in _CH: return _CH[key].copy()
    img = paper(seed=71) * (np.array([236, 238, 226], np.float32) / 228)
    k = Ink(seed=702)
    for i in range(16): k.blot(80 + (i * 233) % 920, 260 + (i * 397) % 1500, 25 + (i * 13) % 50, 0.07)
    img = k.apply(img, np.array([120, 110, 70], np.float32))
    cv2.rectangle(img, (380, 60), (700, 120), (90, 90, 95), -1, cv2.LINE_AA)            # clipboard clip
    img = text(img, "GENERAL WARD - B", (540, 250), 70, INK, stroke=0)
    img = text(img, "NIGHT ROUND   10-11-2026", (540, 325), 46, INK, stroke=0)
    img = text(img, "TOTAL BEDS : 10", (540, 400), 56, BLUE, stroke=0, font=FH)
    cv2.line(img, (100, 445), (980, 445), (40, 40, 50), 3, cv2.LINE_AA)
    y0, dy = 500, 66
    for i in range(10):
        y = y0 + i * dy
        img = text(img, f"{i+1}.", (130, y), 50, INK, "lm", 0)
        img = text(img, NAMES[i], (230, y), 52, BLUE, "lm", 0, FH)
        img = text(img, ["10 PM", "11 PM", "12 AM", "6 AM"][i % 4], (960, y), 44, INK, "rm", 0)
        cv2.line(img, (100, int(y + 36)), (980, int(y + 36)), (150, 150, 150), 1, cv2.LINE_AA)
    y = y0 + 10 * dy + 10
    img = text(img, "11.", (130, y), 74, RED * 1.1, "lm", 0)
    red = name11 != "Shanti Devi"
    nm = text(img.copy(), name11, (230, y), 62, RED * 1.1 if red else BLUE, "lm", 0, FH)
    if reveal < 1:
        xcut = int(230 + 520 * reveal); img[:, :xcut] = nm[:, :xcut]
    else: img = nm
    img = text(img, "2:00 AM", (960, y), 50, RED * 1.1, "rm", 0)
    _CH[key] = img
    return img.copy()

CH_Y11 = 500 + 10 * 66 + 10

def sc_hook(lt, dur, t):
    """FULL-SCREEN proof: 'TOTAL BEDS: 10' but a 11th patient row, '11' circled in red."""
    p = lt / max(dur, 0.1)
    img = chart()
    kr = Ink(seed=703)
    ell = cv2.ellipse2Poly((150, CH_Y11), (80, 66), -8, 0, int(40 + 330 * min(1, p * 1.6)), 6)
    if len(ell) > 2: kr.stroke(ell, 10, 6, 0.95, dry=0.1)
    kr.stroke([(640, 422), (740, 422)], 7, 4, 0.9)                                    # '10' underlined
    img = kr.apply(img, RED * 1.15)
    img = img * (0.8 + 0.2 * flicker(t, 1))
    return zoom(img, 1.02 + 0.12 * p, 540, 800)

def sc_ward(lt, dur, t):
    """long government ward at night; Meena (nurse) walks down the aisle."""
    p = lt / max(dur, 0.1)
    base = ward_base(t)
    g = fig('walk', t * 5, 540, 1900 - 280 * p, 900 - 300 * p)
    base = base * (1 - g[..., None]) + INK * g[..., None]
    return zoom(base, 1.04 + 0.12 * p, 540, 900)

def sc_chart(lt, dur, t):
    """close-up of row 11 on the clipboard: 'Shanti Devi - 2:00 AM'."""
    p = lt / max(dur, 0.1)
    img = chart()
    img = light(img, 520, CH_Y11, 700, t, 0.5)
    return zoom(img, 1.15 + 0.15 * p, 540, CH_Y11, dy=880 - CH_Y11)

def sc_corner(lt, dur, t):
    """ward boy at left foreground; push-in to the empty right corner with rust marks where bed 11 stood."""
    p = lt / max(dur, 0.1)
    base = ward_base(t, 0.15)
    g = fig('boy', 0, 270, 2050, 1150, walk=False, hair=False, dress="shirt")
    base = base * (1 - g[..., None]) + INK * g[..., None]
    cx, cy = P(2.1, 2.3, 7.4)
    return zoom(base, 1.05 + 0.7 * p, cx * p + 540 * (1 - p), cy * p + 900 * (1 - p))

def sc_clock(lt, dur, t):
    """wall clock hits 2:00; lights die one by one; the empty corner creaks (shake)."""
    p = lt / max(dur, 0.1)
    kill = 5 - int(min(4, p * 6))
    base = ward_base(t, 0.35 + 0.3 * p, kill)
    cx, cy = P(3, -1.3, 7.4)
    cv2.circle(base, (int(cx), int(cy)), 46, (235, 235, 225), -1, cv2.LINE_AA)
    cv2.circle(base, (int(cx), int(cy)), 46, (20, 20, 20), 4, cv2.LINE_AA)
    cv2.line(base, (int(cx), int(cy)), (int(cx), int(cy - 34)), (20, 20, 20), 4, cv2.LINE_AA)        # 12
    cv2.line(base, (int(cx), int(cy)), (int(cx + 20), int(cy - 12)), (20, 20, 20), 5, cv2.LINE_AA)   # 2
    a = t * 6.28; cv2.line(base, (int(cx), int(cy)), (int(cx + 38 * math.sin(a)), int(cy - 38 * math.cos(a))), (175, 18, 28), 2, cv2.LINE_AA)
    creak = (lt * 3) % 1 < 0.3 and p > 0.4
    sh = 7 * math.sin(t * 70) if creak else 0
    if creak:
        ex, ey = P(2.1, 1.8, 7.4)
        base = glow(base, ex, ey, 180, np.array([40, 40, 45], np.float32), 0.5)
    z = 1.0 + 1.6 * min(1, p * 1.3)
    return zoom(base, z, cx, cy + 150 * p, dx=sh)

def sc_torch(lt, dur, t):
    """pitch dark; torch beam on the wall: shadow of a hospital bed with someone sitting on it - but no bed."""
    p = lt / max(dur, 0.1)
    img = PAPER.copy() * GREEN / 228 * 0.12
    bx = 560 + 60 * math.sin(t * 2.3) * (1 - p); by = 760 + 30 * math.sin(t * 3.1)
    beam = PAPER.copy() * TORCH / 228 * 0.95
    d = np.sqrt((xx - bx) ** 2 + (yy - by) ** 2)
    m = np.clip(1 - (d / 470) ** 4, 0, 1)[..., None].astype(np.float32) * (0.85 + 0.15 * flicker(t, 2))
    img = img * (1 - m) + beam * m
    # shadow (blurred ink, only visible inside the beam)
    k = Ink(seed=704)
    k.wash([(260, 900), (820, 900), (820, 960), (260, 960)], 0.9, 6)                     # mattress edge
    k.stroke([(280, 960), (280, 1150)], 20, 18, 0.9); k.stroke([(800, 960), (800, 1150)], 20, 18, 0.9)
    k.stroke([(250, 620), (250, 960)], 18, 16, 0.9); k.stroke([(250, 640), (420, 640)], 16, 14, 0.9)
    g = ghost_alpha(0.3 * math.sin(t * 1.2), 600, 1000, 680)
    k.a = np.maximum(k.a, g * (y_cut := (yy < 920).astype(np.float32)))
    sa = cv2.GaussianBlur(k.a, (0, 0), 5)
    img = img * (1 - (sa * m[..., 0])[..., None] * 0.85) + INK * 0.0
    # torch in her hand at the bottom
    kt = Ink(seed=706)
    kt.stroke(bezier((330, 1950), (420, 1700), (480, 1560)), 120, 70, 0.98, dry=0.05)
    kt.wash([(450, 1480), (560, 1480), (540, 1600), (470, 1600)], 0.98, 2)
    img = kt.apply(img)
    return zoom(img, 1.02 + 0.25 * p, 560, 800)

def sc_name(lt, dur, t):
    """the chart again: row 11 now reads 'Meena' in her own handwriting, ink being written."""
    p = lt / max(dur, 0.1)
    img = chart("Meena", min(1, p * 1.8))
    img = light(img, 450, CH_Y11, 650, t, 0.6)
    k = Ink(seed=707)
    for i in range(int(min(1, p * 1.8) * 5)):                                          # wet ink drips
        k.stroke([(260 + i * 70, CH_Y11 + 30), (262 + i * 70, CH_Y11 + 30 + 50 * p + i * 9)], 6, 3, 0.9, dry=0)
    img = k.apply(img, RED)
    return zoom(img, 1.2 + 0.2 * p, 540, CH_Y11, dy=880 - CH_Y11)

def sc_whisper(lt, dur, t):
    """extreme close: dead patient leaning in at Meena's ear, hair over face, red eyes, drip stand behind."""
    p = lt / max(dur, 0.1)
    img = PAPER.copy() * GREEN / 228 * 0.32
    img = glow(img, 640, 500, 600, TUBE, 0.22 * flicker(t, 8))
    kd = Ink(seed=708); kd.stroke([(900, 0), (900, 1300)], 12, 10, 0.9); kd.wash(cv2.ellipse2Poly((900, 260), (50, 90), 0, 0, 360, 10), 0.5, 4)
    img = kd.apply(img)
    sway = math.sin(t * 1.8) * 0.4
    a = ghost_alpha(sway, 620, 3300, 2600)
    base = img * (1 - a[..., None]) + np.array([16, 18, 16], np.float32) * a[..., None]
    g = Ink(seed=9); e1, e2, hu = ghost_front(g, 620, 3300, 2600, sway=0)
    if p > 0.25:
        for (ex, ey) in (e1, e2):
            cv2.circle(base, (int(ex), int(ey)), 12, (255, 35, 30), -1, cv2.LINE_AA)
            base = glow(base, ex, ey, 60, RED * 1.4, 0.4)
    # Meena's nurse cap + cheek silhouette at left
    k = Ink(seed=716); k.wash(cv2.ellipse2Poly((-40, 1100), (260, 520), 0, 0, 360, 10), 0.98, 3)
    k.wash(cv2.ellipse2Poly((200, 1050), (55, 95), 0, 0, 360, 10), 0.98, 2)
    base = k.apply(base)
    cv2.fillPoly(base, [np.int32([(-20, 590), (230, 560), (250, 650), (0, 690)])], (235, 235, 230), cv2.LINE_AA)
    cv2.line(base, (60, 620), (170, 605), (175, 18, 28), 8, cv2.LINE_AA)                 # red cross band
    return zoom(base, 1.0 + 0.25 * p, 600, 900, dx=-80 * p)

SCENES = [sc_hook, sc_ward, sc_chart, sc_corner, sc_clock, sc_torch, sc_name, sc_whisper]

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
    img = text(img, TITLE + "  |  HORROR STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
