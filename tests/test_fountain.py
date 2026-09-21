"""Fountain parser — the elements Monarch M3 depends on."""

from pathlib import Path

import pytest

from monarch.core import fountain
from monarch.core.fountain import (
    ACTION,
    CENTERED,
    CHARACTER,
    DIALOGUE,
    LYRIC,
    NOTE,
    PAGE_BREAK,
    PARENTHETICAL,
    SCENE_HEADING,
    SECTION,
    SYNOPSIS,
    TRANSITION,
)

TITLE_PAGE = """Title:
    THE ICE THAT REFUSED TO MELT
Credit: Written by
Author: Adil Chandio
Draft date: 2026-09-21
Contact: adil@example.com

"""

SCRIPT = """INT. GLACIER - NIGHT #3#

A stickman stands on a blue-white shelf.

VOICEOVER (V.O.)
The ice did not melt. It *waited*.

[[this note must not reach the board]]

> CUT TO:

EXT. VALLEY - DAWN

.MONTAGE - THE LONG THAW

A river argues with the rock.

VOICEOVER (V.O.)
(soft)
It lost. Then it cheated.

@STICKMAN

!The valley floor was gone.

FADE OUT.
"""


def test_title_page_parsed():
    sp = fountain.parse(TITLE_PAGE + SCRIPT)
    assert sp.title_page.title == "THE ICE THAT REFUSED TO MELT"
    assert sp.title_page.author == "Adil Chandio"
    assert sp.title_page.authors == ["Adil Chandio"]
    assert sp.title_page.draft_date == "2026-09-21"
    assert sp.title_page.contact == "adil@example.com"
    assert sp.title_page.byline == "Adil Chandio"


def test_title_page_absent_is_empty():
    sp = fountain.parse("A line of action only.\n")
    assert sp.title_page.is_empty()
    assert sp.elements[0].kind == ACTION


def test_scene_headings_and_slugline_fields():
    sp = fountain.parse(SCRIPT)
    slugs = [e for e in sp.elements if e.kind == SCENE_HEADING]
    assert [e.text for e in slugs] == [
        "INT. GLACIER - NIGHT",
        "EXT. VALLEY - DAWN",
        "MONTAGE - THE LONG THAW",
    ]
    assert slugs[0].slugline.prefix == "INT."
    assert slugs[0].slugline.location == "GLACIER"
    assert slugs[0].slugline.time_of_day == "NIGHT"
    assert slugs[0].slugline.is_interior
    assert slugs[0].scene_number == "3"
    assert not slugs[1].slugline.is_interior
    # forced heading from '.' has no interior/exterior prefix
    assert slugs[2].forced
    assert slugs[2].slugline.location == "MONTAGE - THE LONG THAW"


def test_every_slugline_prefix_variant():
    for text, prefix in [
        ("INT. CAVE - DAY", "INT."),
        ("EXT. RIVER - NIGHT", "EXT."),
        ("INT/EXT CAR - DAY", "INT/EXT"),
        ("INT./EXT. CAR - NIGHT", "INT./EXT."),
        ("EXT/INT HOUSE - DAY", "EXT/INT"),
        ("I/E. PLANE - DAY", "I/E."),
        ("EST. FIELD - DUSK", "EST."),
    ]:
        slug = fountain.parse_slugline(text)
        assert slug is not None, text
        assert slug.prefix == prefix, text
    assert fountain.parse_slugline("I/E. PLANE - DAY").location == "PLANE"


def test_scene_number_in_front_and_at_end():
    assert fountain.parse_slugline("#12# INT. CAVE - DAY").scene_number == "12"
    tail = fountain.parse_slugline("INT. CAVE - DAY #12#")
    assert tail.scene_number == "12"
    assert tail.location == "CAVE"
    assert fountain.parse_slugline("A quiet room, morning light") is None


def test_dialogue_parenthetical_and_extensions():
    sp = fountain.parse(SCRIPT)
    cues = [e for e in sp.elements if e.kind == CHARACTER]
    assert [c.text for c in cues] == ["VOICEOVER", "VOICEOVER", "STICKMAN"]
    assert [c.extension for c in cues] == ["V.O.", "V.O.", ""]
    assert cues[2].forced
    words = [e.text for e in sp.elements if e.kind == DIALOGUE]
    assert words == ["The ice did not melt. It waited.", "It lost. Then it cheated."]
    parens = [e.text for e in sp.elements if e.kind == PARENTHETICAL]
    assert parens == ["(soft)"]
    forced_action = [e for e in sp.elements if e.kind == ACTION and e.forced]
    assert [e.text for e in forced_action] == ["The valley floor was gone."]


def test_forced_action_inside_dialogue_block_stays_dialogue():
    # Fountain ends dialogue at a blank line; an author forcing action must
    # leave the block first.
    sp = fountain.parse("MARA\n!still her line\n\n!this is action\n")
    kinds = [e.kind for e in sp.elements]
    assert kinds == [CHARACTER, DIALOGUE, ACTION]
    assert sp.elements[1].text == "!still her line"
    assert sp.elements[2].forced


def test_emphasis_stripped_but_notes_not_spoken():
    sp = fountain.parse(SCRIPT)
    assert "*" not in " ".join(sp.dialogue)
    assert "note must not reach the board" not in " ".join(e.text for e in sp.elements if e.kind != NOTE)
    assert [e.text for e in sp.elements if e.kind == NOTE] == [
        "this note must not reach the board"
    ]


def test_action_paragraph_joins_lines():
    sp = fountain.parse("A hero walks in\nthe door and stops.\n\nEND OF ACTION\n")
    assert sp.elements[0].kind == ACTION
    assert sp.elements[0].text == "A hero walks in the door and stops."


def test_transitions_centered_lyrics_sections_synopsis():
    text = """> FADE IN:
> the middle of the story <
# Act One
= the hero wants ice cream
~la la la la
CUT TO:
SMASH CUT TO:
===
"""
    sp = fountain.parse(text)
    kinds = [e.kind for e in sp.elements]
    assert kinds == [
        TRANSITION,
        CENTERED,
        SECTION,
        SYNOPSIS,
        LYRIC,
        TRANSITION,
        TRANSITION,
        PAGE_BREAK,
    ]
    assert sp.elements[1].text == "the middle of the story"
    assert sp.elements[2].depth == 1
    assert sp.elements[5].text == "CUT TO:"
    assert not sp.elements[5].forced
    assert sp.elements[6].text == "SMASH CUT TO:"


def test_forced_transition_is_flagged():
    sp = fountain.parse("> CUT TO:\n\nAction.\n")
    assert sp.elements[0].kind == TRANSITION
    assert sp.elements[0].forced


def test_dual_dialogue():
    text = """INT. ROOM - DAY

MARA
Wait.

JONAS ^
No.
"""
    sp = fountain.parse(text)
    cues = [e for e in sp.elements if e.kind == CHARACTER]
    assert [c.text for c in cues] == ["MARA", "JONAS"]
    assert cues[1].dual
    assert not cues[0].dual


def test_boneyard_is_dropped():
    sp = fountain.parse("Visible action.\n\n/*\nINT. SECRET - NIGHT\n\nhidden\n*/\n\nMore action.\n")
    assert [e.text for e in sp.elements] == ["Visible action.", "More action."]


def test_multiline_note_is_one_element():
    sp = fountain.parse("[[first line\nsecond line]]\n\nAction follows.\n")
    notes = [e for e in sp.elements if e.kind == NOTE]
    assert len(notes) == 1
    assert "first line" in notes[0].text and "second line" in notes[0].text
    assert sp.elements[-1].kind == ACTION


def test_escapes_are_literal():
    sp = fountain.parse("\\# not a section\n\n\\.not a slugline\n")
    assert sp.elements[0].kind == ACTION
    assert sp.elements[0].text == "# not a section"
    assert sp.elements[1].kind == ACTION
    assert "not a slugline" in sp.elements[1].text


def test_screenplay_views_and_roundtrip_json():
    sp = fountain.parse(TITLE_PAGE + SCRIPT, source="ice.fountain")
    assert len(sp.scenes) == 3
    assert sp.scenes[0].heading == "INT. GLACIER - NIGHT"
    assert sp.scenes[0].characters == ["VOICEOVER"]
    assert sp.scenes[0].dialogue == ["The ice did not melt. It waited."]
    assert sp.characters == ["VOICEOVER", "STICKMAN"]
    assert sp.counts()[DIALOGUE] == 2
    assert sp.words > 0

    doc = sp.to_dict()
    from monarch.pipelines.fountain import screenplay_from_json

    again = screenplay_from_json(doc)
    assert again.scene_headings == sp.scene_headings
    assert again.title_page.title == sp.title_page.title
    assert [e.to_dict() for e in again.elements] == [e.to_dict() for e in sp.elements]


def test_parse_file(tmp_path: Path):
    p = tmp_path / "ice.fountain"
    p.write_text("\ufeff" + TITLE_PAGE + SCRIPT, encoding="utf-8")
    sp = fountain.parse_file(p)
    assert sp.source == str(p)
    assert sp.title_page.title == "THE ICE THAT REFUSED TO MELT"
    assert "fountain:" in sp.summary()


def test_parse_rejects_none():
    with pytest.raises(ValueError):
        fountain.parse(None)  # type: ignore[arg-type]


def test_crlf_tolerated():
    sp = fountain.parse("INT. CAVE - DAY\r\n\r\nAction here.\r\n")
    assert sp.elements[0].kind == SCENE_HEADING
    assert sp.elements[1].text == "Action here."


def test_all_caps_line_without_next_line_is_not_a_cue():
    sp = fountain.parse("SOMETHING LOUD\n\nINT. CAVE - DAY\n")
    assert sp.elements[0].kind == ACTION
