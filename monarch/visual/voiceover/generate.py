from monarch.core.haan import require_haan
from monarch.schemas import Channel, Scene


def generate_voiceover(operator: str, scenes: list[Scene], channel: Channel) -> str:
    require_haan(operator, "voiceover")
    if channel.vo_mode == "BAKED":
        raise ValueError("BAKED mode has no separate VO file")
    return " ".join(s.vo_line for s in scenes)
