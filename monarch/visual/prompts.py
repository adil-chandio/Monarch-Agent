from __future__ import annotations

from monarch.core.audio_safe import audio_safe
from monarch.schemas import Channel, Scene
from monarch.visual.negatives_text import NEGATIVE_PROSE

MAX_CHARS = 2500


def animation_paragraph(
    scene: Scene,
    channel: Channel,
    *,
    clip_s: float,
    next_match: str = "",
    is_last: bool = False,
) -> str:
    if not channel.character_lock.strip():
        raise ValueError("This is missing, could you provide it: character_lock.")
    lock = channel.character_lock.strip()
    props = scene.visual or "the stickman only"
    action = scene.visual or "stands and gestures with one arm"
    bg = "a hand-drawn doodle background in the same flat 2D style, simple motion only"
    vo = audio_safe(scene.vo_line.strip())

    if channel.vo_mode == "BAKED":
        voice = channel.voice_lock.strip() or (
            "spoken by a warm friendly male narrator in his early thirties with a "
            "neutral North American accent, medium-low pitch, relaxed conversational "
            "pace, clear articulation, gentle enthusiasm, no dramatic emphasis and no announcer tone"
        )
        audio = (
            f'He says "{vo}" {voice} He begins speaking within the first half second '
            "and finishes the full line before the clip ends with no trailing silence "
            "and no cut-off words, mouth moving naturally in sync, eyes blinking occasionally."
        )
    else:
        audio = (
            "There is no speech, no dialogue and no vocal audio of any kind, "
            "and his mouth stays closed except for natural expression."
        )

    match = ""
    if not is_last:
        match = (
            " The last half-second matches the first half-second of the next clip on "
            f"{next_match or 'pose and facing direction'}."
        )

    para = (
        f"This is a {clip_s:g}-second hand-drawn 2D animated clip of {lock} "
        f"Prop palette: {props}. Nothing else appears. "
        f"He {action}. Background: {bg}. {audio}{match} {NEGATIVE_PROSE} "
        "Timeline starts at 0:00. Motion stays simple and smooth."
    )
    para = " ".join(para.split())
    if len(para) > MAX_CHARS:
        raise ValueError(f"prompt {len(para)} chars > {MAX_CHARS}")
    if "\n" in para:
        raise ValueError("animation prompt must be one paragraph")
    return para
