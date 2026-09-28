# RENDER MEMORY — The Next-Level Law (Einstein Ki Galti session, v1→v3 consolidated)

**Injected 2026-09-25 from the live 9:16 Hinglish stickman session. Every
rule below was paid for by a real miss (miss log §10). Read before ANY VO
generation, render, BGM, or QC. L16: a repeat of any logged miss =
AUTO-FAIL.** Dual-canon with PRODUCTION_LAW_V2 (G1–G16) and RENDER_LAWS.

Repo stance unchanged: upload = HAAN human gate; laws describe craft, the
in-repo pipeline enforces the MEASURABLE subset (marked ⚙ below).

---

## 1. VO & TTS LAW (the stranded-word plague)

**The miss:** TTS clips ended with a detached last word — *"aap kitne bhi
successful" → [1s dead air] → "ho"*, alone over the NEXT scene. Root cause:
(a) `—`/`...` made TTS insert long end-pauses stranding the final word;
(b) clips ended mid-sentence; (c) the same word written at the end of one
clip AND the start of the next — spoken twice.

1. **One clip = complete natural sentences. Never end mid-sentence.** Too
   long for the budget? Restructure the sentence — never split across clips.
2. **No `—` and no `...` in VO text.** Commas for soft beats. ⚙ wired:
   `vo_lint` fails the QC on stranded marks.
3. **Continuation words owned by exactly one clip.** Audit BOTH sides of
   every seam; every word spoken exactly once. ⚙ wired: seam-dup check.
4. **Regenerate, never edit audio** to fix words. Re-speak; re-verify.
5. **Hinglish + numbers:** numerals as heard words (`nau guna das`,
   `ikyanve`, `nabbe`) — never digits in VO text. ⚙ wired: digits flag.
6. **Broadcast polish chain on every VO clip:** rumble cut 55 Hz, mud dip
   −1.6 dB @ 300 Hz, presence +2.8 dB @ 3.5 kHz, air +1 dB @ 9 kHz, soft
   RMS compression (50 ms smoothing), gentle tanh saturation, ~6% room
   tone. Voice in front, radio-grade. ⚙ wired: `polish_chain()` on by
   default in `build_voiceover`.

## 2. TIMING & SYNC LAW (measure, never guess)

**The miss:** scene splits from an energy-midpoint guess — cuts fell inside
pauses; stranded words seemed to belong to the wrong scene.

1. **VAD every VO clip before rendering** (20 ms windows, threshold ≈
   30th-percentile × 0.35, merge silences < 0.12 s). Print the segment
   map. Splits at exact word-start timestamps. ⚙ wired: `vad_segments`.
2. **Default inter-clip gap = 0.30 s.** Gap > 0.55 s ONLY as a deliberate
   drama sting (once per video max). Measure the final mix; every > 0.55 s
   gap justifiable or removed. ⚙ wired: gap-budget QC check.
3. **Boundary check:** at every clip boundary, max silence in the ±1.4 s
   window < 0.65 s. Bigger = a word is stranded — fix the TEXT, not the
   timeline. ⚙ wired: boundary QC check.
4. **Two scenes per VO clip** (silence-split) keeps 2–3 s cuts with VO;
   splits land on scene 2's first caption word.
5. **Timeline math lives in ONE place** (`vo_timing.json` convention) —
   every module recomputes from it with the same lead (0.2 s). Never
   hardcode a time twice. (In-repo the manifest VO scenes + timeline.json
   are that single place.)

## 3. BGM LAW (support the story, never fight it)

**The miss:** a frame-accurate "psychological tension" bed (heartbeat
accelerating, drone, sub-drops, silence carves) — operator: *"yeh maza ka
nahi hai, irritating nahi hona chahiye."* Clever ≠ correct.

1. **Motivational storytelling = warm supportive music:** pads breathing
   under the voice (Am → F → C → G → Cadd9), sparse music-box sparkle in
   C-pentatonic (cannot clash), ONE gentle build into the CTA, hopeful
   resolve. ⚙ wired: `mix(music_mood="warm")` — genre-mapped.
2. **Banned unless the operator asks:** heartbeat, drones, sub-drops,
   riser-stacks, silence carves — anything that competes with speech.
   Gimmicks read as irritation in under 10 s. ⚙ wired: warm mood excludes
   them by construction.
3. **Ducking:** music dips to ~40% under speech (25 ms smoothing + 300 ms
   Hanning); full level only in gaps. FELT under VO, AUDIBLE in gaps.
   Verify: mid-gap RMS ≈ 15–30% of VO-window RMS.
4. **Audible from frame 1:** pad attack ≤ 0.5 s (a 1.4 s attack = silent
   hook). ⚙ wired: warm pads attack ≤ 0.4 s; audit checks intro RMS.
5. **Levels:** normalize mix to 0.72–0.82 peak (AAC headroom). Measure
   peaks **per stereo channel** — a mono downmix sums channels and reports
   false clipping (0.78 true peak read 1.099 downmixed). Encoder fear ⇒
   mux with `alimiter=limit=0.93`. ⚙ wired: audit peak check + per-channel
   honesty note (in-repo WAVs are mono).
6. **Music is synthesized (zero copyright, YouTube-safe), tunable in
   seconds** — "thoda tez/halka" = one gain constant, re-mux only, NO
   video re-render.

## 4. EDIT & ANIMATION LAW (dense from frame 1, but premium)

Operator-approved craft layer (render-side; parked pieces stay parked):

1. 2–3 s scene pulse always (18 scenes / 53 s ≈ 2.9 s avg).
2. Chalk write-on for board text (L→R reveal + dust dots at the tip).
3. **Karaoke captions, refined:** spoken word in accent colour ~0.3 s,
   settles to ink; 0.20 s ease-out fade + 10 px rise; NO scale bounce
   (TikTok-spammy). Highlighted key word gets a hand-drawn underline that
   draws on.
4. Stamp effects: tick marks land one-by-one (0.26 s apart) on proof beats.
5. Transitions: 0.12 s cross-dissolve (freeze-frame blend) — no hard cuts,
   no flash overlays; smooth 30 px enter-slide, alternating direction.
6. 3D settle: entry eases a slight perspective tilt (top edge 12 px) to
   flat over 0.28 s — depth without gimmick.
7. Eased camera: smoothstep zoom alternating, punch-in (1.0→1.22) on hits,
   vertical drift on metaphors. Never linear. No sinusoidal shake.
8. Floating chalk dust (16 particles, sine drift) + 2.8% animated grain
   (8-frame cycle) + soft vignette (≤ 78 alpha).
9. SFX map: sub-hit on open/reveals, dry pop on laughter, thud + THE one
   drama sting, ticks on proof, riser into CTA, warm chord on end card.
   Never two twists in a row.
10. Wrong-answer shake: subtle 4 px decaying oscillation — mistakes vibrate.
11. Freeze desaturation: the silence scene drains to ~38% grayscale, holds
    ~25%; colour returns on the next cut.

## 5. ASSET & ENVIRONMENT LAW (the sandbox bites)

**The misses:** image cap hit mid-batch (8 scenes missing); a relative
reference path failed silently; pip ffmpeg vanished between sessions; a
78 MB binary dropped by the snapshot cap; 150–200 MB intermediates
truncated a law file.

1. **Budget generations per turn:** ≤ 10 images. Style anchor +
   highest-emotion scenes FIRST so a cap-hit never blocks the story; VO
   (speech) does NOT count against the image cap — run parallel.
   ⚙ `monarch budget` plans this.
2. **Reference images need absolute workspace paths** (`/home/user/...`).
3. **The style anchor sheet rides EVERY scene gen** — character lock is
   only real if the reference is attached every time.
4. **ffmpeg resolves dynamically:** workspace copy → pip `imageio_ffmpeg`
   path → `get_ffmpeg_exe()`. Never hardcode. ⚙ wired: render.py already
   resolves via imageio_ffmpeg.
5. **Workspace diet, always:** after final mux delete composed/, clips/,
   silent video, mix WAVs, superseded renders. Stay far under the
   ~128 MB snapshot cap — over-cap snapshots silently DROP OR TRUNCATE
   files (a law file lost §1–8 this way). Diet BEFORE the turn ends.
   ⚙ render tests unlink outputs after verifying.
6. **Editor text NEVER enters gen prompts** — sums/captions/end-cards/
   thumbnails are PIL passes. Fonts: Archivo Black (captions), Staatliches
   (chalk).

## 6. PROCESS LAW (the order that worked)

1. **Read every law file before touching media.** The Fountain gate caught
   a real 6≠7 word error that would have shipped broken. ⚙ validate_fountain.
2. **Confirm visual style BEFORE bulk generation** (the operator stopped a
   cinematic-painterly batch to demand stickman — 10 images saved).
3. **Gate → VO → VAD → stills → animate → SFX → BGM → QC → package.**
   VO exists before clips are timed; BGM last (it ducks the real envelope).
4. **User bug reports are locations, not diagnoses.** Run VAD, print
   segment maps, find stranding structurally. Measure, never guess.
5. **Keep both deliverables** (BGM / no-BGM finals) for A/B; a level tweak
   is a 10-second re-mux, not a re-render.
6. **Every fix verified by numbers before presenting:** gap list, boundary
   silences, per-channel peak, RMS windows, duration, fps. Present the
   measurement WITH the file.

## 7. PREMIUM PASS LAW (cheap/cringe → professional)

1. **Restraint is the flex.** Removed after testing: giant word stamps
   ("91!", "NABBE", "GALTI?"), manga "HA HA" pop-ups, confetti bursts,
   sinusoidal shake. What remains: clean motion, one idea per beat.
2. **Branding:** channel name ZERO times in the body. ONE clean end slate
   — "Follow karo" + tagline + thin chalk rule, fade-rise, whitespace.
   Hard-sell FOMO ("shayad phir kabhi nahi milenge") BANNED — warm daily
   invite instead ("Kal milte hain, nayi seekh ke saath").
3. **Soften 30–40% vs the fun version:** flash-cut alpha 120→70 (then
   replaced by crossfade), vignette 110→78, desat 0.50→0.38, shake 6→4 px.
   Punch-in carries hits — no fake earthquakes.
4. **Ending word-maths stays exact (18 × 7)** even after de-branding —
   restructure, never pad.

## 8. EDIT-VERIFY LAW (the silent edit miss — paid for twice)

**The miss:** an edit reported success but never landed; a render shipped
the OLD voice clip ("Biz Thoughts" VO survived de-branding). The operator
heard it; the pipeline didn't.

1. **Every edit verified by grep/read-back before the next step.** A
   successful tool response is NOT proof the file changed.
   `grep -n "<the new line>" file`.
2. **A/V source-of-truth check before render:** print the file list the
   pipeline will actually read (clip-suffix map); confirm content matches
   the approved script.
3. **Caption typography:** no `—` and no `...` ON SCREEN — clutter at
   short-form speeds. Commas only. VO text may keep natural punctuation;
   screen text stays clean.
4. **Knowledge files are deliverables too:** after appending sections,
   `wc -l` + `grep "^## "` proves the document survived the turn.

## 9. QC GATE — run ALL before presenting ANY render

- [ ] Word counts: `monarch screen-script` gate = exit 0 (18 × 7 exact)
- [ ] No clip ends mid-sentence; no word spoken twice (seam audit) ⚙
- [ ] VAD boundary check: max silence at every boundary < 0.65 s ⚙
- [ ] Whole-mix gaps > 0.55 s: only the ONE intentional drama sting ⚙
- [ ] Peak per stereo channel ≤ 0.85 after encode; never mono downmix ⚙ (mono note)
- [ ] Music bed: mid-gap RMS ≈ 15–30% of VO RMS; inaudible-under-voice spot check
- [ ] Music audible from frame 1 (intro RMS > 0.03) ⚙
- [ ] Duration inside brief (short 40–60 s); 30 fps, 9:16, yuv420p ⚙ (drift check)
- [ ] Every scene still exists; every scene has motion + a change within 3 s
- [ ] No branding in body; single clean end slate; no FOMO hard-sell
- [ ] Captions: no `—`, no `...`, karaoke colour on the spoken word
- [ ] Upload package (titles, description, tags, 3 thumbs) matches the FINAL file
- [ ] Workspace under snapshot cap; intermediates deleted; law files verified intact ⚙ (doctor)

## 10. MISS LOG (L16 — each row is a paid-for lesson)

| # | Miss | Root cause | Fix shipped | Rule |
|---|------|-----------|-------------|------|
| 1 | Stranded last words over wrong scene | `—`/`...` in TTS text | commas; regenerate | §1.2 |
| 2 | Continuation word in wrong clip ("ho", "hain") | clip ended mid-sentence | sentence-per-clip restructure | §1.1 |
| 3 | Word spoken twice ("Hain" ×2) | duplicated at clip seam | audit both sides of every seam | §1.3 |
| 4 | Cuts inside pauses | split = duration guess | VAD word-start splits | §2.1 |
| 5 | ~1 s dead air at 2 boundaries | 0.6 s gap + clip head silence | gap budget 0.30 s + boundary check | §2.2–2.3 |
| 6 | BGM rejected as irritating | tension gimmicks vs motivational content | warm-pad rewrite, banned list | §3.1–3.2 |
| 7 | Music inaudible at hook | 1.4 s pad attack | attack ≤ 0.5 s | §3.4 |
| 8 | False clipping alarm (1.099) | mono downmix summed channels | per-channel peaks | §3.5 |
| 9 | 8 scenes missing mid-turn | image cap 10/turn unplanned | batch budgeting, priority order | §5.1 |
| 10 | Reference image "not found" | relative path | absolute paths only | §5.2 |
| 11 | ffmpeg vanished between sessions | pip/binary not persisted | dynamic resolver | §5.4 |
| 12 | 150–200 MB workspace, dropped files | intermediates hoarded | post-mux diet | §5.5 |
| 13 | Scene 7 word count 6≠7 | human count error | Fountain gate caught it | §6.1 |
| 14 | Wrong visual style started | style not confirmed first | stop-and-ask before bulk gens | §6.2 |
| 15 | Caption highlight never underlined | multi-word highlight vs token match | first-word token match | §4.3 |
| 16 | Effects read cheap/cringe | juice over craft | premium pass: restraint law | §7 |
| 17 | "Biz Thoughts" VO survived de-brand | edit silently never landed | grep-verify every edit | §8.1 |
| 18 | `—`/`...` left on screen captions | typography carried from VO text | clean-caption rule | §8.3 |
| 19 | Law file lost §1–8 | snapshot cap truncated it | knowledge-file verify + lean workspace | §5.5, §8.4 |

**One line:** *Write sentences that end where clips end, cut where words
start, score under the voice with warmth, brand once at the end with
grace, verify every edit with grep, measure every claim, budget every
generation, and delete what you do not need.*
