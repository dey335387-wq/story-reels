# python3 make_money_ep.py story.json subs.srt voice.wav  -> writes money_ep.js next to this script
# story.json = {"brand":"PAISA GYAAN","ep":"#1","caps":[{"html":"Roz sirf <b>₹100</b>","st":{"kind":"coins","big":"₹100","sub":"ROZ KI BACHAT"}}, ...]}
# one srt cue per caption (same order); a cap with "st" starts a new 3D station at that cue's start.
import json, re, subprocess, sys, os
story, srt, wav = sys.argv[1:4]
S = json.load(open(story))
cues = []
for b in open(srt, encoding="utf-8").read().strip().split("\n\n"):
    m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)", b)
    if m:
        g = list(map(int, m.groups()))
        cues.append((g[0]*3600+g[1]*60+g[2]+g[3]/1000, g[4]*3600+g[5]*60+g[6]+g[7]/1000))
assert len(cues) == len(S["caps"]), (len(cues), len(S["caps"]))
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",wav]))
T = round(dur + 1.2, 2)
caps, st = [], []
for i, (c, (s, e)) in enumerate(zip(S["caps"], cues)):
    e2 = cues[i+1][0] if i+1 < len(cues) else T
    caps.append({"s": round(s,2), "e": round(e2,2), "html": c["html"]})
    if c.get("st"): st.append({"s": round(max(0.3, s),2), **c["st"]})
out = {"T": T, "brand": S.get("brand","PAISA GYAAN"), "ep": S.get("ep",""), "caps": caps, "st": st}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "money_ep.js"), "w").write("window.EP=" + json.dumps(out, ensure_ascii=False) + ";\n")
print("T", T, "frames", int(T*30), "stations", len(st))
