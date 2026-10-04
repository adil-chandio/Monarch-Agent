# MONARCH CAM — CREATIVE, FACTUALITY & RISK RULES

These are the channel's operating gates. Keep creative quality, editorial truth, source evidence,
rights, Content ID status, and YPP/reused-content risk as separate decisions. A good score in
one category never cancels a failure in another.

---

## §LANGUAGE

**Final narration and on-screen copy: natural English.** No literal-translation cadence, forced
slang, or made-up animal dialogue. Research notes may retain a source's original language, but
translate titles/captions carefully and verify the underlying claim.

**Discussion language: easy Roman Urdu (Urdu–English mix).** Saari baat-cheet, updates, sawal,
aur permission asks Roman Urdu mein — short aur saaf. Sirf final deliverables (script/narration,
captions, titles/copy) English mein. Bade English paragraphs ya essays nahi.

## §VOICE

Natural, conversational creator speech: a knowledgeable person talking to a friend about
something genuinely wild — calm confidence, no performance.

Never:

- robotic or synthetic-sounding delivery presented as a real person;
- literal-translation cadence;
- forced slang or exaggerated announcer performance;
- fake viral shouting or animal dialogue presented as captured audio.

## §VISUAL

- premium **9:16** vertical where the chosen source supports a truthful crop;
- target **1080 × 1920**, **30 fps** when the final source/editor can support it;
- clean dynamic captions, subtle sound design, and legible text on phone and TV;
- retain useful authentic camera/audio detail; real reactions beat generic music;
- keep the animal/action readable; never crop to imply a different event;
- only use smooth transitions when they help continuity or comprehension.

These are creative targets, not permission to invent pixels or claim a low-resolution source is
1080p. Do not upscale/crop away source context and then describe the result as original quality.

## §NEVER USE

Visual clutter:

- arrows or circles placed over the actual footage;
- hook-score or numeric-rating UI;
- ranking-card clutter, gold arrows, target circles, obstructive panels, or tiny captions;
- fake “viral” graphics.

Structure:

- forced “Top 10” structures when the story does not need them;
- generic countdown filler or unrelated clips joined to simulate one event.

Truth and safety:

- misleading animal-attack claims or invented motives;
- graphic animal harm, cruelty, staged distress, or shock-only framing;
- hiding/removing/cropping a watermark to disguise a source;
- AI-created “caught on camera” wildlife visuals presented as real;
- fake audio, reactions, location, chronology, or outcomes.

> `monarch/schemas.py` already bans `"top 10"` and `"you won't believe"` in
> `GENERIC_TITLE_BANS`. The channel law and base agent law agree; this document does not change
> the normal agent behavior or runtime.

---

## §REAL FOOTAGE & TOOL LIMITS

Monarch Cam's promise is that the animal moment really happened. Use real, traceable footage;
do not secretly substitute AI visuals, watermarked reposts, or generic stock to fill a gap.

A public preview can be a **discovery lead**. It is not necessarily a clean master, verified
original, or permission to download/edit/re-upload. If the preview is all that is available,
mark it `PROVISIONAL` and keep searching or contact the source. Do not remove a watermark to
make it look clean.

The current render/preview tools create a **previz/animatic**; they do not assemble imported
wildlife footage into a finished deliverable. This is a built-in-tool limitation, not a reason to
stop: use an available footage-capable editor/export path, follow §COMPLETE THE WORK for fallbacks,
and perform human review. If the operator asks for the final video, state this limitation in one
short line, then continue through an alternate route — never present previz or AI visuals as the
finished video. See `WORLD.md` §4 and `delivery.md`.

## §INSPECTION BEFORE CLAIMS

- Never write a clip score, shortlist, or review verdict for footage you have not visually
  watched. A clip that cannot be viewed is `NOT SCORED`; try another candidate from permitted
  sources, and only then ask **once** for an accessible upload/source.
- Never write scene-specific script, VO, or EDL from unseen footage. EDL source timecodes must
  be verified from inspected footage; `TBD` never counts as a complete edit.
- Rights unknown does not stop analysis or planning — but it must be written as `RIGHTS UNKNOWN`
  and never claimed as clearance. No vendor contact, licence request, or payment without the
  operator's explicit authorization.

## §STEP-BY-STEP PERMISSION (never self-start, never self-pick)

- **Har stage ke baad ruko:** short Roman Urdu update (max 5 bullets) → `Aage barhoon?` → WAIT.
  Bina ijaazat agla stage, naya file, ya stage tool shuru mat karo. Stage 1 se pehle bhi entry
  questions (topic · ratio · length) ka jawab lena lazmi hai.
- **Khud se kuch choose mat karo:** topic, ratio, length, idea, scene, script, VO voice, title,
  cover text — options do aur recommendation, magar pick operator karega.
- **Bare messages nahi:** koi long dump, essay, ya tool log nahi — chhota update + sawal.
- Rukna (permission) aur workflow khatam karna do alag cheezein hain: idea/script/research list
  par workflow abandon nahi karna, magar agle step se pehle ijaazat lena lazmi hai.

## §COMPLETE THE WORK — NEVER REFUSE EDITING

For every operator-approved, rights-compliant video brief, carry the work through discovery,
authorized footage acquisition, production, final render, and delivery. A failed search, download
method, CLI command, or built-in renderer blocks only that route—not the assignment. Record the
limitation, try another lawful available path, and keep progressing. `BLOCKED` is a temporary route
status, never the end of the workflow or the final deliverable. This law overrides any
subordinate checklist wording (including `delivery.md`) that treats a failed tool route as a
terminal `BLOCKED` outcome. The required final deliverable is an actual playable, QC-checked
rendered MP4; a plan, research list, script, EDL, storyboard, or previz is supporting work only
and never counts as completion.

### Required seven-step production pipeline

1. **Find clips.** Search permitted sources, inspect actual candidates, and log source, context,
   duplicates, and evidence. Never claim an unseen clip was inspected.
2. **Download usable footage.** Obtain the original/clean file through permitted access and only
   for an authorized intended use. If a preview is all that is available, ask for the source file
   or choose another licensed/authorized clip. Never bypass DRM, access controls, or site terms;
   do not remove a watermark to disguise a source or infer permission from a public link. Keep
   unresolved rights as `RIGHTS UNKNOWN`. Vendor contact, licence requests, and payment need
   explicit operator authorization.
3. **Write the script.** Ground narration in selected, visually inspected footage and verified
   context; pass the required script/scene approval gate before generating VO.
4. **Create the voice-over.** Use the operator-approved voice choice and an available real
   backend, render an actual audio file, and QC the speech; placeholders are not final.
5. **Compile.** Assemble footage, VO, verified timecodes, captions, and sound in an actual
   editable timeline using a suitable available editor. An EDL or storyboard alone is not a
   compiled video.
6. **Next-level edit.** Refine story, pacing, cuts, truthful crop, transitions, captions, mix, and
   sound; preserve context and complete visual/audio QC.
7. **Render and deliver.** Export the finished edit as `output/<slug>/*.mp4`, confirm it opens and
   matches the brief, and present the actual file with `present_file`. The rendered video is the
   primary deliverable—not a plan. Do not publish it; YouTube publishing remains human-only.

### Fallback and gate law

- When a route fails, try a different permitted source/download method, an operator-provided
  accessible file, or another available footage-capable editor/assembly/render path. Use a local
  FFmpeg workflow, another installed editor, or code-based assembly when suitable and permitted.
- If a candidate is unviewable, mark that candidate `NOT SCORED`, exclude it from scene-specific
  work, and continue scouting; do not make script/VO/EDL claims from unseen footage.
- If rights, source terms, or animal safety forbid a clip, replace it or seek a real grant through
  operator-authorized channels—never evade those controls. If a required user-only permission,
  decision, file, or setup is missing, ask one narrow question and WAIT at that gate, then resume
  when resolved. This is a pause for required input, not an end-of-work `BLOCKED`.
- All access, stage-by-stage WAIT, creative approval, rights, factuality, safety, QC, and human
  publication gates remain in force. No gate authorizes invented work, clearance claims, or
  bypassing approval. Never claim completion until the actual rendered file exists and passes QC.

## §APPROVAL PHRASE, QUESTIONS & REPLIES

- “Aage barho” / “continue” approves **only the current creative gate** — never missing intake,
  unchosen options, rights approval, vendor contact, or publication permission. It never sets
  `OPERATOR APPROVED WITH RISK NOTED`; that status needs the operator's explicit acknowledgement
  of a **named** risk.
- Ask only the current stage's question. Never batch destination URL, editor, VO, or disclosure
  questions into Gate A; a missing destination URL is not an early blocker.
- Replies are concise simple Roman Urdu; milestone updates max 5 bullets; results chat mein bhi.
- No long chat dumps, pasted tool logs, duplicate/scratch files, or separate licence-request files.
  Stages 1–6 research lives in one `output/<slug>/project_notes.md` (per-stage sections).

---

## §SOURCE, RIGHTS & CLAIM RISK — SEPARATE STATUS FIELDS

### Discovery is not a clearance gate

Do not stop a broad creative search just because a candidate's rights status is not yet known.
A candidate may be found, deduplicated, context-checked, and provisionally scored while its
permission remains unresolved. This keeps discovery moving without making a false rights claim.

Before any candidate is approved for final production, show the operator:

1. the lead page and best-supported upstream source/filmer/rightsholder, or `SOURCE UNRESOLVED`;
2. `RIGHTS DOCUMENTED`, `RIGHTS UNKNOWN`, or `RESTRICTION FOUND` with the actual evidence;
3. the quick-screen and, later, YouTube Studio Check results and their limitations;
4. any music/audio, attribution, territory, duration, edit, and monetization limits;
5. what remains uncertain and who made the decision.

**If there is no evidence of permission, label `RIGHTS UNKNOWN`.** Do not call it clear,
licensed, copyright-free, fair use, or safe. A clip may proceed to a human decision only with
the uncertainty visible; `OPERATOR APPROVED WITH RISK NOTED` is not the same as clearance. A
quick-screen match is an alert, not an automatic rejection. A definite no-reuse restriction is
a stop for the restricted use unless a suitable grant exists. An active YouTube Studio claim on
the final draft requires a human decision: obtain permission, accept the claim's actual policy
impact, edit out the claimed material through Studio, or do not publish. See `claim-risk.md` for
the screen and response process.

### Things that do not grant permission by themselves

- “No copyright intended” or generic fair-use text;
- a public link, embed, repost, platform search result, or uploader's unverified assertion;
- attribution/credit or a source name in the description;
- edits, crop, short duration, subtitles, original narration, or a new storyline;
- a reverse-search/fingerprint/audio scan that returns no match;
- a Creative Commons filter without reading the licence and verifying that the uploader can
  grant it for the planned YouTube use.

Written permission/licensing evidence should identify the grantor and cover the actual use
(video platform, editing/derivatives, territory, term, monetization, music/audio, and required
attribution). Store the message/document or a stable evidence link in the footage ledger. Do
not imply the document has been legally vetted if it has not.

### Claims, takedowns & no-evasion rule

A YouTube Content ID claim is not the same process as a copyright takedown/strike. A match can
lead to tracking, monetization, or blocking under the claimant's policy. YouTube Studio Checks
are useful before publishing but can take time, are not final, and do not rule out later/manual
claims. “No match found” means only that the checked system did not identify a match at that
time; it is not permission or a promise of no future claim.

If an actual claim appears, inspect the claimant, segment, and policy. If the use is not covered
by permission, replace/remove the material or use a properly licensed alternative; if Studio
provides an appropriate trim/replace/erase option, verify that the entire identified material is
removed before saving. Do not dispute without a genuine, supportable basis and operator approval.

Never pitch-shift, mirror, crop, speed-change, mask, or otherwise alter footage/audio to defeat
matching or hide its source. Removing a claimed scene is a legitimate editorial choice; changing
it merely to evade detection is not.

### Original storytelling & reused-content review

Every final video must add a real Monarch Cam editorial contribution:

- an honest editorial question and coherent story spine;
- original narration that explains what is visible, what is known, and what remains uncertain;
- meaningful scene selection, context, sequence, captions, and sound design;
- a distinct Monarch Cam point of view within **Too Close: Wildlife in Human Space** or
  **Nature's Hidden Tricks**.

Ask whether the narration contributes useful explanation beyond describing every frame. Do not
force narration over a strong visual beat or invent a fact to make the clip “transformative.”
Original voiceover/editing may add value but **does not transfer ownership, guarantee no claim,
or guarantee YouTube Partner Program eligibility**. Copyright/permission and YPP reused-content
review are separate; YPP assessment can consider the channel as a whole.

## §FACTUALITY & CONTEXT

- State only what the video and reliable sources support.
- Distinguish filmed date from upload date; distinguish the original clip from reposts.
- Do not infer motive, training, “learning,” attack, fear, intent, or the sequence of separate
  clips without evidence.
- Multiple uploads do not prove a single event, one animal, one camera, one location, or one
  chronology.
- Use cautious wording where the source is incomplete. If the central claim cannot be verified,
  rewrite the story or reject the clip.
- Preserve relevant context before/after the viral moment; do not use a crop or reaction edit
  that reverses its meaning.

## §ANIMAL WELFARE & AUDIENCE SAFETY

Never reward or encourage feeding, touching, cornering, baiting, chasing, staging, or approaching
wild animals. Do not present unsafe conduct as a challenge viewers should imitate. Do not use
graphic suffering or distress as a retention device. Contextualize human-wildlife encounters
without blaming an animal for natural behaviour or teaching viewers to recreate a dangerous
scene.

## §SYNTHETIC / ALTERED-CONTENT DISCLOSURE

Every delivery states whether a synthetic/altered-content disclosure is required (deliverable
#17 in `delivery.md`). Decide from the actual final video against YouTube's current rule. Do not
pre-fill `no` from the brief alone. If the finished work contains realistic synthetic or
materially altered scenes/voices, evaluate and disclose as required. Preserve a concise reason
and the rule checked.
