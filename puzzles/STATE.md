# Dimaag Lagao state

- Starts 2026-11-06 12:30 IST. Log each puzzle here (type, answer) so we never repeat.
- 2026-11-06 | FIRST 3D Chotu episode | type: "kaun jhooth bol raha hai" logic (exactly 1 truth-teller) | Raju "main chor nahi", Pinky "chor Golu hai", Golu "Pinky jhooth bol rahi" → answer RAJU (Golu/Pinky thief would give 2 truths) | 38.5 s | IG https://www.instagram.com/reel/DfY_jmmDpck/ (vidIQ upload fe5b9da3-381a-4a60-bd00-d8bfb3e1552a) | FB https://facebook.com/reel/1677294050716922 (PUBLISHED 12:23) | scene tools/v3d/puz.html + ep.js
  Next days: avoid "liar" type for a while; try time/clock trick, matchstick-free math, detective room, sequence, river-crossing style, age puzzle.

## Manager notes (2026-11-06)
- 3D Chotu ep 1: 167 views, only 19% watched, skip 62% (weak). 38 s is too long and the question came late.
- Next episodes: <= 25 s total, the puzzle itself (big text card) visible in the FIRST second, voice starts with the question
  ("Sirf 1% log solve karte hain: ..."), countdown 3 s instead of 5, answer short. Simpler, more visual puzzles.
- 2026-11-07 | FIRST "Socho tum..." scenario (DAY 2, logic/safety type) | 2:40 AM, 14th floor, smoke; fire on 12th; RULE card "dhuan upar jaata hai, neeche jhuk ke chalo"; neighbour Sharma uncle (Puck voice): "Lift chal rahi hai!"; handle is HOT | A: open door, lift down / B: keep door shut, wet towel, call 101 → answer B (hot handle = fire/hot smoke behind door; never use lifts in a fire; towel under door, call 101, signal from window) | 60.4 s, tools/v3d/puz2.html + ep.js (HUD, rule card, A/B cards, smoke, alarm light, door/handle, towel) | IG https://www.instagram.com/reel/DfbkAy3EaJR/ (12:14 IST) | FB https://facebook.com/reel/1487514286924371 (PUBLISHED 12:20)
  Next (2026-11-08, DAY 3): OPEN moral dilemma type (no single right answer), different place (not fire/building). Render took ~30 min at 1 fps — start early.

## Manager notes (2026-11-07)
- "Socho tum" fire episode: 330 views in 10 h (2x the old riddle), 21% watched, skip 47%, 1 comment. Format is better; first seconds still lose half. Next: start ON the danger (smoke + HUD + "Socho..." line under 1 s), keep 45-50 s.
- 2026-11-09 | "Socho tum" DAY 3, OPEN DILEMMA | 1:10 AM, hostel, final exam 9 AM; best friend Rohit (Puck voice) stuck on highway, battery 5%; RULE: gate locked till 6 AM, caught = warden complaint; 40 km, 3 hours | A: jump gate and go / B: stay, call 112 for him, give exam → no single right answer ("dosti vs career") | 48.5 s, puz2.html flags (noSmoke/noAlarm/noHot/noTowel/open, msg) | IG https://www.instagram.com/reel/Dfgr5EGj6NC/ (11:58 IST) | FB Metricool 421414400 (12:07)
  Next (DAY 4): logic/safety type with a clear answer, new place (not fire, not hostel).
- 2026-11-10 | "Socho tum" DAY 4, LOGIC/SAFETY | 11:40 PM, flat kitchen, strong gas smell in the dark, light switch next to hand; msg from Maa "gas band kiya tha na?"; RULE: ek chingaari = dhamaka | A: switch light on to find leak / B: no switches, regulator off, open windows, go out and call LPG 1906 → answer B (switch makes a tiny spark) | 49 s, puz2.html flags | IG https://www.instagram.com/reel/DfjRp_-E_FC/ (12:06 IST) | FB Metricool 422778815 (12:12)
  Render got stopped by the 30-min background limit at frame 924 → resumed with START=924 (render.js), use timeout 5400000 next time.
  Next (DAY 5): OPEN moral dilemma, new place (not fire, hostel, kitchen/gas).
- 2026-11-11 | "Socho tum" DAY 5, OPEN DILEMMA | exam hall, last board paper: best friend copying from a chit in front of you; RULE: copying caught = whole row cancelled (yours too); invigilator asks "kisi ko nakal karte dekha?" | A: tell truth (friend debarred, your paper safe) / B: stay silent (friend may escape, risk yours) → open ending, "best jawab PIN hoga" | 46 s | IG https://www.instagram.com/reel/Dfl5HQ1jyd_/ (12:29 IST) | FB Metricool 424072055 (12:35)
  Note: set is still Chotu's room with a night window although HUD says exam hall 10:42 AM — consider a daytime/classroom variant.
  Next (DAY 6): LOGIC/SAFETY with a clear answer, new place (not fire, hostel, kitchen/gas, exam).
- 2026-11-12 pm | DAY 6, LOGIC/SAFETY | office lift stuck between floors at 9:30 PM, gap in doors; RULE: air does not run out, danger = wrong move | A pry doors + climb out / B alarm + emergency number/112 + stay inside → B | 52.6 s | IG https://www.instagram.com/reel/DfpNgbcjI-q/ (19:25 IST) | FB Metricool 425719886 (19:30)
  12:30 run skipped on 2026-11-12: its trigger was delivered 5h45m late (17:01 IST).
  Next (DAY 7): OPEN dilemma, new place (not fire, hostel, kitchen, exam, lift).
- 2026-11-13 | DAY 7, OPEN DILEMMA | 10 PM bus stop, purse with ₹15,000 + ID (20 km away) + slip 'daughter's fees due tomorrow'; RULE: last bus home in 10 min | A return now, miss bus / B take home, return tomorrow, fee deadline may pass → open, asks for third option, best answer pinned | 49 s | IG https://www.instagram.com/reel/DfrCtQLDQrc/ (12:30 IST) | FB Metricool 426606307 (12:35)
  Next (DAY 8, 19:25): LOGIC/SAFETY, new place (not fire, hostel, kitchen, exam, lift, bus stop).
- 2026-11-13 pm | DAY 8 READY BUT NOT POSTED YET: publish trigger fired 1h12m late (20:35 IST) and vidIQ/Metricool connectors were down (502). Video out/puz20261113p.mp4 kept in repo; vidIQ uploadId 377973e4-2e11-4717-b39e-7d584d707af2. Retry at ~20:52; if it still fails, POST THIS VIDEO AS THE NEXT 12:30 SLOT instead of making a new one (then log it as DAY 8).
