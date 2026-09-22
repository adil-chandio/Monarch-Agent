# Quality gates (structure placeholders)

Every idea / structure / script must pass:

- [ ] Would a stranger click without knowing the channel?
- [ ] Is the angle original vs current winners (not a clone)?
- [ ] Does the first 8 seconds create an open loop they cannot close without watching?
- [ ] Every 15–20s: new information, twist, proof, or tension?
- [ ] Payoff matches (or exceeds) the promise?
- [ ] Works for THIS niche's audience language, not a template dump?
- [ ] Metadata and title are a weapon, not a label?

Fail any gate → loop. Do not output.

## Full QC checklist (17 checks)

See `monarch/core/self_qc.py` for the programmatic enforcement.
Run `python -m monarch qc <notes.json> --stage <stage>` or `python -m monarch qc-render <video> <board.json>`.

| # | Check | Stage |
|---|-------|-------|
| 1 | Research not skipped | research |
| 2 | Gates not hidden | research |
| 3 | Ijazat asked (HAAN) | render |
| 4 | No clone or Top-10 DNA | packaging |
| 5 | Duration matches VO | script |
| 6 | Word count exact per scene | script |
| 7 | Open loop in first 8 s | script |
| 8 | Retention job on every beat | script |
| 9 | Match-cut named (non-final) | script |
| 10 | No baked text in gen prompts | render |
| 11 | Character lock verbatim | render |
| 12 | Negative prompt attached | render |
| 13 | SFX no double-hit | edit |
| 14 | Silence sting before key fact | edit |
| 15 | Postage-stamp readable thumb | packaging |
| 16 | Title + thumb = one sentence | packaging |
| 17 | Click debt paid in script | packaging |
