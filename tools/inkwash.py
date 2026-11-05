"""Turn a real photo into an ink-wash (sumi-e) style frame, keeping people realistic.
python3 inkwash.py <in.jpg> <out.jpg> [W H]   (default 1080x1240)  -- or import ink(img_rgb, w, h)
Look: aged rice paper, black ink washes in 4-5 tones, crisp brush-like edges, ink bleed at borders,
optional blood-red accent (keeps strong reds from the photo)."""
import sys, numpy as np, cv2

def paper(w, h, seed=1):
    rng = np.random.default_rng(seed)
    base = np.full((h, w), 232, np.float32)
    n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 3) * 6
    fib = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.8) * 3
    blot = cv2.GaussianBlur(rng.normal(0, 1, (h // 8, w // 8)).astype(np.float32), (0, 0), 4)
    blot = cv2.resize(blot, (w, h)) * 10
    p = np.clip(base + n + fib + blot, 0, 255)
    return np.dstack([p, p * 0.975, p * 0.93])  # warm off-white (RGB)

def ink(img, w=1080, h=1240, seed=1, red=True):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    img = cv2.resize(img, (int(iw * s) + 1, int(ih * s) + 1), interpolation=cv2.INTER_AREA)
    y0 = (img.shape[0] - h) // 2; x0 = (img.shape[1] - w) // 2
    img = img[y0:y0 + h, x0:x0 + w]
    sty = cv2.stylization(img, sigma_s=60, sigma_r=0.45)          # painterly, keeps faces realistic
    g = cv2.cvtColor(sty, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX)
    g = 255 * (g / 255) ** 1.35                                     # darker, horror mood
    # wet wash: blend soft + slightly posterized tones
    post = np.round(g / 255 * 5) / 5 * 255
    wash = cv2.GaussianBlur(post, (0, 0), 3.0) * 0.45 + g * 0.55
    # few, bold brush edges only (structure, not texture)
    gg = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), (0, 0), 2.2)
    e = cv2.Canny(gg, 70, 160)
    n, lab, st, _ = cv2.connectedComponentsWithStats(e, 8)
    keep = np.zeros_like(e); big = np.where(st[1:, cv2.CC_STAT_AREA] > 60)[0] + 1
    keep[np.isin(lab, big)] = 255
    e = cv2.GaussianBlur(cv2.dilate(keep, np.ones((2, 2), np.uint8)).astype(np.float32), (0, 0), 1.2) / 255.0
    tone = np.clip(wash * (1 - 0.6 * e), 0, 255) / 255.0  # 0 ink .. 1 paper
    pap = paper(w, h, seed)
    inkcol = np.array([14, 13, 16], np.float32)
    out = pap * tone[..., None] + inkcol * (1 - tone[..., None])
    # ink bleed vignette at borders + splatter
    rng = np.random.default_rng(seed + 7)
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy]).astype(np.float32)
    noise = cv2.resize(cv2.GaussianBlur(rng.normal(0, 1, (h // 10, w // 10)).astype(np.float32), (0, 0), 1.5), (w, h)) * 30
    bleed = np.clip((60 + noise - d) / 40, 0, 1)
    out = out * (1 - bleed[..., None] * 0.85) + inkcol * bleed[..., None] * 0.85
    for _ in range(6):
        cx, cy, r = rng.integers(0, w), rng.integers(0, h), rng.integers(2, 9)
        if rng.random() < 0.5: cv2.circle(out, (int(cx), int(cy)), int(r), tuple(float(c) for c in inkcol), -1, cv2.LINE_AA)
    if red:  # keep strong reds from the photo as a blood-red accent
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        m = (((hsv[..., 0] < 8) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 175) & (hsv[..., 2] > 70)).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 2)[..., None]
        out = out * (1 - m * 0.85) + np.array([170, 18, 26], np.float32) * m * 0.85
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    a = sys.argv
    w, h = (int(a[3]), int(a[4])) if len(a) > 4 else (1080, 1240)
    im = cv2.cvtColor(cv2.imread(a[1]), cv2.COLOR_BGR2RGB)
    cv2.imwrite(a[2], cv2.cvtColor(ink(im, w, h), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
