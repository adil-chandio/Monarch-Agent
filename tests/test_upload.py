"""Upload rail tests - the legal-egress gofile (git deliverables branch).

Sandbox egress is github/pypi only; gofile + release assets are
TLS-blocked. The rail: deliverables branch, asset commit, tip-diet
commit, sha256 measurement. Live-network tests skip gracefully when
git egress is unavailable; pure logic (sha, guards) always runs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.core.upload import sha256_of, upload_render


def test_sha256_stable_and_hex():
    p = Path("/tmp/mn_sha_probe")
    p.write_bytes(b"monarch" * 1000)
    a = sha256_of(p)
    b = sha256_of(p)
    assert a == b and len(a) == 64 and a == a.lower()
    p.unlink()


def test_missing_file_fails_closed(tmp_path):
    with pytest.raises(ValueError):
        upload_render(tmp_path / "ghost.mp4")


def test_oversize_fails_closed(tmp_path):
    big = tmp_path / "big.mp4"
    with big.open("wb") as f:
        f.truncate(91 * 1024 * 1024)     # sparse - instant, 0 real bytes
    try:
        with pytest.raises(ValueError, match="90 MB"):
            upload_render(big)
    finally:
        big.unlink(missing_ok=True)


def _egress_ok() -> bool:
    r = subprocess.run(["git", "ls-remote", "--heads",
                        "https://github.com/adil-chandio/Monarch-Agent.git"],
                       capture_output=True, text=True, timeout=30)
    return r.returncode == 0


@pytest.mark.skipif(not _egress_ok(), reason="git egress unavailable")
def test_live_upload_roundtrip(tmp_path):
    f = tmp_path / "roundtrip_probe.txt"
    f.write_bytes(b"monarch upload law probe \n" * 500)
    res = upload_render(f, label="probe (safe to ignore)")
    assert res["bytes"] == f.stat().st_size
    assert res["sha256"] == sha256_of(f)
    assert "/raw/deliverables/" in res["browser_url"] or \
        "blob/deliverables" in res["browser_url"]
    assert res["commit"]


def test_cli_upload_fail_closed(capsys, tmp_path):
    rc = main(["upload", str(tmp_path / "nope.mp4")])
    assert rc == 2 and "FAIL" in capsys.readouterr().out


def test_live_upload_idempotent(tmp_path):
    """Same bytes re-uploaded: rail must NOT die on 'nothing to commit'."""
    f = tmp_path / "same.mp4"
    f.write_bytes(b"IDEMPOTENT-PROBE-BYTES-\x00\x01")
    a = upload_render(f, label="idempotency probe 1 (safe)",
                      keep_on_tip=True)
    b = upload_render(f, label="idempotency probe 2 (safe)",
                      keep_on_tip=True)
    assert a["commit"] == b["commit"]
    upload_render(f, label="idempotency probe diet (safe)")  # tip stays lean
