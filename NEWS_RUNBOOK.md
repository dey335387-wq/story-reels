# Daily News Short runbook (YouTube Shorts, owner's separate news channel)

Owner wants 1 Hinglish daily-news Short per day on their new YouTube channel (Metricool brand 7813457,
youtubeData UCwHbpK7mj-_e857StojX76w), published at 18:30 IST, style like Indian explainer creators
(e.g. Neon Man): one big story explained simply. Shorts only (vertical, 60-90 s). 0 vidIQ credits.

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

## Steps
1. Lock: locks/news-YYYY-MM-DD (same rules as RUNBOOK.md 0b).
2. Research (~10 searches): pick today's single most interesting India/world/tech/science story for a
   young Indian audience. Write facts + source URLs into news/YYYY-MM-DD.md.
3. Script: 8-11 Hindi (Devanagari) lines, 150-190 words total, structure: hook (shocking number/
   question) → kya hua → kyun important → aap par asar → aage kya → CTA "aisi khabron ke liye follow".
   inbox/n<YYYYMMDD>.gtts: line1 `Charon`, line2 style prompt "energetic Indian news explainer, fast,
   clear, confident; follow [tags], don't read them", then [tagged] lines. Same time push
   inbox/n<YYYYMMDD>.img with 5-7 "name|query" lines (places/objects/maps). git push, wait, git pull.
4. Captions: write story.json (see tools/render_news.py docstring): caps = Roman Hinglish phrases in
   spoken order, each with img, hot words, optional stat/kicker. Make tools/align.py read these caps
   (temporarily edit its import or pass list) → /tmp/n.wav + /tmp/n.srt. Count must match.
5. Render: python3 tools/render_news.py story.json /tmp/n.wav /tmp/n.srt /tmp/nv.mp4 --frames ... → look
   → full render → music: BOOM= python3 tools/bgm.py ... is horror-ish; for news use
   NEWS=1 (lighter: set env BGMSTYLE=news if supported) or mix voice only + subtle drone at low volume.
6. Host: out/n<YYYYMMDD>.mp4 → push → vidiq_video_upload(raw URL) → videoUrl.
7. Publish: Metricool createScheduledPost blogId 7813457 at 18:30 IST today, providers [{"network":"youtube"}],
   youtubeData {"title": "<=90 chars Hinglish title + #shorts", "type":"short", "privacy":"public",
   "madeForKids": false, "category":"NEWS_POLITICS" (or SCIENCE_TECHNOLOGY), "tags":[...]},
   text = description: 2-line summary + "Sources:" URLs + photo credits from credits.txt + #shorts.
8. After 18:30 confirm PUBLISHED via getScheduledPosts; record in news/STATE.md (date, title, YouTube URL).
   Remove the mp4 from out/, push. Send owner the link in Hinglish.
