"""Standalone story 'HAAZRI' (girls hostel roll-call, Dehradun) - procedural ink-wash animation (no stock footage).
python3 anim_s2haazri.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FPS = 30
END_CARD = 2.8
TITLE = "HAAZRI"

CAPS = ["HOSTEL KI RAAT KI HAAZRI MEIN...", "30 NAAM BOLE GAYE...", "PAR \"PRESENT\" 31 BAAR AAYA!",
        "MAIN SIMRAN, DEHRADUN GIRLS HOSTEL", "WARDEN KA CHEHRA SAFED PAD GAYA",
        "31VI AWAAZ AAYI THI ROOM NO. 9 SE...", "JO 10 SAAL SE BAND HAI",
        "RIYA BOLI: WAHAN EK LADKI", "HAAZRI KE WAQT GAAYAB HUI THI...", "TAB SE HAR RAAT",
        "EK PRESENT ZYADA AATA HAI",
        "RAAT 2 BAJE... DARWAZE PE DASTAK", "\"SIMRAN... DARWAZA KHOLO, HAAZRI BAAKI HAI\"",
        "DARWAZE KE NEECHE SE...", "LAMBE GEELE BAAL ANDAR PHAILNE LAGE",
        "MAINE RIYA KO JAGANE KE LIYE MUDKE DEKHA...", "USKA BISTAR KHAALI THA",
        "AUR BAHAR SE RIYA KI AWAAZ AAYI...", "\"PRESENT.\""]
HOT = {"31", "PRESENT", "31VI", "9", "BAND", "GAAYAB", "ZYADA", "DASTAK", "BAAKI", "BAAL", "GEELE", "KHAALI", "RIYA"}
SCENE_OF = [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5]
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

_GL = {}
def glow(img, cx, cy, r, col, amt):
    key = (int(cx), int(cy), int(r))
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

WARM = np.array([255, 205, 130], np.float32)
COLD = np.array([190, 205, 230], np.float32)

# ---------- backgrounds (built once) ----------
def register_bg():
    k = Ink(seed=81)
    k.wash_rect(0, 0, W, H, 0.8, 30)                                     # dark desk
    for i in range(12):
        y = 90 + i * 165 + (i % 3) * 11
        k.stroke([(0, y), (W * 0.5, y + 10), (W, y - 8)], 2.5, 2, 0.98, dry=0.5)
    pg = [(150, 330), (950, 300), (980, 1500), (120, 1530)]
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [np.int32(pg)], 1); m = cv2.GaussianBlur(m, (0, 0), 3)
    k.a = k.a * (1 - m) + 0.05 * m
    k.stroke(pg + [pg[0]], 3, 2.5, 0.7)
    k.stroke([(300, 340), (275, 1515)], 2, 2, 0.45)                       # margin line
    w = np.zeros((H, W), np.float32)
    put(w, "GIRLS HOSTEL - NIGHT ROLL CALL", (190, 420), cv2.FONT_HERSHEY_DUPLEX, 1.05, 2)
    names = ["Anjali", "Bhavna", "Divya", "Farah", "Gunjan", "Isha", "Jyoti", "Kavya", "Lata", "Meenu",
             "Neelam", "Pooja", "Riya", "Simran"]
    for r, nm in enumerate(names):
        y = 520 + r * 62
        k.stroke([(180, y + 14), (940, y - 6)], 1.2, 1, 0.25, dry=0.3)
        put(w, f"{17 + r}", (190, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        put(w, nm, (330, y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.5, 3)
        put(w, "P", (820, y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.5, 3)
    put(w, "Total girls: 30", (330, 1420), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.5, 3)
    k.a = np.maximum(k.a, w * 0.9)
    red = np.zeros((H, W), np.float32)
    put(red, "Present: 31 ?", (330, 1530) , cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.1, 5)
    return k, red

RK, RRED = register_bg()

VX, VY = 540, 900   # corridor vanishing point
def corridor_bg():
    k = Ink(seed=91)
    k.wash_rect(0, 0, W, H, 0.55, 30)
    k.wash([(0, 0), (VX - 90, VY - 160), (VX - 90, VY + 160), (0, H)], 0.72, 8)   # left wall
    k.wash([(W, 0), (VX + 90, VY - 160), (VX + 90, VY + 160), (W, H)], 0.72, 8)   # right wall
    k.wash([(0, H), (VX - 90, VY + 160), (VX + 90, VY + 160), (W, H)], 0.45, 8)   # floor
    k.wash_rect(VX - 90, VY - 160, VX + 90, VY + 160, 0.93, 3)                    # far end darkness
    for d in range(1, 6):                                                          # doors both sides
        f = 1 / (1 + d * 0.55)
        for side in (-1, 1):
            x0 = VX + side * (90 + 900 * f); x1 = VX + side * (90 + 760 * f)
            yt0, yb0 = VY - 900 * f, VY + 1000 * f
            yt1, yb1 = VY - 760 * f, VY + 850 * f
            k.wash([(x0, yt0), (x1, yt1), (x1, yb1), (x0, yb0)], 0.95, 2)
            k.stroke([(x0, yt0), (x1, yt1), (x1, yb1), (x0, yb0), (x0, yt0)], 4 * f + 1, 3 * f + 1, 0.99)
    for i in range(8):                                                             # floor tiles
        f = 1 / (1 + i * 0.45); y = VY + 160 + (H - VY - 160) * f
        k.stroke([(VX - 90 - (y - VY - 160) * 0.62, y), (VX + 90 + (y - VY - 160) * 0.62, y)], 2, 2, 0.4)
    # far door "9" with chain
    k.wash_rect(VX - 60, VY - 120, VX + 60, VY + 160, 0.99, 2)
    w = np.zeros((H, W), np.float32); put(w, "9", (VX - 16, VY - 60), cv2.FONT_HERSHEY_DUPLEX, 1.4, 3)
    return k, w

CK, C9 = corridor_bg()

def room_bg():
    k = Ink(seed=101)
    k.wash_rect(0, 0, W, H, 0.6, 25)
    k.wash([(0, 1250), (W, 1200), (W, H), (0, H)], 0.4, 8)                   # floor
    k.wash_rect(620, 300, 960, 760, 0.18, 4)                                  # window (moon)
    k.stroke([(620, 300), (960, 300), (960, 760), (620, 760), (620, 300)], 10, 8)
    k.stroke([(790, 300), (790, 760)], 7, 6); k.stroke([(620, 530), (960, 530)], 7, 6)
    for x in range(650, 960, 45): k.stroke([(x, 300), (x, 760)], 3, 3, 0.8)   # grill
    # bed left (Riya's) - frame + mattress + pillow
    k.wash([(40, 1050), (700, 1000), (760, 1180), (60, 1250)], 0.5, 4)
    k.stroke([(40, 1050), (700, 1000), (760, 1180), (60, 1250), (40, 1050)], 5, 4)
    k.wash([(60, 1250), (760, 1180), (760, 1300), (60, 1380)], 0.9, 3)
    for x in (60, 740): k.stroke([(x, 1300), (x, 1480)], 10, 8)
    k.wash(cv2.ellipse2Poly((180, 1060), (110, 45), -5, 0, 360, 10), 0.22, 4)
    # almirah right
    k.wash_rect(820, 820, 1060, 1450, 0.85, 3); k.stroke([(940, 830), (940, 1440)], 3, 3)
    return k

RMK = room_bg()

DX0, DY0, DX1, DY1 = 250, 320, 830, 1560      # door rect (from inside)
def door_bg():
    k = Ink(seed=111)
    k.wash_rect(0, 0, W, H, 0.82, 25)
    k.wash([(0, 1560), (W, 1560), (W, H), (0, H)], 0.55, 6)                   # floor
    k.wash_rect(DX0, DY0, DX1, DY1, 0.62, 3)
    k.stroke([(DX0, DY0), (DX1, DY0), (DX1, DY1), (DX0, DY1), (DX0, DY0)], 16, 14, 0.99, dry=0)
    for (a, b, c, d) in ((310, 400, 770, 900), (310, 980, 770, 1480)):        # panels
        k.stroke([(a, b), (c, b), (c, d), (a, d), (a, b)], 4, 4, 0.9)
    k.blot(780, 960, 18, 0.99); k.stroke([(780, 960), (730, 965)], 8, 6)      # handle
    k.stroke([(700, 700), (800, 700)], 8, 8, 0.99, dry=0)                      # latch bolt
    return k

DK = door_bg()

def bed_bg():
    k = Ink(seed=121)
    k.wash_rect(0, 0, W, H, 0.78, 25)
    k.wash([(0, 1300), (W, 1250), (W, H), (0, H)], 0.6, 8)
    k.wash([(60, 820), (1020, 780), (1060, 1180), (20, 1240)], 0.3, 6)        # mattress top (close)
    k.stroke([(60, 820), (1020, 780), (1060, 1180), (20, 1240), (60, 820)], 6, 5)
    k.wash([(20, 1240), (1060, 1180), (1060, 1360), (20, 1420)], 0.92, 3)
    k.wash(cv2.ellipse2Poly((300, 880), (180, 70), -3, 0, 360, 10), 0.12, 5) # pillow
    k.stroke(cv2.ellipse2Poly((300, 880), (180, 70), -3, 0, 360, 10)[::2], 3, 3, 0.7)
    # thrown-back sheet with folds
    for i in range(6):
        k.stroke(bezier((520 + i * 70, 820), (560 + i * 60, 1000), (500 + i * 80, 1200)), 3, 1.5, 0.6)
    k.wash(cv2.ellipse2Poly((560, 1010), (260, 90), -4, 0, 360, 10), 0.28, 14)  # body dent
    return k

BDK = bed_bg()

def hair_under_door(k, prog, t, y=DY1, spread=1.0, val=0.97):
    """wet long hair creeping in from under the door gap toward camera."""
    rng = np.random.default_rng(5)
    n = 34
    for i in range(n):
        x0 = DX0 + 40 + (DX1 - DX0 - 80) * i / (n - 1)
        L = (80 + 520 * prog * spread) * (0.6 + 0.6 * rng.random())
        ang = (x0 - (DX0 + DX1) / 2) / 900
        pts = []
        for j in range(10):
            f = j / 9
            pts.append((x0 + math.sin(ang) * L * f * 1.4 + math.sin(t * 2 + i + f * 5) * 10 * f, y + 4 + L * f))
        k.stroke(pts, 11, 2.0, val, jitter=0.6, dry=0.1)
    if prog > 0:
        k.wash([(DX0 + 30, y), (DX1 - 30, y), (DX1 + 60 * prog, y + 260 * prog), (DX0 - 60 * prog, y + 260 * prog)], val * 0.9, 6)

_FIG = {}
def fig_alpha(key, sway, fn):
    sk = round(sway * 5) / 5
    if (key, sk) not in _FIG:
        g = Ink(seed=7); fn(g, sk); _FIG[(key, sk)] = g.a
    return _FIG[(key, sk)]

# ---------- scenes ----------
def sc_register(lt, dur, t):
    base = RK.apply(PAPER.copy())
    p = lt / max(dur, 0.1)
    reveal = min(1, max(0, (lt - 1.2) / 1.0))
    rm = RRED * (xx < 330 + 700 * reveal)
    if lt > 2.3:
        c = np.zeros((H, W), np.float32); e = min(1, (lt - 2.3) / 0.6)
        cv2.ellipse(c, (565, 1512), (260, 85), -4, 0, int(360 * e), 1.0, 7, cv2.LINE_AA)
        rm = np.maximum(rm, c)
    rm = cv2.GaussianBlur(rm, (0, 0), 0.8)[..., None]
    base = base * (1 - rm) + RED * 1.25 * rm
    base = light(base, 560, 1100, 820, t, 0.6)
    # push from the names down to the red total
    cy = 950 + 520 * min(1, p * 1.3)
    return zoom(base, 1.25 + 0.35 * p, 560, cy, dx=0, dy=960 - cy)

def sc_corridor(lt, dur, t):
    k = Ink(seed=92); k.a = CK.a.copy()
    p = lt / max(dur, 0.1)
    fl = flicker(t, 4)
    k.a = np.maximum(k.a, fig_alpha('w', math.sin(t * 1.1) * 0.4, lambda g, sw: person_back(g, 520, 1720, 900, phase=0, walk=False, sway=sw)))
    base = k.apply(PAPER.copy()) * (0.55 + 0.45 * fl)
    base = glow(base, 540, 300, 320, COLD, 0.6 * fl)                                                  # tube light
    # door 9: red number + chain + faint red glow under it
    nm = cv2.GaussianBlur(C9, (0, 0), 0.8)[..., None]
    base = base * (1 - nm) + RED * 1.4 * nm
    ch = Ink(seed=93)
    for i in ([] if 'chain' in _FIG else range(7)):
        ch.stroke(cv2.ellipse2Poly((int(VX - 50 + i * 16), int(VY + 30 + math.sin(i) * 4)), (9, 6), 20, 0, 360, 30), 2.5, 2.5, 0.95, dry=0)
    if 'chain' not in _FIG: _FIG['chain'] = ch.a
    ch.a = _FIG['chain']
    base = ch.apply(base, np.float32([120, 115, 110]))
    base = glow(base, VX, VY + 165, 70, RED * 1.3, 0.35 + 0.25 * math.sin(t * 5) ** 2)
    base = light(base, 540, 800, 900, t, 0.5)
    if p < 0.45:
        return zoom(base, 1.0 + 0.15 * p, 540, 1000)
    q = (p - 0.45) / 0.55
    z = 1.07 + 2.4 * q * q                                                                           # rush toward door 9
    return zoom(base, z, VX, VY, dx=0, dy=(960 - VY))

def sc_room(lt, dur, t):
    k = Ink(seed=102); k.a = RMK.a.copy()
    p = lt / max(dur, 0.1)
    k.a = np.maximum(k.a, fig_alpha('r', math.sin(t * 0.9) * 0.6, lambda g, sw: person_back(g, 330, 1330, 760, walk=False, sway=sw)))
    k.wash([(40, 1180), (760, 1110), (760, 1330), (60, 1400)], 0.9, 3)          # bed front edge covers legs
    base = k.apply(PAPER.copy())
    base = glow(base, 790, 530, 330, COLD, 0.55)                                 # moonlight
    base = light(base, 600, 900, 900, t, 0.55)
    return zoom(base, 1.05 + 0.2 * p, 420, 1000)

def sc_door(lt, dur, t):
    k = Ink(seed=112); k.a = DK.a.copy()
    p = lt / max(dur, 0.1)
    hp = max(0, (p - 0.5) / 0.5)
    base = k.apply(PAPER.copy() * 0.7)
    # thin cold light under the door gap
    base = glow(base, (DX0 + DX1) / 2, DY1 + 6, 260, COLD, 0.5)
    hk = Ink(seed=113)
    if hp > 0: hair_under_door(hk, hp, t); base = hk.apply(base)
    shake = 0
    for kt in (0.25, 0.55, 0.85):                                                 # three knocks
        if 0 <= lt - kt < 0.15: shake = 9 * math.sin((lt - kt) * 120)
    z = 1.05 + 0.12 * min(1, p / 0.5) + 0.12 * hp
    cy = 1000 + 250 * hp
    return zoom(base, z, 540, cy, dx=shake, dy=(960 - cy) * 0.6)

def sc_bed(lt, dur, t):
    k = Ink(seed=122); k.a = BDK.a.copy()
    p = lt / max(dur, 0.1)
    for i in range(12):                                                           # one long wet hair on pillow
        k.stroke(bezier((240 + i * 6, 860), (330 + i * 10, 940), (460 + i * 14, 980 + i * 3)), 1.6, 0.6, 0.9)
    base = k.apply(PAPER.copy())
    base = glow(base, 900, 400, 400, COLD, 0.4)
    base = glow(base, 560, 1000, 520, COLD, 0.35)
    base = light(base, 540, 1000, 800, t, 0.45)
    whip = max(0, 1 - lt / 0.35)                                                  # whip-pan in
    return zoom(base, 1.0 + 0.12 * p, 560, 1000, dx=whip * 500)

def sc_final(lt, dur, t):
    k = Ink(seed=132); k.a = DK.a.copy()
    p = lt / max(dur, 0.1)
    base = k.apply(PAPER.copy() * 0.5) * 0.7
    base = glow(base, (DX0 + DX1) / 2, DY1 + 6, 300, RED * 1.3, 0.55 + 0.2 * math.sin(t * 6))
    hk = Ink(seed=134); hair_under_door(hk, max(0, 1 - p * 1.4), t); base = hk.apply(base)  # hair slides back out
    # two bare feet shadows in the gap
    sh = Ink(seed=133)
    for x in (480, 600):
        sh.wash_rect(x, DY1 - 2, x + 70, DY1 + 12, 0.98, 2)
    base = sh.apply(base)
    if p > 0.55:
        w = np.zeros((H, W), np.float32); put(w, "PRESENT", (330, 860), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 3.2, 7)
        e = min(1, (p - 0.55) / 0.3)
        w = cv2.GaussianBlur(w, (0, 0), 1)[..., None] * e
        base = base * (1 - w) + RED * 1.3 * w
    return zoom(base, 1.2 + 0.35 * p, 540, 1150, dy=-150)

SCENES = [sc_register, sc_corridor, sc_room, sc_door, sc_bed, sc_final]
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
    img = text(img, "HAAZRI  |  HORROR STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
