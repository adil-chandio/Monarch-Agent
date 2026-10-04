# MONARCH CAM — QUICK COPYRIGHT / CLAIM-RISK SCREEN

**Purpose:** give each footage lead a fast, honest warning label before it reaches the edit, then
run YouTube's own upload-time check on the finished draft. This is a workflow screen—not legal
advice, a copyright clearance service, or a promise that a clip will never receive a claim.

## The important distinction

Do not collapse these into one “copyright” answer:

| Question | What answers it | What it does not answer |
|---|---|---|
| Who filmed/owns this clip? | Source tracing and evidence from the filmer/rightsholder | A reverse-image search, upload date, or Content ID result alone |
| Is Monarch Cam permitted to use it on YouTube, in this territory, with this edit/monetization? | A licence or permission whose scope covers that exact use; legal advice where needed | Credit, a public link, a platform embed, original narration, or a “Creative Commons” filter by itself |
| Did the current YouTube reference check find a possible match? | YouTube Studio Checks on the uploaded draft; other tools may flag known references | Whether every owner/reference is enrolled, whether a later/manual claim will happen, or whether the uploader has permission |
| Could this create a reused-content/YPP issue? | A separate channel-level review of original value and YouTube policy | Whether a Content ID claim exists; passing Checks does not decide YPP eligibility |
| Is this safe and truthful to publish? | Monarch Cam's context, authenticity, safety, and editorial review | Any copyright scan |

**Never write “copyright-free,” “cleared,” or “safe” because a search or fingerprint tool found no
match.** Record the exact tool, file/version, date, status, and limits. Rights evidence and
Content ID results are separate ledger fields.

**Contact, licence and payment rule:** analysis and planning may continue while rights are
unknown, but the status is written honestly as `RIGHTS UNKNOWN` — never as clearance. Do **not**
contact a vendor, uploader, agency, or rightsholder, request a licence, or make any payment
without the operator's explicit authorization. Record the label and the open question; the
contact decision belongs to the human.

**Inspection before a screen verdict:** a claim-risk label may be written from public pages and
evidence, but never describe a clip as “reviewed” or give a visual verdict you did not actually
watch. If the clip cannot be viewed, the visual part stays `NOT CHECKED` / `NOT SCORED`, the
candidate goes back to permitted sources, and only then may the agent ask once for an accessible
upload/source.

---

## One-minute lead screen — flag, don't clear

**Target:** about one minute for an initial *manual triage* when pages load quickly. It may take
longer. Do not claim this is a one-minute definitive copyright verdict. Use only public pages
and tools you are allowed to access; do not bypass restrictions or bulk-download media.

1. **Open the lead page (about 10 seconds).** Record the URL, platform, uploader, post date,
   title/caption, any visible watermark, and any stated licence/contact/restriction. A repost or
   compilation is a lead, not proof that the account filmed or owns the clip.
2. **Trace one upstream step (about 15 seconds).** Search the exact caption/uploader and a
   distinctive frame, if available. Note whether the same footage is an obvious repost. Do not
   assume that the earliest copy found is the original.
3. **Look for an explicit reuse grant (about 15 seconds).** Open the source/licensing terms or
   contact page if linked. Confirm that the person offering the clip has authority and that the
   grant covers YouTube, edits, territory, duration, monetization, music/audio, and attribution.
   If any part is missing, mark `RIGHTS UNKNOWN` rather than inferring permission.
4. **Check for known matching/reuse signals (about 15 seconds).** Search the clip/caption on
   YouTube and other public hosts. If an accessible authorized preview is available, inspect
   two or three distinctive frames and the audio/music. A repost, matching title, or music
   recognition is a risk signal—not proof of who owns the footage. Do not download from a site
   when its terms prohibit it.
5. **Write the result (about 5 seconds).** Record the checks actually run and use one of the
   labels below. If a page or search did not load, say `NOT CHECKED`.

### One-minute result labels

- `MATCH/RESTRICTION FOUND` — a platform, owner, or tool shows a possible match, claim, or
  no-reuse restriction. This is a **high-risk alert for human review**, not an automatic creative
  rejection and not proof that a claim will attach to Monarch Cam's version. Identify the exact
  source, segment, and terms; do not publish a known restricted use without a suitable grant or
  an explicit human decision about the platform's available claim options.
- `SOURCE REPOST / OWNER UNVERIFIED` — no reliable original/rightsholder established. This is
  an editorial and rights risk; do not state that the reposting account owns it.
- `RIGHTS DOCUMENTED` — the written grant/evidence has been read and covers the planned use.
  Record scope, expiry, attribution, territory, monetization, edit rights, and music separately.
- `NO MATCH FOUND IN CHECKED SOURCES` — no match appeared in the limited checks performed.
  This is **not** a clearance, permission, or guarantee against a later claim.
- `NOT CHECKED / INCOMPLETE` — the evidence or tool was unavailable; unknown remains unknown.

The one-minute screen is a triage aid for ranking leads. It can flag obvious risks quickly, but
it cannot search every owner's private reference files or determine copyright law.

---

## What tools can and cannot do

### YouTube Studio Checks — best platform-specific pre-publish signal

For an edit intended for YouTube, upload the draft through YouTube Studio and wait for the
**Copyright** checks to finish before deciding whether to publish. Use the intended final edit;
a check on a different cut does not answer for the final cut. Private/unlisted status is a
publishing choice, not permission to upload someone else's content.

Studio may identify a Content ID match and show the affected segment and claim policy. Checks
can take longer than one minute, may change, and are not a final rights ruling. No match at
upload time does not rule out a later or manual claim, a takedown request, regional differences,
or a rightsholder adding a reference later. Keep the result and check time in the delivery
record.

Official references: [YouTube upload videos](https://support.google.com/youtube/answer/57407?hl=en)
and [Content ID overview](https://support.google.com/youtube/answer/2797370?hl=en).

### Other commonly confused checks

- **YouTube Content ID is not a public, universal lookup API.** It compares uploads against
  eligible reference files supplied by participating rightsholders, and Content ID tools are
  limited to approved rights-management partners. A public video search or YouTube Data API
  Creative Commons filter is not a query of that private reference database and does not report
  the clip's claim status. See [YouTube's Content ID partner documentation](https://support.google.com/youtube/answer/3244015?hl=en).
- **YouTube Creative Commons labels** reflect the licence setting the uploader selected for a
  video; the Data API can filter by that setting. It does not prove that the uploader owns every
  element, that the licence is valid for Monarch Cam's specific use, or that no claim exists.
  Read the [API licence filter documentation](https://developers.google.com/youtube/v3/docs/search/list)
  and verify authority/scope before relying on it.
- **Reverse-image search, exact hashes, and perceptual video fingerprints** can surface copies
  already present in the searched sources or your own archive. They cannot see every private
  reference database or establish a licence.
- **Audio recognition/fingerprinting** can identify some catalogued music/audio. It does not
  clear the visuals, prove a sync licence, or predict all YouTube claims. Check music rights
  separately; do not assume platform-library audio remains licensed when moved off-platform.
- **Local tools** such as [Video Duplicate Finder](https://github.com/0x90d/videoduplicatefinder)
  and [Chromaprint](https://acoustid.org/chromaprint) compare files against a corpus you provide
  or a supported database. They are not global YouTube Content ID mirrors. Video Duplicate
  Finder's public repository is AGPL-3.0; review its licence and the licences of optional
  components, maintenance, privacy, and dependencies before adopting it. No tool has been
  installed or wired into Monarch by this document.

---

## Dailymotion-specific check for this workflow

Dailymotion's Terms were updated June 30, 2026 and took effect July 7, 2026. Section 3.2
describes user-to-user reuse within the Dailymotion service, subject to content settings and
its terms; Section 6.7 limits alteration of third-party videos to Dailymotion's offered reuse
features and protects source attribution. These clauses are not a blanket grant to download a
video and publish an edit on YouTube. Section 2.6 also restricts automated access without prior
written approval. Treat a Dailymotion URL as a **discovery lead** unless a separate
source/rightsholder grant covers the planned YouTube use. Re-check the current terms because
they can change: [official Dailymotion Terms of Use](https://legal.dailymotion.com/en/terms-of-use/).

---

## Claim response — do not treat Studio as a claim-removal trick

A **Content ID claim** and a **copyright takedown/strike** are different processes. A claim may
block, monetize, or track a video under the claimant's settings. A takedown request can remove
a video and create a strike. Read the notice in Studio, identify the claimant and timestamps,
and preserve a copy of the notice and the edit/source records.

If a Content ID claim is valid and the source has no permission covering it, review the
claimant's policy and decide whether to leave the claim in place (accepting its block, tracking,
or monetization effect), remove/replace the material in Studio, use a properly licensed
alternative, or leave the video unpublished. A match on someone else's upload is not itself a
claim on Monarch Cam's draft. If Studio offers an editing action (such as trimming or
replacing/erasing claimed content), preview the result and verify that the *entire* claimed
material is gone. YouTube
says Studio Editor changes cannot be reverted after saving (since June 2025); preserve the
original project/file and review the preview before saving. A Studio edit may not resolve a
separate takedown or ownership dispute. Do **not** dispute a claim unless
there is a genuine, supportable basis and the operator authorizes the response; do not disguise,
pitch-shift, crop, mirror, speed-change, or otherwise alter material to evade matching. See
YouTube's [official claim-removal steps](https://support.google.com/youtube/answer/2902117?hl=en)
for the current options and limits.

An edit, new voiceover, attribution, or scene removal may reduce some practical exposure or add
original creative value, but none transfers ownership or guarantees no claim or YPP eligibility.
YouTube's [reused-content monetization policy](https://support.google.com/youtube/answer/1311392?hl=en)
is separate from copyright enforcement and applies to the channel as a whole; permission alone
does not guarantee that a reused-content format qualifies.

---

## Ledger block — copy to each candidate card and final delivery checklist

```text
Rights evidence status: RIGHTS DOCUMENTED / RIGHTS UNKNOWN / RESTRICTION FOUND
Rightsholder/contact and evidence URL or file:
Licence scope (YouTube, edits, territory, term, monetization, attribution):
Footage audio/music included and separate status:
Quick screen run (sources/tools and date):
Quick screen result: MATCH / NO MATCH FOUND IN CHECKED SOURCES / NOT CHECKED
YouTube Studio Checks run on final draft? (yes/no; date/time):
Studio result / claimant / timestamps / policy:
Operator authorization for any vendor contact / licence request / payment: (none | granted + date)
Remaining uncertainty and operator decision:
```
