# "DIMAAG LAGAO" — daily brain-teaser suspense Reel (Instagram + Facebook), 12:30 PM IST

Owner asked (2026-11-05): a 3rd daily Reel, NOT horror — suspense / sawal-jawab that makes viewers think.
Time chosen from Metricool best-time data (FB peak ~10-12): 12:30 PM IST daily, on IG + FB.

## Format from 2026-11-07 — "SOCHO TUM..." choose-your-move scenarios (owner reference Reel, studied
2026-11-06, notes in puzzles/REFERENCE.md). Take the FORMAT only — never copy that creator's characters,
art, story or lines. Standalone episodes (no "part 2" — owner rule: no series).
STRUCTURE (45-60 s):
1. HOOK 0-5 s: "Socho, tum raat 3 baje uthte ho... aur <one concrete alarming fact with a number>."
   Short fragments: "Teeis missed calls. Sab Maa ke." Chotu wakes up on screen at frame 1.
2. SETUP 5-25 s: a person/situation pulls you in fast + ONE clear RULE card ("Rule: darwaza 24 ghante band
   rahega. Koi bhi knock kare.") — rules create stakes.
3. TWIST 25-40 s: one discovery that changes everything (date on a map, a second shadow, a message) — an
   open question ("Use pehle se pata tha.").
4. DILEMMA 40-52 s: time math on screen ("6 minute door. 8 minute bache.") → two cards
   [A] red / [B] green, "Tum kya karoge? A ya B?" 3 s countdown.
5. ENDING: EITHER (a) a moral dilemma left open → "Comment karo A ya B — kal ka episode tumhare jawab se
   alag hoga nahi, naya hoga" (no reveal), OR (b) a logic/safety scenario with one correct answer → reveal
   + one-line reason. Alternate a/b day by day. Always end with "Comment karo: A ya B?".
SCRIPT STYLE: pure 2nd person present tense ("tum dekhte ho", "tumhara phone bajta hai"), very short
sentences and fragments, numbers everywhere, 1-2 other characters with their own short lines
(make a 2nd .gtts with another Gemini voice, e.g. Kore/Puck/Fenrir, and mix it in), no horror/gore.
SCREEN: HUD top-left (red dot DAY n, big clock that ADVANCES during the video, place/floor that changes
with location) + urgency counter top-right ticking down; captions bottom, bold caps, key words yellow;
rule cards; A/B choice cards red/green. SOUND: low pulsing drone rising in tempo, UI pings, knocks,
footsteps, alarm tones (all synthesized).
- Host stays CHOTU (Character Bible) = "tum". Scenes can change (bedroom → stairs → basement…) by
  swapping room props/colours in puz.html; camera pans down between locations.

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
