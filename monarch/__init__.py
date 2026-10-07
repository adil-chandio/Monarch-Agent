"""Monarch — faceless YouTube intelligence. Gates, maths, states are real."""

from monarch.core.fountain import Screenplay, parse, parse_file
from monarch.pipelines.fountain import (
    FountainBeat,
    ScriptReport,
    beats_from_lines,
    beats_from_screenplay,
    build_script,
    write_fountain,
)

__version__ = "0.1.0"

__all__ = [
    "FountainBeat",
    "Screenplay",
    "ScriptReport",
    "__version__",
    "beats_from_lines",
    "beats_from_screenplay",
    "build_script",
    "parse",
    "parse_file",
    "write_fountain",
]
