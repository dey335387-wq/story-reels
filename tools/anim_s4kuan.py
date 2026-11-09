"""Standalone story 'GALLERY' (PG room, Pune, phone photos at 3:07 AM) - procedural ink-wash animation (no stock footage).
python3 anim_s3gallery.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FPS = 30
END_CARD = 2.8
TITLE = "KUAN"

CAPS = ["KUEN KE PAANI MEIN MERI PARCHHAI...", "MUJHSE PEHLE MUSKURAYI",
        "MAIN AMAN. CHHUTTIYON MEIN DADI KE GAON AAYA THA", "DADI KEHTI THI, RAAT KO KUEN MEIN KABHI MAT JHAANKNA",
        "RAAT 1 BAJE PYAAS LAGI. MATKA KHAALI THA", "MAIN LALTEN LEKAR KUEN PE GAYA...", "AUR BALTI NEECHE DAALI",
        "PAANI MEIN MERI PARCHHAI THI... LALTEN KE SAATH", "MAINE LALTEN NEECHE RAKHI...", "PAR PARCHHAI KE HAATH MEIN LALTEN AB BHI THI",
        "TABHI RASSI EK JHATKE MEIN TAN GAYI...", "JAISE NEECHE SE KISI NE KHEENCHA", "MAINE RASSI CHHODI AUR BHAAGA",
        "SUBAH DADI NE POOCHA: RAAT KO PAANI KISNE BHARA?", "MATKA POORA BHARA THA...", "AUR USKE PAAS GEELE PAIRON KE NISHAAN THE.", "CHHOTE PAIRON KE."]
HOT = {"PARCHHAI", "MUSKURAYI", "KUEN", "1", "LALTEN", "AB", "BHI", "TAN", "KHEENCHA", "BHARA", "GEELE", "CHHOTE"}
SCENE_OF = [0, 0, 1, 1, 2, 3, 3, 0, 4, 4, 5, 5, 6, 2, 7, 7, 7]
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


# ---------- backgrounds ----------
def village_bg():
    k = Ink(seed=301)
    k.wash_rect(0, 0, W, H, 0.78, 25)
    k.wash([(0, 1100), (W, 1050), (W, H), (0, H)], 0.5, 10)                      # ground
    for x, h in ((60, 320), (300, 260), (820, 380)):                               # huts / trees
        k.wash([(x, 1100), (x + 200, 1090), (x + 200, 1100 - h), (x + 100, 1100 - h - 90), (x, 1100 - h)], 0.9, 4)
    k.wash(cv2.ellipse2Poly((540, 1290), (230, 70), 0, 0, 360, 10), 0.92, 3)       # well rim
    k.wash_rect(310, 1290, 770, 1500, 0.75, 4)
    k.stroke([(310, 1290), (310, 1500)], 6, 5); k.stroke([(770, 1290), (770, 1500)], 6, 5)
    k.stroke([(360, 1290), (360, 900), (720, 900), (720, 1290)], 10, 8)            # pulley frame
    k.stroke([(540, 900), (540, 1270)], 3, 2, 0.9)                                 # rope
    return k
VK = village_bg()

def wellview_bg():
    """looking down into the well: dark ring + water circle."""
    k = Ink(seed=311)
    k.wash_rect(0, 0, W, H, 0.95, 10)
    for r, v in ((520, 0.95), (440, 0.85), (360, 0.42)):
        k.wash(cv2.ellipse2Poly((540, 960), (r, r), 0, 0, 360, 8), v, 4)
    for ang in range(0, 360, 30):                                                  # bricks
        x = 540 + 470 * math.cos(math.radians(ang)); y = 960 + 470 * math.sin(math.radians(ang))
        k.stroke([(x, y), (540 + 380 * math.cos(math.radians(ang + 8)), 960 + 380 * math.sin(math.radians(ang + 8)))], 3, 2, 0.6)
    return k
WK = wellview_bg()

def home_bg():
    k = Ink(seed=321)
    k.wash_rect(0, 0, W, H, 0.55, 25)
    k.wash([(0, 1300), (W, 1280), (W, H), (0, H)], 0.35, 8)
    k.wash(cv2.ellipse2Poly((540, 1150), (190, 220), 0, 0, 360, 10), 0.85, 4)     # matka
    k.wash_rect(470, 900, 610, 960, 0.85, 3)
    k.stroke([(380, 1080), (700, 1080)], 4, 3, 0.6)
    return k
HK = home_bg()

_FIG = {}
def fig_alpha(key, sway, fn):
    sk = round(sway * 5) / 5
    if (key, sk) not in _FIG:
        g = Ink(seed=7); fn(g, sk); _FIG[(key, sk)] = g.a
    return _FIG[(key, sk)]

_g = Ink(seed=9); EYES = [tuple(int(v) for v in e) for e in ghost_front(_g, 540, 1220, 520, sway=0)[:2]]

def lantern(img, x, y, t, s=1.0):
    img = glow(img, x, y, 220 * s, WARM, 0.75 + 0.15 * math.sin(t * 9))
    cv2.rectangle(img, (int(x - 18 * s), int(y - 30 * s)), (int(x + 18 * s), int(y + 30 * s)), (60, 45, 30), int(5 * s))
    return img

def sc_well_reflection(lt, dur, t, smile=True, lamp_in_hand=True):
    p = lt / max(dur, 0.1)
    k = Ink(seed=312); k.a = WK.a.copy()
    base = k.apply(PAPER.copy() * 0.75)
    base = glow(base, 540, 960, 360, COLD, 0.85)
    fa = fig_alpha('refl', 0.0, lambda g, sw: ghost_front(g, 540, 1220, 520, sway=0))[..., None]
    fa = fa * (0.85 + 0.1 * math.sin(t * 3))
    base = base * (1 - fa) + np.array([12, 12, 16], np.float32) * fa
    if lamp_in_hand: base = lantern(base, 640, 960, t, 0.7)
    if smile:
        m = np.zeros((H, W), np.uint8); cv2.ellipse(m, (EYES[0][0] // 2 + EYES[1][0] // 2, EYES[0][1] + 48), (30, 12), 0, 10, 170, 255, 5, cv2.LINE_AA)
        m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.5)[..., None]; base = base * (1 - m) + RED * 1.4 * m
    rip = 1 + 0.01 * math.sin(t * 6)
    return zoom(base, (1.05 + 0.5 * p) * rip, 540, 900)

def sc_hook(lt, dur, t): return sc_well_reflection(lt, dur, t, smile=lt > 1.2)
def sc_village(lt, dur, t):
    p = lt / max(dur, 0.1)
    k = Ink(seed=302); k.a = VK.a.copy()
    k.a = np.maximum(k.a, fig_alpha('boy', math.sin(t) * 0.5, lambda g, sw: person_back(g, 200, 1500, 560, walk=False, sway=sw, hair_long=False) if 'hair_long' in person_back.__code__.co_varnames else person_back(g, 200, 1500, 560, walk=False, sway=sw)))
    base = k.apply(PAPER.copy() * 0.6)
    base = glow(base, 880, 260, 140, COLD, 0.7)                                    # moon
    return light(zoom(base, 1.05 + 0.15 * p, 540, 1100), 540, 1100, 900, t, 0.45)
def sc_home(lt, dur, t, steps=False):
    p = lt / max(dur, 0.1)
    k = Ink(seed=322); k.a = HK.a.copy()
    if steps:
        for i in range(6):
            x = 300 + i * 60; y = 1560 - i * 50 + (i % 2) * 30
            k.wash(cv2.ellipse2Poly((int(x), int(y)), (16, 26), 20, 0, 360, 10), 0.97, 2)
    base = k.apply(PAPER.copy() * 0.8)
    base = glow(base, 540, 1150, 260, COLD, 0.3 if not steps else 0.5)
    return zoom(base, 1.05 + (0.6 * p if steps else 0.2 * p), 420 if steps else 540, 1400 if steps else 1150)
def sc_walk(lt, dur, t):
    p = lt / max(dur, 0.1)
    k = Ink(seed=303); k.a = VK.a.copy()
    k.a = np.maximum(k.a, fig_alpha('boyw%d' % int(t * 6 % 4), 0, lambda g, sw: person_back(g, 420 + 80 * p, 1500 - 120 * p, 560 - 60 * p, phase=t * 4, sway=0)))
    base = k.apply(PAPER.copy() * 0.6)
    base = lantern(base, 520 + 80 * p, 1150 - 120 * p, t, 0.8)
    return zoom(base, 1.1 + 0.4 * p, 540, 1250)
def sc_lamp_down(lt, dur, t):
    p = lt / max(dur, 0.1)
    return sc_well_reflection(lt, dur, t, smile=p > 0.5, lamp_in_hand=True)
def sc_rope(lt, dur, t):
    p = lt / max(dur, 0.1)
    k = Ink(seed=304); k.a = VK.a.copy()
    jerk = 1 if p > 0.3 else 0
    k.stroke([(540, 900), (540 + 6 * math.sin(t * 40) * jerk, 1280)], 7 if jerk else 3, 5, 0.99, dry=0)
    base = k.apply(PAPER.copy() * 0.55)
    base = lantern(base, 640, 1280, t, 0.8)
    sh = 18 * jerk * math.sin(t * 50)
    return zoom(base, 1.6 + 0.4 * p, 540 + sh, 1100)
def sc_run(lt, dur, t):
    p = lt / max(dur, 0.1)
    k = Ink(seed=305); k.a = VK.a.copy()
    k.a = np.maximum(k.a, fig_alpha('run%d' % int(t * 8 % 4), 0, lambda g, sw: person_back(g, 540, 1500 + 200 * p, 600 + 300 * p, phase=t * 9, sway=0)))
    base = k.apply(PAPER.copy() * 0.5)
    return zoom(base, 1.0 + 0.2 * p, 540, 1100, dx=math.sin(t * 30) * 8)
def sc_morning(lt, dur, t): return sc_home(lt, dur, t, steps=lt > dur * 0.4)

SCENES = [sc_hook, sc_village, sc_home, sc_walk, sc_lamp_down, sc_rope, sc_run, sc_morning]
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
    img = text(img, "KUAN  |  HORROR STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
