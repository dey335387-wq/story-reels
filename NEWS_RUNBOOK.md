# Daily News Short runbook (YouTube Shorts, owner's separate news channel)
On-screen brand: "60 SEC KHABAR" (owner said choose any name). Put it in story.json "channel".

Owner wants 1 Hinglish daily-news Short per day on their new YouTube channel (Metricool brand 7813457,
youtubeData UCwHbpK7mj-_e857StojX76w), published at 18:30 IST, style like Indian explainer creators
(e.g. Neon Man). Shorts only (vertical, 75-90 s). From 2026-11-06: 5-6 stories per Short (see FORMAT). 0 vidIQ credits.

## Rules (non-negotiable)
- Facts only from WebSearch/WebFetch done in this run; every key fact confirmed by 2+ reliable sources
  (PIB/official sites, The Hindu, Indian Express, HT, TOI, NDTV, Reuters, BBC, AP...). No unconfirmed
  breaking news, no rumours, no medical/financial advice. Politics: neutral facts only, both sides if
  contested, no opinion. Note dates precisely ("aaj", "kal", exact date).
- Photos: ONLY free-license (Wikimedia Commons via inbox/<id>.img → media/img/<id>/ + credits.txt).
  NEVER photos of real identifiable public figures (politicians, celebs, players, CEOs) — show the place,
  building, object, map instead and put the name in text. No news-agency/TV images. Look at every
  downloaded photo (Read) before using; drop any that shows a public figure or is off-topic/low quality.
- Every Short different: vary story type, hook, colours of kicker, photo order. No copy-paste scripts.

## FORMAT from 2026-11-06 (owner request): "din ki 5-6 sabse zaroori khabrein" in ONE Short
- Every Short = a daily bulletin of the 5-6 most important stories of the day (mix: India, world,
  sports, tech/science, business/utility news that affects people; no rumours). NOT one big story.
- Length 75-90 s. Hook (≈4 s): "Aaj ki 6 sabse badi khabrein, 60 second mein!" + the most shocking
  headline as a tease. Then each story ≈ 11-13 s = 2 short lines (kya hua + kyun matter karta hai /
  number). Outro (≈4 s): "Kal phir milte hain, follow karo 60 SEC KHABAR."
- Each story: its own photo (free-license, no public figures), kicker "KHABAR 1/6", "2/6"... (or
  topic label like "SPORTS", "DUNIYA", "TECH"), hot words, a stat when there is a number.
- Research: ~15 searches; every story confirmed by 2+ reliable sources; write all facts + URLs into
  news/YYYY-MM-DD.md. Description: one line per story + all sources + photo credits.
- Script ≈ 300-340 Hindi words (Charon after align.py speaks ~7 words/s: 2026-11-06 had ~150 words = 41 s, too short); 6 stories, 3 lines each; .img file with one or two queries per story (6-10 lines).
- Title like "Aaj ki 6 badi khabrein: <top headline> | 6 Nov #shorts".
- Render is ~0.55 s/frame → 90 s ≈ 25 min: start research at 17:30 sharp, voice+images by ~17:50,
  render by ~18:20 at the latest (Metricool publishes 18:30; if late, schedule a few minutes later
  rather than skipping).

## STYLE from 2026-11-06 (owner request): 3D host character + FAST motion graphics
Owner: news Shorts need their OWN consistent character (different from Chotu), fast-moving motion
graphics, and the character must never just stand — it flies up/down/forward/back.
- Scene: tools/v3d/news.html (Three.js, rendered by tools/v3d/render.js with PAGE=news.html NF=<frames>).
  Data: python3 tools/v3d/make_news_ep.py story.json <srt> <voice.wav> → tools/v3d/news_ep.js (prints frames).
  Needs tools/v3d/three (see tools/v3d/README.md; symlink /home/claude/v3d/three if present) and the
  symlink tools/v3d/media -> ../../media (both gitignored).
- CHARACTER BIBLE "KHABRI" (never change; geometry is in news.html — don't edit the bot block):
  original robot reporter; round glossy WHITE body (#f4f6fb) with RED belt ring (#e63946) and a red
  round "60" chest badge; rounded white box head with a dark screen face showing CYAN (#3ef0ff) rounded
  eyes + mouth bar (blinks, talks, "wow" eyes on stat lines, happy eyes at the end); RED headphones with
  band; short antenna with glowing red ball; white capsule arms with red hands; right hand holds a mic
  with a red "60 SEC" flag cube; hovers on a CYAN jet flame (no legs). Scale 0.8.
- Motion rules: Khabri swoops to a new spot on EVERY caption (POS cycle: right-front, left-back,
  right-close, centre-high-back...), arcs up while moving, tilts with speed, bobs, intro fly-in with a
  spin; photos whoosh in from the right on 3D cards and out to the left; Ken Burns inside the card;
  camera punch-in on each caption, extra zoom on stat lines; neon grid floor + speed streaks always
  moving; captions pop word-by-word; kicker slides in; ticker scrolls. Keep it FAST.
- Render ≈ 0.55 s/frame (60 s Short ≈ 17 min) — start the render early, look at 5 test frames first.
- Encode: ffmpeg -framerate 30 -i fr/f%04d.jpg -i music.m4a -vf scale=1080:1920:flags=lanczos
  -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -c:a copy -shortest out/n<date>.mp4
- Music: python3 tools/v3d/news_music.py <voice.wav> <T> music.m4a <caption start times comma>
  (upbeat synth bed + whooshes on cuts, ducked under voice).
- Photo rules unchanged (free-license only, no public figures — Khabri is the "face" of the channel now).

## Steps
1. Lock: locks/news-YYYY-MM-DD (same rules as RUNBOOK.md 0b).
2. Research (~10 searches): pick today's 5-6 most important India/world/sports/tech stories (see FORMAT) for a
   young Indian audience. Write facts + source URLs into news/YYYY-MM-DD.md.
3. Script: 8-11 Hindi (Devanagari) lines, 150-190 words total, structure: hook (shocking number/
   question) → kya hua → kyun important → aap par asar → aage kya → CTA "aisi khabron ke liye follow".
   inbox/n<YYYYMMDD>.gtts: line1 `Charon`, line2 style prompt "energetic Indian news explainer, fast,
   clear, confident; follow [tags], don't read them", then [tagged] lines. Same time push
   inbox/n<YYYYMMDD>.img with 5-7 "name|query" lines (places/objects/maps). git push, wait, git pull.
4. Captions: write story.json (see tools/render_news.py docstring): caps = Roman Hinglish phrases in
   spoken order, each with img, hot words, optional stat/kicker. Make tools/align.py read these caps
   (temporarily edit its import or pass list) → /tmp/n.wav + /tmp/n.srt. Count must match.
5. Render (OLD 2D style, only as fallback if 3D fails): python3 tools/render_news.py story.json /tmp/n.wav /tmp/n.srt /tmp/nv.mp4 --frames ... → look
   → full render → music: BOOM= python3 tools/bgm.py ... is horror-ish; for news use
   NEWS=1 (lighter: set env BGMSTYLE=news if supported) or mix voice only + subtle drone at low volume.
6. Host: out/n<YYYYMMDD>.mp4 → push → vidiq_video_upload(raw URL) → videoUrl.
7. Publish: Metricool createScheduledPost blogId 7813457 at 18:30 IST today, providers [{"network":"youtube"}],
   youtubeData {"title": "<=90 chars Hinglish title + #shorts", "type":"short", "privacy":"public",
   "madeForKids": false, "category":"NEWS_POLITICS" (or SCIENCE_TECHNOLOGY), "tags":[...]},
   text = description: 2-line summary + "Sources:" URLs + photo credits from credits.txt + #shorts.
8. After 18:30 confirm PUBLISHED via getScheduledPosts; record in news/STATE.md (date, title, YouTube URL).
   Remove the mp4 from out/, push. Send owner the link in Hinglish.
