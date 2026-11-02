# Story state

## Camera 4
- Part 1: posted 2026-10-31 ("A midnight notification 🌑 part-1"). 3:12 AM notification "Camera 4, motion detected"; no camera installed; live feed shows own room; man comes out of almirah, leans over sleeper; timestamp 3:02 vs clock 3:12 → it happened 10 min ago.
- Part 2: made 2026-11-02, vidIQ uploadId 0a0ad415-09b7-40f6-b5b4-236f45446011 (Gemini Charon voice w/ emotion tags; old Madhur version 0cf9636b… unused), post 09:15 IST 2026-11-02. Playback: 3:05 back to almirah, 3:08 stares at camera, 3:10 finger on lips "shhh", 3:11 crawls under the bed; now 3:12; from under the bed someone says the narrator's name. Ends "TO BE CONTINUED... PART 3 JALDI".
- Part 2 PUBLISHED 2026-11-02 09:15 IST: https://www.instagram.com/reel/DfOX8aHgH31/
- Part 3 made 2026-11-02 evening (manually, scheduled run didn't fire). Name said in narrator's own voice; phone: "Camera 4 — Person detected: UNDER BED"; feed is from above → red light inside the ceiling fan; on the feed a hand comes out from under the bed while narrator's foot is still outside the sheet. Ends "PART 4 JALDI". vidIQ uploadId 67bae5db-27a9-4122-9bbb-996c342bbf6f. Facebook via Metricool post 414013159 (19:40 IST).
- CLOSED after Part 3 (owner: "ye wala itna sahi nahi hai", start a different series from 2026-11-03).

## NEXT: start a brand-new original series on 2026-11-03 morning
- Must feel stronger than Camera 4: relatable Indian setting (hostel, train, village, old haveli, night shift, wrong-number call...), a clear hero with a name, a scarier and more emotional hook in the first 2 sec, real twist per part, 4-5 parts total.
- New series = new tag text in the HUD (not "CAMERA 4") and visuals redrawn for that setting; same dark comic style + Gemini voice + background music.

## Pipeline
- Voice (preferred): `inbox/<name>.gtts` = line1 Gemini voice (Charon), line2 style prompt (fast, tense, follow [tags]), then Hindi lines with [emotion] tags → media/<name>.mp3; then tools/align.py trims long silences + makes captions; render with TEMPO=1.0.
- Voice (fallback): put `inbox/<name>.tts` (line1 voice e.g. hi-IN-MadhurNeural, line2 rate e.g. -8%, then Hindi text) → GitHub Action writes media/<name>.mp3 + .srt.
- Render: tools/render_p2.py style (CCTV dark comic, 1080x1920, captions in Roman Hinglish).
- Host: push out/<file>.mp4 → vidiq_video_upload(url=raw.githubusercontent...) → delete file from repo.
- Publish: vidiq_instagram_publish_reel, account story_xy_01 (platformAccountId 29346910844996715).
