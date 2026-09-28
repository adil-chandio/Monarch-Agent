"""Deep forensic — competitor dossier -> viral DNA -> ranked ideas.

The "tabahi" pipeline (operator law: 15-20 viral videos, deeply analyzed):

1. The AGENT hunts (page-fetch/search tools) and saves a dossier:
   ``{"niche": ..., "videos": [{id,title,channel,views,likes,duration_s,
   transcript,thumb_note,date}, ...]}`` — transcripts via
   ``transcript-ingest`` (see the deep-forensic skill).
2. THIS module does the deep analysis, all real computation:

   * script DNA — speaking rate (Zack band 65-95 words/30s), hook openness
     (0.1s/N1 + curiosity markers), second-person density, proof density
     (numbers), sentence rhythm, CTA placement, title formula (T1-T8)
   * production DNA — duration distribution, engagement (likes/views),
     outlier multiplier vs channel median
   * topic clusters — what the niche actually rewards
   * ideas — 10 drafts built from the winning patterns (M2 feed; every
     draft still must pass ``monarch gate-idea`` — nothing bypasses gates)

Fail-closed: a dossier entry without views/transcript is rejected with the
exact problem; empty dossiers raise; every claim in the report carries its
N (sample size) — no single-video laws.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
import statistics
from dataclasses import dataclass, field
from pathlib import Path

from monarch.core.words import count_words, tokenize

MIN_VIDEOS = 3
#: hook window (N1: the first seconds decide everything)
HOOK_SECONDS = 12.0
#: Zack D. Films band — words per 30 seconds
ZACK_MIN, ZACK_MAX = 65.0, 95.0

_OPEN_MARKERS = (
    "secret", "secrets", "why", "how", "nobody", "hidden", "actually",
    "wrong", "truth", "until", "before", "never", "really", "what happens",
    "this is", "the most", "found", "found out",
)
_SECOND_PERSON = ("you", "your", "you're", "youre", "yours")
_CTA_WORDS = ("subscribe", "comment", "follow", "like and", "hit the",
              "notification", "check out the", "link in")

STOPWORDS = frozenset(
    "the a an and or but if then so of to in on for with at by from as is are was "
    "were be been being it its it's this that these those he she they them his her "
    "their you your yours i we us our me my mine what which who whom when where why "
    "how not no yes do does did done have has had having will would can could should "
    "shall may might must about into over under out up down off than too very just "
    "one two three all any both each few more most other some such only own same s t "
    "don now here there again further once because while during before after above "
    "below between through video videos like really going got get know think thing "
    "things actually lot bit even still way make made makes".split()
)


# ---------------------------------------------------------------------------
# dossier
# ---------------------------------------------------------------------------


@dataclass
class CompetitorVideo:
    """One competitor video, agent-fetched and normalized."""

    id: str
    title: str
    channel: str
    views: float
    duration_s: float
    transcript: str
    likes: float = 0.0
    thumb_note: str = ""
    date: str = ""

    def __post_init__(self) -> None:
        self.id = (self.id or "").strip()
        self.title = (self.title or "").strip()
        self.channel = (self.channel or "").strip()
        if not self.id:
            raise ValueError("dossier entry missing id")
        if not self.title:
            raise ValueError(f"{self.id}: dossier entry missing title")
        if not self.channel:
            raise ValueError(f"{self.id}: dossier entry missing channel")
        if self.views <= 0:
            raise ValueError(f"{self.id}: views must be > 0 (got {self.views})")
        if self.duration_s <= 0:
            raise ValueError(f"{self.id}: duration_s must be > 0")
        self.transcript = (self.transcript or "").strip()
        if not self.transcript:
            raise ValueError(f"{self.id}: no transcript — run transcript-ingest first")

    @classmethod
    def from_dict(cls, raw: dict) -> "CompetitorVideo":
        return cls(
            id=str(raw.get("id", "")),
            title=str(raw.get("title", "")),
            channel=str(raw.get("channel", "")),
            views=float(raw.get("views", 0)),
            duration_s=float(raw.get("duration_s", 0)),
            transcript=str(raw.get("transcript", "")),
            likes=float(raw.get("likes", 0)),
            thumb_note=str(raw.get("thumb_note", "")),
            date=str(raw.get("date", "")),
        )


def load_dossier(path: str | Path) -> tuple[str, list[CompetitorVideo]]:
    """dossier.json -> (niche, videos). Fail-closed on shape errors."""
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"This is missing, could you provide it: {p}")
    try:
        doc = json.loads(p.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        raise ValueError(f"corrupt dossier {p}: {e}") from e
    if not isinstance(doc, dict) or not isinstance(doc.get("videos"), list):
        raise ValueError("dossier must be {\"niche\": ..., \"videos\": [...]}")
    niche = str(doc.get("niche", "")).strip()
    if not niche:
        raise ValueError("dossier missing niche")
    videos = [CompetitorVideo.from_dict(v) for v in doc["videos"]]
    if len(videos) < MIN_VIDEOS:
        raise ValueError(f"dossier needs >= {MIN_VIDEOS} videos, has {len(videos)}")
    ids = [v.id for v in videos]
    if len(ids) != len(set(ids)):
        raise ValueError("dossier has duplicate video ids")
    return niche, videos


# ---------------------------------------------------------------------------
# per-video analysis — the script + production DNA
# ---------------------------------------------------------------------------


@dataclass
class VideoAnalysis:
    id: str
    title: str
    channel: str
    views: float
    duration_s: float
    # script DNA
    words: int
    wps: float
    words_per_30s: float
    in_zack_band: bool
    hook_text: str
    hook_words: int
    hook_open: bool
    hook_score: int
    second_person: int
    second_person_per_100: float
    numbers: int
    numbers_per_100: float
    sentences: int
    avg_sentence: float
    short_ratio: float  # share of sentences under 6 words
    cta_at: list[float]  # positions 0..1
    title_formula: str
    # production DNA
    engagement: float  # likes/views, 0 when likes unknown
    thumb_note: str
    date: str
    # W2 truth layer (defaults AFTER non-defaults; recency=1.0 = NO DATE, honest)
    age_days: float = -1.0
    recency: float = 1.0
    fresh_rank: float = 0.0

    @property
    def hook_label(self) -> str:
        return "OPEN" if self.hook_open else "closed"


def classify_title(title: str) -> str:
    """Heuristic T1-T8 mapping (growth_formulas.md). First match wins."""
    t = (title or "").lower()
    if re.search(r"\.\.\.(\s*)$", title.strip()) or t.endswith("…"):
        return "T1"
    if re.search(r"\d", t) and re.search(r"%|million|billion|\d+x", t):
        return "T2"
    if re.search(r"nobody (tells|shows|talks|knows)|never (tell|tells|told|shown|shows)", t):
        return "T3"
    if re.search(r"not what you|actually|myth|is wrong|aren't|aren t|are wrong", t):
        return "T4"
    if re.search(r"you('|')?(ve|re) |you have been|you are", t):
        return "T5"
    if re.search(r"secret|insider|trick|hidden", t):
        return "T6"
    if re.search(r"\bvs\b|versus", t):
        return "T7"
    if re.search(r"before it|last |only |disappear|gone|final", t):
        return "T8"
    return "T0"


def _hook(transcript: str, duration_s: float) -> tuple[str, int]:
    words = transcript.split()
    n = max(8, min(len(words), int(round(len(words) * HOOK_SECONDS / max(1.0, duration_s)))))
    return " ".join(words[:n]), n


def _cta_positions(transcript: str, duration_s: float) -> list[float]:
    low = transcript.lower()
    out: list[float] = []
    for w in _CTA_WORDS:
        idx = low.find(w)
        if idx >= 0:
            chars_per_s = max(1, len(low)) / max(1.0, duration_s)
            out.append(round(min(1.0, idx / max(1.0, len(low))), 2))
    return sorted(set(round(p, 2) for p in out))


#: freshness laws (temporal-RAG backed: score = a*quality + (1-a)*0.5**(age/HL),
#: sensitivity says keep a <= 0.7; HL=105d sits between fast news (14d) and
#: slow taste drift (150d) — right for evergreen-leaning YouTube DNA)
HALF_LIFE_DAYS = 105.0
RECENCY_ALPHA = 0.7
LINKROT_AT = 2.0  # age > 2x half-life = link-rot risk flag


def _parse_date(date: str):
    d = (date or "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%SZ", "%d-%m-%Y"):
        try:
            return datetime.strptime(d, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def recency_factor(date: str, *, today=None, half_life: float = HALF_LIFE_DAYS):
    """0..1 recency weight via half-life decay; None when NO DATE (honest)."""
    dt = _parse_date(date)
    if dt is None:
        return None
    now = today or datetime.now(timezone.utc)
    age = max(0.0, (now - dt).total_seconds() / 86400.0)
    return 0.5 ** (age / max(1.0, half_life))


def analyze_video(v: CompetitorVideo, *, today=None,
                  half_life: float = HALF_LIFE_DAYS) -> VideoAnalysis:
    words = count_words(v.transcript)
    wps = words / max(1.0, v.duration_s)
    wp30 = wps * 30.0
    hook_text, hook_words = _hook(v.transcript, v.duration_s)
    low_hook = hook_text.lower()
    score = sum(1 for m in _OPEN_MARKERS if m in low_hook)
    if low_hook.rstrip().endswith(("...", "?", "…")):
        score += 2
    if "?" in low_hook:
        score += 1
    second_person = sum(low_hook.count(" " + w) for w in _SECOND_PERSON)
    # second person across the whole transcript (per-100-words density)
    low_all = v.transcript.lower()
    sp_all = sum(low_all.count(" " + w) for w in _SECOND_PERSON)
    nums = sum(1 for t in tokenize(v.transcript) if any(c.isdigit() for c in t))
    sentences = [s for s in re.split(r"[.!?]+", v.transcript) if s.strip()]
    lens = [count_words(s) for s in sentences]
    rec = recency_factor(v.date, today=today, half_life=half_life)
    rec_val = 1.0 if rec is None else round(rec, 4)
    dt = _parse_date(v.date)
    now0 = today or datetime.now(timezone.utc)
    age = round(max(0.0, (now0 - dt).total_seconds() / 86400.0), 1) if dt else -1.0
    return VideoAnalysis(
        id=v.id, title=v.title, channel=v.channel, views=v.views,
        duration_s=v.duration_s,
        age_days=age, recency=rec_val,
        words=words, wps=round(wps, 2), words_per_30s=round(wp30, 1),
        in_zack_band=ZACK_MIN <= wp30 <= ZACK_MAX,
        hook_text=hook_text, hook_words=hook_words,
        hook_open=score >= 2, hook_score=score,
        second_person=sp_all, second_person_per_100=round(sp_all * 100 / max(1, words), 1),
        numbers=nums, numbers_per_100=round(nums * 100 / max(1, words), 1),
        sentences=len(sentences),
        avg_sentence=round(statistics.fmean(lens), 1) if lens else 0.0,
        short_ratio=round(sum(1 for n in lens if n < 6) / max(1, len(lens)), 2) if lens else 0.0,
        cta_at=_cta_positions(v.transcript, v.duration_s),
        title_formula=classify_title(v.title),
        engagement=round(v.likes / v.views, 4) if v.likes > 0 else 0.0,
        thumb_note=v.thumb_note, date=v.date,
    )


# ---------------------------------------------------------------------------
# dossier analysis — patterns, clusters, ideas
# ---------------------------------------------------------------------------


@dataclass
class DossierReport:
    niche: str
    video_count: int
    channel_count: int
    analyses: list[VideoAnalysis] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    clusters: list[tuple[str, int]] = field(default_factory=list)
    ideas: list[dict] = field(default_factory=list)
    median_views: float = 0.0
    outlier_x: float = 1.0
    zack_share: float = 0.0
    freshness: dict = field(default_factory=dict)

    @property
    def status(self) -> str:
        return "learned" if len(self.patterns) >= 3 else "thin"


def _top_terms(texts: list[str], k: int = 8) -> list[tuple[str, int]]:
    freq: dict[str, int] = {}
    for t in texts:
        for w in tokenize(t.lower()):
            if len(w) > 3 and w not in STOPWORDS and not w.isdigit():
                freq[w] = freq.get(w, 0) + 1
    return sorted(freq.items(), key=lambda kv: -kv[1])[:k]


def _median(vals: list[float]) -> float:
    return statistics.median(vals) if vals else 0.0


def _mean(vals: list[float]) -> float:
    return statistics.fmean(vals) if vals else 0.0


def _build_ideas(niche: str, analyses: list[VideoAnalysis],
                 clusters: list[tuple[str, int]],
                 freshness_note: str = "") -> list[dict]:
    """10 idea drafts from the winning patterns — M2 feed, gates still apply."""
    ideas: list[dict] = []
    top_formula = _mode([a.title_formula for a in analyses if a.title_formula != "T0"]) or "T1"
    terms = [t for t, _ in clusters] or [niche]
    open_hooks = sum(1 for a in analyses if a.hook_open)
    hook_style = "open loop + second person" if open_hooks >= len(analyses) / 2 else "forensic calm"
    for i in range(10):
        a = terms[i % len(terms)]
        b = terms[(i * 3 + 1) % len(terms)]
        if i % 3 == 0:
            title = f"Why {a} hides {b} nobody shows..."
        elif i % 3 == 1:
            title = f"The {a} secret insiders never explain ({b} proof)"
        else:
            title = f"You have been getting {a} wrong the whole time"
        ideas.append({
            "title": title[:70],
            "formula": classify_title(title),
            "hook": f"{hook_style} open on {a} — first line stops mid-reveal, "
                    f"proof with {b} lands before scene 3",
            "itch": "unfinished loop + status secret",
            "evidence": f"'{a}' drives this niche (cluster rank {i % len(terms) + 1}); "
                        f"pattern from {len(analyses)} analyzed videos"
                        + (f"; {freshness_note}" if freshness_note else ""),
        })
    ideas[0]["formula"] = top_formula
    return ideas


def _mode(vals: list[str]) -> str:
    return statistics.mode(vals) if vals else ""


def analyze_dossier(niche: str, videos: list[CompetitorVideo], *,
                    today=None, half_life: float = HALF_LIFE_DAYS) -> DossierReport:
    analyses = [analyze_video(v, today=today, half_life=half_life) for v in videos]
    views = [v.views for v in videos]
    med = _median(views)
    peak = max(views) if views else 0.0
    report = DossierReport(
        niche=niche,
        video_count=len(videos),
        channel_count=len({v.channel for v in videos}),
        analyses=analyses,
        median_views=med,
        outlier_x=round(peak / med, 1) if med > 0 else 1.0,
        zack_share=round(sum(1 for a in analyses if a.in_zack_band) / len(analyses), 2),
    )

    # W2 truth layer: fresh_rank = 0.7*engagement + 0.3*recency (a=0.7 capped)
    dated = [a for a in analyses if a.age_days >= 0]
    if views:
        vmax = max(views) or 1.0
        for a in analyses:
            a.fresh_rank = round(RECENCY_ALPHA * (a.views / vmax)
                                 + (1 - RECENCY_ALPHA) * a.recency, 4)
    stale_ids = [a.id for a in analyses
                 if a.age_days > LINKROT_AT * half_life]
    factors = [a.recency for a in dated] or [1.0]
    ages = [a.age_days for a in dated] or [0.0]
    report.freshness = {
        "half_life_days": half_life,
        "alpha_engagement": RECENCY_ALPHA,
        "dated": f"{len(dated)}/{len(analyses)}",
        "median_age_days": round(statistics.median(ages), 1) if dated else None,
        "median_recency": round(statistics.median(factors), 3),
        "linkrot_risk_ids": stale_ids,
        "note": ("recency=1.0 rows carry NO DATE — honest neutral, not a claim"
                 if len(dated) < len(analyses) else ""),
    }
    if dated:
        rot = f"; LINK-ROT RISK {len(stale_ids)} (age > 2x HL)" if stale_ids else ""
        report.patterns = []  # filled below; freshness line appended after build
        _fresh_line = (f"freshness: median evidence age {statistics.median(ages):.0f}d "
                       f"(HL {half_life:.0f}d), {len(dated)}/{len(analyses)} dated, "
                       f"median recency {statistics.median(factors):.2f}{rot}")
    else:
        _fresh_line = ""

    # top vs bottom median split — the same honest JUDGE step as `learn`
    order = sorted(analyses, key=lambda a: -a.views)
    top = order[: max(1, len(order) // 2)]
    bot = order[len(order) // 2:] or order

    p: list[str] = []
    # script pace
    t30, b30 = _mean([a.words_per_30s for a in top]), _mean([a.words_per_30s for a in bot])
    if abs(t30 - b30) >= 5:
        better = "faster" if t30 > b30 else "slower"
        p.append(f"top performers speak {better} ({t30:.0f} vs {b30:.0f} words/30s) "
                 f"— Zack band 65-95; niche median {report.zack_share:.0%} in band (N={len(analyses)})")
    # hooks
    t_open = sum(1 for a in top if a.hook_open)
    p.append(f"hooks: {t_open}/{len(top)} top videos open with an unresolved loop "
             f"vs {sum(1 for a in bot if a.hook_open)}/{len(bot)} bottom (N1 evidence)")
    # second person
    tsp, bsp = _mean([a.second_person_per_100 for a in top]), _mean([a.second_person_per_100 for a in bot])
    if abs(tsp - bsp) >= 0.3:
        p.append(f"second-person density: top {tsp:.1f}/100w vs bottom {bsp:.1f}/100w — "
                 "direct address correlates with views")
    # proof density
    tn, bn = _mean([a.numbers_per_100 for a in top]), _mean([a.numbers_per_100 for a in bot])
    if abs(tn - bn) >= 0.3:
        p.append(f"proof density (numbers/100w): top {tn:.1f} vs bottom {bn:.1f} (T2 evidence)")
    # durations
    td, bd = _mean([a.duration_s for a in top]), _mean([a.duration_s for a in bot])
    if abs(td - bd) >= 30:
        p.append(f"runtime: top avg {td:.0f}s vs bottom {bd:.0f}s")
    # titles
    from collections import Counter

    formulas = Counter(a.title_formula for a in analyses if a.title_formula != "T0")
    if formulas:
        dom, cnt = formulas.most_common(1)[0]
        p.append(f"dominant title formula: {dom} ({cnt}/{len(analyses)} videos)")
    # CTA placement
    late_cta = [a for a in analyses if a.cta_at and min(a.cta_at) >= 0.5]
    if late_cta:
        p.append(f"{len(late_cta)}/{len(analyses)} videos place first CTA after 50% "
                 "(N4: value-debt before the ask)")
    if _fresh_line:
        p.append(_fresh_line)
    report.patterns = p

    report.clusters = _top_terms(
        [f"{v.title} {v.transcript[:1200]}" for v in videos]
    )
    fresh_note = ""
    if dated:
        fresh_note = (f"evidence freshness: median age "
                      f"{statistics.median(ages):.0f}d (HL {half_life:.0f}d)"
                      + (f"; {len(stale_ids)} stale" if stale_ids else ""))
    report.ideas = _build_ideas(niche, analyses, report.clusters,
                                freshness_note=fresh_note)
    return report


# ---------------------------------------------------------------------------
# rendering
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


def _box(lines: list[str], width: int, heavy: bool = False) -> list[str]:
    tl, tr, bl, br = ("╔", "╗", "╚", "╝") if heavy else ("┌", "┐", "└", "┘")
    hz = "═" if heavy else "─"
    out = [tl + hz * width + tr]
    for line in lines:
        out.append("│ " + line.ljust(width - 2)[: width - 2] + " │")
    out.append(bl + hz * width + br)
    return out


def report_card(r: DossierReport) -> str:
    W = 76
    out: list[str] = []
    out += _box(_wrap(
        f"💀 DEEP FORENSIC — {r.niche.upper()}", W - 2)
        + [f"{r.video_count} videos · {r.channel_count} channels · "
           f"median {r.median_views:,.0f} views · peak {r.outlier_x}x median"],
        W, heavy=True)
    for a in r.analyses:
        body = [
            f"{a.channel} — {a.title}",
            f"views {a.views:,.0f} · {a.duration_s:.0f}s · eng {a.engagement:.2%}"
            + (f" · {a.date}" if a.date else ""),
            f"SCRIPT {a.words}w | {a.words_per_30s:.0f} w/30s "
            f"{'✓ Zack band' if a.in_zack_band else '✗ off-band'} | "
            f"hook {a.hook_label}({a.hook_score}) | you/100w {a.second_person_per_100} | "
            f"nums/100w {a.numbers_per_100}",
            f"FORMULA {a.title_formula} | CTA @ "
            f"{', '.join(f'{p:.0%}' for p in a.cta_at) or '—'} | "
            f"sent {a.sentences} (short {a.short_ratio:.0%})",
        ]
        lines: list[str] = []
        for b in body:
            lines += _wrap(b, W - 6)
        out += _box(lines, W)
    out += _box(["PATTERNS (N=%d)" % r.video_count]
                + [f"{i}) {p}" for i, p in enumerate(r.patterns, 1)], W)
    out += _box(["TOPIC CLUSTERS"] + _wrap(", ".join(f"{t}({n})" for t, n in r.clusters), W - 4), W)
    out += _box(["IDEA DRAFTS (gate before M2 — nothing bypasses gates)"]
                + [f"{i}) [{d['formula']}] {d['title']}" for i, d in enumerate(r.ideas, 1)], W)
    out += _box(["STOP — pick an idea number → gate-idea → M2 → make-short"], W, heavy=True)
    return "\n".join(out) + "\n"


def write_report(r: DossierReport, out_dir: str | Path) -> dict[str, Path]:
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    paths = {
        "report": d / "deep_forensic_report.txt",
        "json": d / "deep_forensic.json",
        "ideas": d / "ideas.json",
    }
    paths["report"].write_text(report_card(r), encoding="utf-8")
    paths["json"].write_text(json.dumps({
        "niche": r.niche,
        "video_count": r.video_count,
        "channel_count": r.channel_count,
        "median_views": r.median_views,
        "outlier_x": r.outlier_x,
        "zack_share": r.zack_share,
        "freshness": r.freshness,
        "patterns": r.patterns,
        "clusters": r.clusters,
        "analyses": [a.__dict__ for a in r.analyses],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["ideas"].write_text(json.dumps(r.ideas, indent=2, ensure_ascii=False),
                              encoding="utf-8")
    return paths


def run_deep_forensic(dossier_path: str | Path, out_dir: str | Path, *,
                      half_life: float = HALF_LIFE_DAYS) -> DossierReport:
    niche, videos = load_dossier(dossier_path)
    report = analyze_dossier(niche, videos, half_life=half_life)
    write_report(report, out_dir)
    return report
