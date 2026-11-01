# Story state

## Camera 4
- Part 1: posted 2026-10-31 ("A midnight notification 🌑 part-1"). 3:12 AM notification "Camera 4, motion detected"; no camera installed; live feed shows own room; man comes out of almirah, leans over sleeper; timestamp 3:02 vs clock 3:12 → it happened 10 min ago.
- Part 2: made 2026-11-02, vidIQ uploadId 0cf9636b-c013-4640-b834-9da14c07bdaf, post 09:15 IST 2026-11-02. Playback: 3:05 back to almirah, 3:08 stares at camera, 3:10 finger on lips "shhh", 3:11 crawls under the bed; now 3:12; from under the bed someone says the narrator's name. Ends "TO BE CONTINUED... PART 3 JALDI".
- Next: Part 3.

## Pipeline
- Voice: put `inbox/<name>.tts` (line1 voice e.g. hi-IN-MadhurNeural, line2 rate e.g. -8%, then Hindi text) → GitHub Action writes media/<name>.mp3 + .srt.
- Render: tools/render_p2.py style (CCTV dark comic, 1080x1920, captions in Roman Hinglish).
- Host: push out/<file>.mp4 → vidiq_video_upload(url=raw.githubusercontent...) → delete file from repo.
- Publish: vidiq_instagram_publish_reel, account story_xy_01 (platformAccountId 29346910844996715).
