# Case Study documentary Shorts — 1 week trial (owner request 2026-11-06)
Channel: the news channel (60 SEC KHABAR, Metricool blogId 7813457, YouTube). One Short per day, published
10:00 AM IST, 7 days: 2026-11-07 … 2026-11-13. Then the manager reports results and asks the owner whether to continue.
0 vidIQ credits. Run starts 07:45 IST (must finish before the 08:50 horror Reel run in the same session).

## Content
- A "CASE STUDY" mini-documentary on a TRENDING topic of the last few days (business/brand move, tech launch,
  viral app, sports-business, science discovery, a big India story) — the "kaise / kyun" behind it, not a news recap.
  Find it with WebSearch (trending India, Google Trends-style coverage, business news); pick something people are
  talking about AND that has a story arc. Avoid political/communal controversies and anything about private people.
- 60-90 s, Hinglish, documentary arc: HOOK (shocking number/question, 0-4 s) → BACKGROUND (kya tha) → THE MOVE
  (kya kiya / kya hua) → WHY IT WORKED / FAILED (2-3 crisp reasons with numbers) → LESSON + open question →
  CTA "Aisi case studies ke liye follow karo".
- Every fact from 2+ reliable sources; notes + URLs in news/case-YYYY-MM-DD.md; sources + photo credits in the
  description. Script ≈ 300-340 Hindi words (Charon after align.py ≈ 7 words/s).
- Photos: free-license Wikimedia only (inbox/<id>.img), NO public-figure photos, check every photo AND the
  place/subject named in credits.txt (image search can return the wrong place). Logos only if free-licensed
  on Commons; otherwise use products/places/generic objects.

## Visual style
- Same 3D host KHABRI and tools/v3d/news.html + make_news_ep.py + news_music.py pipeline as NEWS_RUNBOOK.md
  (Character Bible there). story.json: "date" = "CASE STUDY", ticker = "CASE STUDY • <topic> • ...";
  kickers: "CASE STUDY", "BACKGROUND", "THE MOVE", "KYUN?", "LESSON"; use "stat" for big numbers.
- Render ≈ 0.55 s/frame (90 s ≈ 25 min) — start the render by ~08:15.
- Title: "<Topic>: <hook question> | Case Study #shorts"; category EDUCATION; youtubeData type "short".

## Steps
1. lock locks/cs-YYYY-MM-DD (exists → verify and stop). 2. research. 3. inbox/cs<date>.gtts + .img, push,
wait for media. 4. align (tools/align.py with a caps module), story.json, make_news_ep.py, 5 test frames, full
render, news_music.py, encode (see NEWS_RUNBOOK.md). 5. push out/cs<date>.mp4 → Metricool createScheduledPost
YouTube short at 10:00 IST (media = raw GitHub URL). 6. after Metricool copies the file: git rm the mp4,
log in news/CASE_STATE.md, push, SendUserMessage the owner (Hinglish) with topic + time; the 10:20 watchdog
confirms PUBLISHED and adds the link.
