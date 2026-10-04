# MONARCH CAM — FOOTAGE SOURCING, SCENE SCORING, LEDGER

Stages 2–5 of the pipeline live here.

---

## STAGE 2 — RESEARCH REAL FOOTAGE

Hunt for **real, camera-caught** moments. Useful real commands:

```
monarch search   "<query>"          # YouTube search
monarch wsearch  "<query>"          # web search
monarch rsearch  "<query>"          # reddit search (eyewitness threads, original posters)
monarch scrape   <url>              # Agent-Reach scrape (yt-dlp for YouTube, Jina for web)
monarch transcript <id>             # transcript, for context + who filmed it
```

Hunt targets: local news outlets, wildlife agencies, Storyful-verified uploads, original
social posts by the filmer, dashcam / doorbell / security-camera owners who posted their own
footage, national-park and resort channels.

Rule: **a video being watchable online is not evidence it is usable.** Every candidate is a
lead until Stage 3 traces it.

## STAGE 3 — TRACE ORIGINAL SOURCE

For each candidate, walk **upstream** until the original filmer is found. Reposts, news
roundups, reaction channels and aggregators are **not** the source.

Record for each clip:

| Field | Example |
|---|---|
| Scene ID | `S03` |
| What happens | bear tests three car doors, enters, checks interior |
| Original filmer | Daniel DeMont |
| Source type | Storyful-verified / news / original social post / agency |
| Source URL | the **original** upload, not the repost |
| Date | when it was filmed (not when it was posted) |
| Location | Gatlinburg, TN |
| Clean master available? | yes / no |
| Licence status | `PENDING` / `GRANTED (proof: …)` / `DENIED` / `BLOCKED` |
| Required attribution | exact wording |

## STAGE 4 — VERIFY QUALITY: the 10-criterion scene score

Score every candidate scene 0–10 on each criterion. **Only scenes scoring ≥8.5/10 overall
are selectable.**

| # | Criterion | Question it answers |
|---|---|---|
| 1 | Stop-scroll first frame | Would this frame stop a thumb at second 0? |
| 2 | Immediate clarity | Is the action readable in under 2 seconds, on a TV, squinting? |
| 3 | Escalation | Is it bigger than the scene before it? |
| 4 | Payoff | Does it deliver something the viewer did not have yet? |
| 5 | Real reaction | Is there authentic human/animal sound or behaviour? |
| 6 | Technical quality | Focus, exposure, stability, resolution after 9:16 crop |
| 7 | 9:16 crop suitability | Does the subject survive a vertical crop without losing the action? |
| 8 | Audience safety | No graphic harm, no distress, no age-restriction risk |
| 9 | Original source confidence | How certain are we who actually filmed this? |
| 10 | Rights feasibility | Is a licence realistically obtainable? |

Scoring is arithmetic, not vibes: write the ten numbers, then the mean. A scene at 8.4 does
not ship — find a better scene. Log every score in `output/<slug>/04_scene_scores.md` so a
rejected scene can be re-examined later.

`monarch fit` can be used to sanity-check a line's fit against the timing maths.

## STAGE 5 — VERIFY RIGHTS

Fill the licence column. Human action is required — the agent cannot sign a licence.

- `GRANTED` + proof on file → scene is selectable
- `PENDING` → scene is **not** selectable this run; note it and continue
- `DENIED` / `BLOCKED` → scene is dead; do not "temporarily" use it

**No scene enters Stage 6 without `GRANTED`.** This is the hard gate.

## THE FOOTAGE LEDGER

One markdown table per project at `output/<slug>/03_footage_ledger.md`, one row per clip,
with the licence proof linked or quoted. The ledger is a deliverable (#5 in `delivery.md`) —
it ships with the package, it is not an internal scratch file.

---

## STAGE 6 — SELECT ELITE SCENES

Build a **storyline, not a montage**. Each scene must increase tension, curiosity, surprise,
humour or payoff versus the one before it.

Example spine (from the bear/door assignment):

```
Handle → Door → Vehicle → Bear inside → Bear family payoff
```

Test the spine: if any scene can be deleted without the story losing anything, it is filler.
Delete it. Every clip must **earn its position**.

Then Gate A: present scenes + spine + title promise and WAIT for `perfect | improve`.
