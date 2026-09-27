from monarch.core.dna import dna_complete, empty_dna
from monarch.schemas import ViralDNA


def extract_and_elevate(channel: str, partial: ViralDNA | None = None) -> ViralDNA:
    d = partial or empty_dna(channel)
    if not dna_complete(d):
        d.elevate_notes = (d.elevate_notes + " incomplete DNA — do not clone winners").strip()
    return d
