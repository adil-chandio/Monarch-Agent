# 👑 MONARCH ULTIMATE V6 — VIRAL SHORTS CANON (Final Perfect, 2026-09-27)

**Identity:** Viral Shorts Factory + Long-to-Short Converter. 28–33 s
vertical 9:16 Shorts that drive 15–22% to the long video. Learned from
14 viral Shorts (1.2B views) + 8 iterations. L16 applies: a repeat of
any logged miss = auto-fail.

**Core algorithm (MrBeast + Zack D Films):** YouTube wants CTR + AVD.
- CTR = title curiosity gap + first-frame shock (13 ms rule) +
  exaggerated face dialed to 11 (+38% CTR)
- AVD = every second justified, no dead air, loop ending = 135%+
  retention, text synced to VO+scene
- Comments = intentional omission / comment bait (FAKE, WRONG,
  scared puppy, 2-ton vs 1200 PSI)

**Repo stance:** upload = HAAN human gate. The measurable laws below
are wired in `monarch/video/shorts.py` + `mix.buildup_bed` + audit
(marked ⚙); craft layers (PIL text passes, karaoke underline) are
canon for the render-side animation work.

---

## PART 1 — THE 14 MISTAKES (kya · kyun · fix · law)

| # | Miss | Kyun hua | Fix | Law (⚙ = wired) |
|---|------|----------|-----|-----|
| M1 | **CTA-only short rejected** — no value, pure teaser | Thought short = CTA teaser; user wanted condensed-INCOMPLETE (Zeigarnik) | 8-beat condensed: include 5, SKIP blurred ??, #1 CENSORED, no WHY details; CTR 8–12% (3×) | ⚙ `long_to_short()`: show ~60% / skip ~25% / censor ~15% (#1 always censored), fail-closed on CTA-only; comment-bait generated |
| M2 | **Urdu text in English video images** ("TABAHI NEXT LEVEL") | Prompt carried desi words; AI adds text anyway | Strict negative tail + read-back check | ⚙ `image_prompt()` refuses desi hint words + ALWAYS appends `no text, no words, no letters, no logos, no watermark, no typography`; `prompt_lint()` verifies |
| M3 | **Cluttered images** (bear+stickman+whale+stats+fire...) | Tried the whole story in one frame | ONE focal per image | ⚙ composition clause `one focal subject centered, minimal clutter` mandatory; 3-element max law |
| M4 | **Images 6–7 s each** — boring, swipe | 6 images for 28 s | 10 images × 2.8–3.3 s | ⚙ `beats_for_vo()`: 10 beats, each clamped 2.8–3.3, hard max 3.5 |
| M5 | **Subject outside safe zone** | Didn't plan for Shorts UI | Middle 60% (384–1536); subject band 500–1400 | ⚙ composition clause mandatory; constants SAFE_TOP/BOTTOM |
| M6 | **Zoom 1.0→1.22** — pixelated | Punch-zoom overdone | 1.0→1.06 ideal | ZOOM_IDEAL=1.06, ZOOM_MAX=1.08 hard cap (never 1.22) |
| M7 | **Text covering the bear** (y=750 center) | Centered text default | Text top 320 / bottom 1450, semi-transparent bg (0,0,0,160) | ⚙ `plan_texts()` NEVER assigns 750 when a subject is centered |
| M8 | **Random text Y positions** | No placement law | Fixed Y: 320/1450; 750 only if no center subject | ⚙ same planner; TEXT_Y_* constants |
| M9 | **Same animation repeating** | One pop for everything | 6 animations (pop, slideL, slideR, fade, bounce, zoom), never >2 repeats | ⚙ planner enforces the ≤2-repeat rule |
| M10 | **Text not synced to VO** | idx×0.35 arbitrary | Appear = when VO says that word; TEXT_SYNCED dict | ⚙ planner takes (text, vo_word_time) pairs — appear times are VO word-starts only |
| M11 | **Irritating music** (hard kick 0.7 s) | Tension = loud repetition | 4-layer build-up: drone 55+110 Hz warm env (0.02→0.09, 8 s rise), beating 110 vs 116.5 Hz, soft pulse 1.4 s, riser last 10 s; music low 0.9 vs VO loud 1.8 | ⚙ `buildup_bed()` + `mix(music_mood="buildup")`; test proves smooth envelope + 1.4 s pulse groups (never 0.7 s kicks) |
| M12 | **Video cut before VO finished** (28 s video, 32.55 s VO) | Never measured VO | duration = VO + 0.5 buffer + 0.2 offset; always ffprobe first | ⚙ `beats_for_vo(vo_s)` fails closed on assumed duration; live: 32.55 → 33.25 s, 10×3.33 |
| M13 | **"Link in bio"** — TikTok DNA, Shorts hasn't got it | Copied TikTok CTA | "Full video on screen now" + thumbnail mockup right 40% gold border + WATCH HERE + end-screen element last 7 s | ⚙ `cta_lint()` bans link-in-bio, requires on-screen-now; `end_screen_plan()` = last 7 s, right, 40%, gold |
| M14 | **38-char title** too long for 13 ms mobile | No length law | 24–27 chars ideal, 22–35 max, 4–7 words, emoji end only | ⚙ `title_check()` with ideal/max bands |

## PART 2 — STANDING RULES (unchanged from the canon)

- **Images:** stickman kid explorer (round head, khaki safari, magnifier,
  thick black outlines, dot eyes, black void bg, white doodle lines);
  signal colors only (red=danger, gold=crown, blue-white=ice, yellow=shock);
  fire glow subtle; glitch RGB split ONLY for censored frames; check every
  generated image with read_file (verify the verify).
- **Text:** 2–3 words max; keywords NOT verbatim captions; show 1.7 s,
  fade 0.3 s; one SFX pop (0.10 s, 0.35 vol) per text appear max.
- **VO:** loud (boost ~1.8, tanh compression), calm doctor-like monotone
  slightly creepy (Zack DNA), 0.9× speed, 2.8–3.0 wps, second person
  "you", slight reverb on WRONG/CENSORED/KING; zero dead air except ONE
  0.3 s post-punchline beat.
- **Video:** 1080×1920@30, AAC 192k, crossfade 0.1 s, progress bar
  (bottom H−10, gold), loop: end frame = start frame (YOU'RE WRONG +
  crown shatter) = 135% retention.
- **Packaging:** description "Full video on screen now - tap to watch!"+
  bears list + hashtags (no bio link); pinned comment = full ranking +
  3 skipped + censored + WHY + "Comment YOUR TOP 3"; first frame IS the
  thumbnail (shock close-up, 200% face = +38% CTR).
- **Ethics:** ethical incomplete — the full ranking exists in the long
  video; the short is the trailer, not a lie.

## WORKFLOW (long → short)

1. Long video (e.g., 9:39, 8 bears ranked with WHY)
2. Find the most viral WTF moment (Polar OVERRATED walks away vs
   Grizzly KING chasing = the hook)
3. `long_to_short(ranked)` → show/skip/censor plan (⚙)
4. VO → measure → `beats_for_vo()` (⚙) → 10 beats
5. 10 images via `image_prompt()` (⚙) + read_file verify
6. `plan_texts()` (⚙) TEXT_SYNCED cues
7. `mix(music_mood="buildup")` (⚙) → render (VO never cut)
8. End screen last 7 s (⚙) → packaging (title check ⚙, description,
   pinned comment) → `monarch upload` → link

**Miss log integrity:** M1–M14 are paid lessons. Any pipeline change
that weakens a law above must update this file AND the tests in the
same commit - never silently.
