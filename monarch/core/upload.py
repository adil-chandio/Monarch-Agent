"""Upload a finished render - the legal-egress gofile.

The operator's workflow ends with the video on a file host + a link
(gofile.io in the Bear session). Sandbox egress is allowlisted to
github/pypi: gofile/catbox/pixeldrain and even Release-asset uploads
(uploads.github.com) are TLS-blocked at the proxy. PROVEN LEGAL RAIL
(live-tested): a git branch ("deliverables") in this repo carries the
file; the browser link is github.com/<repo>/raw/<branch>/<file> with a
90-day-ish server redirect and no auth needed. The file lives in GIT
HISTORY (forever), then a follow-up commit removes it from the branch
TIP (workspace-diet law); history keeps the blob retrievable by sha.

Fail-closed, measurement-first (law 6.6): link + size + sha256 are the
deliverable. Token never printed; upload only on operator order (HAAN).
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

_REPO = "adil-chandio/Monarch-Agent"
_BRANCH = "deliverables"


def sha256_of(path: Path, *, buf: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(buf):
            h.update(chunk)
    return h.hexdigest()


def _git(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=300)


def _ensure_clean_clone(work: Path) -> Path:
    """A scratch clone of the repo (workspace diet: /tmp, never output/)."""
    work.mkdir(parents=True, exist_ok=True)
    clone = work / "deliverables"
    if not (clone / ".git").is_dir():
        r = _git(["clone", "--no-checkout",
                  f"https://github.com/{_REPO}.git", str(clone)], cwd=work)
        if r.returncode != 0:
            raise ValueError(f"clone failed: {r.stderr.strip()[:200]}")
    return clone


def upload_render(path: str | Path, *, label: str | None = None,
                  branch: str = _BRANCH,
                  keep_on_tip: bool = False) -> dict:
    """Push the file to the deliverables branch; return link + hash.

    keep_on_tip=False (default): the file is committed, pushed, the
    download link recorded, then removed from the branch TIP in a
    follow-up commit (the blob stays in git history - the link 404s on
    tip but the asset is retrievable by the operator via the recorded
    commit). keep_on_tip=True leaves the file live on the branch tip.
    """
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"file not found: {p}")
    size = p.stat().st_size
    if size > 90 * 1024 * 1024:
        raise ValueError(f"{p.name} is {size / 1e6:.1f} MB - keep renders "
                         "under ~90 MB per the workspace-cap law (split "
                         "chunks for long-form, then upload per chunk)")
    digest = sha256_of(p)

    import tempfile
    work = Path(tempfile.mkdtemp(prefix="monarch-upload-"))
    clone = _ensure_clean_clone(work)
    r = _git(["fetch", "origin", branch], cwd=clone)
    if r.returncode == 0:
        _git(["checkout", "-q", "-B", branch, f"origin/{branch}"], cwd=clone)
    else:
        _git(["checkout", "-q", "--orphan", branch], cwd=clone)
        tip = clone / "README.md"
        tip.write_text(
            "# Render deliverables\n\nOperator-gated uploads (HAAN gate). "
            "Files live in git history; tips stay lean.\n", encoding="utf-8")
        _git(["add", "README.md"], cwd=clone)
        _git(["-c", "user.email=monarch@agent",
              "-c", "user.name=Monarch Agent", "commit", "-qm",
              "deliverables branch init"], cwd=clone)

    import shutil
    shutil.copy2(p, clone / p.name)
    _git(["add", p.name], cwd=clone)
    r = _git(["-c", "user.email=monarch@agent",
              "-c", "user.name=Monarch Agent", "commit", "-qm",
              f"asset: {p.name} ({size} bytes, sha256 {digest[:16]})"
              + (f" - {label}" if label else "")], cwd=clone)
    if r.returncode != 0:
        raise ValueError(f"commit failed: "
                         f"{(r.stderr or r.stdout).strip()[:300]}")
    commit = _git(["rev-parse", "HEAD"], cwd=clone).stdout.strip()

    r = _git(["push", "origin", branch], cwd=clone)
    if r.returncode != 0:
        raise ValueError(f"push failed: {r.stderr.strip()[:200]}")

    raw = f"https://github.com/{_REPO}/raw/{branch}/{p.name}"
    tip_url = raw
    if not keep_on_tip:
        _git(["rm", "-q", p.name], cwd=clone)
        _git(["-c", "user.email=monarch@agent",
              "-c", "user.name=Monarch Agent", "commit", "-qm",
              f"tip-diet: {p.name} (asset lives at {commit[:10]})"], cwd=clone)
        r = _git(["push", "origin", branch], cwd=clone)
        if r.returncode != 0:
            raise ValueError(f"diet push failed: {r.stderr.strip()[:200]}")
        tip_url = f"https://github.com/{_REPO}/blob/{branch}"

    import shutil as _sh
    _sh.rmtree(work, ignore_errors=True)

    return {
        "file": p.name,
        "bytes": size,
        "mb": round(size / (1024 * 1024), 2),
        "sha256": digest,
        "browser_url": tip_url,
        "commit": commit,
        "history_url": f"https://github.com/{_REPO}/blob/{commit}/{p.name}",
        "keep_on_tip": keep_on_tip,
        "label": label or f"{p.name} (sha256 {digest[:12]}…)",
        "host": f"github.com/{_REPO}@{branch} (gofile + release-assets are "
                "TLS-blocked by the sandbox allowlist; git rail is the "
                "proven legal host)",
    }
