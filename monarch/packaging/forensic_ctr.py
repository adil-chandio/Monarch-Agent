from __future__ import annotations

from pathlib import Path

from monarch.core.dna import empty_dna
from monarch.core.missing import missing
from monarch.schemas import ViralDNA


def reverse_packaging(niche: str, transcript_dir: str | Path | None = None) -> ViralDNA:
    """Needs local transcripts. Will not invent scrape results."""
    if not transcript_dir:
        raise ValueError(missing("transcript_dir (local .txt/.vtt of winners)"))
    p = Path(transcript_dir)
    files = list(p.glob("*.txt")) + list(p.glob("*.vtt"))
    if not files:
        raise ValueError(missing(f"transcript files in {p}"))
    dna = empty_dna(niche)
    dna.structure = f"local files: {len(files)} — run LLM forensic next"
    return dna
