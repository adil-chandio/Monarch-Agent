"""W-B3 — the PACKAGING KIT emitter: one dir in, a launch kit out.

`monarch package DIR [--shorts] [--topics ...]` writes kit/ into the
render dir:

  title.txt           - the packaging title (+ title-band score)
  description.txt     - hook line, body lines, the AI-DISCLOSURE line
                        (mandatory - the 3-strike shield), on-screen-now
                        pointer (never "link in bio" - miss #13), hashtags
  pinned_comment.txt  - comment bait (+ the condensed-incomplete tease
                        when --topics is passed)
  disclosure.txt      - the standalone disclosure line (copy-paste)
  thumbnail_first_frame.png - FIRST FRAME IS THE THUMBNAIL (Shorts law)
  upload_checklist.txt - the launch gate (LUFS/srt/HAAN reminders)
  package.json        - everything machine-readable (tooling + audit)

Laws wired at generation time: cta_lint (bio-link banned), title band,
disclosure always present, end-screen pointer phrasing.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from monarch.video.slop import DISCLOSURE_LINE, json_load
from monarch.video.shorts import cta_lint, title_check


def _read_board(d: Path) -> list[dict]:
    b = json_load(d / "board.json")
    rows = b if isinstance(b, list) else (b.get("scenes") or b.get("rows") or [])
    return [r for r in rows if isinstance(r, dict)]


def emit_kit(d: str | Path, *, shorts: bool = False, topics: list[str] | None = None,
             title: str | None = None, hashtags: list[str] | None = None,
             channel: str = "@yourchannel") -> dict:
    d = Path(d)
    if not (d / "board.json").is_file():
        raise ValueError(f"board.json missing in {d} - run make-video first")
    board = _read_board(d)
    if not title:
        try:
            title = str(json_load(d / "timeline.json").get("title") or "")
        except (OSError, ValueError):
            title = ""
    title = (title or d.name).strip()

    # --- title law (V6 M14 for shorts; long band otherwise) --------------
    tc = title_check(title) if shorts else {
        "chars": len(title), "ok": 18 <= len(title) <= 60,
        "ideal": False,
        "issues": ([] if 18 <= len(title) <= 60 else
                   [f"{len(title)} chars outside 18-60 long band"])}

    hook = str(board[0].get("vo_line") or "").strip() if board else ""
    body_lines = [f"- {str(r.get('vo_line') or '').strip()}"
                  for r in board[1:4] if r.get("vo_line")]

    end_screen = False
    plan_p = d / "v6_plan.json"
    if plan_p.is_file():
        try:
            end_screen = bool(json_load(plan_p).get("end_screen"))
        except (OSError, ValueError):
            end_screen = False

    # --- description (disclosure MANDATORY; cta_lint enforced) -----------
    # shorts law (miss #13): the description ALWAYS promises the
    # on-screen pointer; when no end screen was burned the checklist
    # flags the gap instead of weakening the promise
    pointer = ("Full video on screen now - tap to watch!" if shorts
               else "Watch the full breakdown on the channel.")
    tags = hashtags or (["#shorts"] if shorts else ["#youtube"])
    desc_lines = [title, "", hook, "", *body_lines, "",
                  pointer, "", DISCLOSURE_LINE, "", " ".join(tags)]
    description = "\n".join(desc_lines)
    # miss #13 enforcement: the bio-link ban is universal; the
    # on-screen-now pointer requirement is the SHORTS law (long-form
    # kits point at the channel instead)
    if "link in bio" in description.lower():
        raise ValueError("description tripped miss #13: link-in-bio is "
                         "TikTok DNA - point at the end screen/channel")
    if shorts:
        cta = cta_lint(description)
        if not cta["ok"]:
            raise ValueError("shorts description tripped the CTA law: "
                             + "; ".join(cta["issues"]))

    # --- pinned comment ---------------------------------------------------
    bait = ("Comment YOUR TOP 3 - and spot what got skipped and censored. "
            "Wrong answers only below.")
    if topics and len(topics) >= 4:
        from monarch.video.shorts import long_to_short
        plan = long_to_short(topics)
        bait += (f"\nFull ranking lives in the long video: {len(plan['show'])}"
                 f" shown, {len(plan['skipped'])} skipped "
                 f"({', '.join(plan['skipped'][:3])}), "
                 f"#{plan['censored'][0]} censored - no WHY details here.")
    pinned = (f"{title} - the parts nobody lists:\n"
              f"{chr(10).join(body_lines) if body_lines else hook}\n\n{bait}")

    # --- files ------------------------------------------------------------
    kit = d / "kit"
    kit.mkdir(exist_ok=True)
    (kit / "title.txt").write_text(title + "\n", encoding="utf-8")
    (kit / "description.txt").write_text(description + "\n", encoding="utf-8")
    (kit / "pinned_comment.txt").write_text(pinned + "\n", encoding="utf-8")
    (kit / "disclosure.txt").write_text(DISCLOSURE_LINE + "\n",
                                        encoding="utf-8")
    thumb_src = d / "frames" / "frame_00001.png"
    thumb = None
    if thumb_src.is_file():
        shutil.copy2(thumb_src, kit / "thumbnail_first_frame.png")
        thumb = "kit/thumbnail_first_frame.png"

    # --- lufs (if a render exists, measure - the checklist says the truth)
    lufs = None
    mp4s = sorted(d.glob("*.mp4"))
    if mp4s:
        try:
            from monarch.video.render import ffmpeg_exe, measure_lufs
            lufs = measure_lufs(ffmpeg_exe(), max(mp4s, key=lambda p: p.stat().st_mtime))
        except Exception:
            lufs = None

    srt_ok = (d / "captions.srt").is_file()
    checklist = [
        f"[{'x' if tc['ok'] else ' '}] title in band ({tc['chars']} chars"
        + ("" if tc["ok"] else f" - FIX: {'; '.join(tc['issues'])}") + ")",
        f"[{'x' if srt_ok else ' '}] captions.srt ships (L6)",
        f"[{'x' if thumb else ' '}] first-frame thumbnail exported",
        f"[{'x' if lufs is not None and -16 <= lufs <= -12 else ' '}] "
        f"master LUFS in band (measured: {lufs if lufs is not None else 'no mp4 yet'})",
        f"[{'x' if end_screen else ' '}] end-screen planned (last 7s, "
        "right 40%)" + ("" if (not shorts or end_screen) else
                        " - FIX: shorts promise 'on screen now', re-render "
                        "with --v6-end-screen"),
        "[ ] final render versioned (..._v1_render.mp4)",
        "[ ] upload = operator HAAN order only",
    ]
    (kit / "upload_checklist.txt").write_text("\n".join(checklist) + "\n",
                                              encoding="utf-8")

    pkg = {
        "title": title, "title_check": tc, "shorts": shorts,
        "hook": hook, "description": description,
        "pinned_comment": pinned, "disclosure": DISCLOSURE_LINE,
        "end_screen": end_screen, "lufs": lufs, "srt": srt_ok,
        "thumbnail": thumb, "kit_dir": str(kit),
        "files": sorted(p.name for p in kit.iterdir()),
    }
    (kit / "package.json").write_text(json.dumps(pkg, indent=2) + "\n",
                                      encoding="utf-8")
    pkg["checklist"] = checklist
    return pkg
