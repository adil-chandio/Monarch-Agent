from __future__ import annotations

import argparse
import json
import sys

from monarch import __version__
from monarch.core.haan import require_haan
from monarch.core.scene_math import compute_math, maths_line
from monarch.core.state_machine import STATES, Run
from monarch.core.words import count_words
from monarch.core.gates import GateFail, gate_idea, gate_title
from monarch.schemas import Idea


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

    srh = sub.add_parser("search")
    srh.add_argument("query")
    hun = sub.add_parser("hunt")
    hun.add_argument("niche")

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
        from monarch.core.channels import load_channel
        from dataclasses import asdict

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
    return 1


if __name__ == "__main__":
    sys.exit(main())
