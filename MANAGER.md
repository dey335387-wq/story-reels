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
- 2026-11-09 manager: horror am KUAN (154 views, 20% watched) + pm 41VI COPY (177 views, 33%) posted; puzzle DAY 3 dilemma 1,534 views, 9 comments (best Socho so far); news osLZnaS9boA scheduled 18:30; case study 9 Nov MISSED (outage day, trigger created after 07:45) - not posted late at night; next runs 10 Nov ok; vidIQ 18.
- 2026-11-10 manager: am RAJ TALKIES (127 views) + pm BED NO. 11 (145, same "extra count" twist owner disliked — posted before the 20:07 rule) ; puzzle DAY 4 gas leak 158 views; case study 8BGd5MJEKuM + news 5e8eGeV5ZXg scheduled; owner rule 20:07/20:08: no horror, love OK, hook+suspense, story trigger prompt updated; next runs 11 Nov ok; vidIQ 18.
- 2026-11-11 manager: new-rule stories live: am REFUND (scam/detective, 134 views, 36% watched) + pm MEERA (love + twist, 135, 37%); puzzle DAY 5 exam dilemma 1,416 views, 10 comments, 3 shares (2nd best); case study dWCXeisG2go + news 3rah6gWtRAo scheduled; tomorrow runs ok; vidIQ 18.
- 2026-11-12 manager: PAISA GYAAN #1 posted 09:17 (IG DfoH1iWiqRz); case study UPI 1DZAtVDygLc; 12:30 puzzle MISSED (trigger delivered 5h45m late at 17:01, news took priority; not posted late at night); news b3BUddWPvds 18:30; evening puzzle DAY 6 lift posted 19:25 (IG DfpNgbcjI-q). Tomorrow runs all present. vidIQ insights/balance returned Bad Gateway at 22:16 — recheck tomorrow.
- 2026-11-13 manager: all posts out (money #2 125 views/20% watched; case study rupee yjVrwLw0om8 — trial week done, asked owner; puzzle DAY 7 wallet 127; news VpLaPHp7imY; puzzle DAY 8 railway posted late 21:19 after trigger delay + connector 502, 146 views). Trend: since 2 puzzles/day + money, each new Reel ~125-170 views, watch 13-20%, skip 43-63% (vs exam dilemma 1,631 / 33%). Money hooks need to be stronger in first 2 s. Token reminder sent. vidIQ 18 (renews 14 Nov).
