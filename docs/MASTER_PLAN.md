# MASTER PLAN — CHAOS MONARCH (Approved 2026-09-24)

Three avatars: RESEARCH BRAIN (done) → PRODUCTION MACHINE (done — see
RENDER_LAWS.md source journal) → **SELF-AUDITING, SELF-LEARNING,
TRUTH-TESTING BRAIN (this plan)**.

## Waves

- **W0 docs** — RENDER_LAWS.md (15), CONTENT_PLAYBOOK.md, GPU hooks,
  this plan. (shipped with this commit)
- **W1 learn loop** — `learn ingest` (YT Studio CSV/TSV →
  PerformanceRecord → .monarch/performance.jsonl) + Learn 2.0 hygiene
  (lessons: confirmed ≥3 signals / provisional <3 / stale <3∧>90d /
  auto conflict-flag on confirmed same-tag pairs) + `learn hygiene` CLI.
- **W2 truth layer** — deep-forensic recency: factor 0.5^(age/HL),
  HL=105d default (--half-life), rank blend 0.7·engagement + 0.3·recency
  (α=0.7 per temporal-RAG research), evidence_age + NO-DATE honest flags,
  stale row flags (link-rot guard).
- **W3 the eye** — `monarch audit DIR` (anchored deterministic bands:
  hook 1–10, CTR <3/4–6/7–10, pacing, VO-QC, AI-signs, freshness;
  findings = {severity P0–P3, evidence, fix-command, impact}) +
  humanize v2 (hook-shape exemption on cold open + mechanical rewrites).
- **W4 standard** — agentskills.io validator tests (name/dir/≤64,
  desc 1–1024, allowed-keys-only, body ≤500 lines) + full regression.

## Definition of done

Suite ≥315 green · fail-closed everywhere · 4 standing orders unbroken ·
push + PR comment per wave · honest ran-vs-blocked.

## Standing orders (never break)

1. Master-archive gaps (MP4 render stage in-repo, port-8080 player,
   10-SFX-preset task, positional CLI) — do-not-act until operator
   orders. Audit REPORTS gaps, never builds them.
   *ORDER REVERSED (operator, 2026-09-24): "ham PC nahi rakhte - Arena
   agent hi render karega." MP4 render stage ab IN-SANDBOX SHIPPED:
   `monarch render DIR` (monarch/video/render.py, imageio-ffmpeg static
   binary; 2-input concat+audio (G7/L2), duration drift checked vs audio
   +-0.5s (L13), scene captions burned + srt (G11), versioned name (G16).
   Upload par wohi HAAN human gate. *Archive status note:* the MP4 gap was **closed-in-production** via the
   operator's journal session (rebuildable recipe, 166s) — the in-repo
   render stage itself remains parked.
2. ruflo + GPU tools — never dependencies. Hooks/knowledge only.
3. Access key `DoitMon@rch` / lock message / laws — untouchable.
4. youtube-transcript.io token — .env only, never printed/committed.
