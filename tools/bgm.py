"""Original synthesized suspense music (no copyright issues) + mix under a voice track.
python3 bgm.py <voice.wav> <subs.srt> <video_len_sec> <out_mixed.m4a>
Cues: scene boom on each caption start listed in BOOM env (comma idx) else every ~4 caps,
heartbeat that speeds up, drone, wind, dissonant strings, riser into the end card."""
import sys, re, os, subprocess, numpy as np

SR = 44100
voice, srt, total, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
n = int(total * SR); t = np.arange(n) / SR
rng = np.random.default_rng(3)

def times(path):
    r = []
    for a in re.findall(r"(\d+):(\d+):(\d+),(\d+) -->", open(path).read()):
        h, m, s, ms = map(int, a); r.append(h * 3600 + m * 60 + s + ms / 1000)
    return r
caps = times(srt); speech_end = caps[-1] + 2.0 if caps else total - 3
end_card = min(total - 1.5, speech_end + 0.4)

def env(x, a, d): return np.clip(x / a, 0, 1) * np.exp(-np.maximum(x - a, 0) / d)
def lp(x, k):  # cheap one-pole lowpass
    y = np.empty_like(x); acc = 0.0; a = k
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y

mus = np.zeros(n)
# drone
lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
mus += 0.22 * lfo * (np.sin(2 * np.pi * 55 * t) + 0.8 * np.sin(2 * np.pi * 58.3 * t) + 0.3 * np.sin(2 * np.pi * 110.4 * t))
# wind (filtered noise, slow swell)
noise = rng.standard_normal(n)
w = lp(noise, 0.02) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + 1))
mus += 0.5 * w / (np.abs(w).max() + 1e-9) * 0.25
# dissonant high strings, fading in mid-way
st = (np.sin(2 * np.pi * 740 * t) + np.sin(2 * np.pi * 784 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 6 * t))
mus += 0.035 * st * np.clip((t - total * 0.35) / (total * 0.3), 0, 1)
# heartbeat, speeding up toward the end of speech
beat = []; x = 1.0
while x < speech_end:
    beat.append(x); prog = x / max(speech_end, 1); x += 1.05 - 0.45 * prog
for b in beat:
    for off, amp in ((0, 1.0), (0.17, 0.6)):
        i0 = int((b + off) * SR); L = int(0.25 * SR)
        if i0 + L < n:
            tt = np.arange(L) / SR
            mus[i0:i0 + L] += 0.55 * amp * np.sin(2 * np.pi * 48 * tt) * env(tt, 0.005, 0.07)
# booms on scene cuts (every 4th caption + first)
bi = [int(v) for v in os.environ.get("BOOM", "").split(",") if v.strip()] or list(range(0, len(caps), 4))
for k in bi:
    if k < len(caps):
        i0 = int(caps[k] * SR); L = int(1.6 * SR)
        if i0 + L < n:
            tt = np.arange(L) / SR
            f = 70 * np.exp(-tt * 1.5) + 30
            mus[i0:i0 + L] += 0.7 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(tt, 0.004, 0.45)
# riser into end card, then hard stop + final hit
r0 = max(0, end_card - 3.0)
m = (t >= r0) & (t < end_card)
tr = t[m] - r0
mus[m] += 0.25 * ((tr / 3.0) ** 2) * (lp(noise[m], 0.25) + np.sin(2 * np.pi * (200 + 300 * tr) * tr))
cut = int(end_card * SR); mus[cut:] *= 0.0
L = min(int(2.2 * SR), n - cut)
if L > 0:
    tt = np.arange(L) / SR
    mus[cut:cut + L] += 0.9 * np.sin(2 * np.pi * (40 + 25 * np.exp(-tt * 3)) * tt) * env(tt, 0.003, 0.6)
mus = np.tanh(mus * 1.2)
mus /= np.abs(mus).max() + 1e-9
fade = np.clip(t / 0.8, 0, 1); mus *= fade
pcm = (mus * 0.9 * 32767).astype(np.int16).tobytes()
# mix: music ducked under voice (sidechain), music ~ -16 dB vs voice
cmd = ["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-i", voice,
       "-filter_complex",
       "[1:a]aresample=44100,apad,atrim=0:%f,asplit=2[v][sc];" % total +
       "[0:a]volume=0.32[m];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
       "[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
       "-map", "[a]", "-c:a", "aac", "-b:a", "192k", out]
subprocess.run(cmd, input=pcm, check=True)
print("ok", out)
