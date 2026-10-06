# Knowledge source register

**Checked:** 2026-10-06 · URLs below were reviewed for the specific takeaways listed; this is not exhaustive internet coverage.

## Platform primary sources

| ID | Source | Evidence used | Scope / limitation |
|---|---|---|---|
| YT-REC | [YouTube's Recommendation System](https://support.google.com/youtube/answer/16533387?hl=en) | Personalization, long-term viewer satisfaction, audience-first guidance, upload-time limits | Official creator-facing description, not a disclosure of every ranking signal or a deterministic formula. Re-check if platform guidance changes. |
| YT-PERF | [Understand content performance](https://support.google.com/youtube/answer/16559650?hl=en) | Appeal, engagement, satisfaction; packaging and opening should fit the promise | Signals differ by format; do not assume equal weights or rank from one metric. |
| YT-RET | [Measure key moments for audience retention](https://support.google.com/youtube/answer/9314415?hl=en&co=GENIE.Platform%3DDesktop) | Intro is measured at first 30 seconds; retention report is video-level and helps diagnose expectation/engagement | Report availability, sample size and processing vary; compare relevant videos and segments. |
| YT-LENGTH | [Good to know about recommendations](https://support.google.com/youtube/answer/16559651) | No universal optimal video length; audience retention helps fit length | Do not convert into a fixed duration target. |
| YT-TRENDS | [Explore trends on YouTube](https://support.google.com/youtube/answer/11962757?hl=en&co=GENIE.Platform%3DAndroid) | Studio Trends gives recent audience/search context, including rolling 28-day cards/content gaps | Availability is contextual; a recent signal is not a universal market-size estimate. |
| YT-AB | [A/B test titles & thumbnails](https://support.google.com/youtube/answer/13861714?hl=en) | Up to three variants; watch time is used; outcomes can be winner, same or inconclusive; tests may take up to two weeks | Use the actual native test result and eligibility; never manufacture significance. |
| YT-API-METRICS | [YouTube Analytics API metrics](https://developers.google.com/youtube/analytics/metrics) | Definitions of audienceWatchRatio and relativeRetentionPerformance | Authorized channel analytics access required. `audienceWatchRatio` is not always a unique-viewer percentage and may exceed 1 due to replays. |
| YT-API-DIMS | [YouTube Analytics API dimensions](https://developers.google.com/youtube/analytics/dimensions) | `elapsedVideoTimeRatio`; documented 100 equally spaced points | These are time buckets, not exact viewer events. Actual coverage depends on authorization and query support. |
| YT-API-AUTH | [YouTube Analytics API reference](https://developers.google.com/youtube/analytics/reference) | OAuth 2.0 access for reports | Monarch's additive importer does not perform OAuth. |

## Research and recognized standard

| ID | Source | Evidence used | Scope / limitation |
|---|---|---|---|
| ML-2022 | [Mayer & Fiorella, multimedia learning review chapter](https://edtechuvic.ca/wp-content/uploads/sites/11/2022/09/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles.pdf) | Coherence, signaling, spatial/temporal contiguity and related instructional design principles | Evidence is for multimedia learning tasks; not a universal entertainment-retention or recommendation formula. |
| CURIOSITY-2026 | [Frede et al., “Knowledge Gap Illustrations Spark Curiosity,” Journal of Cognition](https://journalofcognition.org/articles/10.5334/joc.501) | Two preregistered article-reading experiments (n=501, n=511); moderate explicit knowledge gaps increased information seeking | Reading/chapter-choice task, not a YouTube retention experiment. Use as a script hypothesis only. |
| DOPAMINE-2024 | [Gershman et al., “Explaining dopamine through prediction errors and beyond,” Nature Neuroscience](https://www.nature.com/articles/s41593-024-01705-4) | Dopamine theory has important nuance beyond simplistic reward-prediction-error slogans | Do not claim creative tactics control dopamine or viewers' brains. |
| EBU-R128 | [EBU R 128, version 5.0 (November 2023)](https://tech.ebu.ch/publications/r128) | Broadcast programme loudness recommendation of -23 LUFS and LRA/Maximum True Peak descriptors | Broadcast context; not a universal YouTube target and not a replacement for the active approved Style-B reference. |

## GitHub architecture references — README-level review only

| ID | Repository | Pattern noted | Validation limit |
|---|---|---|---|
| GH-OPENMONTAGE | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | Layered tools, pipeline manifests, stage-specific skills, knowledge packs, checkpoints and QA artifacts | Public README claims are not an independent performance benchmark; not cloned or executed; not a drop-in renderer. |
| GH-YT-CREATOR | [ITZSHOAIB/youtube-creator-skills](https://github.com/ITZSHOAIB/youtube-creator-skills) | Creator-approved channel memory; firsthand creator experience separately interviewed from product facts and public evidence | Workflow inspiration only; no code was copied or run. |
| GH-YT-AGENCY | [Heuresis/YouTube-Agency](https://github.com/Heuresis/YouTube-Agency) | Channel operating docs, proof-bank and learning assets | Large role/skill catalog may be overkill and is niche-oriented; not independently benchmarked. |
| GH-MOTION-FILM | [Iziedking/motion-film-skill](https://github.com/Iziedking/motion-film-skill) | Deterministic time-based scene idea, explicit claim checks and measured QC | Different renderer/toolchain from Monarch Style B; recently published at review time; not adopted or run. |
| GH-PROMPTFOO | [promptfoo](https://github.com/promptfoo/promptfoo) | Prompt/agent evaluation, regression and red-team suite patterns | Optional tool reference only; no dependency added and no model evaluations run in this pass. |

## Stewardship rule

When using a source for a new task, verify the live official/primary page if the claim is volatile or high-impact. Record a new checked date rather than silently treating this register as permanently current. Repository README statements describe design intent; code, tests, license and runtime must be inspected before any future adoption. No external repository content or code was copied into Monarch by this knowledge layer.
