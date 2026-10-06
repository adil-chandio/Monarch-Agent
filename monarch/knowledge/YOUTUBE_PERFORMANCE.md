# YouTube performance knowledge — audience first, evidence always

**Reviewed:** 2026-10-06 · Platform facts below are dated and must be re-checked when a volatile policy or feature affects a live task. See [`SOURCES.md`](SOURCES.md).

## What official guidance supports

YouTube describes recommendations as personalized and aimed at helping each viewer find content they will enjoy, including long-term viewer satisfaction. Its creator guidance groups video response into **appeal** (whether people choose to watch), **engagement** (whether they stay) and **satisfaction** (whether they enjoyed it). The signals may vary by format and surface; this is not a public, complete ranking formula. [Recommendation system](https://support.google.com/youtube/answer/16533387?hl=en) · [Performance guidance](https://support.google.com/youtube/answer/16559650?hl=en)

The title and thumbnail set expectations. The opening should promptly honor that promise. Audience-retention reports define the intro as the share of viewers still watching after the first 30 seconds and allow comparison with a video's own relevant history; do not convert that into a mandatory hook structure for all videos. [Retention guidance](https://support.google.com/youtube/answer/9314415?hl=en&co=GENIE.Platform%3DDesktop)

YouTube says there is no universal ideal video length. Use the length needed for the material and compare channel/format retention; do not pad a video to hit a platform folklore number. Publish time is not known to affect long-term performance, although audience availability matters for live streams and premieres. [Length and timing guidance](https://support.google.com/youtube/answer/16559651)

Studio's Trends tab surfaces recent activity/search context, including signals around the audience's recent viewing and a rolling 28-day window. Treat it as a dated lead for research, not a complete or durable estimate of total market demand. [Trends tab](https://support.google.com/youtube/answer/11962757?hl=en&co=GENIE.Platform%3DAndroid)

## Packaging tests

YouTube Studio's native title/thumbnail A/B tests can compare up to three variants and select using watch time, not CTR alone. Results can take days (up to about two weeks) and can be inconclusive or show no clear winner. Record the exact Studio outcome; never force an inconclusive test into a winner or substitute a third-party sequential CTR test as equivalent evidence. [Native A/B testing](https://support.google.com/youtube/answer/13861714?hl=en)

Packaging QA must confirm: (1) title and thumbnail communicate the same truthful promise, (2) the video actually pays that promise, and (3) the opening begins delivering it. Clicks without the expected experience are not a successful outcome.

## Metrics: keep their meanings separate

Use metrics that match the decision and format; do not optimize a single universal “viral score.” When authorized data exists, useful views can include:

- **Appeal/packaging:** impressions and CTR, interpreted by traffic source/surface and exposure volume.
- **Engagement:** average view duration, average percentage viewed and the time-indexed retention curve. Absolute minutes and relative percentage answer different questions.
- **Shorts:** format-specific engaged/stayed-to-watch and swipe behavior; do not merge uncritically with long-form.
- **Satisfaction/business:** available returning-viewer, subscription, survey/feedback or channel-goal signals, with their definitions and time windows.
- **Experiments:** official test result, tested variants, duration/window, metric used, and whether Studio called it a winner, preference, same, or inconclusive.

Audience retention curve data is available in the YouTube Analytics API for authorized channel analytics: `elapsedVideoTimeRatio` identifies the time point and `audienceWatchRatio` / `relativeRetentionPerformance` describe different retention views. The API documents 100 equally spaced points per video; the relative value is not an absolute count. `audienceWatchRatio` may exceed 1 for a segment that viewers replay. Map a point to an approximate segment time using video duration; do not claim to know which exact line caused a dip without matching the curve to a verified timeline. [Metrics](https://developers.google.com/youtube/analytics/metrics) · [Dimensions](https://developers.google.com/youtube/analytics/dimensions)

## Monarch capability boundary

The existing `monarch learn ingest` path imports aggregate Studio CSV/TSV fields (title, views, average percentage viewed and optional subscribers/date/duration). `monarch learn distill` makes provisional patterns; it does not establish causation or receive private channel data automatically. The additive `monarch learn retention` importer can read a user-supplied retention export and produce a curve report; `monarch learn experiment record/log` can store an operator-transcribed Studio test outcome. Neither command family calls YouTube or authenticates OAuth; neither verifies the data/result source or export owner's permission. See [`CAPABILITY_MAP.md`](CAPABILITY_MAP.md).

```text
monarch learn retention ingest retention.csv --video-id VIDEO_ID --title "Title" --duration-s 120
monarch learn retention report --video-id VIDEO_ID
monarch learn experiment record --test-id TEST_ID --video-id VIDEO_ID --title "Title" --test-type thumbnail --outcome inconclusive --variant A --variant B
monarch learn experiment log --video-id VIDEO_ID
```

The retention importer requires `elapsedVideoTimeRatio` (or a supported elapsed-time alias) and `audienceWatchRatio` columns; `relativeRetentionPerformance` is optional. It rejects an aggregate APV export as a substitute. The default log is `.monarch/retention_curves.jsonl`, which is local session state. The experiment recorder stores the native result from the operator; it requires 2–3 variant labels and does not execute/verify the Studio experiment. It rejects a claimed winner when the recorded outcome is `inconclusive`, `performed_same`, `in_progress` or `not_run`. Its default log is `.monarch/experiments.jsonl`.

If a curve, traffic-source split, native experiment outcome or satisfaction measure was not provided, mark it `NOT MEASURED`. Never claim an exact-second retention diagnosis from aggregate APV alone. Never infer competitors' private metrics from public views.

## Prohibited growth claims

Do not teach agents that:

- there is one secret ranking hack, ideal video length, universally best upload hour, mandatory hook formula or guaranteed viral structure;
- tags alone are essential to discovery;
- a single underperforming video proves that a channel is penalized;
- high public views reveal private CTR, retention or satisfaction;
- a CTR increase by itself means the viewer experience improved;
- a correlation or before/after change proves the edit caused the result.

Use a documented hypothesis, a relevant baseline and a measured outcome. Keep creative formulas available as ideas, but label them `HYPOTHESIS` until the channel data supports them.
