"""Monarch Video — autonomous video production, stdlib only.

The Neuro-Psychology Playbook (``monarch/playbook/neuro_psychology.md``)
drives every module here:

* :mod:`monarch.video.director`   — storyboard + Fountain screenplay, N-law tags
* :mod:`monarch.video.engine`     — procedural 1080x1920 frames (PNG, no deps)
* :mod:`monarch.video.audio`      — psychoacoustic SFX + DSP filters (WAV)
* :mod:`monarch.video.compositor` — Ken Burns camera motion + timeline stitcher
* :mod:`monarch.video.pipeline`   — ``make_video`` end-to-end

No render, no upload: everything stops before the HAAN gate, unchanged.
"""

from __future__ import annotations

from monarch.video.director import (
    NEURO_DRIVERS,
    Storyboard,
    plan_storyboard,
    render_box_card,
)
from monarch.video.pipeline import make_video

__all__ = [
    "NEURO_DRIVERS",
    "Storyboard",
    "make_video",
    "plan_storyboard",
    "render_box_card",
]
