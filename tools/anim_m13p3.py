"""13vi Manzil Part 3 - procedural ink-wash animation (no stock footage).
python3 anim_m13p3.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FPS = 30
END_CARD = 2.6

CAPS = ["REGISTER KA AAKHRI NAAM...", "NEHA - 1303", "AUR LIKHAWAT... MERI APNI THI",
        "MAINE PANNE PALTE...", "HAR SAAL, ISI TAAREEKH KO... EK NAAM", "AUR HAR NAAM KE AAGE... LAAPATA",
        "MAINE MAA KO PHONE KIYA...", "MAA, MAIN PHANS GAYI HOON...",
        "KYA BOL RAHI HAI NEHA?", "TU TOH APNE KAMRE MEIN SO RAHI HAI", "MAINE ABHI TUJHE CHADAR ODHAAI HAI",
        "TABHI PHONE KE PAAS SE... MERI HI AAWAAZ AAYI", "\"MAA... PHONE KISKA HAI?\""]
HOT = {"1303", "NEHA", "APNI", "LAAPATA", "PHANS", "SO", "CHADAR", "MERI", "KISKA", "TAAREEKH"}
# caption index -> scene
SCENE_OF = [0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4]

PAPER = paper(seed=7)
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.5 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)).clip(0.3, 1)[..., None].astype(np.float32)

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

def script_text(mask, s, org, scale, th):
    put(mask, s, org, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, scale, th)

def torch(img, cx, cy, r, t, amt=0.75):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    jit = 1 + 0.03 * math.sin(t * 13) + 0.02 * math.sin(t * 29)
    m = np.clip(1 - (d / (r * jit)) ** 2, 0, 1)[..., None].astype(np.float32)
    return img * (1 - amt + amt * m)

# ---------- backgrounds (built once) ----------
def register_bg():
    k = Ink(seed=61)
    k.wash_rect(0, 0, W, H, 0.82, 30)                                   # dark desk
    pg = [(70, 330), (1010, 300), (1040, 1640), (40, 1660)]
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [np.int32(pg)], 1); m = cv2.GaussianBlur(m, (0, 0), 3)
    k.a = k.a * (1 - m) + 0.08 * m                                       # pages = paper
    k.stroke([(540, 315), (545, 990), (540, 1650)], 9, 5, 0.75)          # spine
    k.stroke([pg[0], pg[1], pg[2], pg[3], pg[0]], 4, 3, 0.8)
    for side in (0, 1):
        x0, x1 = (110, 500) if side == 0 else (585, 990)
        for r in range(17):
            y = 420 + r * 70 + side * 4
            k.stroke([(x0, y), (x1, y + 3)], 1.6, 1.2, 0.32, dry=0.3)
        k.stroke([(x0 + 70, 380), (x0 + 72, 1610)], 1.6, 1.2, 0.38)
    names = Ink(seed=62)
    rows = []
    for side in (0, 1):
        x0 = 110 if side == 0 else 585
        for r in range(16 if side == 0 else 11):
            y = 410 + r * 70 + side * 4
            rows.append((x0, y))
    return k, rows

RK, ROWS = register_bg()
SCRIB = np.zeros((H, W), np.float32)
_rng = np.random.default_rng(3)
_fake = ["Sunita", "R. Mehta", "Pooja", "Anil K.", "Farida", "Joseph", "Kavya", "S. Rao", "Meena", "Imran", "Lata",
         "Deepak", "Ritu", "Gopal", "Asha", "Vikram", "Shalini", "Manoj", "Nisha", "Harish", "Tara", "Sameer", "Uma",
         "Kiran", "Rekha", "Arjun", "Seema"]
for i, (x, y) in enumerate(ROWS):
    yr = 1999 + i
    script_text(SCRIB, f"{yr}", (x - 8, y), 0.9, 2)
    script_text(SCRIB, f"{_fake[i % len(_fake)]} 13{i % 4 + 1:02d}", (x + 80, y), 1.05, 2)
REDROW_Y = 1310   # last row on right page (row 10): "Neha - 1303"
NEHA = np.zeros((H, W), np.float32); script_text(NEHA, "Neha - 1303", (660, REDROW_Y), 1.9, 4)
LAAP = []
for i, (x, y) in enumerate(ROWS):
    m = np.zeros((H, W), np.float32)
    put(m, "LAAPATA", (x + 270 if x < 540 else x + 250, y), cv2.FONT_HERSHEY_DUPLEX, 0.75, 2)
    LAAP.append(m)

def corridor_bg():
    k = Ink(seed=11); vx, vy = W / 2, 820
    k.wash([(0, 0), (W, 0), (vx + 110, vy - 140), (vx - 110, vy - 140)], 0.6, 10)
    k.wash([(0, H), (W, H), (vx + 110, vy + 150), (vx - 110, vy + 150)], 0.4, 14)
    k.wash_rect(vx - 110, vy - 140, vx + 110, vy + 150, 0.7, 4)
    k.stroke([(vx - 110, vy - 140), (vx + 110, vy - 140), (vx + 110, vy + 150), (vx - 110, vy + 150), (vx - 110, vy - 140)], 5, 4)
    for side in (-1, 1):
        xo = 0 if side < 0 else W; xi = vx + side * 110
        k.stroke([(xo, 0), (xi, vy - 140)], 7, 3); k.stroke([(xo, H), (xi, vy + 150)], 7, 3)
        for i, f in enumerate((0.12, 0.38, 0.6, 0.78)):
            def P(ff, yo, yi): return (xo + (xi - xo) * ff, yo + (yi - yo) * ff)
            q = [P(f, 380, vy - 90), P(f + 0.1, 380, vy - 90), P(f + 0.1, H - 160, vy + 130), P(f, H - 160, vy + 130)]
            k.wash(q, 0.6 + 0.1 * i, 3); k.stroke([q[0], q[1], q[2], q[3], q[0]], 3, 2)
    return k

CK = corridor_bg()

def bedroom_bg():
    k = Ink(seed=71)
    k.wash_rect(0, 0, W, H, 0.8, 25)                                      # walls
    k.wash([(0, 1250), (W, 1180), (W, H), (0, H)], 0.78, 12)              # floor
    k.wash_rect(640, 260, 960, 700, 0.15, 8)                              # window (moonlight)
    k.stroke([(640, 260), (960, 260), (960, 700), (640, 700), (640, 260)], 7, 6)
    k.stroke([(800, 260), (800, 700)], 5, 4); k.stroke([(640, 480), (960, 480)], 5, 4)
    k.wash_rect(110, 380, 330, 1300, 0.95, 4)                             # open door, black gap
    k.stroke([(100, 370), (340, 370), (340, 1300), (100, 1300)], 8, 6)
    # bed
    k.wash([(260, 1080), (1040, 1030), (1060, 1500), (220, 1560)], 0.72, 4)
    k.stroke([(240, 900), (240, 1580)], 12, 9); k.stroke([(240, 900), (420, 890)], 10, 8)
    k.stroke([(220, 1560), (1060, 1500)], 10, 8)
    return k

BK = bedroom_bg()

def sheet_layer(t, empty=False):
    s = Ink(seed=72)
    if not empty:
        br = 1 + 0.012 * math.sin(t * 2.2)
        lump = np.vstack([bezier((300, 1110), (650, 960 - 40 * br), (1010, 1060)), [(1030, 1260), (290, 1300)]])
        lm = np.zeros_like(s.a); cv2.fillPoly(lm, [np.int32(lump)], 1.0); s.lump = cv2.GaussianBlur(lm, (0, 0), 3)
        s.stroke(bezier((300, 1110), (650, 958 - 40 * br), (1010, 1060)), 4, 3, 0.7)
        for k in range(4):
            x = 450 + k * 140
            s.stroke(bezier((x, 1040), (x + 30, 1150), (x - 10, 1270)), 2, 1, 0.45)
        s.wash(cv2.ellipse2Poly((330, 1050), (85, 50), -10, 0, 360, 10), 0.97, 3)  # head (hair) on pillow
        for k in range(12):
            a = -0.6 + k * 0.13
            s.stroke(bezier((330, 1050), (300 - 60 * math.cos(a), 1060 + 70 * math.sin(a)), (250 - 110 * math.cos(a) + math.sin(t + k) * 3, 1090 + 120 * math.sin(a))), 2.4, .6, 0.92)
    else:
        s.wash(np.vstack([bezier((520, 1150), (800, 1090), (1020, 1120)), [(1030, 1270), (560, 1290)]]), 0.2, 3)
        s.stroke(bezier((520, 1150), (800, 1090), (1020, 1120)), 4, 3, 0.7)
    return s

# ---------- scenes ----------
def sc_register(lt, dur, t):
    k = Ink(seed=63); k.a = RK.a.copy()
    base = k.apply(PAPER.copy())
    sa = SCRIB[..., None]; base = base * (1 - sa * 0.85) + INK * sa * 0.85
    reveal = min(1, 0.55 + lt / 1.6)                                      # hook: mostly written already at t=0
    xm = (xx < 640 + 560 * reveal)[..., None]
    nm = cv2.GaussianBlur(NEHA, (0, 0), 0.8)[..., None] * xm
    base = base * (1 - nm) + RED * 1.15 * nm
    if lt > 1.2:                                                          # ink drip from last letter
        dl = min(1, (lt - 1.2) / 3) * 160
        cv2.line(base, (1000, REDROW_Y + 8), (1002, int(REDROW_Y + 8 + dl)), tuple(float(c) for c in RED), 5, cv2.LINE_AA)
    base = torch(base, 780 - lt * 15, REDROW_Y - 40, 520, t)
    p = lt / max(dur, 0.1)
    return zoom(base, 1.35 + 0.35 * p, 800, REDROW_Y - 40, dx=-260, dy=-300 + 0 * p)

def sc_pages(lt, dur, t):
    k = Ink(seed=64); k.a = RK.a.copy()
    base = k.apply(PAPER.copy())
    sa = SCRIB[..., None]; base = base * (1 - sa * 0.85) + INK * sa * 0.85
    flip = lt < 0.7
    if flip:                                                             # page turning over
        f = lt / 0.7; xr = 1010 - 900 * f
        pk = Ink(seed=65); pk.wash([(545, 310), (xr, 300 + 60 * math.sin(f * 3.14)), (xr + 20, 1640), (545, 1650)], 0.2 + 0.4 * f, 4)
        pk.stroke([(xr, 300), (xr + 20, 1640)], 5, 4, 0.8)
        base = pk.apply(base)
    nshow = int(max(0, (lt - 0.8)) / max(0.1, (dur - 1.0)) * len(ROWS) * 1.1) + 1
    for i in range(min(nshow, len(ROWS))):
        m = LAAP[i][..., None]; base = base * (1 - m) + RED * 1.2 * m
    nm = NEHA[..., None]; base = base * (1 - nm) + RED * 1.15 * nm
    base = torch(base, 540, 500 + min(1, lt / dur) * 900, 650, t, 0.6)
    p = lt / max(dur, 0.1)
    return zoom(base, 1.18, 540, 500 + 800 * p, dx=0, dy=460 - 800 * p)

def sc_phone(lt, dur, t):
    fl = flicker(t, 2)
    k = Ink(seed=33); k.a = CK.a.copy()
    person_back(k, W / 2 + 40, 1640, 1050, phase=0.3, walk=False, sway=math.sin(t * 1.6) * 0.6)
    base = k.apply(PAPER.copy()) * (0.5 + 0.5 * fl)
    hu = 1050 / 8; px, py = W / 2 + 40 + hu * 0.5, 1640 - 1050 + hu * 0.6
    g = np.zeros((H, W), np.float32); cv2.circle(g, (int(px), int(py)), 50, 1, -1)
    g = cv2.GaussianBlur(g, (0, 0), 45)[..., None] * (0.8 + 0.2 * math.sin(t * 8))
    base = base * (1 - g * 0.6) + np.array([230, 240, 255], np.float32) * g * 0.6
    m13 = np.zeros((H, W), np.float32); put(m13, '13', (int(W / 2 - 34), 730), cv2.FONT_HERSHEY_DUPLEX, 1.7, 3)
    m13 = cv2.GaussianBlur(m13, (0, 0), 1.2)[..., None] * (0.6 + 0.4 * math.sin(t * 6))
    base = base * (1 - m13) + RED * 1.3 * m13
    p = lt / max(dur, 0.1)
    return zoom(base, 1.0 + 0.12 * p, W / 2, 800)

def sc_bedroom(lt, dur, t):
    k = Ink(seed=73); k.a = BK.a.copy()
    base = k.apply(PAPER.copy())
    sl = sheet_layer(t); lm = sl.lump[..., None]
    base = base * (1 - lm) + PAPER * 0.92 * lm
    base = sl.apply(base)
    # moonlight from window on bed
    mw = np.zeros((H, W), np.float32); cv2.fillPoly(mw, [np.int32([(640, 700), (960, 700), (1080, 1300), (420, 1300)])], 1)
    mw = cv2.GaussianBlur(mw, (0, 0), 40)[..., None]
    base = base * (1 + 0.45 * mw)
    p = lt / max(dur, 0.1)
    return zoom(base, 1.05 + 0.2 * p, 450, 1080)

def sc_double(lt, dur, t):
    k = Ink(seed=74); k.a = BK.a.copy()
    base = k.apply(PAPER.copy()) * 0.75
    base = sheet_layer(t, empty=True).apply(base)
    g = Ink(seed=75)
    grow = min(1, lt / 2.5)
    e1, e2, hu = ghost_front(g, 225, 1300, 840 + 60 * grow, sway=math.sin(lt * 1.5) * 1.2)
    fig = g.a[..., None]; hairw = np.clip((g.a - 0.93) / 0.04, 0, 1)[..., None]
    figcol = np.array([172, 168, 160], np.float32) * (1 - hairw) + INK * hairw
    base = base * (1 - fig) + figcol * fig
    edge = cv2.morphologyEx(g.a, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))[..., None]
    base = base * (1 - edge * .8) + INK * edge * .8
    if lt > 1.2:
        for (ex, ey) in (e1, e2):
            cv2.ellipse(base, (int(ex), int(ey)), (9, 4), 0, 0, 360, tuple(float(c) for c in RED * 1.35), -1, cv2.LINE_AA)
    p = min(1, lt / max(dur, 0.1))
    return zoom(base, 1.15 + 0.55 * p, 225, 640)

SCENES = [sc_register, sc_pages, sc_phone, sc_bedroom, sc_double]

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
        img = text(img, "13VI MANZIL", (W / 2, 760), 110, RED * 1.25)
        img = text(img, "TO BE CONTINUED...", (W / 2, 950), 80, np.array([235, 232, 225]) * e)
        img = text(img, "PART 4: FINALE", (W / 2, 1090), 90, RED * 1.3 * e)
        img = text(img, "AAJ RAAT", (W / 2, 1200), 70, np.array([235, 232, 225]) * e)
        return finish(img, t, 9)
    si = max(i for i, (a, b) in enumerate(spans) if t >= a)
    a, b = spans[si]
    img = SCENES[si](t - a, b - a, t)
    img = glitch(np.float32(img), t, [s[0] for s in spans[1:]])
    img = finish(img, t, si)
    img = np.float32(img)
    img = text(img, "13VI MANZIL  |  PART 3", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
