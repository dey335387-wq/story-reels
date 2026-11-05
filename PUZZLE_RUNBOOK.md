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

## Visuals
Same procedural ink-wash animation kit (tools/inkanim.py, see tools/sample_inkanim.py) but BRIGHTER,
non-scary: warm paper, ink drawings of rooms/objects/clocks/people (from behind or side, no faces), red
accent for clues, a "?" ink splash. HUD tag "DIMAAG LAGAO". Countdown numbers big in the centre.
Write tools/anim_puz_<date>.py per episode. Music: tools/bgm.py is horror-ish — for puzzles use a light
ticking bed instead (ffmpeg sine ticks / soft pad), ducked under voice, -14 LUFS.

## Steps
Lock locks/puz-YYYY-MM-DD → Gemini Charon voice (style prompt: "curious, energetic Indian quiz host,
fast, playful suspense") via inbox/*.gtts → tools/align.py → render → frames check → music → push
out/*.mp4 → vidiq_video_upload (raw GitHub URL) → vidiq_instagram_publish_reel (29346910844996715,
caption ends with "Answer comment karo 👇 #dimaaglagao #riddle #paheli #brainteaser #hindi") → Metricool
Facebook REEL (blogId 7813457, +5 min) → remove mp4 → record in puzzles/STATE.md (date, puzzle, answer,
links) → push → tell owner links in Hinglish.
