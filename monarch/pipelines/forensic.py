from pathlib import Path

from monarch.core.missing import missing


def dissect(transcript_path: str) -> dict:
    p = Path(transcript_path)
    if not p.exists():
        raise FileNotFoundError(missing(f"transcript at {transcript_path}"))
    text = p.read_text(encoding="utf-8")
    words = text.split()
    return {"path": str(p), "chars": len(text), "words": len(words)}
