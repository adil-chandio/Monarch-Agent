from monarch.core.gates import gate_scenes
from monarch.core.scene_math import compute_math
from monarch.schemas import Scene


def write_script(scenes: list[Scene], total_s: float) -> list[Scene]:
    m = compute_math(total_s)
    gate_scenes(scenes, m.words_per_clip)
    return scenes
