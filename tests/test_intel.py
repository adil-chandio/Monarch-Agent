import json
from monarch.intel.ideas import _parse_ideas
from monarch.intel.export import package_for_human_upload
from monarch.schemas import Channel, Idea, Scene
from pathlib import Path


def test_parse_ideas_json_fence():
    text = """```json
    [{"title":"The ice that refused to melt","hook":"one glacier never died",
      "itch":"incongruity","visual_anchor":"pulsing iceberg"}]
    ```"""
    ideas = _parse_ideas(text)
    assert ideas[0].title.startswith("The ice")


def test_export(tmp_path: Path):
    idea = Idea(
        title="The ice that refused to melt",
        hook="h",
        itch="incongruity",
        visual_anchor="ice",
    )
    p = package_for_human_upload(
        tmp_path / "pkg.json",
        idea=idea,
        titles=[idea.title],
        listing={"privacy": "private"},
        thumbs=[],
        scenes=[Scene(id=1, vo_line="one two three four five six seven")],
        prompts=["para"],
        channel=Channel(id="x", niche="n"),
    )
    doc = json.loads(p.read_text())
    assert "OPERATOR" in doc["upload"]
