# "DIMAAG LAGAO" — daily brain-teaser suspense Reel (Instagram + Facebook), 12:30 PM IST

Owner asked (2026-11-05): a 3rd daily Reel, NOT horror — suspense / sawal-jawab that makes viewers think.
Time chosen from Metricool best-time data (FB peak ~10-12): 12:30 PM IST daily, on IG + FB.

## Format from 2026-11-07 — "SOCHO TUM..." survival / decision scenarios (owner reference 2026-11-06: an
"Imagine you wake up..." Reel with a DAY / time / floor HUD; we take the FORMAT only — never copy that
creator's character, art, script or story)
- 2nd-person scenario: "Socho, tum raat 3:12 baje uthte ho... 9th floor... aur ..." → one strange/tense
  situation with a clear logic clue → 3 options on cards: A / B / C → "Tum kya karoge?" → 3 s countdown →
  the SMART answer + one-line reason (logic, safety knowledge, observation) → "Comment karo tumne kya chuna".
- Suspense yes, horror NO (no ghosts/gore). Answer must be logically airtight and safe advice (e.g. fire:
  touch the door first; lift stuck: press alarm, don't pry doors; lost in forest: stay put...) or a clever
  observation clue hidden in the scene (clock, floor number, shadow, footprints).
- Episodes are standalone. Each new day = new scenario + new HUD: "DAY <n>  <time>  <place>".
- Length 25-30 s max. The scenario hook + HUD must be on screen in the FIRST second; voice starts
  immediately with "Socho...". Captions big, key word yellow.
- Host stays CHOTU (see Character Bible): Chotu is the "tum" in the scenario — he wakes up / walks into the
  situation, looks around, scratches head at the options, celebrates or facepalms at the answer.

## Visuals — 3D VOXEL style with the SAME host character every episode (owner request 2026-11-06)
- Base: tools/v3d/scene.html + tools/v3d/render.js (Three.js via headless Chromium; see tools/v3d/README.md for
  getting three.js from GitHub — npm is blocked). USE tools/v3d/puz.html (data-driven) and only rewrite tools/v3d/ep.js per
  episode: C = countdown start (after voice part A), B = answer start, T = total, cards [{text,col,t,x,y}],
  caps [[start,end,html]]. Two voice files: part A (question) and part B (answer) — 5 s countdown between.
  Render: cd tools/v3d && PAGE=puz.html NF=<T*30> node render.js <framedir>  (2026-11-06 episode = example).
- CHARACTER BIBLE "CHOTU" (never change): voxel kid; head 1.5 cube, skin #f2c29a; face texture = dark square
  eyes, black ROUND GLASSES, pink cheeks, small dark-red smile; ORANGE beanie #ff7a1a with darker band #e8620e
  and small YELLOW pom cube #ffd23f on top; TEAL hoodie #1fb5a8 with white chest patch; navy trousers #2d3a8c;
  white shoes. Same proportions/geometry as in scene.html (copy the kid block verbatim). He is the quiz host:
  waves at the start, does the hand-on-chin "thinking" pose during the countdown, celebrates at the end.
- HUD overlay top-left (red dot "DAY n", big time, small place) like a survival-game timer.
- Keep the visual identity: cozy purple room / colourful voxel cubes / floating chat cards / big yellow 3D "?" /
  yellow countdown top-right / orange "DIMAAG LAGAO" tag. Rooms/props can change per puzzle (kitchen, street,
  classroom...) but Chotu stays identical.
- Render ~0.6 s per frame (30 s video ≈ 9-10 min): render 4-5 test frames first, look, then full render.
- Captions are HTML overlays inside scene (#cap), timed from tools/align.py SRT.
- Music: light ticking bed + pops (see how the sample was made: synthesized in numpy), ducked under voice.

## Steps
Lock locks/puz-YYYY-MM-DD → Gemini Charon voice (style prompt: "curious, energetic Indian quiz host,
fast, playful suspense") via inbox/*.gtts → tools/align.py → render → frames check → music → push
out/*.mp4 → vidiq_video_upload (raw GitHub URL) → vidiq_instagram_publish_reel (29346910844996715,
caption ends with "Answer comment karo 👇 #dimaaglagao #riddle #paheli #brainteaser #hindi") → Metricool
Facebook REEL (blogId 7813457, +5 min) → remove mp4 → record in puzzles/STATE.md (date, puzzle, answer,
links) → push → tell owner links in Hinglish.
