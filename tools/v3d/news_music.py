"""Upbeat news bed (synth, royalty-free) + whooshes on caption changes, ducked under voice.
python3 news_music.py voice.wav T out.m4a [cap_start_times_comma]"""
import sys, numpy as np, subprocess
SR = 44100; vf, T, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
cuts = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
n = int(SR * T); t = np.arange(n) / SR
v = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", vf, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
voice = np.zeros(n, np.float32); voice[:min(n, len(v))] = v[:n]
m = np.zeros(n, np.float32); bpm = 124; beat = 60 / bpm
for k in np.arange(0, T, beat):                       # kick
    a = int(k * SR); tt = np.arange(min(int(.2 * SR), n - a)) / SR
    m[a:a + len(tt)] += .5 * np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12)
rng = np.random.default_rng(3)
for k in np.arange(beat / 2, T, beat):               # hat
    a = int(k * SR); L = min(int(.05 * SR), n - a); m[a:a + L] += .06 * rng.normal(0, 1, L) * np.exp(-np.arange(L) / SR * 80)
prog = [110, 87.3, 130.8, 98]                         # bass Am F C G
for i, k in enumerate(np.arange(0, T, beat / 2)):
    f = prog[int(k / (beat * 4)) % 4]; a = int(k * SR); tt = np.arange(min(int(beat / 2 * SR), n - a)) / SR
    m[a:a + len(tt)] += .09 * np.sign(np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 9)
for c in cuts:                                         # whoosh
    a = int(max(0, c - .25) * SR); L = min(int(.45 * SR), n - a); tt = np.arange(L) / SR
    nz = rng.normal(0, 1, L); nz = np.convolve(nz, np.ones(6) / 6, "same")
    m[a:a + L] += .18 * nz * np.sin(np.pi * tt / .45) ** 2
env = np.convolve(np.abs(voice), np.ones(2205) / 2205, "same"); duck = 1 - .7 * np.clip(env * 12, 0, 1)
mix = voice + .35 * m * duck; mix *= np.minimum(1, (T - t) / 1.0); mix /= np.abs(mix).max() / .9
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "loudnorm=I=-14:TP=-1.5",
                "-ar", "44100", "-c:a", "aac", "-b:a", "160k", out], input=mix.astype(np.float32).tobytes(), check=True)
print("ok")
