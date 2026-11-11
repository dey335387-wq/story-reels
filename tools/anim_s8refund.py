"""Standalone story 'REFUND' (con/scam thriller: fake Cyber-Cell 'inspector' slips by naming a debit only the thief knew) -
procedural ink-wash animation (no stock footage).  python3 anim_s8refund.py voice.wav caps.srt out.mp4 [--frames t1,t2]"""
import sys, os, math, re, subprocess, textwrap, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inkanim import *
from PIL import Image, ImageDraw, ImageFont
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FH = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
FPS = 30
END_CARD = 2.8
TITLE = "REFUND"

CAPS = ["SUBAH 7 BAJE SMS AAYA...", "MERE KHAATE SE 2 LAAKH KAT GAYE!",
        "10 MINUT BAAD CALL AAYA", "MAIN CYBER CELL SE INSPECTOR RATHORE", "AAPKA PAISA ABHI ROKA JA SAKTA HAI",
        "BAS REFUND KE LIYE EK OTP BATA DIJIYE", "MAIN OTP PADHNE LAGA, TABHI WO BOLE...",
        "JALDI KIJIYE, AAPKE 2 LAAKH 14 HAZAAR ATKE HAIN", "14 HAZAAR? SMS MEIN TOH SIRF 2 LAAKH THA",
        "APP KHOLA... 14 HAZAAR KA DOOSRA DEBIT", "JISKA SMS AAYA HI NAHI THA",
        "BANK NE BATAYA NAHI... TOH POLICE KO KAISE PATA?", "YE SIRF WO JAANTA THA, JISNE PAISA NIKALA",
        "PHIR MAINE OTP WALA MESSAGE POORA PADHA...", "YE OTP 5 LAAKH KE TRANSFER KE LIYE HAI"]
HOT = {"2", "LAAKH", "OTP", "14", "HAZAAR", "NAHI", "KAISE", "NIKALA", "5", "TRANSFER", "REFUND"}
SCENE_OF = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
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



# ================= REFUND: scenes =================
DARKBG = np.array([24, 26, 34], np.float32)
SCR = np.array([236, 236, 230], np.float32)       # screen paper
GREENB = np.array([40, 150, 80], np.float32)
REDB = np.array([200, 40, 40], np.float32)
MORN = np.array([255, 232, 190], np.float32)
MON = np.array([150, 190, 255], np.float32)
FM = "/usr/share/fonts/opentype/inter/Inter-Black.otf"

def phone_frame(img, x0=70, y0=90, x1=1010, y1=1830, scr=SCR, glowamt=0.0):
    """big phone body (ink) with a light screen inside; returns image."""
    k = Ink(seed=801)
    k.wash([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.97, 4)
    img = k.apply(img)
    m = np.zeros((H, W), np.float32)
    cv2.rectangle(m, (x0 + 34, y0 + 70), (x1 - 34, y1 - 60), 1, -1)
    m = cv2.GaussianBlur(m, (0, 0), 2)[..., None]
    sp = paper(seed=88) * scr / 228
    img = img * (1 - m) + sp * m
    cv2.rectangle(img, (int((x0 + x1) / 2 - 70), y0 + 28), (int((x0 + x1) / 2 + 70), y0 + 44), (10, 10, 12), -1, cv2.LINE_AA)
    return img

_ST = {}
def static(key, fn):
    if key not in _ST: _ST[key] = fn()
    return _ST[key].copy()

def sms_screen():
    img = PAPER.copy() * DARKBG / 228
    img = phone_frame(img)
    img = text(img, "7:00", (540, 260), 90, INK, stroke=0)
    img = text(img, "Messages", (540, 360), 44, (90, 90, 100), stroke=0)
    cv2.rectangle(img, (140, 440), (940, 1080), (250, 250, 246), -1, cv2.LINE_AA)
    cv2.rectangle(img, (140, 440), (940, 1080), (60, 60, 70), 3, cv2.LINE_AA)
    img = text(img, "BANK ALERT", (180, 510), 46, (60, 60, 70), "lm", 0)
    img = text(img, "A/c XX4417 DEBITED", (180, 600), 54, INK, "lm", 0)
    img = text(img, "Rs 2,00,000", (540, 760), 125, RED * 1.15, stroke=0)
    img = text(img, "on 11-11 at 06:59 AM", (180, 900), 44, INK, "lm", 0)
    img = text(img, "Not you? Call bank.", (180, 990), 44, (90, 90, 100), "lm", 0)
    return img

def sc_hook(lt, dur, t):
    """FULL-SCREEN proof: SMS 'Rs 2,00,000 DEBITED' circled red."""
    p = lt / max(dur, 0.1)
    img = static("sms", sms_screen)
    kr = Ink(seed=803)
    ell = cv2.ellipse2Poly((540, 765), (400, 110), -3, 0, int(30 + 330 * min(1, p * 1.7)), 6)
    if len(ell) > 2: kr.stroke(ell, 12, 7, 0.95, dry=0.1)
    img = kr.apply(img, RED * 1.15)
    sh = 6 * math.sin(t * 80) if lt < 0.5 else 0
    return zoom(img, 1.02 + 0.12 * p, 540, 760, dx=sh)

def call_screen():
    img = PAPER.copy() * DARKBG / 228
    img = phone_frame(img, scr=np.array([200, 205, 215], np.float32))
    img = text(img, "Incoming call...", (540, 300), 50, (60, 60, 70), stroke=0)
    k = Ink(seed=804)                                   # caller avatar: police cap silhouette
    k.wash(cv2.ellipse2Poly((540, 560), (130, 150), 0, 0, 360, 10), 0.9, 3)
    k.wash([(380, 470), (700, 470), (660, 410), (420, 410)], 0.97, 2)
    img = k.apply(img)
    img = text(img, "INSPECTOR RATHORE", (540, 820), 70, INK, stroke=0)
    img = text(img, "CYBER CELL", (540, 910), 56, (40, 60, 140), stroke=0)
    img = text(img, "+91 98XXX 0X1X3", (540, 990), 44, (70, 70, 80), stroke=0)
    return img

def sc_call(lt, dur, t):
    """incoming call from 'Inspector Rathore, Cyber Cell', phone vibrating."""
    p = lt / max(dur, 0.1)
    img = static("call", call_screen)
    pulse = 0.5 + 0.5 * math.sin(t * 8)
    for cx, col in ((300, GREENB), (780, REDB)):
        cv2.circle(img, (cx, 1250), int(85 + 12 * pulse * (cx == 300)), tuple(float(c) for c in col), -1, cv2.LINE_AA)
    img = text(img, "ANSWER", (300, 1380), 40, INK, stroke=0)
    img = text(img, "DECLINE", (780, 1380), 40, INK, stroke=0)
    buzz = 5 * math.sin(t * 90) if (lt * 2) % 1 < 0.4 else 0
    return zoom(img, 1.0 + 0.1 * p, 540, 800, dx=buzz, rot=0.6 * buzz / 5)

# ---------- room: man at window on the call ----------
def room_bg():
    k = Ink(seed=805)
    k.wash_rect(0, 0, W, H, 0.55, 0)
    k.a[300:1200, 330:860] = 0.0                        # window opening
    k.a = cv2.GaussianBlur(k.a, (0, 0), 6)
    for x in (330, 595, 860): k.stroke([(x, 300), (x, 1200)], 16, 14, 0.95, dry=0)
    for y in (300, 750, 1200): k.stroke([(330, y), (860, y)], 16, 14, 0.95, dry=0)
    for i in range(7): k.stroke([(380 + i * 70, 1200), (390 + i * 70, 300)], 3, 2, 0.35)   # grill bars
    k.wash([(0, 1650), (W, 1600), (W, H), (0, H)], 0.8, 8)                               # floor
    k.wash([(700, 1350), (1080, 1330), (1080, 1600), (700, 1620)], 0.85, 5)              # bed edge
    base = k.apply(PAPER.copy() * MORN / 228)
    return base

def sc_room(lt, dur, t):
    """man from behind at the morning window, phone at his ear (glow); OTP notification drops in."""
    p = lt / max(dur, 0.1)
    base = static("room", room_bg)
    g = static("man", lambda: (lambda g: (person_back(g, 560, 1820, 1300, walk=False, hair_long=False, dress="shirt"), g.a)[1])(Ink(seed=7)))
    base = base * (1 - g[..., None]) + INK * g[..., None]
    base = glow(base, 640, 690, 120, np.array([170, 210, 255], np.float32), 0.55 + 0.1 * math.sin(t * 5))
    img = zoom(base, 1.05 + 0.15 * p, 560, 800)
    if p > 0.45:                                         # OTP notification banner
        q = min(1, (p - 0.45) / 0.15)
        y = int(-220 + 420 * q)
        cv2.rectangle(img, (60, y), (1020, y + 200), (245, 245, 240), -1, cv2.LINE_AA)
        cv2.rectangle(img, (60, y), (1020, y + 200), (40, 40, 50), 4, cv2.LINE_AA)
        img = text(img, "BANK  |  now", (100, y + 50), 38, (80, 80, 90), "lm", 0)
        img = text(img, "OTP 482917 for ...", (100, y + 130), 62, INK, "lm", 0)
    return img

def amount_screen():
    img = PAPER.copy() * DARKBG / 228
    img = phone_frame(img, scr=np.array([200, 205, 215], np.float32))
    img = text(img, "INSPECTOR RATHORE", (540, 300), 60, INK, stroke=0)
    img = text(img, "on call", (540, 380), 44, (60, 60, 70), stroke=0)
    img = text(img, "SMS:", (180, 600), 50, (60, 60, 70), "lm", 0)
    img = text(img, "Rs 2,00,000", (540, 700), 110, INK, stroke=0)
    img = text(img, "Inspector:", (180, 900), 50, (60, 60, 70), "lm", 0)
    return img

def sc_amount(lt, dur, t):
    """on-call screen: SMS said Rs 2,00,000 but the 'inspector' says 2,14,000 - '14,000' flashes red."""
    p = lt / max(dur, 0.1)
    img = static("amt", amount_screen)
    s = int(lt) + 41
    img = text(img, "00:%02d" % (s % 60), (540, 450), 50, (30, 110, 60), stroke=0)
    col = RED * 1.15 if (p > 0.45 and (lt * 3) % 1 < 0.7) else INK
    img = text(img, "Rs 2,", (470, 1010), 110, INK, "rm", stroke=0)
    img = text(img, "14,000", (485, 1010), 110, col, "lm", stroke=0)
    if p > 0.45:
        kr = Ink(seed=806); ell = cv2.ellipse2Poly((660, 1012), (220, 95), 4, 0, int(30 + 330 * min(1, (p - 0.45) * 3)), 6)
        if len(ell) > 2: kr.stroke(ell, 10, 6, 0.95, dry=0.1)
        img = kr.apply(img, RED * 1.15)
        img = text(img, "?", (920, 1000), 160, RED * 1.15, stroke=0)
    return zoom(img, 1.03 + 0.12 * p, 560, 900)

def app_screen():
    img = PAPER.copy() * DARKBG / 228
    img = phone_frame(img)
    cv2.rectangle(img, (104, 160), (976, 330), (40, 60, 140), -1, cv2.LINE_AA)
    img = text(img, "MY BANK  -  STATEMENT", (540, 250), 54, (245, 245, 240), stroke=0)
    rows = [("06:58 AM", "UPI DEBIT", "- 14,000", "SMS: NOT SENT"), ("06:59 AM", "IMPS DEBIT", "- 2,00,000", "SMS: SENT"),
            ("10-11", "SALARY", "+ 48,500", "")]
    for i, (tm, what, amt, sms) in enumerate(rows):
        y = 470 + i * 230
        img = text(img, tm, (150, y), 40, (80, 80, 90), "lm", 0)
        img = text(img, what, (150, y + 60), 54, INK, "lm", 0)
        img = text(img, amt, (930, y + 30), 60, RED if amt.startswith("-") else (30, 120, 60), "rm", 0)
        if sms: img = text(img, sms, (930, y + 100), 36, RED * 1.1 if "NOT" in sms else (80, 80, 90), "rm", 0)
        cv2.line(img, (130, y + 140), (950, y + 140), (170, 170, 170), 2, cv2.LINE_AA)
    return img

def sc_app(lt, dur, t):
    """bank app: a hidden 14,000 debit at 06:58, 'SMS: NOT SENT', circled red; push in."""
    p = lt / max(dur, 0.1)
    img = static("app", app_screen)
    kr = Ink(seed=807); ell = cv2.ellipse2Poly((540, 530), (460, 120), -2, 0, int(30 + 330 * min(1, p * 1.6)), 6)
    if len(ell) > 2: kr.stroke(ell, 12, 7, 0.95, dry=0.1)
    img = kr.apply(img, RED * 1.15)
    img = light(img, 540, 530, 900, t, 0.35)
    return zoom(img, 1.05 + 0.35 * p, 540, 530, dy=800 - 530)

# ---------- scammer's dark room ----------
def con_bg():
    img = PAPER.copy() * np.array([30, 34, 48], np.float32) / 228
    for i, (x, y) in enumerate(((150, 520), (540, 470), (930, 520))):          # 3 monitors
        img = glow(img, x, y, 360, MON, 0.45)
        cv2.rectangle(img, (x - 170, y - 120), (x + 170, y + 120), (200, 220, 245), -1, cv2.LINE_AA)
        cv2.rectangle(img, (x - 170, y - 120), (x + 170, y + 120), (10, 10, 14), 8, cv2.LINE_AA)
        for r in range(5):
            cv2.line(img, (x - 140, y - 80 + r * 40), (x + 40 + (r * 37 % 90), y - 80 + r * 40), (60, 70, 100), 8, cv2.LINE_AA)
    # sticky note list on wall
    cv2.rectangle(img, (720, 760), (1020, 1080), (235, 225, 140), -1, cv2.LINE_AA)
    img = text(img, "XX4417", (870, 820), 44, INK, stroke=0)
    img = text(img, "2,14,000", (870, 900), 50, INK, stroke=0)
    img = text(img, "OTP > 5L", (870, 990), 50, RED * 1.1, stroke=0)
    k = Ink(seed=808)
    k.wash([(0, 1250), (W, 1250), (W, 1320), (0, 1320)], 0.95, 3)                # desk
    for i in range(6):                                                            # row of phones on desk
        x = 120 + i * 160
        k.wash([(x, 1180), (x + 80, 1180), (x + 80, 1250), (x, 1250)], 0.95, 2)
    img = k.apply(img)
    for i in range(6): img = glow(img, 160 + i * 160, 1200, 60, MON, 0.35)
    g = Ink(seed=7); person_back(g, 470, 2150, 1500, walk=False, hair_long=False, dress="shirt")
    img = img * (1 - g.a[..., None]) + INK * 0.6 * g.a[..., None]
    kh = Ink(seed=809); kh.stroke(bezier((370, 1000), (470, 860), (570, 1000)), 16, 14, 0.98, dry=0)   # headset
    kh.stroke(bezier((380, 1010), (330, 1080), (420, 1120)), 9, 6, 0.98, dry=0)
    img = kh.apply(img)
    return img

def sc_con(lt, dur, t):
    """reveal: the 'inspector' is a con-man in a dark room full of phones; sticky note has my account."""
    p = lt / max(dur, 0.1)
    img = static("con", con_bg)
    img = img * (0.85 + 0.15 * flicker(t, 4))
    return zoom(img, 1.0 + 0.25 * p, 760 * p + 540 * (1 - p), 920 * p + 900 * (1 - p))

OTP_UL = [900]
def otp_screen():
    img = PAPER.copy() * DARKBG / 228
    img = phone_frame(img)
    img = text(img, "BANK ALERT", (150, 330), 50, (80, 80, 90), "lm", 0)
    lines = [("OTP  482917", INK, 100), ("for TRANSFER of", INK, 66), ("Rs 5,00,000", RED * 1.15, 112),
             ("to A/c XX9031.", INK, 66), ("Do NOT share OTP", INK, 60), ("with anyone, even police.", INK, 52)]
    y = 460
    for s, c, sz in lines:
        img = text(img, s, (150, y), sz, c, "lm", 0)
        if s.startswith("Rs"): OTP_UL[0] = y + 75
        y += sz + 42
    return img

def sc_otp(lt, dur, t):
    """full OTP message: 'for TRANSFER of Rs 5,00,000' - red underline, slow push in."""
    p = lt / max(dur, 0.1)
    img = static("otp", otp_screen)
    kr = Ink(seed=810); x1 = 150 + 760 * min(1, p * 1.5)
    kr.stroke([(150, OTP_UL[0]), (x1, OTP_UL[0] + 5)], 12, 8, 0.95, dry=0.1)
    img = kr.apply(img, RED * 1.15)
    img = img * (0.92 + 0.08 * flicker(t, 6))
    return zoom(img, 1.05 + 0.15 * p, 540, 700)

SCENES = [sc_hook, sc_call, sc_room, sc_amount, sc_app, sc_con, sc_otp]

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
    img = text(img, TITLE + "  |  SUSPENSE STORY", (W / 2, 140), 44, RED * 1.25, stroke=4)
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
