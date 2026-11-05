"""Procedural ink-wash animation kit (no stock footage): paper, brush strokes, washes, realistic-proportion
human figures (8-head canon), simple rigs (walk, sway, hair), light flicker. 1080x1920 frames (RGB uint8)."""
import math, numpy as np, cv2
W, H = 1080, 1920
INK = np.array([16, 14, 18], np.float32)
RED = np.array([175, 18, 28], np.float32)

def paper(w=W, h=H, seed=1):
    rng = np.random.default_rng(seed)
    n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 3) * 6
    blot = cv2.resize(cv2.GaussianBlur(rng.normal(0, 1, (h // 8, w // 8)).astype(np.float32), (0, 0), 4), (w, h)) * 10
    p = np.clip(228 + n + blot, 0, 255)
    return np.dstack([p, p * 0.972, p * 0.925]).astype(np.float32)

class Ink:
    """Alpha layer of ink (0..1) with brush helpers; composite onto paper with .apply()."""
    def __init__(self, w=W, h=H, seed=3):
        self.a = np.zeros((h, w), np.float32); self.rng = np.random.default_rng(seed); self.w, self.h = w, h
    def wash(self, pts, val=0.5, blur=18):
        m = np.zeros_like(self.a); cv2.fillPoly(m, [np.int32(pts)], 1.0)
        if blur: m = cv2.GaussianBlur(m, (0, 0), blur)
        self.a = np.maximum(self.a, m * val)
    def wash_rect(self, x0, y0, x1, y1, val=0.5, blur=18):
        self.wash([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], val, blur)
    def stroke(self, pts, w0=6, w1=2, val=0.95, jitter=0.6, dry=0.15):
        """Tapered brush stroke: smooth polygon from offset normals + dry-brush texture."""
        pts = np.asarray(pts, np.float32)
        if len(pts) < 2: return
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); L = seg.sum() + 1e-6
        n = max(4, int(L / 4)); t = np.linspace(0, 1, n)
        cum = np.concatenate([[0], np.cumsum(seg)]) / L
        P = np.stack([np.interp(t, cum, pts[:, 0]), np.interp(t, cum, pts[:, 1])], 1)
        d = np.gradient(P, axis=0); d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-6)
        nrm = np.stack([-d[:, 1], d[:, 0]], 1)
        wid = (w0 + (w1 - w0) * t) * (0.9 + 0.2 * np.sin(t * 9 + self.rng.random() * 6)) * np.minimum(1, (t + 0.08) * 6)
        wob = self.rng.normal(0, jitter, (n, 1))
        poly = np.vstack([P + nrm * (wid[:, None] / 2 + wob), (P - nrm * (wid[:, None] / 2 - wob))[::-1]])
        m = np.zeros_like(self.a); cv2.fillPoly(m, [np.int32(poly)], 1.0, cv2.LINE_AA)
        if dry > 0:
            x0, y0 = np.int32(np.maximum(0, poly.min(0) - 4)); x1, y1 = np.int32(np.minimum([self.w, self.h], poly.max(0) + 4))
            if x1 > x0 and y1 > y0:
                tex = self.rng.random((y1 - y0, x1 - x0)).astype(np.float32)
                tex = cv2.GaussianBlur(tex, (0, 0), 1.2)
                m[y0:y1, x0:x1] *= np.clip(1 - dry * 2.5 * (tex < 0.42), 0, 1)
        m = cv2.GaussianBlur(m, (0, 0), 0.7)
        self.a = np.maximum(self.a, m * val)
    def line(self, p0, p1, w=5, val=0.95):
        self.stroke([p0, p1], w, w * 0.6, val)
    def blot(self, x, y, r, val=0.9):
        m = np.zeros_like(self.a); cv2.circle(m, (int(x), int(y)), int(r), 1.0, -1, cv2.LINE_AA)
        self.a = np.maximum(self.a, cv2.GaussianBlur(m, (0, 0), r * 0.25 + 1) * val)
    def apply(self, base, col=INK):
        a = self.a[..., None]
        return base * (1 - a) + col * a

def bezier(p0, p1, p2, n=24):
    t = np.linspace(0, 1, n)[:, None]; p0, p1, p2 = map(np.float32, (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

def person_back(ink, cx, feet, height, phase=0.0, walk=True, hair_long=True, sway=0.0, val=0.97, dress="kurta"):
    """Woman seen from behind, 8-head proportions. phase drives walk cycle; sway drives hair motion."""
    hu = height / 8.0  # head unit
    top = feet - height
    s = math.sin(phase); c = math.cos(phase)
    bob = abs(s) * hu * 0.06 if walk else 0
    hx, hy = cx, top + hu * 0.5 - bob
    # head + hair mass
    head = cv2.ellipse2Poly((int(hx), int(hy)), (int(hu * 0.42), int(hu * 0.52)), 0, 0, 360, 10)
    ink.wash(head, val, 2)
    if hair_long:
        hair = np.vstack([bezier((hx - hu * .45, hy - hu * .1), (hx - hu * .62 + sway * 8, hy + hu * 1.4), (hx - hu * .28 + sway * 14, hy + hu * 2.7)),
                          bezier((hx + hu * .28 + sway * 14, hy + hu * 2.7), (hx + hu * .62 + sway * 8, hy + hu * 1.4), (hx + hu * .45, hy - hu * .1))])
        ink.wash(hair, val, 3)
        for k in range(9):  # loose strands
            ox = (k - 4) * hu * 0.09
            ink.stroke(bezier((hx + ox, hy + hu * .3), (hx + ox * 1.6 + sway * 10, hy + hu * 1.6), (hx + ox * 1.2 + sway * 18 + math.sin(k + phase) * 4, hy + hu * 2.9)), 2.2, 0.8, val)
    # neck
    ink.wash([(hx - hu * .16, hy + hu * .4), (hx + hu * .16, hy + hu * .4), (hx + hu * .2, top + hu * 1.5), (hx - hu * .2, top + hu * 1.5)], val, 2)
    sh_y = top + hu * 1.45 - bob
    sw = hu * 0.78
    L_side = np.vstack([bezier((cx - sw, sh_y), (cx - hu * .62, top + hu * 2.6), (cx - hu * .52, top + hu * 3.2)),
                        bezier((cx - hu * .52, top + hu * 3.2), (cx - hu * .82, top + hu * 4.1), (cx - hu * .95 - abs(s) * hu * .1, top + hu * 5.6))])
    R_side = np.vstack([bezier((cx + sw, sh_y), (cx + hu * .62, top + hu * 2.6), (cx + hu * .52, top + hu * 3.2)),
                        bezier((cx + hu * .52, top + hu * 3.2), (cx + hu * .82, top + hu * 4.1), (cx + hu * .95 + abs(s) * hu * .1, top + hu * 5.6))])
    shoulder = bezier((cx - sw, sh_y), (cx, sh_y - hu * .22), (cx + sw, sh_y))
    torso = np.vstack([shoulder, R_side, L_side[::-1]])
    ink.wash(torso, val * 0.88, 2.5)
    ink.stroke(L_side, 3.2, 1.6, val); ink.stroke(R_side, 3.2, 1.6, val)
    for k in range(3):  # kurta folds
        fx = cx + (k - 1) * hu * .35
        ink.stroke(bezier((fx, top + hu * 3.6), (fx + s * hu * .1, top + hu * 4.6), (fx + s * hu * .15, top + hu * 5.5)), 1.6, .6, val * .55)
    # arms: tapered, natural swing
    for side, ph in ((-1, s), (1, -s)):
        ax = cx + side * sw * 0.92; ay = sh_y + hu * 0.12
        sw_a = ph * 0.30 if walk else 0.04 * side
        ex = ax + side * hu * 0.10 + math.sin(sw_a) * hu * 1.35; ey = ay + math.cos(sw_a) * hu * 1.4
        wx = ex + math.sin(sw_a * 1.4) * hu * 1.2 + side * hu * .05; wy = ey + math.cos(sw_a * 1.4) * hu * 1.2
        ink.stroke([(ax, ay), (ex, ey)], hu * 0.22, hu * 0.15, val, dry=0.05)
        ink.stroke([(ex, ey), (wx, wy)], hu * 0.15, hu * 0.09, val, dry=0.05)
        ink.stroke([(wx, wy), (wx + side * hu * .03, wy + hu * .35)], hu * 0.11, hu * 0.04, val, dry=0)
    # legs below kurta (salwar), stride
    hip_y = top + hu * 5.4
    for side, ph in ((-1, s), (1, -s)):
        lx = cx + side * hu * 0.26
        st = ph * 0.26 if walk else 0
        fx = lx + math.sin(st) * hu * 2.4; fy = feet - (hu * .15 if (walk and ph < -0.3) else 0)
        kx = (lx + fx) / 2 + math.sin(st) * hu * .2; ky = (hip_y + fy) / 2
        ink.stroke([(lx, hip_y), (kx, ky), (fx, fy)], hu * 0.3, hu * 0.13, val, dry=0.08)
        ink.stroke([(fx - hu * .08, fy), (fx + side * hu * .05, fy + hu * .08)], hu * 0.12, hu * 0.1, val, dry=0)
    # dupatta / scarf trailing
    ink.stroke(bezier((cx - sw * .9, sh_y + hu * .1), (cx - sw * 1.4 + sway * 20, sh_y + hu * 2), (cx - sw * 1.2 + sway * 30, sh_y + hu * 3.6)), hu * .18, hu * .05, val * .8)

def ghost_front(ink, cx, feet, height, sway=0.0, val=0.98, eyes=1.0):
    """Tall figure facing camera, long hair covering the face (classic Indian horror), 8-head proportions."""
    hu = height / 8.0; top = feet - height
    hx, hy = cx, top + hu * 0.5
    ink.wash(cv2.ellipse2Poly((int(hx), int(hy)), (int(hu * .45), int(hu * .55)), 0, 0, 360, 10), val, 2)
    hair = np.vstack([bezier((hx - hu * .5, hy - hu * .2), (hx - hu * .8 + sway * 6, hy + hu * 2), (hx - hu * .55 + sway * 12, hy + hu * 3.6)),
                      bezier((hx + hu * .55 + sway * 12, hy + hu * 3.6), (hx + hu * .8 + sway * 6, hy + hu * 2), (hx + hu * .5, hy - hu * .2))])
    ink.wash(hair, val, 4)
    for k in range(14):
        ox = (k - 6.5) * hu * 0.07
        ink.stroke(bezier((hx + ox, hy - hu * .2), (hx + ox * 1.5 + sway * 8, hy + hu * 1.8), (hx + ox * 1.3 + sway * 15, hy + hu * 3.7)), 2, .8, val)
    sh = top + hu * 1.5
    Ls = np.vstack([bezier((cx - hu * .7, sh), (cx - hu * .55, top + hu * 3.2), (cx - hu * .75, top + hu * 4.5)),
                    bezier((cx - hu * .75, top + hu * 4.5), (cx - hu * 1.05, top + hu * 6.5), (cx - hu * 1.25 + sway * 6, feet))])
    Rs = np.vstack([bezier((cx + hu * .7, sh), (cx + hu * .55, top + hu * 3.2), (cx + hu * .75, top + hu * 4.5)),
                    bezier((cx + hu * .75, top + hu * 4.5), (cx + hu * 1.05, top + hu * 6.5), (cx + hu * 1.25 + sway * 6, feet))])
    body = np.vstack([bezier((cx - hu * .7, sh), (cx, sh - hu * .25), (cx + hu * .7, sh)), Rs, Ls[::-1]])
    ink.wash(body, 0.88, 3)
    ink.stroke(Ls, 3, 1.5, 0.9); ink.stroke(Rs, 3, 1.5, 0.9)
    for k in range(5):  # saree folds
        fx = cx + (k - 2) * hu * .3
        ink.stroke(bezier((fx, top + hu * 3.8), (fx + sway * 4, top + hu * 6), (fx + (k - 2) * 6 + sway * 8, feet - 10)), 1.8, .6, 0.91)
    for side in (-1, 1):  # long thin arms hanging, long fingers
        ax = cx + side * hu * .72; ay = sh + hu * .1
        ink.stroke(bezier((ax, ay), (ax + side * hu * .3, ay + hu * 1.8), (ax + side * hu * .22, ay + hu * 3.3)), hu * .16, hu * .08, val, dry=0.05)
        bx, by = ax + side * hu * .22, ay + hu * 3.3
        for f in range(4):
            ink.stroke([(bx + (f - 1.5) * hu * .05, by), (bx + (f - 1.5) * hu * .07, by + hu * .55 + (f % 2) * 6)], hu * .04, hu * .015, val, dry=0)
    return (hx - hu * .16, hy + hu * .08), (hx + hu * .16, hy + hu * .08), hu  # eye positions (drawn in red later)

def flicker(t, seed=0):
    r = math.sin(t * 31 + seed) * math.sin(t * 7.3 + seed * 2)
    return 0.35 if (r > 0.82 or (int(t * 10) % 37 == 0)) else 1.0

def finish(rgb, t, seed=0):
    """grain + vignette + ink-bleed edges."""
    h, w = rgb.shape[:2]
    rng = np.random.default_rng(int(t * 24) + seed)
    g = rng.normal(0, 5, (h // 2, w // 2)).astype(np.float32)
    rgb = rgb + cv2.resize(g, (w, h))[..., None]
    yy, xx = np.mgrid[0:h, 0:w]
    v = (1 - 0.5 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)).clip(0.3, 1)
    rgb = rgb * v[..., None] + INK * (1 - v[..., None]) * 0.6
    return np.clip(rgb, 0, 255).astype(np.uint8)
