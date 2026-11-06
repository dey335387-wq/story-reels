"""story.json + voice srt -> news_ep.js for news.html (3D KHABRI style).
python3 make_news_ep.py story.json subs.srt voice.wav  [writes tools/v3d/news_ep.js]
story.json caps: {"t": "Roman Hinglish caption", "img": "media/img/<id>/x_0.jpg", "hot": ["WORD"], "stat": "opt", "kicker": "opt"}
"""
import sys, json, re, subprocess, os, html
st = json.load(open(sys.argv[1])); s = open(sys.argv[2], encoding="utf-8").read()
f = lambda x: (lambda h, m, q: int(h) * 3600 + int(m) * 60 + float(q.replace(",", ".")))(*x.split(":"))
tm = [(f(a), f(b)) for a, b in re.findall(r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)", s)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", sys.argv[3]], capture_output=True, text=True).stdout)
assert len(tm) == len(st["caps"]), (len(tm), len(st["caps"]))
T = round(dur + 1.2, 2); caps = []
for i, (c, (a, b)) in enumerate(zip(st["caps"], tm)):
    words = []
    hot = [h.upper() for h in c.get("hot", [])]
    for w in html.escape(c["t"]).split():
        words.append(f"<b>{w}</b>" if re.sub(r"[^A-Z0-9]", "", w.upper()) in [re.sub(r"[^A-Z0-9]", "", h) for h in hot] else w)
    e = tm[i + 1][0] if i + 1 < len(tm) else T
    caps.append({"s": round(0 if i == 0 else a, 2), "e": round(e, 2), "html": " ".join(words), "img": c["img"],
                 **({"stat": c["stat"]} if c.get("stat") else {}), **({"kicker": c["kicker"]} if c.get("kicker") else {})})
ep = {"T": T, "date": st["date"], "ticker": st.get("ticker", st["headline"]), "credit": "Photos: Wikimedia Commons", "caps": caps}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_ep.js"), "w").write("window.NEWS=" + json.dumps(ep, ensure_ascii=False) + ";")
print("T", T, "frames", int(T * 30))
