# Project manager checklist (runs daily 22:15 IST + whenever owner asks)

Goal: owner never has to remind anyone. 2 Reels/day (~9:15 AM, ~7:25 PM IST) on Instagram + Facebook,
new original horror series (Camera 4 closed), Gemini voice, bgm.py music, 0 vidIQ credits.

1. git pull. For today's slots (am, pm): STATE.md must have an Instagram permalink + Facebook status.
   - Missing slot → do that Reel now per RUNBOOK.md (respect locks/), then note "late post" in STATE.md.
   - Facebook: Metricool getScheduledPosts (blogId 7813457, today) → any FAILED/ERROR → re-post once.
2. Schedules (list_triggers, enabled one-shots in this session): tomorrow must have
   - 08:50 IST production run, 09:35 IST watchdog, and the run chain must reach 18:50 + 19:35.
   - Missing → create with send_later using the production prompt in the most recent run trigger
     (or RUNBOOK.md), and the watchdog prompt.
   - Next day's 22:15 manager review must exist; schedule it last.
3. Quality: series has a written plan in STATE.md (title, parts, twist), each part 25-35 s, hook in 2 s,
   cliffhanger, music present (check last video has 2 audio sources mixed, not just voice).
   Pull Instagram insights for recent Reels (vidiq_instagram_owner_insights, 0 credits) and note what's working.
4. Budget: vidiq_balance must not drop (all steps are 0-credit). Gemini quota errors → fallback voice.
5. Send the owner one short Hinglish daily report: today's 2 links (IG+FB), views if available,
   any problem fixed, tomorrow's plan.
