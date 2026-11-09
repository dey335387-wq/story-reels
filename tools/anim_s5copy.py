"""Standalone story '41VI COPY' (college exam hall, evening invigilation, 40 students but 41 answer copies) -
procedural ink-wash animation (no stock footage).  python3 anim_s5copy.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FH = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"   # 'handwriting'
FPS = 30
END_CARD = 2.8
TITLE = "41VI COPY"

CAPS = ["40 BACHCHE...", "PAR COPIYAAN 41",
        "MAIN KAVITA. COLLEGE MEIN SHAAM KI EXAM DUTY THI",
        "MAINE TEEN BAAR GINA", "ATTENDANCE MEIN 40, COPIYAAN 41",
        "41VI COPY PE NAAM THA... PRIYA VERMA",
        "PRINCIPAL NE KAHA, PRIYA TOH 5 SAAL PEHLE", "ISI HALL MEIN, EXAM KE BEECH... GIR GAYI THI",
        "MAINE COPY KHOLI", "HAR PANNE PE EK HI LINE...", "MUJHE PAPER POORA KARNE DO",
        "AUR AAKHRI PANNE KI SYAHI...", "ABHI GEELI THI",
        "PEECHHE SE KOI BOLA...", "MADAM, EXTRA SHEET MILEGI?",
        "HALL KHAALI THA.", "PAR AAKHRI BENCH PE... KOI AB BHI LIKH RAHA THA."]
HOT = {"40", "41", "41VI", "PRIYA", "VERMA", "GIR", "POORA", "GEELI", "EXTRA", "SHEET", "KHAALI", "LIKH"}
SCENE_OF = [0, 0, 1, 2, 2, 3, 4, 4, 5, 5, 5, 5, 5, 6, 6, 7, 7]
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


# ---------- backgrounds ----------
def hall_bg(seed=401):
    """exam hall in perspective: rows of benches receding to a back wall, tube lights, blackboard at back."""
    k = Ink(seed=seed)
    k.wash_rect(0, 0, W, H, 0.62, 25)
    k.wash([(0, 0), (W, 0), (760, 520), (320, 520)], 0.4, 12)                      # ceiling
    k.wash_rect(320, 520, 760, 900, 0.5, 6)                                         # back wall
    k.wash_rect(380, 580, 700, 760, 0.92, 3)                                        # blackboard
    k.wash([(0, H), (W, H), (760, 900), (320, 900)], 0.45, 10)                      # floor
    for x0, x1 in ((330, 750), (0, 320), (760, W)):
        pass
    for i in range(6):                                                              # bench rows
        f = i / 5.0; y = 900 + (1 - f) * 0 + f * 0
        y = 930 + (1 - (1 - f) ** 1.6) * 0  # placeholder
    rows = [(960, 0.18), (1060, 0.3), (1200, 0.48), (1390, 0.7), (1650, 1.0)]
    for y, s in rows:
        for cx in (540 - 300 * s - 40 * s, 540 + 300 * s + 40 * s):
            bw = 230 * s + 40; th = 18 * s + 3
            k.wash_rect(cx - bw, y - th, cx + bw, y + th, 0.9, 2)                   # desk top
            k.stroke([(cx - bw + 10, y), (cx - bw + 10, y + 110 * s + 20)], 5 * s + 2, 3 * s + 1, 0.9)
            k.stroke([(cx + bw - 10, y), (cx + bw - 10, y + 110 * s + 20)], 5 * s + 2, 3 * s + 1, 0.9)
            k.wash_rect(cx - bw, y + 50 * s, cx + bw, y + 62 * s + 4, 0.85, 2)       # seat
    for lx in (420, 660):
        k.stroke([(lx - 60, 440), (lx + 60, 440)], 10, 10, 0.9, dry=0)
    return k
HK = hall_bg()

_FIG = {}
def fig_alpha(key, sway, fn):
    sk = round(sway * 5) / 5
    if (key, sk) not in _FIG:
        g = Ink(seed=7); fn(g, sk); _FIG[(key, sk)] = g.a
    return _FIG[(key, sk)]

def tubes(img, t, on=1.0):
    f = flicker(t, 3) * on
    for lx in (420, 660):
        img = glow(img, lx, 440, 160, WARM, 0.55 * f)
    return img

def sheet(seed=0, lines=True):
    """off-white ruled paper filling the frame."""
    p = paper(seed=31 + seed) * 1.04
    if lines:
        for y in range(380, H, 78):
            p[y:y + 2, :] = p[y:y + 2, :] * 0.78 + np.array([120, 140, 200]) * 0.22
        p[:, 150:153] = p[:, 150:153] * 0.6 + RED * 0.4
    return p

# ---------- scenes ----------
def sc_hook(lt, dur, t):
    """FULL-SCREEN proof: invigilator's report: PRESENT 40, COPIES 41 (41 circled in red), tally marks."""
    p = lt / max(dur, 0.1)
    img = sheet(0)
    img = text(img, "EXAM HALL - ROOM 6", (540, 420), 64, INK, stroke=0, font=FB)
    img = text(img, "Present :", (190, 640), 110, BLUE, "lm", 0, FH, rot=2)
    img = text(img, "40", (740, 640), 170, BLUE, "mm", 0, FH, rot=2)
    img = text(img, "Copies :", (190, 960), 110, BLUE, "lm", 0, FH, rot=1)
    img = text(img, "41", (740, 960), 190, RED * 1.1, "mm", 0, FH, rot=-3)
    k = Ink(seed=402)
    ell = cv2.ellipse2Poly((745, 965), (150, 110), -8, 0, int(40 + 330 * min(1, p * 1.6)), 6)
    if len(ell) > 2: k.stroke(ell, 9, 5, 0.95, dry=0.1)
    for i in range(8):                                                              # tally marks
        x = 210 + i * 70
        k.stroke([(x, 1200), (x + 12, 1330)], 8, 4, 0.9)
    k.stroke([(190, 1310), (520, 1210)], 7, 4, 0.9)
    k.stroke([(530, 1310), (760, 1220)], 7, 4, 0.9)
    base = k.apply(img * 1.0, INK)
    base = base * (1 - 0.0) ; a = k.a[..., None] * 0
    # red circle over 41
    kr = Ink(seed=403); kr.a = np.zeros_like(k.a)
    if len(ell) > 2: kr.stroke(ell, 10, 6, 0.95, dry=0.1)
    base = kr.apply(base, RED * 1.15)
    # a wet red drip running down from 41
    dl = 80 + 380 * p
    kd = Ink(seed=404); kd.stroke([(800, 1050), (803, 1050 + dl)], 10, 6, 0.9, dry=0); kd.blot(803, 1050 + dl, 9, 0.9)
    base = kd.apply(base, RED)
    base = base * (0.78 + 0.22 * flicker(t, 1))
    return zoom(base, 1.05 + 0.18 * p, 640, 820)

def sc_hall(lt, dur, t, figure=True, dark=0.0, ghost=False):
    p = lt / max(dur, 0.1)
    k = Ink(seed=405); k.a = HK.a.copy()
    if figure:
        k.a = np.maximum(k.a, fig_alpha('teacher', math.sin(t * 1.3) * 0.5,
                                        lambda g, sw: person_back(g, 540, 1880, 820, walk=False, sway=sw)))
    base = k.apply(PAPER.copy() * (0.85 - dark))
    base = tubes(base, t, 1 - dark)
    return zoom(base, 1.04 + 0.12 * p, 540, 900)

def sc_count(lt, dur, t):
    """stack of answer copies on the desk, counting fingers, pages flip."""
    p = lt / max(dur, 0.1)
    img = PAPER.copy() * 0.55
    k = Ink(seed=406)
    k.wash_rect(0, 1100, W, H, 0.85, 8)                                             # desk
    base = k.apply(img)
    n = int(min(41, 1 + p * 46))
    for i in range(14):                                                             # stack edges
        y = 1180 - i * 16
        cv2.rectangle(base, (210, y - 300), (870, y), tuple(float(v) for v in (232 - i, 228 - i, 215 - i)), -1)
        cv2.rectangle(base, (210, y - 300), (870, y), (90, 85, 80), 2, cv2.LINE_AA)
    base = text(base, "ANSWER BOOK", (540, 820), 66, INK, stroke=0)
    base = text(base, f"{n}", (540, 560), 230, RED * 1.15 if n > 40 else WHITE, stroke=8)
    base = glow(base, 540, 900, 500, WARM, 0.25 * flicker(t, 2))
    return zoom(base, 1.05 + 0.2 * p, 540, 800, dx=math.sin(t * 2) * 4)

def sc_copy(lt, dur, t):
    """cover page of the 41st copy: NAME: Priya Verma, old date."""
    p = lt / max(dur, 0.1)
    img = paper(seed=77) * 0.93
    k = Ink(seed=407)
    for i in range(30):                                                             # age stains
        k.blot(100 + (i * 233) % 900, 300 + (i * 397) % 1500, 30 + (i * 13) % 50, 0.12)
    img = k.apply(img, np.array([110, 80, 40], np.float32))
    cv2.rectangle(img, (110, 260), (970, 1680), (60, 60, 70), 6, cv2.LINE_AA)
    img = text(img, "ANSWER BOOK", (540, 400), 84, INK, stroke=0)
    img = text(img, "NAME :", (170, 700), 70, INK, "lm", 0)
    img = text(img, "Priya Verma", (430, 700), 88, BLUE, "lm", 0, FH, rot=2)
    img = text(img, "ROOM :", (170, 900), 70, INK, "lm", 0)
    img = text(img, "6", (450, 900), 110, BLUE, "lm", 0, FH)
    img = text(img, "DATE :", (170, 1100), 70, INK, "lm", 0)
    img = text(img, "09-11-2021", (450, 1100), 100, BLUE, "lm", 0, FH, rot=1)
    img = img * (0.8 + 0.2 * flicker(t, 4))
    return zoom(img, 1.0 + 0.25 * p, 540, 700 + 150 * p)

def sc_fall(lt, dur, t):
    """memory: same hall 5 years ago, one bench at the back lit, chair tipped, copy on the floor."""
    p = lt / max(dur, 0.1)
    base = sc_hall(lt, dur, t, figure=False, dark=0.35)
    k = Ink(seed=408)
    k.stroke([(700, 1660), (860, 1590)], 14, 10, 0.95)                             # tipped chair
    k.stroke([(860, 1590), (900, 1700)], 10, 6, 0.95); k.stroke([(700, 1660), (690, 1760)], 10, 6, 0.95)
    k.wash([(380, 1760), (620, 1740), (640, 1800), (400, 1820)], 0.9, 3)          # copy on floor
    for i in range(7):                                                              # spilled hair-like ink on floor
        k.stroke(bezier((520, 1790), (560 + i * 30, 1830), (600 + i * 45, 1880 + (i % 3) * 10)), 4, 1, 0.9)
    base = k.apply(base)
    base = glow(base, 620, 1700, 360, COLD, 0.45 + 0.2 * math.sin(t * 5))
    return zoom(base, 1.1 + 0.5 * p, 640, 1650)

def sc_pages(lt, dur, t):
    """pages flipping; every page the same line; last page: wet ink running."""
    p = lt / max(dur, 0.1)
    t11 = SRT[11][0] - (t - lt)                     # local time when 'aakhri panne' starts
    last = lt >= t11
    q = min(1, max(0, (lt - t11) / max(0.5, dur - t11)))
    page = int(lt * 3)
    img = sheet(1 + min(page, 4))
    nlines = 16 if not last else int(6 + 10 * min(1, q * 1.4))
    for i in range(nlines):
        y = 440 + i * 78 + 20
        img = text(img, "mujhe paper poora karne do", (190, y), 54, BLUE if not last else RED * 0.9, "lm", 0, FH,
                   rot=(i % 3 - 1) * 0.6)
    if last:
        k = Ink(seed=409)
        for j in range(5):
            x = 260 + j * 150; L = (200 + j * 70) * q
            k.stroke([(x, 900), (x + 3, 900 + L)], 9, 5, 0.9, dry=0); k.blot(x + 3, 900 + L, 8, 0.9)
        img = k.apply(img, RED * 0.9)
    img = img * (0.82 + 0.18 * flicker(t, 5))
    sh = (lt * 3 % 1) if not last else 1
    return zoom(img, 1.05 + 0.15 * p, 540, 960, dx=(1 - min(1, sh * 3)) * -300 if not last else 0)

def sc_voice(lt, dur, t):
    """teacher from behind at front of the empty hall; a long dark hand rises at her shoulder."""
    p = lt / max(dur, 0.1)
    base = sc_hall(lt, dur, t, figure=True, dark=0.25)
    k = Ink(seed=410)
    rise = min(1, p * 1.5)
    hx, hy = 860, 1500 - 420 * rise
    k.stroke(bezier((1080, 1920), (980, 1700), (hx, hy)), 70, 44, 0.98, dry=0.05)
    k.blot(hx, hy - 30, 40, 0.98)
    for f in range(4):
        k.stroke([(hx + (f - 1.5) * 20, hy - 40), (hx - 30 + (f - 1.5) * 30, hy - 200 - (f % 2) * 30)], 18, 8, 0.98, dry=0)
    base = k.apply(base, np.array([205, 200, 190], np.float32))          # pale dead hand
    for f in range(4):
        cv2.circle(base, (int(hx - 30 + (f - 1.5) * 30), int(hy - 200 - (f % 2) * 30)), 8, tuple(float(v) for v in RED), -1, cv2.LINE_AA)
    base = base * (0.7 + 0.3 * flicker(t, 6))
    return zoom(base, 1.15 + 0.25 * p, 620, 1300)

def sc_lastbench(lt, dur, t):
    """the hall is empty; push-in to the last bench where a long-haired girl bends over a copy, writing; red eyes."""
    p = lt / max(dur, 0.1)
    k = Ink(seed=411); k.a = HK.a.copy()
    sway = math.sin(t * 2.2) * 0.4
    show = (t - lt) + lt >= SRT[16][0] - 0.2
    if show: k.a = np.maximum(k.a, fig_alpha('girl', sway, lambda g, sw: ghost_front(g, 540, 1080, 260, sway=sw)))
    base = k.apply(PAPER.copy() * 0.55)
    base = tubes(base, t, 0.35)
    base = glow(base, 540, 980, 220, COLD, 0.35)
    _g = Ink(seed=9); e1, e2, hu = ghost_front(_g, 540, 1080, 260, sway=0)
    eye = 1.0 if p > 0.55 else 0.0
    for (ex, ey) in (e1, e2):
        if eye and show: cv2.circle(base, (int(ex), int(ey)), 4, (255, 30, 30), -1, cv2.LINE_AA)
    # pen scratching (moving hand at desk)
    px = 540 + 25 * math.sin(t * 14)
    if show: cv2.line(base, (int(px), 1000), (int(px + 14), 965), (20, 18, 22), 4, cv2.LINE_AA)
    return zoom(base, 1.15 + 1.6 * p, 540, 960)

SCENES = [sc_hook, sc_hall, sc_count, sc_copy, sc_fall, sc_pages, sc_voice, sc_lastbench]

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
    img = text(img, "41VI COPY  |  HORROR STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
