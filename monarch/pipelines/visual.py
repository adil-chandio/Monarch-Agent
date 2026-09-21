from monarch.core.haan import require_haan
from monarch.core.state_machine import STATES
from monarch.schemas import Channel, Scene
from monarch.visual.prompts import animation_paragraph

STAGES = STATES


def run_prompts(scenes: list[Scene], channel: Channel, clip_s: float) -> list[str]:
    out = []
    for i, s in enumerate(scenes):
        last = i == len(scenes) - 1
        nxt = scenes[i + 1].visual if not last else ""
        out.append(
            animation_paragraph(
                s, channel, clip_s=clip_s, next_match=nxt, is_last=last
            )
        )
    return out


def run_generate(operator: str, *_a, **_k) -> str:
    require_haan(operator, "render")
    return "HAAN accepted — Arena Agent Mode generates VO + scenes."
