---
name: deep-forensic
description: >
  Full competitor takedown for one niche: hunt 15-20 viral videos across
  channels, ingest their transcripts, run 'monarch deep-forensic' for script
  DNA (Zack band, hooks, you-density, proof density, formulas) + production
  DNA + topic clusters + 10 gated idea drafts, then feed the winner into
  M2 -> make-short. Use when the operator says "analyze this niche",
  "competitors ka forensic karo", or approves a deep research run.
---

# Skill: deep-forensic — niche → 15-20 viral videos → DNA → ideas → video

The division of labor is law: **the AGENT fetches** (page tools, platform
network), **Monarch analyzes** (real computation, no vibes), **gates decide**
(nothing ships without them).

## Phase 1 — HUNT (agent does this)

1. Fix the niche: `NICHE` (e.g. "history mysteries").
2. Use your web-search + page-fetch tools to find **5-8 channels** killing it
   in the niche. For each channel, pick their **2-4 biggest outliers**
   (views far above the channel's own median — that's the viral signal).
   Target **15-20 videos total** (minimum 3 for the tool; the operator law
   is 15-20).
3. Good hunt signals: outlier multiplier, recency, comments saying
   "how does this only have X views".

## Phase 2 — INGEST transcripts (agent + monarch)

For every selected video:

1. Page-fetch: `https://www.youtube.com/watch?v=$VID` → save markdown
   (title, channel, views, likes, length, description, `## Transcript`).
2. Normalize into the pipeline:
   ```
   monarch transcript-ingest fetch_$VID.txt --save transcripts/
   ```
3. Note the runtime from the page (`Length: 00:12:34` → `duration_s: 754`).

## Phase 3 — BUILD the dossier

Create `dossier.json` (fail-closed schema — the tool rejects gaps):

```json
{
  "niche": "history mysteries",
  "videos": [
    {
      "id": "dQw4w9WgXcQ",
      "title": "...",
      "channel": "...",
      "views": 4200000,
      "likes": 180000,
      "duration_s": 754,
      "date": "2025-11-02",
      "thumb_note": "one face, high contrast, red circle",
      "transcript": "paste the transcript text here (or read it in from
                     transcripts/<id>.txt before writing the dossier)"
    }
  ]
}
```

## Phase 4 — ANALYZE (Monarch computes)

```
monarch deep-forensic dossier.json --out output/forensic/$SLUG
```

You get, per video and aggregated:

- **script DNA** — words/30s (Zack band 65-95), hook OPEN/closed (N1),
  second-person density, proof density (numbers/100w), sentence rhythm,
  CTA placement (N4 check), title formula T1-T8
- **production DNA** — runtime distribution, engagement (likes/views),
  outlier multiplier vs median
- **patterns** — top-vs-bottom median split with N (no single-video laws)
- **topic clusters** — what the niche rewards
- **10 idea drafts** built from the winning patterns

Read `deep_forensic_report.txt` with the operator. This is the STOP point.

## Phase 5 — GATE the winner (never skip)

```
monarch gate-idea --title "$T" --hook "$H" --itch "$I" --visual "$V"
```

Pick the idea (operator picks if interactive), fix what the gate flags,
then hand off: **Script Doctor → make-short skill** (the video phase:
storyboard → box card → SFX → previz → HAAN → QC).

## Phase 6 — REMEMBER

```
monarch memory save --topic "$TOPIC" --notes "forensic: output/forensic/$SLUG"
```

## Guardrails

- Views/dates come from the fetched pages — never invent numbers.
- Patterns carry N; one video is an anecdote, not a law.
- Every idea passes `gate-idea` — clones and generic titles die at the gate.
- No render without HAAN. No upload by the agent, ever.
