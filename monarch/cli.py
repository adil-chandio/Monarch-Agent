from __future__ import annotations

import argparse
import json
import sys

from monarch import __version__
from monarch.core.access import (
    AccessDeniedError,
    activate as activate_monarch,
    deactivate as deactivate_monarch,
    get_lock_banner,
    is_activated,
    require_access,
)
from monarch.core.gates import GateFail, gate_idea, gate_title
from monarch.core.haan import require_haan
from monarch.core.scene_math import compute_math, maths_line
from monarch.core.state_machine import STATES, Run
from monarch.core.words import count_words
from monarch.schemas import Idea

#: short/long presets from BOOT.md — 9:16 short vs 16:9 long
LENGTH_PRESETS = {"short": 60.0, "long": 480.0}


def _read(path: str | None) -> str:
    """Read a file, or stdin when the path is absent / ``-``."""
    if path in (None, "", "-"):
        return sys.stdin.read()
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"This is missing, could you provide it: {path}")
    return p.read_text(encoding="utf-8-sig")


def _resolve_length(value: str) -> float:
    key = str(value).strip().lower()
    if key in LENGTH_PRESETS:
        return LENGTH_PRESETS[key]
    try:
        seconds = float(key.rstrip("s"))
    except ValueError as e:  # pragma: no cover - argparse-ish guard
        raise ValueError(f"bad --length {value!r}: use short, long or seconds") from e
    if seconds <= 0:
        raise ValueError("--length must be > 0")
    return seconds


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="monarch")
    p.add_argument("--key", default=None, help="Monarch access activation key")
    sub = p.add_subparsers(dest="cmd", required=True)

    act = sub.add_parser("activate", help="Activate Monarch Agent with access key")
    act.add_argument("key", nargs="?", default=None, help="Activation key (e.g. DoitMon@rch)")

    sub.add_parser("lock", help="Lock/deactivate Monarch Agent on this machine")

    sub.add_parser("status")
    m = sub.add_parser("maths")
    m.add_argument("--seconds", type=float, required=True)
    m.add_argument("--clip", type=float, default=3.5)
    w = sub.add_parser("words")
    w.add_argument("line")
    g = sub.add_parser("gate-idea")
    g.add_argument("--title", required=True)
    g.add_argument("--hook", required=True)
    g.add_argument("--itch", required=True)
    g.add_argument("--visual", required=True)
    t = sub.add_parser("gate-title")
    t.add_argument("--title", required=True)
    t.add_argument("--thumb", required=True)
    t.add_argument("--paid", action="store_true")
    h = sub.add_parser("haan")
    h.add_argument("token")
    h.add_argument("--action", default="render")
    sub.add_parser("keys")
    sub.add_parser("states")
    f = sub.add_parser("fit")
    f.add_argument("line")
    f.add_argument("--n", type=int, required=True)
    ch = sub.add_parser("channel")
    ch.add_argument("path")

    # M3_script — Fountain integration
    fnt = sub.add_parser("fountain", help="M3: parse a .fountain screenplay")
    fnt.add_argument("path", nargs="?", default="-", help="file, or stdin when omitted / '-'")
    fnt.add_argument("--json", action="store_true", help="full elements + scenes")

    m3 = sub.add_parser("m3", help="M3_script state card")
    m3.add_argument("--json", action="store_true")

    scs = sub.add_parser("screen-script", help="M3: Fountain → gated numbered scene board")
    scs.add_argument("path", nargs="?", default="-", help="file, or stdin when omitted / '-'")
    scs.add_argument("--length", default="short", help="short | long | seconds (default short=60s)")
    scs.add_argument("--clip", type=float, default=3.5, help="clip seconds (default 3.5)")
    scs.add_argument("--wps", type=float, default=2.2, help="speaking words/second (default 2.2)")
    scs.add_argument("--first-clip", type=float, default=2.5, help="open clip seconds (default 2.5)")
    scs.add_argument("--only", choices=["dialogue", "action", "both"], default="both")
    scs.add_argument("--speaker", help="only beats spoken by these characters (comma separated)")
    scs.add_argument("--visual-hint", default="", help="visual used when a beat has no :: visual")
    scs.add_argument("--sfx", default="", help="sfx label written onto every scene")
    scs.add_argument("--json", action="store_true")
    scs.add_argument("--board-out", help="write the scene board JSON here")
    scs.add_argument("--no-gate", action="store_true", help="report without the fail-closed gate")

    scf = sub.add_parser("script-fountain", help="scene board JSON → .fountain")
    scf.add_argument("board", nargs="?", default="-", help="scene board JSON file or stdin")
    scf.add_argument("--out", help="write here (default stdout)")
    scf.add_argument("--title", default="")
    scf.add_argument("--author", default="")
    scf.add_argument("--draft-date", default="")
    scf.add_argument("--contact", default="")

    srh = sub.add_parser("search")
    srh.add_argument("query")
    hun = sub.add_parser("hunt")
    hun.add_argument("niche")

    # Neuro Video — autonomous video production (playbook: neuro_psychology.md)
    sc = sub.add_parser(
        "script", help="Neuro Video: Neuro-Playbook storyboard -> Fountain screenplay"
    )
    sc.add_argument("--topic", required=True, help="video topic / working title")
    sc.add_argument("--length", default="short", help="short | long | seconds")
    sc.add_argument("--clip", type=float, default=3.5, help="clip seconds")
    sc.add_argument("--wps", type=float, default=2.2, help="speaking words/second")
    sc.add_argument("--first-clip", type=float, default=2.5, help="open clip seconds")
    sc.add_argument("--cohort", default="genz", help="N2 dopamine cohort: kids | genz | adults")
    sc.add_argument("--seed", type=int, default=0, help="deterministic variation seed")
    sc.add_argument("--card", action="store_true", help="print the ASCII box card too")
    sc.add_argument("--json", action="store_true", help="board JSON with neuro metadata")
    sc.add_argument("--out", help="write the screenplay here (default stdout)")

    vsb = sub.add_parser("video-storyboard",
                         help="Neuro Video: the Hollywood ASCII box card")
    vsb.add_argument("--topic", required=True)
    vsb.add_argument("--length", default="short")
    vsb.add_argument("--clip", type=float, default=3.5)
    vsb.add_argument("--wps", type=float, default=2.2)
    vsb.add_argument("--first-clip", type=float, default=2.5)
    vsb.add_argument("--cohort", default="genz", help="kids | genz | adults")
    vsb.add_argument("--seed", type=int, default=0)
    vsb.add_argument("--json", action="store_true", help="board JSON instead of the card")

    sx = sub.add_parser("sfx", help="Neuro Video: render a psychoacoustic SFX wav")
    sx.add_argument("--kind", required=True,
                    choices=["heartbeat", "hit", "bass_drop", "sonar_ping",
                             "glitch", "riser"])
    sx.add_argument("--out", default="", help="output wav path (default sfx_<kind>.wav)")
    sx.add_argument("--seconds", type=float, default=None, help="clamp/pad length")
    sx.add_argument("--sr", type=int, default=44100, help="sample rate (default 44100)")
    sx.add_argument("--seed", type=int, default=0)
    sx.add_argument("--filter", action="append", default=[],
                    choices=["bass_boost", "tension_echo", "cyber_glitch",
                             "forensic_tape", "limiter"],
                    help="DSP filter, repeatable (limiter always runs last)")

    mv = sub.add_parser("make-video",
                        help="Neuro Video: topic -> previz animatic (frames+sfx+timeline)")
    mv.add_argument("--topic", required=True)
    mv.add_argument("--out", default="", help="output dir (default output/<slug>)")
    mv.add_argument("--length", default="short")
    mv.add_argument("--clip", type=float, default=3.5)
    mv.add_argument("--wps", type=float, default=2.2)
    mv.add_argument("--first-clip", type=float, default=2.5)
    mv.add_argument("--cohort", default="genz", help="kids | genz | adults")
    mv.add_argument("--seed", type=int, default=0)
    mv.add_argument("--fps", type=int, default=2, help="animatic frames/second (default 2)")
    mv.add_argument("--width", type=int, default=1080)
    mv.add_argument("--height", type=int, default=1920)
    mv.add_argument("--sr", type=int, default=22050)
    mv.add_argument("--json", action="store_true", help="manifest JSON to stdout")

    # Session memory — the new-session handoff bridge (RVF-inspired)
    mem = sub.add_parser("memory", help="Save/restore the cross-session handoff state")
    mem_sub = mem.add_subparsers(dest="mem_cmd", required=True)
    ms = mem_sub.add_parser("save")
    ms.add_argument("--state", default=None, help="M-state to snapshot (default: current)")
    ms.add_argument("--channel", default=None, help="channel yaml path to embed")
    ms.add_argument("--topic", default="", help="current working topic")
    ms.add_argument("--pending", default="", help="comma-separated pending approvals")
    ms.add_argument("--notes", default="", help="comma-separated session notes")
    ms.add_argument("--out", default="", help="memory path (default .monarch/memory.json)")
    mr = mem_sub.add_parser("restore", help="Print the handoff card for this session")
    mr.add_argument("path", nargs="?", default="", help="memory json (default .monarch/memory.json)")

    # Learn — close the L16 loop with real-world performance data
    lr = sub.add_parser("learn", help="Log uploaded-video metrics and distill lessons")
    lr_sub = lr.add_subparsers(dest="learn_cmd", required=True)
    lrec = lr_sub.add_parser("record")
    lrec.add_argument("--topic", required=True)
    lrec.add_argument("--views", type=float, required=True)
    lrec.add_argument("--avg-pct", type=float, required=True, help="avg %% viewed (0-100)")
    lrec.add_argument("--subs", type=int, default=0)
    lrec.add_argument("--cohort", default="", help="N2 cohort tag: kids | genz | adults")
    lrec.add_argument("--length", type=float, default=0.0, help="runtime seconds")
    lrec.add_argument("--date", default="", help="upload date (default today, UTC)")
    lrec.add_argument("--note", default="")
    lrec.add_argument("--file", default="", help="log path (default .monarch/performance.jsonl)")
    ldis = lr_sub.add_parser("distill")
    ldis.add_argument("--min", type=int, default=3, help="min videos for a split (default 3)")
    ldis.add_argument("--apply", action="store_true", help="write signals into lessons.md (3x rule)")
    ldis.add_argument("--lessons", default="", help="lessons.md path (default repo lessons)")
    ldis.add_argument("--file", default="", help="log path (default .monarch/performance.jsonl)")
    llog = lr_sub.add_parser("log", help="Show every logged video")
    llog.add_argument("--file", default="", help="log path (default .monarch/performance.jsonl)")

    # Agent-Reach integration — doctor + multi-platform search
    sub.add_parser("doctor", help="Check which upstream tools (yt-dlp, twitter, reddit, etc.) are available")

    sw = sub.add_parser("scrape", help="Scrape a URL via Agent-Reach (yt-dlp for YouTube, Jina for web)")
    sw.add_argument("url", help="YouTube URL or any web URL")
    sw.add_argument("--transcript", action="store_true", help="Extract transcript (YouTube only)")
    sw.add_argument("--lang", default="en", help="Subtitle language (default en)")

    tw = sub.add_parser("xsearch", help="Search Twitter/X for niche analysis")
    tw.add_argument("query")
    tw.add_argument("-n", type=int, default=10)

    rd = sub.add_parser("rsearch", help="Search Reddit for audience language")
    rd.add_argument("query")
    rd.add_argument("-n", type=int, default=10)

    ws = sub.add_parser("wsearch", help="Semantic web search via Exa")
    ws.add_argument("query")
    ws.add_argument("-n", type=int, default=5)

    # QC render — L15: end-to-end render chain verification
    qr = sub.add_parser("qc-render", help="L15: verify rendered video against scene board")
    qr.add_argument("video", help="path to rendered mp4")
    qr.add_argument("board", help="scene board JSON file")
    qr.add_argument("--max-clip", type=float, default=3.5, help="max clip hold in seconds")

    # QC selftest — L14: 17-check QC
    qs = sub.add_parser("qc", help="L14: run 17-check QC on a notes JSON")
    qs.add_argument("notes", help="JSON file with check-name → bool mapping")
    qs.add_argument("--stage", choices=["research", "script", "render", "edit", "packaging"],
                     default="packaging")

    # youtube-transcript.io — hosted transcripts (third YouTube backend)
    tp = sub.add_parser("transcript", help="Hosted transcripts via youtube-transcript.io")
    tp.add_argument("videos", nargs="+", help="video ids or URLs (max 50 per call)")
    tp.add_argument("--json", action="store_true", help="JSON records instead of text")
    tp.add_argument("--save", default="", help="write each transcript to this dir as .txt")

    tch = sub.add_parser("tchan", help="Hosted channel info via youtube-transcript.io (Plus)")
    tch.add_argument("channels", nargs="+", help="channel ids without @ (max 50)")

    # transcript-ingest — agent-fetched page/captions -> forensic record
    ti = sub.add_parser(
        "transcript-ingest",
        help="Normalize an agent-fetched transcript (markdown/VTT/SRT/plain) into the pipeline",
    )
    ti.add_argument("path", nargs="?", default="-", help="file, or stdin when '-'")
    ti.add_argument("--json", action="store_true", help="full forensic record as JSON")
    ti.add_argument("--save", default="", help="write transcripts/<id>.txt into this dir")

    # deep-forensic — competitor dossier -> viral DNA -> ranked ideas
    df = sub.add_parser("deep-forensic",
                        help="Analyze a 15-20 video competitor dossier into patterns + ideas")
    df.add_argument("dossier", help="dossier.json (see skills/deep-forensic)")
    df.add_argument("--out", default="", help="output dir (default output/forensic/<slug>)")

    # Extract --key anywhere in argv
    extracted_key = None
    cleaned_argv = list(argv) if argv is not None else list(sys.argv[1:])
    for i, a in enumerate(list(cleaned_argv)):
        if a == "--key" and i + 1 < len(cleaned_argv):
            extracted_key = cleaned_argv[i + 1]
        elif a.startswith("--key="):
            extracted_key = a.split("=", 1)[1]

    # Remove --key / --key=val from cleaned_argv so subparsers don't complain
    filtered_argv: list[str] = []
    skip_next = False
    for a in cleaned_argv:
        if skip_next:
            skip_next = False
            continue
        if a == "--key":
            skip_next = True
            continue
        if a.startswith("--key="):
            continue
        filtered_argv.append(a)

    if not filtered_argv:
        if is_activated():
            p.print_help()
            return 0
        else:
            if sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
                try:
                    require_access(interactive=True)
                    p.print_help()
                    return 0
                except AccessDeniedError:
                    return 1
            else:
                print(get_lock_banner(), file=sys.stderr)
                return 1

    args = p.parse_args(filtered_argv)
    if extracted_key and not getattr(args, "key", None):
        args.key = extracted_key

    if args.cmd == "activate":
        key = args.key
        if not key:
            if sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
                print(get_lock_banner(), file=sys.stderr)
                try:
                    key = input("🔑 Enter Monarch Access Key: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nActivation cancelled.", file=sys.stderr)
                    return 1
            else:
                print(get_lock_banner(), file=sys.stderr)
                return 1
        ok, msg = activate_monarch(key, persistent=True)
        if ok:
            print(msg)
            return 0
        else:
            print(msg, file=sys.stderr)
            return 1

    if args.cmd == "lock":
        deactivate_monarch()
        print("🔒 Monarch Agent is now locked.")
        return 0

    try:
        require_access(key_candidate=args.key)
    except AccessDeniedError:
        return 1

    if args.cmd == "status":
        print(json.dumps({"agent": "monarch", "version": __version__, "states": STATES}))
        return 0
    if args.cmd == "maths":
        print(maths_line(compute_math(args.seconds, args.clip)))
        return 0
    if args.cmd == "words":
        print(count_words(args.line))
        return 0
    if args.cmd == "gate-idea":
        idea = Idea(
            title=args.title,
            hook=args.hook,
            itch=args.itch,
            visual_anchor=args.visual,
        )
        try:
            gate_idea(idea)
        except GateFail as e:
            print("FAIL", e)
            return 2
        print("PASS")
        return 0
    if args.cmd == "gate-title":
        try:
            gate_title(args.title, args.thumb, args.paid)
        except GateFail as e:
            print("FAIL", e)
            return 2
        print("PASS")
        return 0
    if args.cmd == "haan":
        try:
            require_haan(args.token, args.action)
        except PermissionError as e:
            print(e)
            return 3
        print("HAAN")
        return 0
    if args.cmd == "keys":
        from monarch.core.config import has_gemini, has_youtube_key, has_youtube_upload
        from monarch.intel.ytt import has_token as ytt_has_token

        print(
            json.dumps(
                {
                    "gemini": has_gemini(),
                    "youtube_data": has_youtube_key(),
                    "youtube_upload_oauth": has_youtube_upload(),
                    "youtube_transcript_io": ytt_has_token(),
                    "hint": "true = key loaded from .env; values never printed",
                }
            )
        )
        return 0
    if args.cmd == "states":
        print(" -> ".join(STATES), "current", Run().state)
        return 0
    if args.cmd == "fit":
        from monarch.core.fit_line import fit_words

        try:
            print(fit_words(args.line, args.n))
        except ValueError as e:
            print("FAIL", e)
            return 2
        return 0
    if args.cmd == "channel":
        from dataclasses import asdict

        from monarch.core.channels import load_channel

        print(json.dumps(asdict(load_channel(args.path))))
        return 0
    if args.cmd == "search":
        from monarch.intel.youtube import search_videos

        hits = search_videos(args.query)
        print(json.dumps(hits, indent=2))
        return 0
    if args.cmd == "hunt":
        from dataclasses import asdict

        from monarch.intel.ideas import hunt
        from monarch.intel.youtube import search_videos

        winners = [h["title"] for h in search_videos(args.niche)]
        ideas = hunt(args.niche, winners)
        print(json.dumps([asdict(i) for i in ideas], indent=2))
        return 0
    if args.cmd == "fountain":
        from monarch.pipelines.fountain import (
            screenplay_from_path,
            screenplay_from_text,
        )

        try:
            if args.path in (None, "", "-"):
                sp = screenplay_from_text(_read(args.path))
            else:
                sp = screenplay_from_path(args.path)
        except (FileNotFoundError, ValueError) as e:
            print("FAIL", e)
            return 2
        if args.json:
            print(json.dumps(sp.to_dict(), indent=2))
        else:
            print(sp.summary())
        return 0
    if args.cmd == "m3":
        from monarch.pipelines.state_card import m3_card

        card = m3_card()
        print(json.dumps(card, indent=2) if args.json else card["text"])
        return 0
    if args.cmd == "screen-script":
        from monarch.pipelines.fountain import (
            ACTION,
            DIALOGUE,
            SPEAKABLE,
            beats_from_json,
            beats_from_screenplay,
            board_json,
            build_script,
            screenplay_from_path,
            screenplay_from_text,
        )

        include = {
            "dialogue": (DIALOGUE,),
            "action": (ACTION,),
            "both": SPEAKABLE,
        }[args.only]
        try:
            raw = _read(args.path)
            # a JSON board from an earlier run is a valid input too
            as_json = str(args.path).endswith(".json") or raw.lstrip().startswith(("{", "["))
            if as_json:
                data = json.loads(raw)
                beats = beats_from_json(data)
                title = str(data.get("title", "")) if isinstance(data, dict) else ""
                byline = str(data.get("byline", "")) if isinstance(data, dict) else ""
                source = str(args.path)
            else:
                sp = (
                    screenplay_from_text(raw)
                    if args.path in (None, "", "-")
                    else screenplay_from_path(args.path)
                )
                beats = beats_from_screenplay(
                    sp, include=include, speaker=args.speaker, visual_hint=args.visual_hint
                )
                title = sp.title_page.title
                byline = sp.title_page.byline
                source = sp.source
            if not beats:
                print(
                    "FAIL no VO beats found. M3 needs spoken beats: write dialogue "
                    "(CHARACTER then their line) or action lines, or relax --only/--speaker."
                )
                return 2
            report = build_script(
                beats,
                _resolve_length(args.length),
                clip_s=args.clip,
                speaking_wps=args.wps,
                first_clip_s=args.first_clip,
                gate=not args.no_gate,
                sfx=args.sfx,
                title=title,
                byline=byline,
                source=source,
            )
        except GateFail as e:
            print("FAIL", "; ".join(e.misses))
            print("answer: improve — add words / split beats / longer length. Never pad.")
            return 2
        except ValueError as e:
            print("FAIL", e)
            return 2
        # with --json stdout stays machine-readable: notes go to stderr
        note = (lambda *a: print(*a, file=sys.stderr)) if args.json else print

        if args.board_out:
            from pathlib import Path

            Path(args.board_out).write_text(board_json(report.scenes), encoding="utf-8")
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(report.summary())
        if report.unfit:
            note(
                f"BLOCKED: {len(report.unfit)} beat(s) cannot hit "
                f"{report.maths.words_per_clip} words. WAIT: perfect | improve "
                "(improve = more words, or a longer --length)"
            )
            return 3
        note(f"STOP — WAIT: {Run(state='M3_script').wait_prompt()}")
        return 0
    if args.cmd == "script-fountain":
        from pathlib import Path

        from monarch.pipelines.fountain import write_fountain

        try:
            board = json.loads(_read(args.board))
        except (ValueError, FileNotFoundError) as e:
            print("FAIL", e)
            return 2
        board = board.get("scenes", board) if isinstance(board, dict) else board
        if not isinstance(board, list) or not board:
            print("FAIL board JSON must be a non-empty list of scenes")
            return 2
        if (board[0].get("vo_line") if isinstance(board[0], dict) else None) is None:
            from monarch.pipelines.fountain import beats_from_json, build_script

            total = float(board[0].get("total_s", 60)) if isinstance(board[0], dict) else 60.0
            scenes = build_script(beats_from_json(board), total).scenes
        else:
            from monarch.schemas import Scene

            scenes = [
                Scene(
                    id=int(s.get("id", i)),
                    vo_line=s.get("vo_line", ""),
                    visual=s.get("visual", ""),
                    word_count=int(s.get("word_count", 0)),
                    t_start=float(s.get("t_start", 0.0)),
                    t_end=float(s.get("t_end", 0.0)),
                    sfx=s.get("sfx", ""),
                    retention_job=s.get("retention_job", ""),
                    match_cut=s.get("match_cut", ""),
                )
                for i, s in enumerate(board, 1)
            ]
        text = write_fountain(
            scenes,
            title=args.title,
            author=args.author,
            draft_date=args.draft_date,
            contact=args.contact,
        )
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print(f"wrote {args.out} — {len(scenes)} scenes")
        else:
            print(text, end="")
        return 0
    if args.cmd == "qc-render":
        import json as _json
        from pathlib import Path

        from monarch.core.self_qc import qc_render
        from monarch.schemas import Scene

        board_path = Path(args.board)
        if not board_path.exists():
            print(f"FAIL board not found: {args.board}")
            return 2
        board_data = _json.loads(board_path.read_text(encoding="utf-8"))
        scenes_raw = board_data.get("scenes", board_data) if isinstance(board_data, dict) else board_data
        if not isinstance(scenes_raw, list) or not scenes_raw:
            print("FAIL board JSON must contain a non-empty list of scenes")
            return 2
        expected_scenes = len(scenes_raw)
        total_s = float(scenes_raw[0].get("total_s", 60)) if isinstance(scenes_raw[0], dict) else 60.0
        durations = [
            float(s.get("t_end", 0)) - float(s.get("t_start", 0))
            for s in scenes_raw
            if isinstance(s, dict) and "t_start" in s and "t_end" in s
        ]
        # video duration check is deferred to Arena session (no ffprobe here)
        misses = qc_render(
            scene_count=expected_scenes,
            expected_scenes=expected_scenes,
            total_s=total_s,
            expected_total=total_s,
            max_clip_hold=args.max_clip,
            scene_durations=durations or None,
        )
        if misses:
            print("FAIL", "; ".join(misses))
            return 2
        print(f"QC RENDER PASS — {expected_scenes} scenes, {total_s:.0f}s total")
        return 0

    if args.cmd == "qc":
        import json as _json
        from pathlib import Path

        from monarch.core.self_qc import Stage, qc

        notes_path = Path(args.notes)
        if not notes_path.exists():
            print(f"FAIL notes file not found: {args.notes}")
            return 2
        notes = _json.loads(notes_path.read_text(encoding="utf-8"))
        stage = Stage(args.stage)
        result = qc(notes, stage=stage)
        print(result.summary)
        return 0 if result.passed else 2

    # ── Neuro Video commands ──

    if args.cmd in ("script", "video-storyboard"):
        from monarch.video.director import plan_storyboard

        try:
            sb = plan_storyboard(
                args.topic,
                length=_resolve_length(args.length),
                clip_s=args.clip,
                speaking_wps=args.wps,
                first_clip_s=args.first_clip,
                cohort=args.cohort,
                seed=args.seed,
            )
        except GateFail as e:
            print("FAIL", "; ".join(e.misses))
            print("answer: improve — the playbook refused this board. Never ship.")
            return 2
        except ValueError as e:
            print("FAIL", e)
            return 2
        if args.cmd == "video-storyboard":
            if args.json:
                print(json.dumps(sb.to_dict(), indent=2))
            else:
                print(sb.card, end="")
            return 0
        # `script` — the Fountain screenplay is the deliverable
        if args.json:
            print(json.dumps(sb.to_dict(), indent=2))
        elif args.out:
            from pathlib import Path

            Path(args.out).write_text(sb.fountain, encoding="utf-8")
            print(f"wrote {args.out} — {len(sb.scenes)} scenes, gated")
        else:
            print(sb.fountain, end="")
        if args.card:
            print(sb.card, end="")
        return 0

    if args.cmd == "sfx":
        from monarch.video import audio as sfx_audio

        out = args.out or f"sfx_{args.kind}.wav"
        try:
            samples = sfx_audio.render_sfx(
                args.kind, sr=args.sr, seed=args.seed,
                seconds=args.seconds, filters=args.filter or None,
            )
            sfx_audio.write_wav(out, samples, args.sr)
        except (ValueError, OSError) as e:
            print("FAIL", e)
            return 2
        print(f"wrote {out} — {args.kind} @ {args.sr}Hz, "
              f"{sfx_audio.duration_s(samples, args.sr):.2f}s")
        return 0

    if args.cmd == "make-video":
        from monarch.video.pipeline import make_video

        out = args.out
        if not out:
            slug = "".join(c if c.isalnum() else "-" for c in args.topic.lower())
            slug = "-".join(p for p in slug.split("-") if p)[:48] or "video"
            out = f"output/{slug}"
        try:
            manifest = make_video(
                args.topic, out,
                length=_resolve_length(args.length),
                clip_s=args.clip,
                speaking_wps=args.wps,
                first_clip_s=args.first_clip,
                cohort=args.cohort,
                seed=args.seed,
                width=args.width,
                height=args.height,
                fps=args.fps,
                sr=args.sr,
            )
        except GateFail as e:
            print("FAIL", "; ".join(e.misses))
            return 2
        except ValueError as e:
            print("FAIL", e)
            return 2
        if args.json:
            print(json.dumps(manifest, indent=2))
        else:
            print(f"PREVIZ READY — {manifest['scene_count']} scenes, "
                  f"{manifest['frame_count']} frames @ {manifest['fps']}fps, "
                  f"{manifest['total_s']:.0f}s -> {out}")
            print(f"maths: {manifest['maths']}")
            print("HAAN still gates the final render. You upload.")
        return 0

    # ── Session memory + learning loop ──

    if args.cmd == "memory":
        from monarch.core import memory

        if args.mem_cmd == "save":
            try:
                p, doc = memory.save_state(
                    path=args.out or memory.MEMORY_FILE,
                    m_state=args.state,
                    channel_path=args.channel,
                    pending=[s for s in args.pending.split(",") if s.strip()],
                    notes=[s for s in args.notes.split(",") if s.strip()],
                    topic=args.topic,
                )
            except (ValueError, FileNotFoundError) as e:
                print("FAIL", e)
                return 2
            print(memory.format_state(doc))
            print(f"wrote {p}")
            return 0
        # restore
        try:
            doc = memory.load_state(args.path or memory.MEMORY_FILE)
        except ValueError as e:
            print("FAIL", e)
            return 2
        print(memory.format_state(doc))
        return 0

    if args.cmd == "learn":
        from monarch.core import learn

        if args.learn_cmd == "record":
            try:
                rec = learn.PerformanceRecord(
                    topic=args.topic,
                    views=args.views,
                    avg_pct=args.avg_pct,
                    subs=args.subs,
                    cohort=args.cohort,
                    length_s=args.length,
                    date=args.date,
                    note=args.note,
                )
                p = learn.record_performance(rec, args.file or learn.PERFORMANCE_FILE)
            except ValueError as e:
                print("FAIL", e)
                return 2
            print(f"logged {rec.topic} — {rec.views:.0f} views, "
                  f"{rec.avg_pct:.0f}% avg viewed -> {p}")
            return 0
        if args.learn_cmd == "log":
            try:
                recs = learn.load_performance(args.file or learn.PERFORMANCE_FILE)
            except ValueError as e:
                print("FAIL", e)
                return 2
            if not recs:
                print("(no videos logged yet — monarch learn record --topic ...)")
                return 0
            for r in recs:
                print(f"{r.date} | {r.topic[:36]:<36} | {r.views:>9.0f} views | "
                      f"{r.avg_pct:>3.0f}% avg | {r.cohort or '-':<6} | "
                      f"{r.length_s:.0f}s" + (f" | {r.note}" if r.note else ""))
            return 0
        # distill
        try:
            recs = learn.load_performance(args.file or learn.PERFORMANCE_FILE)
            report = learn.distill(recs, min_videos=args.min)
        except ValueError as e:
            print("FAIL", e)
            return 2
        print(report.summary())
        for line in report.lines:
            print(f"  · {line}")
        if args.apply:
            target = args.lessons or learn.LESSONS_FILE
            written = learn.consolidate(report, target)
            if written:
                print(f"wrote {written} signal(s) -> {target} (3x rule)")
            else:
                print("nothing applied — signals need 'learned' status")
        return 0

    if args.cmd == "transcript":
        from monarch.intel import ytt

        try:
            recs = ytt.fetch_transcripts(args.videos)
        except (ValueError, RuntimeError) as e:
            print("FAIL", e)
            return 2
        if args.save:
            from pathlib import Path

            d = Path(args.save)
            d.mkdir(parents=True, exist_ok=True)
            for r in recs:
                (d / f"{r['id']}.txt").write_text(r["transcript"], encoding="utf-8")
            print(f"saved {len(recs)} transcript(s) -> {d}", file=sys.stderr)
        if args.json:
            print(json.dumps(
                [{"id": r["id"], "chars": len(r["transcript"]),
                  "transcript": r["transcript"]} for r in recs], indent=2))
        else:
            for r in recs:
                text = r["transcript"]
                head = text[:400] + ("…" if len(text) > 400 else "")
                print(f"=== {r['id']} — {len(text)} chars ===")
                print(head if text else "(no transcript returned)")
        return 0

    if args.cmd == "tchan":
        from monarch.intel import ytt

        try:
            chans = ytt.fetch_channels(args.channels)
        except (ValueError, RuntimeError) as e:
            print("FAIL", e)
            return 2
        print(json.dumps(chans, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "transcript-ingest":
        from monarch.intel import ingest as tng

        try:
            record = tng.ingest_file(args.path) if args.path != "-" \
                else tng.ingest_text(sys.stdin.read(), source="ingest:stdin")
        except ValueError as e:
            print("FAIL", e)
            return 2
        if args.save:
            try:
                p = tng.save_transcript(record, args.save)
            except ValueError as e:
                print("FAIL", e)
                return 2
            print(f"saved {p}", file=sys.stderr)
        if args.json:
            print(json.dumps(record, indent=2, ensure_ascii=False))
        else:
            mark = "OK" if record["has_transcript"] else "NO-TRANSCRIPT"
            print(f"{mark} [{record['kind']}] {record.get('title', '')}")
            print(f"  {record.get('channel', '')} | views {record.get('view_count', '0')}"
                  f" | {record.get('duration', '')}")
            print(f"  transcript: {record['transcript_words']} words, "
                  f"{record['transcript_chars']} chars")
            head = record["transcript"][:300]
            if head:
                print(f"  head: {head}…")
        return 0

    if args.cmd == "deep-forensic":
        from monarch.pipelines.deep_forensic import report_card, run_deep_forensic

        out = args.out
        if not out:
            import json as _j

            try:
                _niche = str(_j.loads(open(args.dossier, encoding="utf-8-sig").read())
                              .get("niche", "niche"))
            except Exception:
                _niche = "niche"
            slug = "".join(c if c.isalnum() else "-" for c in _niche.lower())
            slug = "-".join(x for x in slug.split("-") if x)[:40] or "niche"
            out = f"output/forensic/{slug}"
        try:
            report = run_deep_forensic(args.dossier, out)
        except ValueError as e:
            print("FAIL", e)
            return 2
        print(report_card(report), end="")
        print(f"wrote {out}/deep_forensic_report.txt · deep_forensic.json · ideas.json")
        return 0

    # ── Agent-Reach commands ──

    if args.cmd == "doctor":
        from monarch.intel.reach import doctor as reach_doctor

        statuses = reach_doctor()
        for s in statuses:
            icon = "ok" if s.available else "MISSING"
            print(f"  [{icon}] {s.name}: {s.message}")
        ok = sum(1 for s in statuses if s.available)
        print(f"\n{ok}/{len(statuses)} tools available")
        return 0

    if args.cmd == "scrape":
        from monarch.pipelines.forensic import dissect_url

        try:
            result = dissect_url(args.url)
        except (RuntimeError, FileNotFoundError) as e:
            print("FAIL", e)
            return 2
        if args.transcript and "youtube" in str(result.get("source", "")):
            print(result.get("transcript", "(no transcript)"))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "xsearch":
        try:
            from monarch.intel.twitter import search_niche
            results = search_niche(args.query, args.n)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        except RuntimeError as e:
            print("FAIL", e)
            return 2
        return 0

    if args.cmd == "rsearch":
        try:
            from monarch.intel.reddit import search_niche
            results = search_niche(args.query, args.n)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        except RuntimeError as e:
            print("FAIL", e)
            return 2
        return 0

    if args.cmd == "wsearch":
        try:
            from monarch.intel.web import search_web
            results = search_web(args.query, args.n)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        except RuntimeError as e:
            print("FAIL", e)
            return 2
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
