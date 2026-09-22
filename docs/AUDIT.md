# Forensic audit — what was actually blocking us

Not vibes. Failures.

| Flaw | Effect | Fix |
| --- | --- | --- |
| Every `.py` was `raise NotImplementedError` | Agent cannot compute, only sermon | Real maths, gates, state machine, schemas |
| Constitution ≠ code | Rules evaporate at runtime | Gates as functions that fail closed |
| No channel/niche schema | Multi-channel was a folder with `.gitkeep` | YAML template + loader |
| No scene maths | Stickman engine’s #1 re-roll cause ignored | `scene_math.py` + exact word count |
| Render gate boolean was tautology | HAAN could be bypassed by confusion | Single `require_haan()` |
| Duplicate metadata vs packaging | Two stubs, zero owner | Packaging owns CTR; pipelines call it |
| Vendor cloned, never imported | Theater | DNA schema + skills rewritten in `monarch/` |
| No CLI | Cannot prove the engine exists | `python -m monarch` |
| No tests | Ego, not proof | `tests/` on words/maths/gates/haan |
| Name “Monarch” with empty brain | Cosplay | This pass |

Still waiting (honest): LLM idea hunt, Flow/Veo render, OAuth upload, channel list from operator.

## Agent-Reach integration (done)

Live internet access via upstream CLI tools:
- YouTube: yt-dlp (zero-config, no API key)
- Twitter/X: twitter-cli
- Reddit: rdt-cli / OpenCLI
- Web: Jina Reader (zero-config)
- Semantic search: Exa / mcporter
- GitHub: gh CLI (zero-config)
- Doctor: `python -m monarch doctor`
