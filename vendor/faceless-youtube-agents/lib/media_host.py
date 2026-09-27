import requests
from pathlib import Path

from lib.config import FILE_HOST_URL


def upload_file(file_path: str) -> str:
    """Upload a local file and return a public URL.

    Default uses file.io (free, auto-deletes after first download).
    Set FILE_HOST_URL in .env to use a custom endpoint.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if "file.io" in FILE_HOST_URL:
        return _upload_fileio(file_path)
    else:
        return _upload_generic(file_path)


def _upload_fileio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://file.io",
            files={"file": (Path(file_path).name, f)},
            data={"expires": "1d"},
            timeout=600,
        )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"file.io upload failed: {data}")
    url = data["link"]
    print(f"  Uploaded to file.io: {url}")
    return url


def _upload_generic(file_path: str) -> str:
    """Upload to a custom endpoint that accepts multipart file upload and returns {url: ...}."""
    with open(file_path, "rb") as f:
        resp = requests.post(
            FILE_HOST_URL,
            files={"file": (Path(file_path).name, f)},
            timeout=600,
        )
    resp.raise_for_status()
    data = resp.json()
    url = data.get("url") or data.get("link") or data.get("download_url", "")
    if not url:
        raise RuntimeError(f"Upload response missing URL: {data}")
    print(f"  Uploaded: {url}")
    return url
