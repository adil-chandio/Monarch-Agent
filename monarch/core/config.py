from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


_load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class Secrets:
    gemini: str
    youtube: str
    yt_client_id: str
    yt_client_secret: str
    yt_refresh: str


def secrets() -> Secrets:
    return Secrets(
        gemini=os.environ.get("GEMINI_API_KEY", "").strip(),
        youtube=os.environ.get("YOUTUBE_API_KEY", "").strip(),
        yt_client_id=os.environ.get("YOUTUBE_CLIENT_ID", "").strip(),
        yt_client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip(),
        yt_refresh=os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip(),
    )


def has_gemini() -> bool:
    return bool(secrets().gemini)


def has_youtube_key() -> bool:
    return bool(secrets().youtube)


def has_youtube_upload() -> bool:
    s = secrets()
    return bool(s.yt_client_id and s.yt_client_secret and s.yt_refresh)
