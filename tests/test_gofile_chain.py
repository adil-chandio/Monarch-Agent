"""Gofile-first upload chain (operator order 2026-09-28).

All tests are network-free: transport functions are monkeypatched.
Laws under test: real errors reported per attempt (no invented
links), gofile primary -> tmpfiles -> GitHub rail, link file written
on gofile success, fail-closed size/missing guards.
"""

from __future__ import annotations

import json

import pytest
from PIL import Image

import monarch.core.gofile as G
from monarch.cli import main


@pytest.fixture()
def small_png(tmp_path):
    p = tmp_path / "clip.png"
    Image.new("RGB", (8, 8), (6, 6, 10)).save(p)
    return p


def test_multipart_header_shape(tmp_path):
    p = tmp_path / "f.bin"
    p.write_bytes(b"AB" * 10)
    body, ctype = G._multipart("file", p)
    assert ctype.startswith("multipart/form-data; boundary=----MonarchBoundary")
    assert body.startswith(b"------MonarchBoundary")          # -- boundary
    assert b'filename="f.bin"' in body and body.endswith(b"--\r\n")


def test_chain_gofile_primary(tmp_path, small_png, monkeypatch):
    monkeypatch.setattr(G, "gofile_upload",
                        lambda p, timeout=120: "https://gofile.io/d/OK1")
    res = G.upload_deliverable(small_png)
    assert res["host"] == "gofile" and res["link"] == "https://gofile.io/d/OK1"
    assert res["expires"] == "never"
    assert "gofile_error" not in res and res["bytes"] == small_png.stat().st_size


def test_chain_tmpfiles_fallback(tmp_path, small_png, monkeypatch):
    def boom(p, timeout=120):
        raise ValueError("gofile upload: SSL_error_simulated")
    monkeypatch.setattr(G, "gofile_upload", boom)
    monkeypatch.setattr(G, "tmpfiles_upload",
                        lambda p, timeout=60: "https://tmpfiles.org/1/x.png")
    res = G.upload_deliverable(small_png)
    assert res["host"] == "tmpfiles" and res["expires"] == "1h"
    assert "SSL_error_simulated" in res["gofile_error"]


def test_chain_github_rail_last(tmp_path, small_png, monkeypatch):
    def boom(p, timeout=120):
        raise ValueError("gofile down")
    def boom2(p, timeout=60):
        raise ValueError("tmpfiles down")
    monkeypatch.setattr(G, "gofile_upload", boom)
    monkeypatch.setattr(G, "tmpfiles_upload", boom2)
    monkeypatch.setattr(G, "upload_render",
                        lambda p, label=None: {
                            "browser_url": "https://github.com/rail",
                            "commit": "c0ffee0", "sha256": "ab" * 32})
    res = G.upload_deliverable(small_png, label="x")
    assert res["host"] == "github-rail"
    assert res["link"] == "https://github.com/rail"
    assert res["gofile_error"] == "gofile down"
    assert res["tmpfiles_error"] == "tmpfiles down"


def test_missing_and_oversize_fail_closed(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        G.upload_deliverable(tmp_path / "ghost.mp4")
    big = tmp_path / "big.mp4"
    big.write_bytes(b"\0" * (G.SIZE_CAP + 1))
    with pytest.raises(ValueError, match="MB"):
        G.upload_deliverable(big)


def test_gofile_server_real_error_shape():
    """A payload-shape failure surfaces as a real, grep-able error."""
    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"not-json"
    orig = G.urllib.request.urlopen
    G.urllib.request.urlopen = lambda *a, **k: FakeResp()
    try:
        with pytest.raises(ValueError, match="gofile servers:"):
            G.gofile_server()
    finally:
        G.urllib.request.urlopen = orig


def test_gofile_upload_writes_link_file(tmp_path, small_png, monkeypatch):
    d = {"calls": []}

    def fake_server(timeout=15):
        return "store1"

    def fake_http_json(url, *, data=None, content_type=None, timeout=15):
        d["calls"].append(url)
        assert "store1.gofile.io" in url and data and content_type
        return {"data": {"downloadPage": "https://gofile.io/d/LNK9"}}
    monkeypatch.setattr(G, "gofile_server", fake_server)
    monkeypatch.setattr(G, "_http_json", fake_http_json)
    monkeypatch.chdir(tmp_path)
    link = G.gofile_upload(small_png)
    assert link == "https://gofile.io/d/LNK9"
    assert (tmp_path / "output/gofile_link.txt").read_text().strip() == link
    assert len(d["calls"]) == 1


def test_cli_upload_reports_chain(tmp_path, small_png, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(G, "gofile_upload",
                        lambda p, timeout=120: "https://gofile.io/d/CLI1")
    rc = main(["upload", str(small_png), "--label", "chain probe"])
    out = capsys.readouterr().out
    assert rc == 0 and "via gofile" in out and "gofile.io/d/CLI1" in out
    rc2 = main(["upload", str(tmp_path / "ghost.mp4")])
    assert rc2 == 2 and "FAIL" in capsys.readouterr().out
