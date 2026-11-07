"""Standalone story 'GALLERY' (PG room, Pune, phone photos at 3:07 AM) - procedural ink-wash animation (no stock footage).
python3 anim_s3gallery.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FPS = 30
END_CARD = 2.8
TITLE = "GALLERY"

CAPS = ["MERE PHONE KI GALLERY MEIN EK NAYI PHOTO THI...", "RAAT 3:07 KI", "PHOTO MEIN MAIN SO RAHI THI...", "UPAR SE KHEENCHI HUI",
        "MAIN KAVYA, PUNE KE PG MEIN AKELI RAHTI HOON", "LAGA KISI KA MAZAAK HAI...", "PAR DARWAZA ANDAR SE BAND THA",
        "AGLI RAAT MAIN JAAGTI RAHI", "3:06 PE CAMERA APNE AAP KHULA...", "AUR FLASH JALA",
        "SCREEN PE MAIN THI...", "AUR MERE PEECHE, ALMIRAH KE UPAR...", "KOI BAITHA THA",
        "MAINE MUDKE DEKHA...", "ALMIRAH KHAALI THA",
        "TABHI EK AUR PHOTO SAVE HUI... 3:08", "IS BAAR PHOTO MEIN...", "MERE KANDHE PE EK HAATH THA"]
HOT = {"3:07", "3:06", "3:08", "UPAR", "BAND", "FLASH", "PEECHE", "ALMIRAH", "BAITHA", "KHAALI", "HAATH", "AKELI"}
SCENE_OF = [0, 0, 0, 0, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6]
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
def room_bg():
    k = Ink(seed=201)
    k.wash_rect(0, 0, W, H, 0.62, 25)
    k.wash([(0, 1250), (W, 1200), (W, H), (0, H)], 0.42, 8)
    k.wash_rect(110, 330, 430, 720, 0.2, 4)                                   # window left
    k.stroke([(110, 330), (430, 330), (430, 720), (110, 720), (110, 330)], 10, 8)
    k.stroke([(270, 330), (270, 720)], 7, 6)
    k.wash([(40, 1050), (700, 1010), (760, 1180), (60, 1250)], 0.5, 4)        # bed
    k.stroke([(40, 1050), (700, 1010), (760, 1180), (60, 1250), (40, 1050)], 5, 4)
    k.wash([(60, 1250), (760, 1180), (760, 1300), (60, 1380)], 0.9, 3)
    k.wash_rect(800, 640, 1060, 1450, 0.86, 3); k.stroke([(930, 650), (930, 1440)], 3, 3)  # tall almirah right
    k.stroke([(800, 640), (1060, 640)], 6, 5)
    return k
RMK = room_bg()

DX0, DY0, DX1, DY1 = 250, 320, 830, 1560
def door_bg():
    k = Ink(seed=211)
    k.wash_rect(0, 0, W, H, 0.82, 25)
    k.wash([(0, 1560), (W, 1560), (W, H), (0, H)], 0.55, 6)
    k.wash_rect(DX0, DY0, DX1, DY1, 0.62, 3)
    k.stroke([(DX0, DY0), (DX1, DY0), (DX1, DY1), (DX0, DY1), (DX0, DY0)], 16, 14, 0.99, dry=0)
    for (a, b, c, d) in ((310, 400, 770, 900), (310, 980, 770, 1480)):
        k.stroke([(a, b), (c, b), (c, d), (a, d), (a, b)], 4, 4, 0.9)
    k.blot(780, 960, 18, 0.99); k.stroke([(780, 960), (730, 965)], 8, 6)
    k.wash_rect(640, 690, 820, 712, 0.99, 2); k.wash_rect(800, 670, 830, 735, 0.99, 2)   # bolt shut
    return k
DK = door_bg()

def topview_bg():
    """girl sleeping, seen from the ceiling (the 'photo')."""
    k = Ink(seed=221)
    k.wash_rect(0, 0, W, H, 0.7, 20)
    k.wash([(200, 300), (880, 300), (880, 1650), (200, 1650)], 0.25, 6)       # mattress
    k.stroke([(200, 300), (880, 300), (880, 1650), (200, 1650), (200, 300)], 6, 5)
    k.wash(cv2.ellipse2Poly((540, 470), (230, 90), 0, 0, 360, 10), 0.12, 5)   # pillow
    k.wash(cv2.ellipse2Poly((540, 520), (85, 100), 0, 0, 360, 10), 0.97, 4)   # head (hair)
    k.wash(cv2.ellipse2Poly((540, 1050), (190, 430), 0, 0, 360, 10), 0.45, 10) # body under sheet
    for i in range(5): k.stroke(bezier((380 + i * 70, 700), (420 + i * 60, 1000), (360 + i * 80, 1450)), 3, 1.5, 0.55)
    for i in range(14): k.stroke(bezier((470 + i * 10, 470), (420 + i * 12, 560), (380 + i * 16, 640)), 1.8, 0.8, 0.9)  # hair spread
    return k
TVK = topview_bg()

_FIG = {}
def fig_alpha(key, sway, fn):
    sk = round(sway * 5) / 5
    if (key, sk) not in _FIG:
        g = Ink(seed=7); fn(g, sk); _FIG[(key, sk)] = g.a
    return _FIG[(key, sk)]

def room_img(t, ghost=False, hand=False, girl=True):
    k = Ink(seed=202); k.a = RMK.a.copy()
    if girl:
        k.a = np.maximum(k.a, fig_alpha('g', math.sin(t * 0.9) * 0.6, lambda g, sw: person_back(g, 360, 1330, 760, walk=False, sway=sw)))
        k.wash([(40, 1180), (760, 1110), (760, 1330), (60, 1400)], 0.9, 3)
    eyes = None
    if ghost:
        ga = fig_alpha('gh', 0.0, lambda g, sw: ghost_front(g, 930, 640, 520, sway=0))
        k.a = np.maximum(k.a, ga)
    if hand:                                                                   # dark long-fingered hand on her shoulder
        for i in range(4):
            k.stroke([(470, 760), (430 - i * 6, 800 + i * 4), (400 - i * 10, 850 + i * 8)], 9, 3, 0.99, dry=0)
        k.stroke([(560, 640), (500, 720), (470, 760)], 18, 10, 0.99, dry=0)
    base = k.apply(PAPER.copy())
    base = glow(base, 270, 520, 300, COLD, 0.5)
    if ghost:
        for ex in (905, 955): base = glow(base, ex, 455, 26, RED * 1.4, 0.9)
    return light(base, 560, 900, 900, t, 0.5)

def phone(img_in, lt, t, stamp, flash=0.0, pz=1.0):
    """phone held in hand showing img_in on its screen."""
    bg = Ink(seed=231); bg.wash_rect(0, 0, W, H, 0.9, 30); base = bg.apply(PAPER.copy() * 0.6)
    PX0, PY0, PX1, PY1 = 170, 230, 910, 1690
    sw, sh = PX1 - PX0 - 60, PY1 - PY0 - 200
    scr = cv2.resize(np.float32(img_in), (sw, sh), interpolation=cv2.INTER_AREA)
    scr = scr * (1 - flash) + 255 * flash
    out = base.copy()
    k = Ink(seed=232)
    k.wash_rect(PX0, PY0, PX1, PY1, 0.97, 4)
    out = k.apply(out)
    out[PY0 + 110:PY0 + 110 + sh, PX0 + 30:PX0 + 30 + sw] = scr
    out = text(out, stamp, (W / 2, PY0 + 60), 46, (235, 232, 225), stroke=3)
    hk = Ink(seed=233)                                                         # thumb + fingers
    hk.wash(cv2.ellipse2Poly((150, 1250), (90, 260), 10, 0, 360, 10), 0.92, 6)
    hk.wash(cv2.ellipse2Poly((930, 1100), (70, 200), -10, 0, 360, 10), 0.92, 6)
    out = hk.apply(out)
    return zoom(out, pz, 540, 960, dy=math.sin(t * 2.3) * 6)

def sc_photo(lt, dur, t):
    p = lt / max(dur, 0.1)
    shot = TVK.apply(PAPER.copy()); shot = light(shot, 540, 700, 650, t, 0.8); shot = glow(shot, 540, 600, 500, COLD, 0.25)
    return phone(shot, lt, t, "Gallery  -  Today 3:07 AM", pz=1.0 + 0.35 * p)

def sc_room(lt, dur, t):
    p = lt / max(dur, 0.1)
    return zoom(room_img(t), 1.05 + 0.2 * p, 420, 1000)

def sc_door(lt, dur, t):
    p = lt / max(dur, 0.1)
    k = Ink(seed=212); k.a = DK.a.copy()
    base = k.apply(PAPER.copy() * 0.7)
    base = glow(base, (DX0 + DX1) / 2, DY1 + 6, 260, COLD, 0.45)
    return zoom(base, 1.05 + 0.5 * p, 730, 700, dy=(960 - 700) * min(1, p))

def sc_flash(lt, dur, t):
    p = lt / max(dur, 0.1)
    fl = 0.0
    if p > 0.62: fl = max(0, 1 - (p - 0.62) / 0.25)
    img = room_img(t, girl=True)
    img = cv2.flip(np.float32(img), 1)
    return phone(img, lt, t, "Camera  -  3:06 AM", flash=fl, pz=1.0 + 0.1 * p)

def sc_ghost(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = room_img(t, ghost=True)
    return zoom(img, 1.1 + 1.0 * p * p, 930, 700, dy=(960 - 700) * p)

def sc_empty(lt, dur, t):
    p = lt / max(dur, 0.1)
    whip = max(0, 1 - lt / 0.35)
    img = room_img(t, girl=False)
    return zoom(img, 1.6 - 0.3 * p, 930, 900, dx=whip * 600, dy=60)

def sc_final(lt, dur, t):
    p = lt / max(dur, 0.1)
    img = room_img(t, hand=p > 0.45)
    return phone(img, lt, t, "New photo  -  3:08 AM", pz=1.0 + 0.45 * p)

SCENES = [sc_photo, sc_room, sc_door, sc_flash, sc_ghost, sc_empty, sc_final]
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
    img = text(img, "GALLERY  |  HORROR STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
