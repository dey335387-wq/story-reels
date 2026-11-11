# MONEY_RUNBOOK — "PAISA GYAAN" daily Reel (Instagram + Facebook, ~9:15 AM IST)
Owner (2026-11-11 23:40): replace the suspense stories with ONE video a day on "how to make money": FULL motion-graphics,
SEAMLESS 3D camera movement, ORANGE theme. Dimaag Lagao now runs 2x/day (12:30 + 19:25). 0 vidIQ credits.

## Content rules
- One practical, HONEST idea per video, 40-60 s Hinglish: hook (a number or a surprising claim) → the idea in 3-5 steps → one example with real numbers → CTA "Follow PAISA GYAAN".
- Ideas: skills that pay (freelancing, editing, Canva, typing/data entry, tuition), side income, budgeting (50-30-20), emergency fund, compounding/SIP basics, avoiding scams (task scams, fake trading apps, OTP), negotiating salary, selling old items, etc.
- NO get-rich-quick promises, NO specific stock/crypto tips, NO "guaranteed" returns. Any return % = "anumaanit / assumption"; the page always shows "Sirf jaankari ke liye • financial advice nahi".
- Compute every number in code (e.g. SIP future value) or check it with 2 sources (year of page!). Log the topic in money/STATE.md so it never repeats.

## Pipeline
1. git pull; lock `locks/money-YYYY-MM-DD`.
2. `inbox/money<YYYYMMDD>.gtts` (line 1 `Charon`, line 2 style: "Energetic, friendly Indian money-explainer, fast and clear...", then [tag] Devanagari lines). Wait for `media/money<id>.mp3`.
3. Voice: ffmpeg atempo 1.0-1.08 (aim 40-60 s) → tools/align.py with CAPS = romanized line per caption (same pattern as news: copy scratchpad al.py, nc.py).
4. story.json `{"brand":"PAISA GYAAN","ep":"#N","caps":[{"html":"...<b>hot</b>...","st":{"kind":"coins|chart|rupee|clock|phone|warn|piggy|arrow","big":"₹100","sub":"ROZ KI BACHAT"}}]}` — one cap per srt cue; add "st" on 4-7 caps (each st = a new 3D station; camera glides there seamlessly). big ≤ 9 chars ideally.
5. `cd tools/v3d && python3 make_money_ep.py story.json v.srt v.wav` → money_ep.js; test 4-5 frames (`node render.js out t1,t2,...` with PAGE=money.html PORT=8766), then full render in background with timeout 5400000 (START env resumes).
6. Music: `python3 tools/v3d/news_music.py v.wav T m.m4a <station times>`; encode 1080x1920 crf 21.
7. Push out/money<id>.mp4 → vidiq_video_upload (raw URL) → at ~09:13 IST vidiq_instagram_publish_reel (platformAccountId 29346910844996715) until PUBLISHED → Facebook Reel via Metricool blogId 7813457 (+5 min) → git rm mp4 → log in money/STATE.md → push → Hinglish message to owner.
Caption: hook line + 3 bullet points + "Follow for daily PAISA GYAAN 💰" + "#paisa #money #earnmoney #sidehustle #financetips #hindi #reels". Never promise income.
