"""Gofile-first deliverable upload chain (operator order 2026-09-28).

Chain: gofile.io (permanent, no expiry) -> tmpfiles.org (1h fallback)
-> GitHub deliverables rail (the proven in-sandbox host). Every failed
attempt reports its REAL transport error - a link is never claimed
without an actual successful response (law). On gofile success the
link is also written to output/gofile_link.txt.

Production flow (operator note): render and upload in the SAME bash
call so the deliverable never waits - `monarch render ... && monarch
upload out.mp4`.

Stdlib urllib only: no new dependencies (GPU/external tools stay
knowledge-hooks, never dependencies).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from .upload import sha256_of, upload_render

GOFILE_SERVERS = "https://api.gofile.io/servers"
TMPFILES_UPLOAD = "multipart-void"  # replaced in _post; kept for grep-ability
SIZE_CAP = 90 * 1024 * 1024         # same cap as the git rail


def _multipart(field: str, path: Path) -> tuple[bytes, str]:
    b = f"----MonarchBoundary{uuid.uuid4().hex}"
    head = (f"--{b}\r\nContent-Disposition: form-data; name=\"{field}\"; "
            f"filename=\"{path.name}\"\r\n"
            "Content-Type: application/octet-stream\r\n\r\n").encode()
    tail = f"\r\n--{b}--\r\n".encode()
    return head + path.read_bytes() + tail, f"multipart/form-data; boundary={b}"


def _http_json(url: str, *, data: bytes | None = None,
               content_type: str | None = None,
               timeout: float = 15) -> dict:
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    if content_type:
        req.add_header("Content-Type", content_type)
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
        return json.loads(r.read().decode("utf-8", "replace"))


def _err(e: Exception) -> str:
    if isinstance(e, urllib.error.URLError):
        reason = getattr(e, "reason", e)
        return f"{type(reason).__name__}: {reason}"
    return f"{type(e).__name__}: {e}"


def gofile_server(timeout: float = 15) -> str:
    try:
        d = _http_json(GOFILE_SERVERS, timeout=timeout)
        name = d["data"]["servers"][0]["name"]
    except Exception as e:  # transport OR shape - both are real failures
        raise ValueError(f"gofile servers: {_err(e) if not d_shape_ok(e) else e}") from None
    return name


def d_shape_ok(e: Exception) -> bool:
    """True when the failure was payload shape, not transport."""
    return isinstance(e, (KeyError, IndexError, TypeError, json.JSONDecodeError))


def gofile_upload(path: str | Path, timeout: float = 120) -> str:
    """Upload to gofile.io; return the permanent downloadPage link."""
    p = Path(path)
    server = gofile_server(timeout=min(timeout, 15))
    body, ctype = _multipart("file", p)
    try:
        d = _http_json(f"https://{server}.gofile.io/contents/uploadfile",
                       data=body, content_type=ctype, timeout=timeout)
        link = d["data"]["downloadPage"]
    except Exception as e:
        raise ValueError(f"gofile upload: {_err(e)}") from None
    if not link:
        raise ValueError("gofile upload: no downloadPage in response")
    link_p = Path("output/gofile_link.txt")
    link_p.parent.mkdir(parents=True, exist_ok=True)
    link_p.write_text(f"{link}\n", encoding="utf-8")
    return link


def tmpfiles_upload(path: str | Path, timeout: float = 60) -> str:
    """Fallback host (1h expiry) per the operator's researched chain."""
    p = Path(path)
    body, ctype = _multipart("file", p)
    try:
        d = _http_json("https://tmpfiles.org/api/v1/upload",
                       data=body, content_type=ctype, timeout=timeout)
        link = d["data"]["url"]
    except Exception as e:
        raise ValueError(f"tmpfiles upload: {_err(e)}") from None
    if not link:
        raise ValueError("tmpfiles upload: no url in response")
    return link


def upload_deliverable(path: str | Path, *, label: str | None = None,
                       size_cap: int = SIZE_CAP) -> dict:
    """gofile -> tmpfiles -> GitHub rail; the winning attempt wins.

    Returns one dict: file/mb/sha256/host/link/expires + the real
    error text of every failed attempt (gofile_error, tmpfiles_error).
    """
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"file not found: {p}")
    size = p.stat().st_size
    if size > size_cap:
        raise ValueError(f"{p.name} is {size / 1e6:.1f} MB - keep uploads "
                         f"under ~{size_cap // (1024 * 1024)} MB (split "
                         "long-form into chunks)")
    result: dict = {
        "file": p.name,
        "bytes": size,
        "mb": round(size / (1024 * 1024), 2),
        "sha256": sha256_of(p),
    }
    for host, fn, expires in (("gofile", gofile_upload, "never"),
                              ("tmpfiles", tmpfiles_upload, "1h")):
        try:
            link = fn(p)
        except ValueError as e:
            result[f"{host}_error"] = str(e)
            continue
        result.update({"host": host, "link": link, "expires": expires})
        return result
    res = upload_render(p, label=label)
    result.update({"host": "github-rail", "link": res["browser_url"],
                   "expires": "never (git history)",
                   "commit": res["commit"],
                   "gofile_error": result.get("gofile_error"),
                   "tmpfiles_error": result.get("tmpfiles_error")})
    return result
