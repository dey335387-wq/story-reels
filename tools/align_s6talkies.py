"""Trim long dead air and make caption timings for a voice file without subtitles.
python3 align.py in.mp3 out.wav out.srt  (caption texts = CAPS from render_p2.py)"""
import sys, subprocess, numpy as np, re
sys.path.insert(0, "/home/claude/story-reels/tools"); from anim_s6talkies import CAPS
src, wav, srt = sys.argv[1:4]
SR = 24000
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                                 capture_output=True).stdout, np.int16).astype(np.float32)
win = SR // 50
rms = np.array([np.sqrt((a[i:i + win] ** 2).mean()) for i in range(0, len(a), win)])
db = 20 * np.log10(rms + 1); quiet = db < 40
# shorten quiet runs longer than 0.8s to 0.6s
keep = np.ones(len(rms), bool); i = 0
while i < len(rms):
    if quiet[i]:
        j = i
        while j < len(rms) and quiet[j]: j += 1
        if (j - i) > 40: keep[i + 15:j - 15] = False
        i = j
    else: i += 1
out = np.concatenate([a[k * win:(k + 1) * win] for k in range(len(rms)) if keep[k]])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", wav],
               input=out.astype(np.int16).tobytes(), check=True)
q = quiet[keep]; T = len(q) / 50
# speech chunks separated by >=0.18s quiet
chunks, i = [], 0
while i < len(q):
    if not q[i]:
        j = i
        while j < len(q):
            if q[j]:
                k = j
                while k < len(q) and q[k]: k += 1
                if k - j >= 9 or k == len(q): break
                j = k
            else: j += 1
        chunks.append((i / 50, j / 50)); i = j
    else: i += 1
w = np.array([len(re.sub(r"[^A-Z0-9]", "", c)) + 3 for c in CAPS], float)
sp0, sp1 = chunks[0][0], chunks[-1][1]
starts = sp0 + (sp1 - sp0) * np.concatenate([[0], np.cumsum(w)[:-1]]) / w.sum()
cs = np.array([c[0] for c in chunks])
for n in range(len(starts)):
    k = np.argmin(abs(cs - starts[n]))
    if abs(cs[k] - starts[n]) < 0.7: starts[n] = cs[k]
for n in range(1, len(starts)):
    starts[n] = max(starts[n], starts[n - 1] + 0.55)
ends = list(starts[1:]) + [sp1]
f = lambda t: "%02d:%02d:%02d,%03d" % (t // 3600, t % 3600 // 60, t % 60, (t % 1) * 1000)
open(srt, "w").write("".join(f"{n+1}\n{f(s)} --> {f(e)}\n{CAPS[n]}\n\n" for n, (s, e) in enumerate(zip(starts, ends))))
print("dur %.2f chunks %d" % (T, len(chunks)))
