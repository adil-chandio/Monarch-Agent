"""Forensic-sweep wave (2026-09-28): flaws the microscope found, pinned
as laws. docs/CHAOS_MAX_FORENSIC.md findings F1 (zoom-law breach in our
own compositor) and F2 (tipeline walrus typo); Motion clamp defense."""

from __future__ import annotations

import pytest

from monarch.video.compositor import Motion, plan_camera


V6_ZOOM_MAX = 1.08   # docs/VIRAL_SHORTS_V6.md miss #6 - never above


def test_motion_dataclass_clamps_any_caller():
    m = Motion("zoom_in", 1.0, 1.30)
    assert m.zoom_to == V6_ZOOM_MAX
    m2 = Motion("zoom_out", 0.8, 1.0)
    assert m2.zoom_from == 1.0          # below 1.0 is also nonsense


def test_motion_table_literals_within_band():
    from monarch.video import compositor as C
    for name in ("_OPEN", "_ALTERNATE", "_HOLD"):
        table = getattr(C, name)
        for m in (table if isinstance(table, (tuple, list)) else (table,)):
            assert 1.0 <= m.zoom_from <= V6_ZOOM_MAX, (name, m)
            assert 1.0 <= m.zoom_to <= V6_ZOOM_MAX, (name, m)


def test_plan_camera_zoom_band_all_roles_seeds():
    roles = ("hook", "body", "payoff", "payoff+cua", "cua", "body2")
    for seed in range(8):
        for sid in range(1, 61):
            m = plan_camera(sid, roles[sid % len(roles)], seed)
            for z in (m.zoom_from, m.zoom_to):
                assert 1.0 <= z <= V6_ZOOM_MAX, (sid, seed, m)
            # a zoom MOVE stays a nudge (<= 8 percent)
            assert abs(m.zoom_to - m.zoom_from) <= 0.0801  # float-safe 8%


def test_open_snap_still_snaps_after_clamp():
    m = plan_camera(1, "hook", 0)
    assert m.kind == "zoom_in"
    assert m.zoom_to > m.zoom_from       # frame one still moves (N1)
