# MONARCH CAM — PACKAGING & CONVERSION

Stage 12. Packaging is an important lever on this channel: the operator-supplied Analytics
snapshot reports Browse Features supplied 68–90% of traffic on the benchmarked winners (see
`analytics.md`). Treat that as historical context, not a guarantee about a new upload.

---

## THE PACKAGING LAW

**Generic = dead. Specific must also be true.** A title should state the actual, verified viral
premise—not upgrade a sighting into an attack, infer motive, or promise more than the clip shows.

Banned example (too generic, does not communicate the premise):

```
✗ Bears Caught on Camera… Wait Till the Last One
```

Possible directions for the bear-door brief, **only if the selected source supports the exact
claim**:

```
✓ A Bear Opened This Car Door
✓ This Bear Got Into a Car — Here's What the Clip Shows
✓ Why Bears Check Cars for Food                    (requires reliable factual sourcing)
```

“Learned,” “knew exactly,” “our doors,” and “keeps coming back” are **not approved default
claims**. Use them only if the footage, source, and factual context support them. A strong title
must be specific without attributing unverified motive, combining unrelated clips into one
event, or pretending the location/door belongs to Monarch Cam.

Also banned by the base agent (`GENERIC_TITLE_BANS` in `monarch/schemas.py`): “top 10,”
“you won't believe,” “gone wrong,” “subscribe,” “link in bio,” and year-stamp titles. Run every
title through `monarch gate-title`, then manually verify its factual promise against the final
edit.

## THE “PART N” BAN

From `analytics.md`: Part 2 of a benchmarked winner had **better** completion (38.5% vs 34.9%)
and **far fewer** impressions (1.2M vs 3.2M). A sequel title can create entry friction and
reduce independent clickability.

**Every upload needs a standalone promise.** Avoid “Part 2,” “Part 3,” “More of…,” and “The
sequel” unless the operator explicitly chooses a serialized format with a clear reason.

## COVER TEXT

Two to four words, readable on a phone at arm's length and on a TV across a room.

Possible bear-brief text (use only if the selected frame makes it literally true):

```
DOOR OPENED
BEAR INSIDE?
```

Rules: no arrows, target circles, rating UI, or clutter (see `rules.md`). Cover text is a
promise the final video must keep.

## PINNED COMMENT

Route the viewer to a connected long-form story or playlist that actually exists:

```
Full story: <verified related story or playlist> → [link]
```

Avoid “subscribe for more” filler. If no relevant destination exists, do not invent a URL;
flag the missing destination and propose the next content asset.

## EVERY SHORT SHOULD LEAD SOMEWHERE

Pick one relevant destination and wire it in:

- a related long-form video;
- a relevant playlist;
- a relevant next Short;
- an end-screen or description path where available.

End screens were a traffic source on Bear Part 3 in the supplied snapshot; that is useful
channel context, not a guarantee. They are never filler.

## THE ACTUAL GOAL

```
Shorts discovery → connected wildlife story → returning viewers → subscribers
                  → evergreen recommendation system
```

Views are the input, not the output. The supplied snapshot reports ~1.83 subscribers per 1,000
views (`analytics.md`); a Short that gets views and leads nowhere has not done its connection
job.

## OTHER PLATFORMS

- **TikTok caption** — native to TikTok, not a YouTube description copy-paste.
- **Instagram Reels caption** — native to Reels.
- **Hashtags** — platform-appropriate set, not a keyword dump.
- **Tags** — YouTube tags from the verified premise and its search variants.

## FINAL PACKAGE CHECK

```
monarch package ...      # build the package
monarch gate-title ...   # gate the titles
monarch slop-audit ...   # catch generic/filler language
```

A tool gate does not fact-check the footage. If `gate-title` or `slop-audit` complains, fix the
copy, then verify the final title promise against the actual edit. Never change the facts to
save a catchy title.
