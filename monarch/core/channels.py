from __future__ import annotations

from pathlib import Path

from monarch.schemas import Channel

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


def load_channel(path: str | Path) -> Channel:
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    if yaml:
        data = yaml.safe_load(raw)
    else:
        data = _naive_yaml(raw)
    return Channel(
        id=str(data["id"]),
        niche=str(data["niche"]),
        aspect=data.get("aspect", "16:9"),  # type: ignore[arg-type]
        language=str(data.get("language", "en")),
        accent_color=str(data.get("accent_color", "#E8B923")),
        vo_mode=data.get("vo_mode", "SILENT"),  # type: ignore[arg-type]
        character_lock=str(data.get("character_lock", "")),
        voice_lock=str(data.get("voice_lock", "")),
    )


def _naive_yaml(raw: str) -> dict:
    out: dict = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.split("#", 1)[0].strip().strip('"').strip("'")
        out[k.strip()] = v
    return out


