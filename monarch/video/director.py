"""Storyboard + Fountain screenplay director — the Neuro Playbook made code.

Every scene the director emits carries:

* a ``NEURO_DRIVER`` tag (which N-law is firing) as a Fountain ``[[ ]]`` note,
* a retention role (``hook`` / ``tease`` / ``payoff`` / ``value-debt`` /
  ``silence-sting`` / ``payoff+cua``),
* an SFX cue from :mod:`monarch.video.audio`.

Fail-closed like everything in Monarch: the generated screenplay is run back
through the real M3 gate (:func:`monarch.pipelines.fountain.build_script`), so
a storyboard that breaks the maths line or the scene gates cannot exist.
Word counts come from the maths line — the director composes, ``fit_words``
trims, never pads.
"""

from __future__ import annotations

import re

import random
from dataclasses import dataclass, field
from pathlib import Path

from monarch.core.fit_line import fit_words
from monarch.core.gates import GateFail
from monarch.core.scene_math import SceneMath, compute_math, maths_line
from monarch.core.words import count_words
from monarch.video import story
from monarch.video.humanize import humanize
from monarch.pipelines.fountain import (
    ScriptReport,
    beats_from_screenplay,
    build_script,
    screenplay_from_text,
)
from monarch.schemas import Scene

#: creator credit that goes on every title page (access.py is the source of truth)
CREATOR = "Adil Chandio"
CONTACT = "workadilchandio@gmail.com"

COHORTS = ("kids", "genz", "adults")

#: N-law registry — mirrors monarch/playbook/neuro_psychology.md (N1-N5)
NEURO_DRIVERS: dict[str, dict[str, str]] = {
    "N1 THUMB-STOP": {
        "law": "0.1s superior colliculus / amygdala reflex",
        "gate": "one focal point, motion on frame one, contrast first",
    },
    "N2 DOPAMINE": {
        "law": "demographic dopamine modulation",
        "gate": "palette + pace + payoff density match the cohort row",
    },
    "N3 VARIABLE-RATIO": {
        "law": "B.F. Skinner variable ratio reward loops",
        "gate": "payoff every 2-4 scenes, never predictable, never closing",
    },
    "N4 VALUE-DEBT": {
        "law": "Cialdini reciprocity subscription mechanics",
        "gate": "value lands before any ask; ask rides the payoff peak",
    },
    "N5 SILENCE-STING": {
        "law": "40Hz sub-bass pressure + the 0.3s silence drop",
        "gate": "key fact lands after total silence, once per video",
    },
}

ROLES = ("hook", "tease", "payoff", "value-debt", "silence-sting", "payoff+cua")

#: role -> spoken-line templates (front-loaded meaning; fit_words trims to maths).
#: Multiple templates per role so consecutive scenes never read identical.
#: RENDER MEMORY 1.1 fragment banks - complete-sentence composition.
#: open + mid + end word-counts must sum EXACTLY to n (the maths line).
#: Coverage per role: sums 5..9 reachable (shorts budgets 6-9, maths 7).
_FRAGMENTS: dict[str, dict[str, list[tuple[str, int]]]] = {
    "hook": {
        "open": [("stop scrolling", 2), ("look closer now", 3),
                 ("nobody shows you", 3), ("the first frame proves", 4)],
        "mid": [("on {topic}", 2), ("about {topic}", 2),
                ("this side of {topic}", 4)],
        "end": [("now.", 1), ("today.", 1), ("right now.", 2),
                ("and it bites.", 3), ("before it fades.", 3),
                ("and the room knows.", 4)],
    },
    "tease": {
        "open": [("the twist", 2), ("still unopened", 2),
                 ("most people miss", 3), ("the strange part", 3),
                 ("most people scroll past", 4)],
        "mid": [("in {topic}", 2), ("about {topic}", 2),
                ("around {topic}", 2)],
        "end": [("yet.", 1), ("next.", 1), ("has not landed.", 3),
                ("is still forming.", 3), ("stays one beat away.", 4)],
    },
    "payoff": {
        "open": [("proof lands", 2), ("the record", 2),
                 ("measured on camera", 3), ("here is the proof", 4)],
        "mid": [("{topic} works", 2), ("{topic} breaks it", 3),
                ("{topic} flips the count", 4)],
        "end": [("today.", 1), ("still.", 1), ("as claimed.", 2),
                ("on camera.", 2), ("in the real world.", 4),
                ("like skeptics said never.", 4)],
    },
    "value-debt": {
        "open": [("take it", 2), ("no gate", 2), ("keep the method", 3),
                 ("this channel pays debts", 4)],
        "mid": [("on {topic}", 2), ("for {topic}", 2),
                ("use {topic} today", 3)],
        "end": [("today.", 1), ("no charge.", 2), ("nothing held back.", 3),
                ("and pass it on.", 4)],
    },
    "silence-sting": {
        "open": [("look here", 2), ("hold this", 2), ("watch closely now", 3),
                 ("everything stops here", 3)],
        "mid": [("one fact", 2), ("this breath holds", 3),
                ("the next line carries", 4)],
        "end": [("now.", 1), ("here.", 1), ("the whole point.", 3),
                ("the entire weight.", 3), ("everything this means.", 3)],
    },
    "payoff+cua": {
        "open": [("debt paid", 2), ("loop closed", 2),
                 ("that was the payoff", 4), ("if this repaid you", 4)],
        "mid": [("and subscribe", 2), ("so subscribe now", 3),
                ("then follow along", 3)],
        "end": [("now.", 1), ("today.", 1), ("right now.", 2),
                ("subscribers see it first.", 4), ("the next digs deeper.", 4)],
    },
}



#: honest tail bank — appended only when the maths line demands more words
_TAILS: dict[str, list[str]] = {
    "hook": ["no hype", "just the reflex", "watch the first frame", "then decide"],
    "tease": ["hold on", "the reveal is close", "stay one more beat", "it compounds"],
    "payoff": ["measured", "not claimed", "on record", "with the numbers", "shown twice"],
    "value-debt": ["no strings", "no signup", "yours now", "use it tonight", "then repay nothing"],
    "silence-sting": ["total silence", "then it lands", "once", "only here", "feel the drop"],
    "payoff+cua": ["same time", "same channel", "no fluff", "only proofs", "subs see it first"],
}


@dataclass
class Storyboard:
    """A gated scene board + per-scene neuro metadata + the Fountain text."""

    topic: str
    title: str
    cohort: str
    seed: int
    maths: SceneMath
    report: ScriptReport
    #: per-scene neuro metadata, parallel to ``report.scenes``
    drivers: list[dict] = field(default_factory=list)
    fountain: str = ""
    card: str = ""

    @property
    def scenes(self) -> list[Scene]:
        return self.report.scenes

    @property
    def math_line(self) -> str:
        return maths_line(self.maths)

    def board(self) -> list[dict]:
        """Scene dicts with NEURO_DRIVER + retention_role metadata merged in."""
        out = []
        for scene, meta in zip(self.scenes, self.drivers):
            d = {
                "id": scene.id,
                "vo_line": scene.vo_line,
                "visual": scene.visual,
                "word_count": scene.word_count,
                "t_start": scene.t_start,
                "t_end": scene.t_end,
                "retention_role": meta["role"],
                "neuro_driver": meta["driver"],
                "law": meta["law"],
                "sfx": meta["sfx"],
                "match_cut": scene.match_cut,
            }
            if meta.get("silence_before_s"):
                d["silence_before_s"] = meta["silence_before_s"]
            out.append(d)
        return out

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "title": self.title,
            "cohort": self.cohort,
            "seed": self.seed,
            "maths": self.math_line,
            "scene_count": len(self.scenes),
            "scenes": self.board(),
            "fountain": self.fountain,
        }


# --------------------------------------------------------------------------
# scene planning — the N3 variable ratio schedule
# --------------------------------------------------------------------------


def _plan_roles(n: int, seed: int) -> list[dict]:
    """Assign role + driver + sfx per scene (fail-closed on the plan itself)."""
    if n < 2:
        raise ValueError("a storyboard needs at least 2 scenes (hook + payoff)")
    rng = random.Random(seed * 7919 + 13)
    roles: list[dict | None] = [None] * n
    roles[0] = {"role": "hook", "driver": "N1 THUMB-STOP", "sfx": "hit"}
    roles[-1] = {"role": "payoff+cua", "driver": "N4 VALUE-DEBT", "sfx": "hit"}

    # N5: the key fact lands after the 0.3s silence drop -> penultimate scene
    sting = n - 2 if n >= 3 else None
    if sting is not None and sting > 0:
        roles[sting] = {
            "role": "silence-sting",
            "driver": "N5 SILENCE-STING",
            "sfx": "riser",  # riser cuts to 0.3s silence, payoff lands after
            "silence_before_s": 0.3,
        }

    # N4: the free takeaway rides ~65% in, before the payoff peak
    debt = max(1, int(round(n * 0.65)))
    if debt >= n - 1:
        debt = n - 2 if n >= 3 else 1
    if roles[debt] is None:
        roles[debt] = {"role": "value-debt", "driver": "N4 VALUE-DEBT", "sfx": "heartbeat"}

    # N3: seeded variable ratio — reward every 2-4 scenes, never predictable
    gap = rng.randint(2, 4)
    since = 0
    for i in range(1, n - 1):
        if roles[i] is not None:
            continue
        since += 1
        nxt = roles[i + 1]
        nxt_is_reward = bool(nxt and nxt["role"] in ("payoff", "payoff+cua"))
        if since >= gap and not nxt_is_reward:
            roles[i] = {"role": "payoff", "driver": "N3 VARIABLE-RATIO", "sfx": "bass_drop"}
            gap = rng.randint(2, 4)
            since = 0
        else:
            roles[i] = {"role": "tease", "driver": "N3 VARIABLE-RATIO", "sfx": "sonar_ping"}
        # the scene right before a payoff carries the riser into it
        if nxt and nxt["role"] == "payoff" and roles[i]["sfx"] != "riser":
            roles[i]["sfx"] = "riser"

    # every slot filled — fail closed if the schedule broke
    for i, r in enumerate(roles):
        if r is None:
            raise GateFail([f"scene {i + 1} has no role — plan bug"])
        if r["driver"] not in NEURO_DRIVERS:
            raise GateFail([f"scene {i + 1} driver {r['driver']!r} not in the playbook"])
    return roles


def _compose_line(role: str, topic: str, n_words: int,
                  rng: random.Random) -> str:
    """RENDER MEMORY 1.1: complete sentence at EXACTLY n words.

    open + mid + end fragment counts must sum to n (fail-closed ValueError
    otherwise - never trim mid-sentence). Topics longer than 3 words are
    referred to as "this tale" (the topic lives in title/logline/board).
    Deterministic under the passed rng.
    """
    topic = (topic or "").strip().lower()
    if not topic:
        raise ValueError("empty topic")
    tlen = count_words(topic)
    sub = topic if tlen <= 3 else "this tale"
    # banks count "{topic}" as ONE word; a real subject costs tlen words
    # (the referer "this tale" costs 2)
    shift = (tlen if tlen <= 3 else 2) - 1
    bank = _FRAGMENTS.get(role)
    if bank is None:
        raise ValueError(f"no fragment bank for role {role!r}")
    opens, mids, ends = (list(bank["open"]), list(bank["mid"]),
                         list(bank["end"]))
    rng.shuffle(opens)
    rng.shuffle(mids)
    rng.shuffle(ends)
    for o, oc in opens:
        for m, mc in mids:
            me = (mc + shift) if "{topic}" in m else mc
            if me < 1:
                continue
            for e, ec in ends:
                if oc + me + ec == n_words:
                    line = f"{o} {m.replace('{topic}', sub)} {e}"
                    if count_words(line) != n_words:
                        raise ValueError(f"composer sum broken: {line!r}")
                    return line
    raise ValueError(
        f"cannot compose a complete {n_words}-word sentence for role "
        f"{role!r} (topic words {tlen}) - extend the fragment bank "
        f"(fail-closed, no padding)")

# --------------------------------------------------------------------------
# Fountain emission — screenplay + NEURO_DRIVER notes
# --------------------------------------------------------------------------


def _slug(scene_id: int, total: int, role: str) -> str:
    tag = role.upper().replace("+", " + ")
    return f"EXT. NEURAL DECK - SCENE {scene_id:02d} OF {total:02d} - {tag}"


def _fountain_text(sb_title: str, scenes: list[Scene], metas: list[dict],
                   cohort: str, seed: int) -> str:
    import datetime

    today = datetime.date.today().isoformat()
    out: list[str] = [
        f"Title: {sb_title}",
        "Credit: directed by",
        f"Author: Monarch Video Director ({CREATOR})",
        f"Draft date: {today}",
        f"Contact: {CONTACT}",
        "Notes: NEURO-PSYCHOLOGY PLAYBOOK N1-N5 - laws.md still applies",
        "",
    ]
    n = len(scenes)
    for scene, meta in zip(scenes, metas):
        out.append(_slug(scene.id, n, meta["role"]))
        out.append("")
        out.append("VOICEOVER (V.O.)")
        out.append(f"::{scene.visual}:: {scene.vo_line}")
        note = (
            f"[[NEURO_DRIVER: {meta['driver']} | role: {meta['role']} | "
            f"sfx: {meta['sfx']} | cohort: {cohort} | seed: {seed}"
        )
        if meta.get("silence_before_s"):
            note += f" | silence_before_s: {meta['silence_before_s']}"
        note += "]]"
        out.append(note)
        out.append(f"[[VO: {meta.get('prosody', '')} | beat: {meta.get('beat', '')}]]")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


# --------------------------------------------------------------------------
# the Hollywood ASCII box card
# --------------------------------------------------------------------------


def _wrap(text: str, width: int) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for w in words[1:]:
        if len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _box(lines: list[str], width: int, heavy: bool = False) -> str:
    l, r, tl, tr, bl, br = ("╔", "╗", "╠", "╣", "╚", "╝") if heavy else ("┌", "┐", "├", "┤", "└", "┘")
    hz = "═" if heavy else "─"
    out = [tl + hz * width + tr]
    for line in lines:
        out.append("│ " + line.ljust(width - 2)[: width - 2] + " │")
    out.append(bl + hz * width + br)
    return out


def render_box_card(sb: Storyboard) -> str:
    """The one-card storyboard: title, maths line, every scene in a box."""
    W = 76
    out: list[str] = []
    out += _box(
        _wrap(f"{sb.title} — NEURAL STORYBOARD", W - 2)
        + [f"Monarch Video Director · Neuro Playbook N1-N5 · cohort: {sb.cohort}"
           f" · seed: {sb.seed}"],
        W,
        heavy=True,
    )
    out += _box(_wrap(f"MATHS  {sb.math_line}", W - 2), W)
    for scene, meta in zip(sb.scenes, sb.drivers):
        head = (f"SCENE {scene.id:02d}  {scene.t_start:.1f}s-{scene.t_end:.1f}s  "
                f"ROLE: {meta['role'].upper()}")
        body = [
            head,
            f"DRIVER  {meta['driver']} — {meta['law']}",
            f"SFX     {meta['sfx'] or '(silence drop)'}"
            + (f"  + {meta['silence_before_s']}s silence" if meta.get('silence_before_s') else ""),
            f"VO      {scene.vo_line}  [{scene.word_count} words]",
            f"VISUAL  {scene.visual}",
            f"MATCH   {meta.get('match_cut') or '(hold — last scene)'}",
        ]
        lines: list[str] = []
        for b in body:
            lines += _wrap(b, W - 6) or [""]
        out += _box(lines, W)
    out += _box(_wrap("STOP — WAIT: perfect | improve · no render without HAAN", W - 2),
                W, heavy=True)
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# the plan
# --------------------------------------------------------------------------


def plan_storyboard(
    topic: str,
    *,
    length: float = 60.0,
    clip_s: float = 3.5,
    speaking_wps: float = 2.2,
    first_clip_s: float = 2.5,
    cohort: str = "genz",
    seed: int = 0,
    genre: str = "mystery",
) -> Storyboard:
    """Topic -> gated storyboard. Raises GateFail/ValueError — never ships broken."""
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("This is missing, could you provide it: topic.")
    cohort = cohort.strip().lower()
    if cohort not in COHORTS:
        raise ValueError(f"bad cohort {cohort!r}: use {' | '.join(COHORTS)}")
    from monarch.video.genres import GENRES, logline as _logline
    if genre not in GENRES:
        raise ValueError(f"unknown genre {genre!r}: use {' | '.join(GENRES)}")

    maths = compute_math(length, clip_s=clip_s, speaking_wps=speaking_wps,
                         first_clip_s=first_clip_s)
    rng = random.Random(seed * 104729 + 17)
    roles = _plan_roles(maths.scenes, seed)
    arc = story.plan_arc([r["role"] for r in roles])

    title = topic.upper()
    sb_logline = _logline(topic.strip().lower(), genre)
    scenes: list[Scene] = []
    metas: list[dict] = []
    for i, plan in enumerate(roles, 1):
        arc_i = arc[i - 1]
        draft = _compose_line(plan["role"], topic, maths.words_per_clip, rng)
        # STORY layer: partial payoff + re-hook before the full answer (N3.5)
        if arc_i.get("partial"):
            draft = story.partialize(draft, rng)
        if arc_i.get("rehook"):
            draft = story.rehook_into(draft, arc_i["rehook"])
        # HUMANIZE pass: AI-tell phrases die before the script exists
        # (cold open keeps its not-just shape — proven retention pattern)
        draft, hum = humanize(draft, hook=(plan["role"] == "hook"))
        # RENDER MEMORY 1.1: fit_words tokenizes punctuation away - the
        # complete sentence must END with its terminal mark on screen/VO
        if not draft.rstrip().endswith((".", "!", "?")):
            draft = draft.rstrip() + "."
        visual = (
            f"one focal {plan['role']} visual on {topic}, high contrast, "
            f"single subject, motion snap"
        )
        match = "pose and facing direction" if i < len(roles) else ""
        # compose the final spoken line: fit_words trims the draft to the maths
        spoken = fit_words(draft, maths.words_per_clip)
        # RENDER MEMORY 1.1: fit_words tokenizes punctuation away - the
        # complete sentence must end with its terminal mark (never ship a
        # clipped-looking VO line; miss #2)
        if not spoken.rstrip().endswith((".", "!", "?")):
            spoken = spoken.rstrip() + "."
        scenes.append(Scene(
            id=i,
            vo_line=spoken,
            visual=visual,
            word_count=maths.words_per_clip,
            retention_job=plan["role"],
            match_cut=match,
            sfx=plan["sfx"],
        ))
        metas.append({**plan, "law": NEURO_DRIVERS[plan["driver"]]["law"],
                      "match_cut": match,
                      "beat": arc_i["beat"],
                      "prosody": arc_i["prosody"],
                      "partial": arc_i.get("partial", False),
                      "rehook": arc_i.get("rehook", "")})

    # run the draft back through the real M3 gate — fail closed
    fountain = _fountain_text(title, scenes, metas, cohort, seed)
    sp = screenplay_from_text(fountain)
    report = build_script(
        beats_from_screenplay(sp),
        length,
        clip_s=clip_s,
        speaking_wps=speaking_wps,
        first_clip_s=first_clip_s,
        gate=True,
        title=title,
        byline=f"Monarch Video Director — {CREATOR}",
        source="monarch.video.director",
    )
    if len(report.scenes) != maths.scenes:  # pragma: no cover - gate covers this
        raise GateFail(["director beat count drifted from the maths line"])

    sb = Storyboard(
        topic=topic, title=title, cohort=cohort, seed=seed, maths=maths,
        report=report, drivers=metas, fountain=fountain,
    )
    sb.genre = genre
    sb.logline = sb_logline
    # RENDER MEMORY 1.1 (miss #2): the M3 gate re-parses the fountain and
    # its tokenizer DROPS terminal punctuation (the G4 quirk). The board
    # is the truth the VO/captions read - so the complete-sentence mark is
    # restored HERE, after the gate, before anything downstream. Word
    # counts are punctuation-blind, so the maths stays exact.
    for _sc in sb.scenes:
        if _sc.vo_line and not _sc.vo_line.rstrip().endswith((".", "!", "?")):
            _sc.vo_line = _sc.vo_line.rstrip() + "."

    sb.card = render_box_card(sb)
    return sb


def write_storyboard_files(sb: Storyboard, out_dir: str | Path) -> dict[str, Path]:
    """Write screenplay.fountain / board.json / storyboard.txt — returns paths."""
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    paths = {
        "fountain": d / "screenplay.fountain",
        "board": d / "board.json",
        "card": d / "storyboard.txt",
    }
    paths["fountain"].write_text(sb.fountain, encoding="utf-8")
    import json

    paths["board"].write_text(
        json.dumps({"title": sb.title, "maths": sb.math_line, "scenes": sb.board()},
                   indent=2),
        encoding="utf-8",
    )
    paths["card"].write_text(sb.card, encoding="utf-8")
    paths["av"] = d / "av_script.md"
    from monarch.video.genres import av_script as _av
    paths["av"].write_text(_av(sb.board(), sb.title), encoding="utf-8")
    validate_fountain(sb)
    return paths


def validate_fountain(sb) -> int:
    """G4/G9: the written fountain must RE-COUNT to the same word maths.

    Verify the verifier: parse every :: visual :: spoken line back out of
    the fountain text, count spoken words with the ENGINE tokenizer (never
    by hand), and demand it matches the board scene's vo_line count, beat
    for beat. Fail-closed: writer drift dies here, not on render day.
    """
    spoken = re.findall(r"^::.*?::\s*(.+)$", sb.fountain, re.M)
    rows = sb.board()
    if len(spoken) != len(rows):
        raise ValueError(
            f"fountain beats {len(spoken)} != board scenes {len(rows)} (G4)")
    for i, (line, row) in enumerate(zip(spoken, rows), 1):
        a = count_words(line)
        b = count_words(str(row["vo_line"]))
        if a != b:
            raise ValueError(
                f"scene {i}: fountain spoken words {a} != board {b} (G4)")
    return len(spoken)
