from __future__ import annotations

import argparse
import json
import sys

from monarch import __version__
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
    sub = p.add_subparsers(dest="cmd", required=True)

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

    args = p.parse_args(argv)

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

        print(
            json.dumps(
                {
                    "gemini": has_gemini(),
                    "youtube_data": has_youtube_key(),
                    "youtube_upload_oauth": has_youtube_upload(),
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

    return 1


if __name__ == "__main__":
    sys.exit(main())
