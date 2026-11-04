# Story state

## Camera 4
- Part 1: posted 2026-10-31 ("A midnight notification 🌑 part-1"). 3:12 AM notification "Camera 4, motion detected"; no camera installed; live feed shows own room; man comes out of almirah, leans over sleeper; timestamp 3:02 vs clock 3:12 → it happened 10 min ago.
- Part 2: made 2026-11-02, vidIQ uploadId 0a0ad415-09b7-40f6-b5b4-236f45446011 (Gemini Charon voice w/ emotion tags; old Madhur version 0cf9636b… unused), post 09:15 IST 2026-11-02. Playback: 3:05 back to almirah, 3:08 stares at camera, 3:10 finger on lips "shhh", 3:11 crawls under the bed; now 3:12; from under the bed someone says the narrator's name. Ends "TO BE CONTINUED... PART 3 JALDI".
- Part 2 PUBLISHED 2026-11-02 09:15 IST: https://www.instagram.com/reel/DfOX8aHgH31/
- Part 3 made 2026-11-02 evening (manually, scheduled run didn't fire). Name said in narrator's own voice; phone: "Camera 4 — Person detected: UNDER BED"; feed is from above → red light inside the ceiling fan; on the feed a hand comes out from under the bed while narrator's foot is still outside the sheet. Ends "PART 4 JALDI". vidIQ uploadId 67bae5db-27a9-4122-9bbb-996c342bbf6f. Facebook via Metricool post 414013159 (19:40 IST).
- CLOSED after Part 3 (owner: "ye wala itna sahi nahi hai", start a different series from 2026-11-03).

## Manager notes (2026-11-03 insights)
- Views: KC P1 165, KC P2 80, Cam4 P2 182, P3 118. Avg watched only 12-30%, skip rate ~50% → hook is the problem.
- From now: first 1.5 s must show the scariest image + a shock line (start in the middle of the action,
  recap later), keep Reels 22-30 s, captions bigger on first line, end on a sharper cliffhanger.

## Khaali Coach (current series, 4 parts) — tools/render_kc1.py
Plan: Rohan (Dadar→Thane, last local 12:40). P1 empty coach, no station comes, woman in red saree says "tumhara station toh do saal pehle nikal gaya", window shows HIS face instead of hers. P2: he runs to the door — doors won't open; old newspaper on seat: "Dadar-Thane local hadsa, 2 saal pehle" with his photo among the dead? (he thinks he's the ghost). P3: twist — phone has 47 missed calls from "Maa", time frozen 12:40; the woman is the one who died and keeps reliving it; she wants him to stay. P4: final — he pulls the chain, wakes in hospital bed (coma 2 years after the accident); nurse in red saree... last shot red saree on chair. Ending card "THE END".
- Part 1 PUBLISHED 2026-11-03 am https://www.instagram.com/reel/DfQ6RhOjOGO/ (vidIQ upload 4667950d-3c97-4983-83f0-d356ad9461de, FB Metricool 414797030 09:05).
- Part 2 PUBLISHED 2026-11-03 pm https://www.instagram.com/reel/DfR_F39DVIf/ (FB https://facebook.com/reel/1055563830873748): doors won't open, outside only darkness; old newspaper "Dadar-Thane local haadsa, 17 maut", 2 years ago; 3rd photo of the dead = Rohan; she whispers at his ear "Ab samjhe Rohan? Hum dono yahin rehte hain." vidIQ upload 21f4a70e-d215-4549-9f90-5396be8b5129; FB Metricool 415268439 (19:05). tools/render_kc2.py.
- Part 3 PUBLISHED 2026-11-04 am https://www.instagram.com/reel/DfTfHqznD0v/ (vidIQ upload 82c2fbae-1af1-4a14-9269-781438e4a582; FB Metricool 416052701 scheduled 09:01 IST, PENDING at post time). Hook: phone "Maa — 47 missed calls", clock frozen 12:40, her face reflected behind him; "agar main 2 saal pehle mar chuka hoon toh Maa call kyun kar rahi hai?"; Maa calling → crying "Rohan, aankhein khol beta!"; red saree woman behind him: "Phone rakh do, Rohan."; newspaper again: under his photo "GAMBHIR GHAYAL" — he never died!; her dark hand with red bangles grips his wrist: "Is dibbe mein... main akeli nahi rahungi." End card "PART 4: FINALE". 29.5 s. tools/render_kc3.py.
- Part 4 FINALE made 2026-11-04 pm: pulls emergency chain, lights out, she screams ROHAN; ICU monitor beep; Maa crying 'Doctor! isne aankhein khol di'; 2 saal coma since the accident; nurse with RED BANGLES whispers 'Agli baar... train mat chhodna, Rohan.' End card 'THE END...?'. vidIQ upload 60a06fae-4b6b-4ba5-8027-91bfe4715fbc; FB Metricool 416503620 (19:33). tools/render_kc4.py. SERIES CLOSED.
- (old plan) Part 4 = FINALE (2026-11-04 pm): he pulls the chain / fights to answer Maa → wakes in hospital bed (coma 2 years); nurse in red saree... last shot red saree on chair. End card "THE END". After that start a new original series (2026-11-05 am).

## NEXT: new original series from 2026-11-05 am (Khaali Coach is finished). Apply manager hook notes.

## (old) NEXT: start a brand-new original series on 2026-11-03 morning
- Must feel stronger than Camera 4: relatable Indian setting (hostel, train, village, old haveli, night shift, wrong-number call...), a clear hero with a name, a scarier and more emotional hook in the first 2 sec, real twist per part, 4-5 parts total.
- New series = new tag text in the HUD (not "CAMERA 4") and visuals redrawn for that setting; same dark comic style + Gemini voice + background music.

## Pipeline
- Voice (preferred): `inbox/<name>.gtts` = line1 Gemini voice (Charon), line2 style prompt (fast, tense, follow [tags]), then Hindi lines with [emotion] tags → media/<name>.mp3; then tools/align.py trims long silences + makes captions; render with TEMPO=1.0.
- Voice (fallback): put `inbox/<name>.tts` (line1 voice e.g. hi-IN-MadhurNeural, line2 rate e.g. -8%, then Hindi text) → GitHub Action writes media/<name>.mp3 + .srt.
- Render: tools/render_p2.py style (CCTV dark comic, 1080x1920, captions in Roman Hinglish).
- Host: push out/<file>.mp4 → vidiq_video_upload(url=raw.githubusercontent...) → delete file from repo.
- Publish: vidiq_instagram_publish_reel, account story_xy_01 (platformAccountId 29346910844996715).
