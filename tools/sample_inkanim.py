"""15 s sample: fully hand-made (procedural) ink-wash animation, no stock footage.
python3 sample_inkanim.py out.mp4 [--frames t1,t2]"""
import sys, os, math, subprocess, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FPS, T = 30, 15.0
PAPER = paper(seed=5)
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.5 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)).clip(0.3, 1)[..., None].astype(np.float32)

def corridor_bg():
    k = Ink(seed=11); vx, vy = W / 2, 820
    k.wash([(0, 0), (W, 0), (vx + 110, vy - 140), (vx - 110, vy - 140)], 0.55, 10)          # ceiling
    k.wash([(0, H), (W, H), (vx + 110, vy + 150), (vx - 110, vy + 150)], 0.35, 14)        # floor
    k.wash_rect(vx - 110, vy - 140, vx + 110, vy + 150, 0.45, 4)                         # far end: lift door
    k.stroke([(vx, vy - 140), (vx, vy + 150)], 3, 3, 0.8)
    k.stroke([(vx - 110, vy - 140), (vx + 110, vy - 140), (vx + 110, vy + 150), (vx - 110, vy + 150), (vx - 110, vy - 140)], 5, 4)
    for side in (-1, 1):
        xo = 0 if side < 0 else W; xi = vx + side * 110
        k.stroke([(xo, 0), (xi, vy - 140)], 7, 3); k.stroke([(xo, H), (xi, vy + 150)], 7, 3)
        k.stroke([(xi, vy - 140), (xi, vy + 150)], 4, 3)
        for i, f in enumerate((0.12, 0.38, 0.6, 0.78)):                                   # doors
            def P(ff, yo, yi): return (xo + (xi - xo) * ff, yo + (yi - yo) * ff)
            q = [P(f, 380, vy - 90), P(f + 0.1, 380, vy - 90), P(f + 0.1, H - 160, vy + 130), P(f, H - 160, vy + 130)]
            k.wash(q, 0.55 + 0.1 * i, 3); k.stroke([q[0], q[1], q[2], q[3], q[0]], 3, 2)
            hx, hy = P(f + 0.085, 1180, vy + 30); k.blot(hx, hy, max(2, 9 * (1 - f)), 0.95)
        for j in range(8):                                                              # wall texture strokes
            f = k.rng.random() * 0.9; y = 300 + k.rng.random() * 1200
            a = (xo + (xi - xo) * f, y + (vy - y) * f); b = (a[0] + side * 30, a[1] + 60)
            k.stroke([a, b], 2, 0.5, 0.35)
    lights = []
    for f in (0.0, 0.35, 0.62):                                                           # tube lights
        y = 60 + (vy - 140 - 60) * f; half = (W / 2 - 40) * (1 - f) * 0.4
        lights.append((vx - half, y, vx + half, y + 30 * (1 - f) + 10))
    return k, lights

CK, LIGHTS = corridor_bg()

def panel_bg():
    k = Ink(seed=21)
    k.wash_rect(0, 0, W, H, 0.42, 30)
    k.wash_rect(260, 250, 820, 1500, 0.75, 6)
    k.stroke([(260, 250), (820, 250), (820, 1500), (260, 1500), (260, 250)], 8, 6)
    btn = []
    for r in range(7):
        for cc in range(2):
            x, y = 420 + cc * 240, 400 + r * 150; btn.append((x, y, 13 - (r * 2 + cc)))
            k.stroke(bezier((x - 55, y), (x, y - 75), (x + 55, y)), 4, 4, 0.9)
            k.stroke(bezier((x + 55, y), (x, y + 75), (x - 55, y)), 4, 4, 0.9)
    return k, btn

PK, BTNS = panel_bg()

def text(img, s, xy, size, col, anchor="mm", stroke=6):
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil)
    d.text(xy, s, font=ImageFont.truetype(FB, size), fill=tuple(int(c) for c in col), anchor=anchor, stroke_width=stroke, stroke_fill=(10, 10, 12))
    return np.asarray(pil)

CAPS = [(0.3, 3.0, "RAAT 2:47 BAJE..."), (3.0, 6.0, "NEHA LIFT KI TARAF CHAL RAHI THI"),
        (6.2, 10.4, "AUR LIFT MEIN... 13 JAL RAHA THA"), (10.6, 13.2, "DARWAZA KHULA..."), (13.2, 14.2, "...")]

def zoom(img, z, cx=W / 2, cy=H / 2):
    M = cv2.getRotationMatrix2D((cx, cy), 0, z)
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)

def frame(t):
    if t < 6.0:  # corridor walk
        fl = flicker(t, 1)
        k = Ink(seed=int(t * 30) % 7 + 30); k.a = CK.a.copy()
        p = t / 6.0
        h = 1150 - 560 * p; feet = 1760 - 560 * p
        person_back(k, W / 2 + math.sin(t * 0.8) * 10, feet, h, phase=t * 4.2, sway=math.sin(t * 2.1))
        base = k.apply(PAPER.copy())
        for (x0, y0, x1, y1) in LIGHTS:
            cv2.rectangle(base, (int(x0), int(y0)), (int(x1), int(y1)), (250, 248, 230) if fl > .5 else (90, 90, 90), -1)
        base = base * (0.55 + 0.45 * fl)
        g13 = (0.6 + 0.4 * math.sin(t * 6)); m13 = np.zeros((H, W), np.uint8); cv2.putText(m13, '13', (int(W/2-28), 700), cv2.FONT_HERSHEY_DUPLEX, 1.4, 255, 3, cv2.LINE_AA); m13 = cv2.GaussianBlur(m13.astype(np.float32) / 255, (0, 0), 1.2)[..., None] * g13; base = base * (1 - m13) + RED * 1.3 * m13
        img = zoom(base, 1.0 + 0.06 * p, W / 2, 900)
    elif t < 10.5:  # lift panel, 13 glows
        lt = t - 6.0
        k = Ink(seed=41); k.a = PK.a.copy()
        base = k.apply(PAPER.copy())
        img0 = base.copy()
        glow = min(1, lt / 1.2) * (0.75 + 0.25 * math.sin(lt * 9))
        x, y, _ = BTNS[0]
        m = np.zeros((H, W), np.float32); cv2.circle(m, (x, y), 70 + int(lt * 25), 1, -1)
        m = cv2.GaussianBlur(m, (0, 0), 25)[..., None] * glow
        img0 = img0 * (1 - m * 0.8) + RED * m * 0.8
        img0 = np.clip(img0, 0, 255).astype(np.uint8)
        for (bx, by, n) in BTNS:
            img0 = text(img0, str(n), (bx, by), 64, (235, 60, 60) if n == 13 else (200, 196, 186), stroke=3)
        img = zoom(img0.astype(np.float32), 1.0 + 0.12 * (lt / 4.5), BTNS[0][0], BTNS[0][1])
    else:  # doors open, figure inside
        lt = t - 10.5
        k = Ink(seed=51)
        k.wash_rect(0, 0, W, H, 0.5, 30)
        op = min(1, max(0, (lt - 0.3) / 1.6))
        k.wash_rect(180, 260, 900, 1720, 0.99, 3)  # dark inside
        base = k.apply(PAPER.copy())
        g = Ink(seed=52)
        e1, e2, hu = ghost_front(g, W / 2, 1700, 1300 + 120 * min(1, lt / 4), sway=math.sin(lt * 1.7) * 1.5)
        # figure is lit faintly: draw as slightly lighter grey inside the black lift
        fig = g.a[..., None]
        hairw = np.clip((g.a - 0.93) / 0.04, 0, 1)[..., None]
        figcol = np.array([168, 164, 158], np.float32) * (1 - hairw) + INK * hairw
        base = base * (1 - fig) + figcol * fig
        edge = cv2.morphologyEx(g.a, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))[..., None]
        base = base * (1 - edge * .8) + INK * edge * .8
        if lt > 2.8:
            for (ex, ey) in (e1, e2):
                cv2.ellipse(base, (int(ex), int(ey)), (14, 6), 0, 0, 360, tuple(float(c) for c in RED * 1.3), -1, cv2.LINE_AA)
        d = Ink(seed=53)
        dw = 360 * (1 - op)
        d.wash_rect(180, 260, 180 + dw, 1720, 0.85, 2); d.wash_rect(900 - dw, 260, 900, 1720, 0.85, 2)
        d.stroke([(180, 260), (900, 260), (900, 1720), (180, 1720), (180, 260)], 10, 8)
        base = d.apply(base, np.array([60, 60, 66], np.float32))
        base = np.where(np.broadcast_to(d.a[..., None] > 0.5, base.shape), base, base)
        img = zoom(base, 1.0 + 0.05 * lt)
    img = np.asarray(img, np.float32)
    rng = np.random.default_rng(int(t * 24))
    img = img + cv2.resize(rng.normal(0, 5, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None]
    img = img * VIG + INK * (1 - VIG) * 0.6
    img = np.clip(img, 0, 255).astype(np.uint8)
    for a, b, s in CAPS:
        if a <= t < b:
            import textwrap
            for li, ln in enumerate(textwrap.wrap(s, 18)):
                img = text(img, ln, (W / 2, 1520 + li * 90), 72, (245, 242, 235))
    if t > 14.0:
        e = min(1, (t - 14.0) / 0.4)
        img = (img * (1 - e * 0.85)).astype(np.uint8)
        img = text(img, "13VI MANZIL", (W / 2, 900), 120, RED * 1.2)
    return img

if __name__ == "__main__":
    out = sys.argv[1]
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            cv2.imwrite(f"{out}_{ts}.jpg", cv2.cvtColor(frame(float(ts)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        sys.exit()
    tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(T * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out); print("ok")
