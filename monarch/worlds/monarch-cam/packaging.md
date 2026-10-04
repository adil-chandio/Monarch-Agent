# MONARCH CAM — PACKAGING & CONVERSION

Stage 12. Packaging is the primary lever on this channel: Browse Features supplied 68–90% of
traffic on every benchmarked winner (see `analytics.md`).

---

## THE PACKAGING LAW

**Generic = dead.** A title must state the *specific* viral premise.

Banned example (too generic, does not communicate the premise):

```
✗ Bears Caught on Camera… Wait Till the Last One
```

Strong directions:

```
✓ Bears Have Learned How to Open Our Doors          (primary)
✓ This Bear Knew Exactly How to Get Inside          (A/B)
✓ Why Bears Keep Breaking Into Cars and Cabins      (A/B)
```

Why the first one wins: subject + learned behaviour + **our** doors. It is a claim about
intelligence and proximity, not a promise of a clip.

Also banned by base agent (`GENERIC_TITLE_BANS` in `monarch/schemas.py`): "top 10",
"you won't believe", "gone wrong", "subscribe", "link in bio", year-stamp titles. Run every
title through `monarch gate-title`.

## THE "PART N" BAN

From `analytics.md`: Part 2 of a proven winner had **better** completion (38.5% vs 34.9%) and
**far worse** reach (1.2M vs 3.2M impressions). A sequel title creates entry friction and
kills independent clickability.

**Every upload needs a standalone irresistible promise.** Never "Part 2", "Part 3",
"More of…", "The sequel".

## COVER TEXT

Two to four words, readable on a phone at arm's length and on a TV across a room.

```
IT OPENED THE DOOR
BEAR INSIDE?
```

Rules: no arrows, no target circles, no rating UI, no clutter (see `rules.md`). The cover
text must be *true* — it is the promise the video keeps.

## PINNED COMMENT

Always routes the viewer to the connected long-form story or playlist:

```
Full story: Why Bears Keep Coming Back to Human Homes → [link]
```

Never "subscribe for more". Never empty.

## EVERY SHORT MUST LEAD SOMEWHERE

Pick one, deliberately, and wire it in:

- a relevant long-form video
- a relevant playlist
- a relevant next Short
- an end screen or description path where available

End screens are a proven traffic source on this channel (14.3% on Bear Part 3) — they are
never filler.

## THE ACTUAL GOAL

```
Shorts discovery → connected wildlife story → returning viewers → subscribers
                  → evergreen recommendation system
```

Views are the input, not the output. The channel's real problem is ~1.83 subs per 1,000
views (`analytics.md`) — so a Short that gets views and leads nowhere has not done its job.

## OTHER PLATFORMS

- **TikTok caption** — native to TikTok, not a YouTube description copy-paste
- **Instagram Reels caption** — native to Reels
- **Hashtags** — platform-appropriate set, not a keyword dump
- **Tags** — YouTube tags from the real premise and its search variants

## FINAL PACKAGE CHECK

```
monarch package ...      # build the package
monarch gate-title ...   # gate the titles
monarch slop-audit ...   # catch generic/filler language
```

If `gate-title` or `slop-audit` complains, the title changes. The gate is not advisory.
