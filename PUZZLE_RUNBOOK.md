# "DIMAAG LAGAO" — daily brain-teaser suspense Reel (Instagram + Facebook), 12:30 PM IST

Owner asked (2026-11-05): a 3rd daily Reel, NOT horror — suspense / sawal-jawab that makes viewers think.
Time chosen from Metricool best-time data (FB peak ~10-12): 12:30 PM IST daily, on IG + FB.

## Format (30-40 s, vertical, Hinglish)
1. Hook (0-2 s): bold question on screen + voice, e.g. "Kamra andar se band tha... phir chor gaya kahan?"
2. Mini-mystery (8-18 s): a short original situation with 3-4 clues (detective case, logic riddle,
   impossible-looking situation, "kaun jhooth bol raha hai", math/time trick, optical/logic paradox).
3. Question + countdown: "Socho... 5 4 3 2 1" with a ticking sound (big numbers on screen).
4. Answer + why (6-10 s), with the clue highlighted that gives it away.
5. CTA: "Sahi socha tha? Comment mein batao. Roz dopahar 12:30 naya sawal."
Rules: puzzle must be logically airtight (re-check the answer step by step before rendering), clean
(no gore/horror/politics), original wording (no copy-paste from other creators); vary type every day.

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
