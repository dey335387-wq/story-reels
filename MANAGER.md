# Project manager checklist (runs daily 22:15 IST + whenever owner asks)

Goal: owner never has to remind anyone. 2 Reels/day (~9:15 AM, ~7:25 PM IST) on Instagram + Facebook,
Also daily 12:30 PM "Dimaag Lagao" puzzle Reel on IG+FB (PUZZLE_RUNBOOK.md, puzzles/STATE.md) — verify it too.
STANDALONE horror stories — one complete story per Reel, NO series/parts (owner rule 2026-11-06), Gemini voice, bgm.py music, 0 vidIQ credits.

1. git pull. For today's slots (am, pm): STATE.md must have an Instagram permalink + Facebook status.
   - Missing slot → do that Reel now per RUNBOOK.md (respect locks/), then note "late post" in STATE.md.
   - Facebook: Metricool getScheduledPosts (blogId 7813457, today) → any FAILED/ERROR → re-post once.
2. Schedules (list_triggers, enabled one-shots in this session): tomorrow must have
   - 08:50 IST production run, 09:35 IST watchdog, and the run chain must reach 18:50 + 19:35.
   - Missing → create with send_later using the production prompt in the most recent run trigger
     (or RUNBOOK.md), and the watchdog prompt.
   - Next day's 22:15 manager review must exist; schedule it last.
3. Quality: each Reel is a complete standalone story (no part-N / to be continued), logged in STATE.md, each part 25-35 s, hook in 2 s,
   cliffhanger, music present (check last video has 2 audio sources mixed, not just voice).
   Pull Instagram insights for recent Reels (vidiq_instagram_owner_insights, 0 credits) and note what's working.
4. Budget: vidiq_balance must not drop (all steps are 0-credit). Gemini quota errors → fallback voice.
5. Send the owner one short Hinglish daily report: today's 2 links (IG+FB), views if available,
   any problem fixed, tomorrow's plan.

## Case study trial (2026-11-07 … 2026-11-13)
- Check today's 10:00 case-study Short is PUBLISHED (news/CASE_STATE.md + Metricool); next day's 07:45 run exists
  (until 13 Nov). On 13 Nov report the week's results and ask the owner whether to continue.
