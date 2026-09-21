from monarch.core.audio_safe import audio_safe
from monarch.core.gates import GateFail, gate_idea, gate_scenes, gate_title
from monarch.core.haan import require_haan
from monarch.core.scene_math import compute_math
from monarch.core.state_machine import Run
from monarch.core.words import assert_word_count, count_words
from monarch.schemas import Idea, Scene
import pytest


def test_words():
    assert count_words("This is six words exactly here") == 6
    assert_word_count("one two three four five six", 6)
    with pytest.raises(ValueError):
        assert_word_count("too short", 6)


def test_maths_30s():
    m = compute_math(30, clip_s=3.5)
    assert m.scenes >= 8
    assert 4 <= m.words_per_clip <= 7


def test_generic_idea_fails():
    with pytest.raises(GateFail):
        gate_idea(
            Idea(
                title="Top 10 Bear Attacks",
                hook="bears",
                itch="fear",
                visual_anchor="bear",
            )
        )


def test_open_too_long_fails():
    scenes = [
        Scene(
            id=1,
            vo_line="one two three four five six",
            visual="x",
            word_count=6,
            t_start=0,
            t_end=5,
            retention_job="hook",
        )
    ]
    with pytest.raises(GateFail):
        gate_scenes(scenes, 6)


def test_haan():
    with pytest.raises(PermissionError):
        require_haan("maybe", "render")
    require_haan("haan", "render")


def test_state_cannot_skip_haan():
    r = Run(state="M5b_haan_video")
    with pytest.raises(PermissionError):
        r.advance("")
    assert r.advance("haan") == "M5c_video_qc"


def test_cannot_skip_idea_pick():
    r = Run(state="M2_ideas_plus_top1")
    with pytest.raises(PermissionError):
        r.advance("go")
    assert r.advance("3") == "F1_script_forensic"


def test_title_unpaid():
    with pytest.raises(GateFail):
        gate_title("The day the ice said no", "stickman vs iceberg", False)


def test_audio_safe():
    assert "mallet" in audio_safe("hit with a hammer")
