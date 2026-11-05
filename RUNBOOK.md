# Daily Reel runbook (Instagram @story_xy_01)

Owner wants 2 original Hinglish horror/suspense story Reels per day, posted automatically
(no review) around 9:15 AM and 7:25 PM IST. Everything must cost 0 vidIQ credits.

## 0. Setup
- Repo: dey335387-wq/story-reels (public). Clone, read STATE.md (story so far + what's next).
- Instagram account: platformAccountId 29346910844996715 (story_xy_01) via vidIQ connector.

## 0b. Lock (prevents double posting — two schedulers may fire at once)
- Slot id = YYYY-MM-DD-am or -pm (IST). git pull; if locks/<slot> exists, STOP (another run owns it).
- Else create locks/<slot>, commit, push. If the push is rejected (someone else pushed first),
  git pull and re-check: if locks/<slot> now exists from the other run, STOP.

## 1. Pick the next episode
- Continue the current series in STATE.md. Owner did NOT like "Camera 4" much: it is closed after
  Part 3; do not continue it. After a series ends, start a NEW original
  series (3-5 parts), never reuse plots from other creators.
- Each part: 25-35 sec, hook in first 2 sec, cliffhanger ending (last part: final twist).
- Write ~8-10 Hindi (Devanagari) narration lines, each with an [emotion] tag.

## 2. Voice (free, Google Gemini via GitHub Actions)
- Create inbox/<id>.gtts : line1 `Charon`, line2 style prompt (fast, tense horror narrator,
  follow bracketed tags but don't read them, last line terrified whisper), then tagged lines.
- Commit + push. The `media` workflow writes media/<id>.mp3 in ~40 s (git pull to get it).
  If it fails, check `gh run list`/`gh run view --log-failed`. Fallback: inbox/<id>.tts
  (line1 hi-IN-MadhurNeural, line2 -5%, then plain text).

## 3. Video (local, free) — CURRENT STYLE from 2026-11-05 evening (owner approved the 15 s sample)
- Owner said: no stock footage/photos — make the animation ourselves. APPROVED look = tools/sample_inkanim.py:
  procedural INK-WASH animation drawn in code with tools/inkanim.py (paper, tapered brush strokes, washes,
  realistic-proportion 8-head figures via person_back()/ghost_front(), flicker, grain, vignette, red accent).
- For each episode write tools/anim_<id>.py based on sample_inkanim.py: 4-6 animated scenes matching the
  script beats (new backgrounds per setting: corridor, lift panel, stairwell, room, train...), camera
  push-ins, moving hair/dupatta, flicker; captions = Roman Hinglish phrases timed from tools/align.py SRT
  (wrap ~18 chars, hot words red), end card "TO BE CONTINUED... / PART N ..." (finale: "THE END...?").
- Faces: keep people seen from behind / in shadow / hair over face (code-drawn faces look bad).
- Speed: ~15 s render per 1 s video; render frames first, look, then full render.
- Music: tools/bgm.py as before.

## 3-prev. (retired 2026-11-05) photo ink-wash via render_ink.py — do NOT use (owner rejected stock photos)

- Owner said the old halftone/stick-figure look is "ajeeb, bas dots dikhte hain". From now on ALL horror
  Reels use INK-WASH style with realistic-looking people: free-license real photos (inbox/<id>.img →
  Wikimedia; Pexels later if a PEXELS_API_KEY secret exists) turned into ink-wash paintings by
  tools/inkwash.py, rendered with tools/render_ink.py (story.json like render_news: series/part/next,
  caps with img/hot/stat/kicker/focus 0-1 for vertical crop). Pick photos of places/objects/anonymous
  people (never public figures); look at every photo + rendered frames before the full render.
- The old tools/render_*.py drawing renderers are retired (don't use halftone again).

## 3-old. Video (local, free) — retired
- Copy tools/render_p2.py → render_<id>.py; rewrite CAPS (Roman Hinglish caption per spoken
  phrase), HOT words, SCENE_OF, STAMP and scene_img() drawings for this episode's beats.
  Keep the CCTV dark-comic look (CAMERA 4 tag, red/white captions, halftone, glitch cuts,
  TO BE CONTINUED end card). New series: change the tag/title text to the series name.
- python3 tools/align.py media/<id>.mp3 /tmp/<id>.wav /tmp/<id>.srt  (needs CAPS importable:
  adjust the import line to your render file), then
  TEMPO=1.0 python3 render_<id>.py /tmp/<id>.wav /tmp/<id>.srt /tmp/<id>.mp4 --frames t1,t2,...
  Look at frames, fix, then full render (keep file < 95 MB).
- Background music (REQUIRED, owner asked): python3 tools/bgm.py /tmp/<id>.wav /tmp/<id>.srt <video_sec> /tmp/<id>.m4a
  (original synthesized suspense score: drone, heartbeat, booms on cuts, riser, ducked under voice, -14 LUFS),
  then ffmpeg -i /tmp/<id>.mp4 -i /tmp/<id>.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest out/<id>.mp4

## 4. Host + publish
- Copy to out/<id>.mp4, commit, push. vidiq_video_upload(url=
  https://raw.githubusercontent.com/dey335387-wq/story-reels/main/out/<id>.mp4)
- vidiq_instagram_publish_reel(platformAccountId=29346910844996715, videoUrl=<returned>,
  caption="<Series> 🌑 part-N | <hook line> #horrorstory #hindistory #scarystories #explore #reelsgrowth"),
  continue with containerId until PUBLISHED. Never publish the same episode twice:
  check STATE.md first; if a step fails, stop and report, don't retry blindly.
- Facebook (same video): right after the Instagram Reel is PUBLISHED, call Metricool
  createScheduledPost with blogId 7813457, date = now + 5 min (ISO, +05:30), info JSON:
  {"autoPublish":true,"draft":false,"descendants":[],"firstCommentText":"","hasNotReadNotes":false,
   "shortener":false,"smartLinkData":{"ids":[]},"mediaAltText":[],"media":[<vidIQ videoUrl>],
   "providers":[{"network":"facebook"}],"publicationDate":{"dateTime":"<same time>","timezone":"Asia/Calcutta"},
   "text":"<caption>","facebookData":{"type":"REEL","title":"<Series> part-N"}}
  If it errors, report it; the Instagram post still counts.
- git rm out/<id>.mp4; update STATE.md (episode summary, permalink, date); commit + push.
- Report the permalink to the owner.
